"""Evaluate consented REAL_STAGED tagged camera recordings against frozen manual labels.

Never generates labels, substitutes synthetic media, or feeds labels into inference.
Recorded media/provenance are operator-declared; this is not forensic authentication.
"""
try:
    from . import bootstrap
except ImportError:
    import bootstrap
import argparse
import csv
import datetime as dt
import json
from pathlib import Path
import time
import cv2
import numpy as np
from steplock.procedure.recipe import Recipe
from steplock.procedure.engine import ProcedureEngine
from steplock.sources.replay import video_frames, inspect_video, hash_file
from steplock.vision.aruco import Detector
from scripts.eval_metrics import CLASSES, match_events, rates
from scripts.inspect_external_video import dump, write_csv


def validate_population(labels, registered, recipe_hash, root=bootstrap.ROOT):
    if labels.get("population") != "REAL_STAGED" or labels.get("annotation_status") != "FROZEN" or labels.get("reviewed_before_inference") is not True:
        raise ValueError("Require independently reviewed, frozen REAL_STAGED labels before inference")
    if labels.get("recipe_sha256") != recipe_hash or len(labels.get("capture_provenance", "").strip()) < 20:
        raise ValueError("Recipe hash and actual-camera provenance are required")
    clips = labels.get("clips", [])
    if not clips:
        raise ValueError("No real recordings provided; no physical metrics can be produced")
    registered = {row["clip_id"]: row for row in registered}
    ids = set()
    validated = []
    for truth in clips:
        clip_id = truth["clip_id"]
        if clip_id in ids or clip_id not in registered:
            raise ValueError("Duplicate or unregistered clip ID")
        ids.add(clip_id)
        row = registered[clip_id]
        if row.get("consent_recorded", "").lower() != "true" or row.get("source_kind") != "REPLAY_TAGGED":
            raise ValueError("Registered camera replay with consent is required")
        path = (Path(root) / row["relative_path"]).resolve()
        if not path.is_relative_to((Path(root) / "fixtures/recorded").resolve()):
            raise ValueError("Registered real media must remain under fixtures/recorded")
        if row.get("recipe_sha256") != recipe_hash or truth.get("source_sha256") != row["source_sha256"] or hash_file(path) != row["source_sha256"]:
            raise ValueError("Registered source, recipe or truth hash mismatch")
        if truth.get("event_annotation_complete") is not True:
            raise ValueError("Complete manual event annotation is required for precision/recall")
        if row.get("expected_final_status") not in ("PASS", "HOLD_FOR_REVIEW"):
            raise ValueError("Unsupported expected final status")
        duration = inspect_video(path)["duration_ms"]
        for event in truth.get("events", []):
            if event["kind"] not in CLASSES or not 0 <= event["onset_ms"] <= duration:
                raise ValueError("Invalid manually annotated event")
            boundary = event.get("boundary_ms")
            if boundary is not None and not event["onset_ms"] <= boundary <= duration:
                raise ValueError("Invalid event boundary")
        frame_ids = [frame["frame_index"] for frame in truth.get("frames", [])]
        if len(frame_ids) != len(set(frame_ids)):
            raise ValueError("Duplicate manually annotated frame index")
        validated.append((row, truth, path))
    return validated


