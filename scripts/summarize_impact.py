"""Inspect native IMPACT annotations and retain isolated tag-decoding anomalies.

Evaluator-only: labels are inspected after predictions, never passed to inference.
"""
try:
    from . import bootstrap
except ImportError:
    import bootstrap
from collections import Counter
import argparse
import csv
import html
import json
from pathlib import Path
import cv2
from steplock.schemas import FrameObservation
from steplock.procedure.recipe import Recipe
from steplock.vision.aruco import Detector, png_bytes
from scripts.acquire_impact import sha256
from scripts.inspect_external_video import dump
import hashlib


def summarize(root, run):
    root, run = Path(root), Path(run)
    metrics = json.loads((run / "metrics.json").read_text(encoding="utf-8"))
    sample = root / "extracted/IMPACT-v1.1/sample"
    predictions = list(csv.DictReader((run / "predictions_per_window.csv").open(newline="", encoding="utf-8")))
    video_ids = {row["video_id"] for row in predictions}
    atr_unique, occurrences = {}, 0
    for path in sorted((sample / "annotations/ATR").rglob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            value = json.loads(line)
            if value["video_id"] not in video_ids:
                continue
            occurrences += 1
            key = value["sample_id"]
            labels = tuple(value["label_names"])
            if key in atr_unique and atr_unique[key]["labels"] != labels:
                raise ValueError("Native anomaly labels conflict across split files")
            atr_unique[key] = {"labels": labels, "video_id": value["video_id"], "entity": value["entity"],
                               "start_frame": value["start_frame"], "end_frame": value["end_frame"]}
    anomaly_counts = Counter(label for value in atr_unique.values() for label in value["labels"])
    phases = {}
    for side in ("L", "R"):
        files = list((sample / f"annotations/PPR/groundTruth_PPR_{side}").glob("*.txt"))
        counts = Counter()
        for path in files:
            if path.stem in video_ids:
                counts.update(line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
        phases[side] = dict(counts)
    asr = []
    for path in sorted((sample / "annotations/ASR").rglob("*.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        asr.append({"video_id": value["video_id"], "fps": value["fps"], "frame_count": value["frame_count"],
                    "workflow": value["workflow"], "component_count": len(value["components"]),
                    "state_sequence_entries": len(value["state_sequence"]), "timestamp_unit": "source frame index"})
    inventory = {"dataset": "IMPACT v1.1 sample", "rgb_videos": len(video_ids),
                 "camera_views": sorted({name.rsplit("_", 1)[1] for name in video_ids}),
                 "native_video_fps": sorted({float(row["native_fps"]) for row in predictions}),
                 "native_rgb_dimensions": sorted({row["native_width"] + "x" + row["native_height"] for row in predictions}),
                 "duration_seconds_range": [min(float(r["source_duration_ms"])/1000 for r in predictions), max(float(r["source_duration_ms"])/1000 for r in predictions)],
                 "ASR": asr, "ATR_unique_segments": len(atr_unique), "ATR_label_occurrences_unique_segments": dict(anomaly_counts),
                 "ATR_rows_across_split_files": occurrences, "ATR_deduplication": "sample_id, preventing repeated split membership from inflating counts",
                 "ATR_timestamps": "start_frame/end_frame; native frame indices, not millisecond values",
                 "PPR_frame_labels_by_hand": phases,
                 "annotation_population_note": "Counts describe native labels, not independently predicted events. Views and split memberships are correlated.",
                 "compatibility": "No four-anchor fixture calibration or component-tag observation adapter; no native task accuracy scored."}
    dump(run / "native_annotation_summary.json", inventory)
    local = Path(metrics["local_artifact_directory"])
    detector = Detector(Recipe.load(bootstrap.ROOT / "recipes/tagged_four_part_v1.yaml"))
    videos = {path.stem: path for path in sample.glob("videos/*/*") if path.suffix.lower() in (".mp4", ".avi", ".mkv")}
    anomalies = []
    for line in (local / "observations.jsonl").read_text(encoding="utf-8").splitlines():
        logged = json.loads(line)
        if not logged["marker_ids"]:
            continue
        video_id, window = logged.pop("video_id"), logged.pop("window")
        logged.pop("population")
        logged.pop("analysis_resize_max_width")
        record = FrameObservation.model_validate(logged)
        cap = cv2.VideoCapture(str(videos[video_id]))
        try:
            cap.set(cv2.CAP_PROP_POS_FRAMES, record.frame_index)
            ok, native = cap.read()
            if not ok:
                raise ValueError("Cannot recover anomaly source frame")
        finally:
            cap.release()
        image = cv2.resize(native, (record.width, record.height))
        if hashlib.sha256(png_bytes(image)).hexdigest() != record.frame_sha256:
            raise ValueError("Recovered frame differs from logged prediction pixels")
        stem = f"isolated-id-{video_id}-{record.frame_index}"
        original = local / (stem + "-original.png")
        overlay = local / (stem + "-overlay.jpg")
        original.write_bytes(png_bytes(image))
        cv2.imwrite(str(overlay), detector.overlay(image, record))
        anomalies.append({"video_id": video_id, "window": window, "source_frame_index": record.frame_index,
                          "marker_ids": record.marker_ids, "calibration_id": record.calibration_id,
                          "prediction_frame_sha256": record.frame_sha256, "original_png_sha256": sha256(original),
                          "overlay_sha256": sha256(overlay), "original_name": original.name, "overlay_name": overlay.name,
                          "status": "ISOLATED_UNVERIFIED_ID_DECODE_NOT_FIXTURE_SUPPORT"})
    dump(run / "isolated_marker_decodes.json", anomalies)
    gallery = '<!doctype html><meta charset="utf-8"><title>Isolated ArUco decodes on physical IMPACT recordings</title><style>body{background:#111;color:#eee;font:16px system-ui;margin:30px}img{width:48%;margin:1%}article{margin:30px 0}</style><h1>Retained compatibility failure cases</h1><p>Real public IMPACT video, CC BY-NC-SA 4.0. These isolated IDs have no known fixture calibration or independent physical tag truth. They are not component recognitions. No passing verdict follows. Analysis PNG hashes match the original prediction log.</p>'
    for item in anomalies:
        gallery += f'<article><h2>{html.escape(item["video_id"])} / frame {item["source_frame_index"]}</h2><p>Decoded IDs {item["marker_ids"]}; calibration absent.</p><img src="{item["original_name"]}" alt="Actual analysis pixels"><img src="{item["overlay_name"]}" alt="Detector boxes on same pixels"></article>'
    (local / "isolated_marker_gallery.html").write_text(gallery, encoding="utf-8")
    print(json.dumps(inventory, indent=2))
    print(f"Retained {len(anomalies)} isolated-ID frame pairs, verified against logged PNG hashes.")
    return inventory, anomalies


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=bootstrap.ROOT / "data/external/impact_v1_1")
    parser.add_argument("--run", type=Path, required=True)
    args = parser.parse_args()
    summarize(args.root, args.run)
