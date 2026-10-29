"""Optional real-video preset guards; generated test bytes are not physical evidence."""
import hashlib
import time
import pytest
from fastapi.testclient import TestClient
from backend import app as api_module
from steplock import demo_recording
from steplock.sources.replay import inspect_video


def test_missing_or_changed_pinned_bytes_are_unavailable(tmp_path, monkeypatch):
    path = tmp_path / "not_a_real_recording.avi"
    monkeypatch.setattr(demo_recording, "RECORDING_PATH", path)
    assert demo_recording.pinned_recording() is None
    path.write_bytes(b"generated unit-test payload; never physical video")
    monkeypatch.setattr(demo_recording, "RECORDING_SHA256", "a" * 64)
    assert demo_recording.pinned_recording() is None


def test_provider_metadata_preserves_population_and_license(tmp_path, monkeypatch):
    # Tests the metadata contract only, not decoding or real-world accuracy.
    path = tmp_path / "test_payload_only.avi"
    path.write_bytes(b"explicitly generated metadata-test payload")
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    monkeypatch.setattr(demo_recording, "RECORDING_PATH", path)
    monkeypatch.setattr(demo_recording, "RECORDING_SHA256", digest)
    metadata = demo_recording.pinned_recording()
    assert metadata["source_sha256"] == digest
    assert metadata["source_kind"] == "REPLAY_TAGGED"
    assert metadata["population"] == "EXTERNAL_PHYSICAL_UNTAGGED"
    assert metadata["tagged_fixture"] is False
    assert metadata["license"] == "CC BY-NC-SA 4.0"
    assert "calibration" in metadata["notice"].lower()
    assert not any(key in metadata for key in ("relative_path", "local_path", "access_token"))


def test_real_preset_rejects_missing_consent_and_synthetic_kind(tmp_path):
    with TestClient(api_module.create_app(runtime_root=tmp_path), base_url="http://127.0.0.1") as client:
        for body in (
            {"source_kind": "REPLAY_TAGGED", "example_id": demo_recording.PINNED_ID},
            {"source_kind": "SYNTHETIC_FIXTURE", "example_id": demo_recording.PINNED_ID, "consent_recorded": True},
        ):
            assert client.post("/api/sessions", json=body).status_code == 400


def test_missing_asset_does_not_become_a_synthetic_fallback(tmp_path, monkeypatch):
    monkeypatch.setattr(api_module, "pinned_recording", lambda: None)
    with TestClient(api_module.create_app(runtime_root=tmp_path), base_url="http://127.0.0.1") as client:
        catalog = client.get("/api/demo/scenarios").json()
        assert catalog["pinned_recording"] is None
        assert any(example["id"] == "normal" for example in catalog["scenarios"])
        response = client.post("/api/sessions", json={"source_kind": "REPLAY_TAGGED", "consent_recorded": True,
                                                     "example_id": demo_recording.PINNED_ID})
        assert response.status_code == 404
        assert not client.app.state.manager.sessions


def test_actual_local_real_preset_is_decoded_and_never_unsupported_pass(tmp_path):
    """Optional local integration; CI has no licensed media and must skip explicitly."""
    metadata = demo_recording.pinned_recording()
    if metadata is None:
        pytest.skip("Licensed local IMPACT excerpt not installed; no real footage is substituted")
    inspected = inspect_video(demo_recording.RECORDING_PATH)
    with TestClient(api_module.create_app(runtime_root=tmp_path), base_url="http://127.0.0.1") as client:
        created = client.post("/api/sessions", json={"source_kind": "REPLAY_TAGGED", "consent_recorded": True,
                                                     "example_id": demo_recording.PINNED_ID})
        assert created.status_code == 201, created.text
        credentials = created.json()
        sid = credentials["session_id"]
        auth = {"Authorization": "Bearer " + credentials["access_token"]}
        initial = credentials["snapshot"]
        assert initial["source_metadata"]["population"] == "EXTERNAL_PHYSICAL_UNTAGGED"
        assert initial["source_sha256"] == inspected["source_sha256"]
        assert client.post(f"/api/sessions/{sid}/start", headers=auth,
                           json={"checkpoint_at_end": False}).status_code == 200
        deadline = time.monotonic() + inspected["duration_ms"] / 1000 + 12
        while time.monotonic() < deadline:
            state = client.get(f"/api/sessions/{sid}", headers=auth).json()
            assert state["decision"]["status"] != "PASS"
            if state["state"] != "running":
                break
            time.sleep(.05)
        assert state["state"] == "finished", state
        # The bounded real-time queue intentionally drops stale frames under load.
        # Require complete source decoding and explicit accounting for every skip.
        runtime = state["runtime"]
        assert runtime["frames_in"] == inspected["frame_count"]
        assert runtime["frames_analyzed"] > 0
        assert runtime["frames_analyzed"] + runtime["frames_dropped"] == runtime["frames_in"]
        assert state["latest_frame"]["frame_index"] == inspected["frame_count"] - 1
        assert state["decision"]["status"] == "CALIBRATION_REQUIRED"
        assert state["quality"]["calibration_id"] is None
        frame_id = state["latest_frame"]["frame_id"]
        original = client.get(f"/api/sessions/{sid}/frames/{frame_id}?annotated=false", headers=auth)
        assert hashlib.sha256(original.content).hexdigest() == state["latest_frame"]["frame_sha256"]
        report = client.get(f"/api/sessions/{sid}/report", headers=auth)
        assert report.status_code == 200
        assert report.json()["source_metadata"]["population"] == "EXTERNAL_PHYSICAL_UNTAGGED"
        assert credentials["access_token"] not in report.text
        stopped = client.post(f"/api/sessions/{sid}/stop", headers=auth).json()
        assert stopped["decision"]["status"] == "SOURCE_LOST"