def run(annotations, manifest):
    annotations, manifest = Path(annotations), Path(manifest)
    if not manifest.exists():
        raise ValueError("REAL_STAGED NOT_PROVIDED: no registered physical recordings")
    labels = json.loads(annotations.read_text(encoding="utf-8"))
    with manifest.open(newline="", encoding="utf-8") as stream:
        registered = list(csv.DictReader(stream))
    recipe = Recipe.load(bootstrap.ROOT / "recipes/tagged_four_part_v1.yaml")
    clips = validate_population(labels, registered, recipe.sha256)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    output = bootstrap.ROOT / "data/physical_runs" / stamp
    output.mkdir(parents=True, exist_ok=False)
    frozen_hash = hash_file(annotations)
    (output / "frozen_labels.json").write_bytes(annotations.read_bytes())
    rows, all_events, timings = [], [], []
    visible_total = visible_tp = extra_tags = zone_total = zone_correct = 0
    with (output / "observations.jsonl").open("w", encoding="utf-8") as log:
        for row, truth, path in clips:
            detector, engine = Detector(recipe), ProcedureEngine(recipe)
            frame_truth = {frame["frame_index"]: frame for frame in truth.get("frames", [])}
            encountered = set()
            first, last, error = None, None, None
            try:
                for index, ts, image in video_frames(path):
                    began = time.perf_counter()
                    observation, _, overlay = detector.analyze(image, index, ts, "REPLAY_TAGGED", row["source_sha256"])
                    engine.consume(observation)
                    timings.append({"clip_id": row["clip_id"], "frame_index": index, "source_time_ms": ts,
                                    "vision_ms": observation.vision_ms, "detector_engine_ms": (time.perf_counter() - began)*1000})
                    log.write(json.dumps({"clip_id": row["clip_id"], "population": "REAL_STAGED", **observation.model_dump(mode="json")}) + "\n")
                    if index in frame_truth:
                        encountered.add(index)
                        expected = {int(k): v for k, v in frame_truth[index]["visible_markers"].items()}
                        observed = set(observation.marker_ids)
                        visible_total += len(expected)
                        visible_tp += len(set(expected) & observed)
                        extra_tags += len(observed - set(expected))
                        zone_total += sum(zone is not None for zone in expected.values())
                        zone_correct += sum(ob.marker_id in expected and expected[ob.marker_id] is not None and ob.zone_id == expected[ob.marker_id] for ob in observation.observations)
                    if first is None:
                        first = image.copy()
                    last = overlay
                if encountered != set(frame_truth):
                    raise ValueError("Manual frame annotations exceed decoded clip")
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"
            snapshot = engine.checkpoint() if error is None else engine.snapshot()
            matched = match_events(truth.get("events", []), engine.events)
            delays = [m["delay_ms"] for m in matched["matches"] if m["truth"]["kind"] != "MISSING_AT_CHECKPOINT"]
            rows.append({"clip_id": row["clip_id"], "scenario": row["scenario"], "source_sha256": row["source_sha256"],
                         "expected": row["expected_final_status"], "predicted": snapshot["decision"]["status"] if error is None else "ERROR",
                         "tp": matched["tp"], "fp": matched["fp"], "fn": matched["fn"],
                         "correction_expected": truth.get("correction_expected", False),
                         "correction_detected": any(e["kind"] == "CORRECTED" for e in engine.events),
                         "first_matched_alert_delay_ms": min(delays) if delays else None, "error": error})
            all_events.extend({"clip_id": row["clip_id"], **event} for event in engine.events)
            if first is not None:
                cv2.imwrite(str(output / (row["clip_id"] + "-original.jpg")), first)
                cv2.imwrite(str(output / (row["clip_id"] + "-last-overlay.jpg")), last)
    if hash_file(annotations) != frozen_hash:
        raise ValueError("Manual truth changed during inference; reject this run")
    scores = rates(sum(r["tp"] for r in rows), sum(r["fp"] for r in rows), sum(r["fn"] for r in rows))
    invalid = [r for r in rows if r["expected"] != "PASS"]
    confusion = [{"expected": e, "predicted": p, "count": sum(r["expected"] == e and r["predicted"] == p for r in rows)}
                 for e in ("PASS", "HOLD_FOR_REVIEW") for p in sorted({r["predicted"] for r in rows})]
    metrics = {"population": "REAL_STAGED", "clips": len(rows), "frames": len(timings), "manual_truth_sha256": frozen_hash,
               "recipe_sha256": recipe.sha256, "event_scores": scores,
               "false_pass_count": sum(r["predicted"] == "PASS" for r in invalid), "false_pass_denominator": len(invalid),
               "correct_final_status": sum(r["predicted"] == r["expected"] for r in rows),
               "marker_visible_opportunities": visible_total, "marker_recall": visible_tp/visible_total if visible_total else None,
               "marker_unexpected_ids": extra_tags, "placement_opportunities": zone_total,
               "placement_accuracy": zone_correct/zone_total if zone_total else None,
               "corrections_expected": sum(r["correction_expected"] for r in rows),
               "corrections_detected": sum(r["correction_expected"] and r["correction_detected"] for r in rows),
               "processing_failures": sum(r["error"] is not None for r in rows),
               "vision_p95_ms": float(np.percentile([r["vision_ms"] for r in timings],95)) if timings else None,
               "capture_to_visible_alert_ms": None, "capture_to_visible_alert_status": "NOT_MEASURED_BY_OFFLINE_REPLAY",
               "latency_scope": "Source-time onset to matched event; detector processing measured separately",
               "provenance_scope": "Operator-declared camera capture, consent and independent labels; not forensic authentication",
               "confusion_matrix": confusion, "media_publication_authorized": False}
    dump(output / "metrics.json", metrics)
    dump(output / "events.json", all_events)
    write_csv(output / "predictions_per_clip.csv", rows)
    write_csv(output / "latency.csv", timings)
    write_csv(output / "confusion_matrix.csv", confusion)
    (output / "summary.md").write_text(f"# REAL_STAGED run\n\n{len(rows)} consented camera clips; {len(timings)} actual decoded frames.\n\nEvent scores: {scores}.\n\nThis is controlled tagged tabletop validation, not industrial field validation. Offline processing is not live capture-to-alert latency. Original/overlay images and every failed clip remain retained.\n", encoding="utf-8")
    print(f"Saved immutable REAL_STAGED run: {output}")
    return output, metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--annotations", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, default=bootstrap.ROOT / "fixtures/recorded/manifest.csv")
    args = parser.parse_args()
    run(args.annotations, args.manifest)
