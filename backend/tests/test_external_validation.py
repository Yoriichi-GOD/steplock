"""Research-tool regressions use fake archives/pixels only, never claim physical data."""
import hashlib
import json
import zipfile
import cv2
import numpy as np
import pytest
from scripts.acquire_impact import safe_member, verify_file, extract_relevant
from scripts.inspect_external_video import sampled_frames, window_starts, video_metadata
from scripts.run_physical_eval import validate_population
from steplock.procedure.recipe import Recipe
from steplock.procedure.engine import ProcedureEngine
from steplock.vision.aruco import Detector
from steplock.config import ROOT


@pytest.mark.parametrize("name", ["../outside", "/absolute", "C:/outside", "x\\outside", "root/../../file"])
def test_untrusted_zip_paths_are_rejected(name):
    with pytest.raises(ValueError):
        safe_member(name)


def test_integrity_size_and_hash_are_independent(tmp_path):
    path = tmp_path / "archive.zip"
    path.write_bytes(b"actual source bytes")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    assert verify_file(path, path.stat().st_size, digest) == digest
    with pytest.raises(ValueError, match="size"):
        verify_file(path, 1, digest)
    with pytest.raises(ValueError, match="SHA"):
        verify_file(path, path.stat().st_size, "a" * 64)


def test_selective_extraction_preserves_original_bytes_and_rejects_mutation(tmp_path):
    archive = tmp_path / "sample.zip"
    with zipfile.ZipFile(archive, "w") as zipped:
        zipped.writestr("IMPACT-v1.1/videos/front/real.mp4", b"untouched video bytes")
        zipped.writestr("IMPACT-v1.1/annotations/ASR/real.json", b'{"label":"native"}')
        zipped.writestr("IMPACT-v1.1/audio/ego/file.wav", b"not selected")
    dest = tmp_path / "extract"
    entries = extract_relevant(archive, dest)
    assert sum(e["selected"] for e in entries) == 2
    target = dest / "IMPACT-v1.1/videos/front/real.mp4"
    assert target.read_bytes() == b"untouched video bytes"
    assert not (dest / "IMPACT-v1.1/audio").exists()
    extract_relevant(archive, dest)
    target.write_bytes(b"wrong source bytes!!")
    with pytest.raises(ValueError):
        extract_relevant(archive, dest)


def test_video_sampling_keeps_source_indices_and_does_not_create_tags(tmp_path):
    path = tmp_path / "fake_test_only.avi"
    writer = cv2.VideoWriter(str(path), cv2.VideoWriter_fourcc(*"MJPG"), 10, (160, 100))
    assert writer.isOpened()
    for index in range(30):
        writer.write(np.full((100, 160, 3), 50 + index * 3, np.uint8))
    writer.release()
    assert video_metadata(path)["frame_count"] == 30
    frames = list(sampled_frames(path, 1, 1, 5))
    assert [r[0] for r in frames] == [10, 12, 14, 16, 18]
    assert [r[1] for r in frames] == [1000, 1200, 1400, 1600, 1800]
    assert window_starts(50, 10) == [0, 20, 40]
    recipe = Recipe.load(ROOT / "recipes/tagged_four_part_v1.yaml")
    engine, detector = ProcedureEngine(recipe), Detector(recipe)
    for index, timestamp, image in frames:
        record, _, _ = detector.analyze(image, index, timestamp, "REPLAY_TAGGED", "b" * 64)
        engine.consume(record)
        assert not record.marker_ids
    assert engine.checkpoint()["decision"]["status"] == "CALIBRATION_REQUIRED"


@pytest.mark.parametrize("labels", [
    {"population": "SYNTHETIC_FIXTURE"},
    {"population": "REAL_STAGED", "annotation_status": "PENDING"},
    {"population": "REAL_STAGED", "annotation_status": "FROZEN", "reviewed_before_inference": True,
     "recipe_sha256": "a" * 64, "capture_provenance": "Camera provenance described by operator", "clips": []}])
def test_physical_runner_refuses_synthetic_pending_or_empty_populations(labels):
    with pytest.raises(ValueError):
        validate_population(labels, [], "a" * 64)


def test_real_registration_cannot_escape_recording_folder(tmp_path):
    truth = {"clip_id": "one", "source_sha256": "a" * 64, "event_annotation_complete": True}
    labels = {"population": "REAL_STAGED", "annotation_status": "FROZEN", "reviewed_before_inference": True,
              "capture_provenance": "Actual physical object recording from an operator camera", "recipe_sha256": "b" * 64, "clips": [truth]}
    registered = [{"clip_id": "one", "consent_recorded": "True", "source_kind": "REPLAY_TAGGED", "relative_path": "../outside.avi"}]
    with pytest.raises(ValueError, match="fixtures/recorded"):
        validate_population(labels, registered, "b" * 64, root=tmp_path)
