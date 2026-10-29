"""Pixel-only compatibility experiment on genuine public IMPACT recordings.

This is deliberately not an untagged action-recognition model. Dataset labels are
never passed to Detector or ProcedureEngine. Unsupported capture is not a correctly
recognized procedural mistake. All images/video remain under ignored data/.
"""
try:
    from . import bootstrap
except ImportError:
    import bootstrap
import argparse
from collections import Counter
import csv
import datetime as dt
import html
import json
import math
from pathlib import Path
import platform
import subprocess
import time
import cv2
import numpy as np
from steplock.procedure.recipe import Recipe
from steplock.procedure.engine import ProcedureEngine
from steplock.vision.aruco import Detector
from scripts.acquire_impact import sha256


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False), encoding="utf-8")


def write_csv(path, rows):
    if not rows:
        raise ValueError("Cannot silently produce an empty prediction table")
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def video_metadata(path):
    cap = cv2.VideoCapture(str(path))
    try:
        if not cap.isOpened():
            raise ValueError("Cannot open video")
        fps = float(cap.get(cv2.CAP_PROP_FPS))
        count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if not math.isfinite(fps) or not 1 <= fps <= 240 or count < 1:
            raise ValueError("Invalid FPS/frame-count metadata")
        return {"fps": fps, "frame_count": count, "duration_ms": count / fps * 1000,
                "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "timestamp_method": "FPS_INDEX_FALLBACK_DECLARED; not hardware capture timestamps"}
    finally:
        cap.release()


def window_starts(duration_seconds, window_seconds):
    if not 0 < window_seconds <= 120 or duration_seconds <= 0:
        raise ValueError("Invalid bounded observation window")
    end = max(0., duration_seconds - window_seconds)
    return sorted(set([0., end / 2, end]))


def sampled_frames(path, start_seconds, seconds, sample_hz=5):
    """Decode real frames at fixed source-index intervals; no interpolation or tags."""
    metadata = video_metadata(path)
    cap = cv2.VideoCapture(str(path))
    start = round(start_seconds * metadata["fps"])
    stop = min(metadata["frame_count"], round((start_seconds + seconds) * metadata["fps"]))
    stride = max(1, round(metadata["fps"] / sample_hz))
    try:
        cap.set(cv2.CAP_PROP_POS_FRAMES, start)
        index = int(round(cap.get(cv2.CAP_PROP_POS_FRAMES)))
        if index != start:
            raise ValueError(f"Decoder seek landed at {index}, requested {start}")
        while index < stop:
            ok, frame = cap.read()
            if not ok:
                raise ValueError(f"Decode ended early at source frame {index}/{stop}")
            yield index, index / metadata["fps"] * 1000, frame
            skip = min(stride - 1, stop - index - 1)
            for _ in range(skip):
                if not cap.grab():
                    raise ValueError("Decoder failed while advancing through real media")
            index += skip + 1
    finally:
        cap.release()


def inspect_annotations(root):
    schemas = Counter()
    files = []
    for path in sorted(root.rglob("*.json")):
        if "annotations" not in path.parts and "metadata" not in path.parts:
            continue
        value = json.loads(path.read_text(encoding="utf-8-sig"))
        keys = sorted(value) if isinstance(value, dict) else ["list"] if isinstance(value, list) else [type(value).__name__]
        schemas[" | ".join(keys)] += 1
        files.append({"path": path.relative_to(root).as_posix(), "sha256": sha256(path), "top_level_keys": keys,
                      "top_level_count": len(value) if isinstance(value, (dict, list)) else None})
    return {"json_files": len(files), "top_level_schemas": dict(schemas), "files": files,
            "label_mapping": "NOT_DEFINED: native task/state/anomaly classes are not STEPLOCK part-marker/zone observations"}


def run(root, seconds=12, sample_hz=5):
    root = Path(root).resolve()
    acquisition = json.loads((root / "acquisition.json").read_text(encoding="utf-8"))
    if acquisition.get("dataset") != "IMPACT" or acquisition.get("checksum_verified") is not True:
        raise ValueError("A verified IMPACT acquisition receipt is required")
    extracted = root / "extracted"
    videos = sorted(p for p in extracted.rglob("*") if p.suffix.lower() in (".mp4", ".avi", ".mkv", ".mov") and "videos" in p.parts)
    if len(videos) != 15:
        raise ValueError(f"Expected official three-execution/five-view sample, found {len(videos)} RGB videos")
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    local = root / "validation" / stamp
    public = bootstrap.ROOT / "benchmarks/external_runs" / (stamp + "_impact_compatibility")
    local.mkdir(parents=True, exist_ok=False)
    public.mkdir(parents=True, exist_ok=False)
    recipe = Recipe.load(bootstrap.ROOT / "recipes/tagged_four_part_v1.yaml")
    commit = subprocess.check_output(["git", "-C", str(bootstrap.ROOT), "rev-parse", "HEAD"], text=True).strip()
    source_hashes = {"backend/steplock/vision/aruco.py": sha256(bootstrap.ROOT / "backend/steplock/vision/aruco.py"),
                     "backend/steplock/procedure/engine.py": sha256(bootstrap.ROOT / "backend/steplock/procedure/engine.py"),
                     "recipes/tagged_four_part_v1.yaml": recipe.sha256,
                     "scripts/inspect_external_video.py": sha256(Path(__file__))}
    rows, timing, gallery = [], [], []
    observations = local / "observations.jsonl"
    all_events = local / "events.jsonl"
    demonstration = local / "physical_compatibility_demonstration.avi"
    writer = cv2.VideoWriter(str(demonstration), cv2.VideoWriter_fourcc(*"MJPG"), sample_hz, (960, 600))
    if not writer.isOpened():
        raise ValueError("Demonstration encoder unavailable")
    try:
        with observations.open("w", encoding="utf-8") as log, all_events.open("w", encoding="utf-8") as events:
            for path in videos:
                metadata = video_metadata(path)
                source_hash = sha256(path)
                verified = next((f for f in acquisition["files"] if f["path"] == path.relative_to(extracted).as_posix()), None)
                if not verified or verified.get("sha256") != source_hash:
                    raise ValueError("Media differs from verified acquisition")
                for window_id, start in enumerate(window_starts(metadata["duration_ms"] / 1000, seconds)):
                    detector, engine = Detector(recipe), ProcedureEngine(recipe)
                    n, calibrated, tagged, decoded_ids = 0, 0, 0, Counter()
                    error, first_frame, first_overlay, last_image = None, None, None, None
                    try:
                        for index, ts, native in sampled_frames(path, start, seconds, sample_hz):
                            height, width = native.shape[:2]
                            image = cv2.resize(native, (round(width * min(1, 960 / width)), round(height * min(1, 960 / width))))
                            began = time.perf_counter()
                            # Legacy SourceKind is transport metadata, not a claim that tags are present.
                            observation, _, overlay = detector.analyze(image, index, ts, "REPLAY_TAGGED", source_hash)
                            engine.consume(observation)
                            decision_ms = (time.perf_counter() - began) * 1000
                            n += 1
                            calibrated += observation.calibration_id is not None
                            tagged += bool(observation.marker_ids)
                            decoded_ids.update(observation.marker_ids)
                            log.write(json.dumps({"video_id": path.stem, "window": window_id, "population": "EXTERNAL_PHYSICAL_UNTAGGED",
                                                  "analysis_resize_max_width": 960, **observation.model_dump(mode="json")}) + "\n")
                            timing.append({"video_id": path.stem, "window": window_id, "frame_index": index,
                                           "source_time_ms": ts, "vision_ms": observation.vision_ms, "detector_plus_engine_ms": decision_ms})
                            if first_frame is None:
                                first_frame, first_overlay = native.copy(), overlay.copy()
                            last_image = overlay
                            # Actual dataset frames, visibly labeled as compatibility replay.
                            if window_id == 1 and n <= sample_hz * 3:
                                panel = np.zeros((600, 960, 3), np.uint8)
                                view = cv2.resize(overlay, (960, 540))
                                panel[:540] = view
                                cv2.putText(panel, "IMPACT physical recording / compatibility only / NO semantic scoring", (12, 560), cv2.FONT_HERSHEY_SIMPLEX, .48, (230, 230, 230), 1)
                                cv2.putText(panel, engine.snapshot()["decision"]["status"] + " | " + path.stem[:72], (12, 585), cv2.FONT_HERSHEY_SIMPLEX, .45, (100, 190, 255), 1)
                                writer.write(panel)
                    except Exception as exc:
                        error = f"{type(exc).__name__}: {exc}"
                    snapshot = engine.checkpoint() if not error and n else engine.snapshot()
                    row = {"video_id": path.stem, "window": window_id, "start_seconds": start, "window_seconds": seconds,
                           "native_fps": metadata["fps"], "native_width": metadata["width"], "native_height": metadata["height"],
                           "source_duration_ms": metadata["duration_ms"], "sampled_frames": n, "calibrated_frames": calibrated,
                           "frames_with_decoded_ids": tagged, "decoded_ids": json.dumps(dict(decoded_ids)),
                           "predicted": snapshot["decision"]["status"] if n and not error else "ERROR",
                           "reason": snapshot["decision"]["reason"], "semantic_ground_truth": "NOT_COMPARABLE",
                           "source_sha256": source_hash, "error": error}
                    rows.append(row)
                    for event in engine.events:
                        events.write(json.dumps({"video_id": path.stem, "window": window_id, **event}) + "\n")
                    if first_frame is not None:
                        stem = f"{path.stem}-w{window_id}"
                        for suffix, frame in (("original", first_frame), ("overlay", first_overlay), ("last-overlay", last_image)):
                            cv2.imwrite(str(local / (stem + "-" + suffix + ".jpg")), frame)
                        gallery.append(f'<article><h2>{html.escape(path.stem)} / window {window_id}</h2><p>{html.escape(row["predicted"])}: {html.escape(row["reason"])}</p><img src="{stem}-original.jpg" alt="Original physical recording"><img src="{stem}-overlay.jpg" alt="Unmodified STEPLOCK detector output"></article>')
                    print(f"{path.stem} window {window_id}: {n} frames, {row['predicted']}, calibration {calibrated}/{n}", flush=True)
    finally:
        writer.release()
    annotation_inventory = inspect_annotations(extracted)
    dump(public / "annotation_inventory.json", annotation_inventory)
    write_csv(public / "predictions_per_window.csv", rows)
    write_csv(public / "processing_times.csv", timing)
    counts = Counter(row["predicted"] for row in rows)
    write_csv(public / "confusion_matrix.csv", [{"native_truth": "NOT_COMPARABLE", "predicted_capture_gate": status, "windows": count} for status, count in sorted(counts.items())])
    measured = [r["vision_ms"] for r in timing]
    metrics = {"population": "EXTERNAL_PHYSICAL_UNTAGGED", "dataset": "IMPACT v1.1 official three-execution sample",
               "experiment": "Pixel-level ingestion and conservative capture-gate compatibility; NOT procedural mistake recognition",
               "git_commit": commit, "prediction_source_hashes": source_hashes, "python": platform.python_version(), "opencv": cv2.__version__,
               "acquisition": {k: v for k, v in acquisition.items() if k != "files"},
               "videos": len(videos), "windows": len(rows), "window_seconds": seconds, "sampling_hz_requested": sample_hz,
               "window_policy": "start, midpoint, end; independent engine per window; no fabricated prior assembly history",
               "source_timestamp_method": "FPS_INDEX_FALLBACK_DECLARED", "source_kind_legacy_transport": "REPLAY_TAGGED (does not imply decoded tags)",
               "analysis_resize_max_width": 960, "frames_analyzed": len(timing), "calibrated_frames": sum(r["calibrated_frames"] for r in rows),
               "frames_with_decoded_ids": sum(r["frames_with_decoded_ids"] for r in rows), "status_counts": dict(counts),
               "unsafe_pass_on_unsupported_windows": sum(r["predicted"] == "PASS" and r["calibrated_frames"] == 0 for r in rows),
               "decode_or_processing_failures": sum(r["error"] is not None for r in rows),
               "marker_recall": None, "marker_truth_opportunities": None, "placement_accuracy": None,
               "mistake_precision": None, "mistake_recall": None, "mistake_f1": None, "false_pass_count_native_tasks": None,
               "correction_detection_native_tasks": None, "procedural_alert_delay_ms": None, "capture_to_visible_alert_ms": None,
               "vision_p50_ms": float(np.percentile(measured, 50)) if measured else None,
               "vision_p95_ms": float(np.percentile(measured, 95)) if measured else None,
               "detector_engine_p95_ms": float(np.percentile([r["detector_plus_engine_ms"] for r in timing], 95)) if timing else None,
               "processing_latency_scope": "offline sampled real-video frames, including PNG hashing; not live capture-to-browser latency",
               "raw_observations_sha256": sha256(observations), "raw_events_sha256": sha256(all_events),
               "demonstration_sha256": sha256(demonstration), "local_artifact_directory": str(local),
               "real_staged_marker_recordings": "NOT_PROVIDED", "native_task_scoring": "NOT_RUN_NO_VALID_OBSERVATION_ADAPTER",
               "limitations": ["Untouched ArUco engine needs four known anchors plus known component tags and recipe geometry.",
                               "Native industrial states/anomaly labels cannot be converted to marker observations without independent visual recognition.",
                               "No manual calibration, marker overlays, generated tags, truth-derived observations, retraining, or paid model calls.",
                               "Calibration refusal is evidence of safe unsupported-input handling, not correct mistake classification.",
                               "Three windows per video are sampled; this is not full-video or official IMPACT benchmark evaluation.",
                               "Five views of the same execution are correlated, not 15 independent assembly trials.",
                               "Marker recall, placement accuracy and semantic confusion are unmeasurable without compatible reference annotations."]}
    dump(public / "metrics.json", metrics)
    (local / "gallery.html").write_text('<!doctype html><meta charset="utf-8"><title>IMPACT physical compatibility evidence</title><style>body{background:#111;color:#eee;font:16px system-ui;margin:30px}article{margin:30px 0}img{width:48%;margin:1%}</style><h1>Real physical recordings — unsupported capture gallery</h1><p>CC BY-NC-SA 4.0, IMPACT authors. Compatibility experiment only. Missing calibration is not mistake recognition. Original and detector overlay below.</p>' + "\n".join(gallery), encoding="utf-8")
    summary = f"# IMPACT physical-video compatibility experiment\n\n{len(videos)} real RGB videos, {len(rows)} sampled windows, {len(timing)} analyzed frames. Statuses: {dict(counts)}.\n\nCalibration valid: {metrics['calibrated_frames']}/{len(timing)} frames. Unsupported-window PASS: {metrics['unsafe_pass_on_unsupported_windows']}. Processing failures: {metrics['decode_or_processing_failures']}.\n\nNative mistake precision/recall/F1, native false PASS, correction detection, marker recall and placement accuracy: **NOT_SCORABLE**. No defensible untagged-video observation adapter exists in this experiment.\n\nOffline real-video vision p50/p95: {metrics['vision_p50_ms']}/{metrics['vision_p95_ms']} ms. Capture-to-visible latency: **NOT_MEASURED**.\n\nOriginal/overlay failure gallery, full observations, events and demonstration AVI stay local in `{local}`. Raw data license: CC BY-NC-SA 4.0; source https://github.com/Kratos-Wen/IMPACT.\n\n" + "\n".join("- " + item for item in metrics["limitations"]) + "\n"
    (public / "summary.md").write_text(summary, encoding="utf-8")
    print(f"Saved measured report: {public}\nLocal gallery: {local / 'gallery.html'}\nDemonstration: {demonstration}", flush=True)
    return public, metrics


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=bootstrap.ROOT / "data/external/impact_v1_1")
    parser.add_argument("--seconds", type=int, default=12, choices=range(2, 31))
    parser.add_argument("--sample-hz", type=int, default=5, choices=[5, 10])
    args = parser.parse_args()
    run(args.root, args.seconds, args.sample_hz)
