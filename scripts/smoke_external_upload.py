"""Exercise real-video upload, inference, evidence export and source loss in isolation.

Uses the actual FastAPI routes in an isolated TestClient, not the UI chat's server.
The input is a declared resized/re-encoded excerpt of licensed IMPACT video.
"""
try:
    from . import bootstrap
except ImportError:
    import bootstrap
import argparse
import hashlib
import json
from pathlib import Path
import time
import cv2
from fastapi.testclient import TestClient
from backend.app import create_app
from scripts.acquire_impact import sha256
from scripts.inspect_external_video import sampled_frames, dump


def run(root, output):
    root, output = Path(root), Path(output)
    output.mkdir(parents=True, exist_ok=False)
    source = root / "extracted/IMPACT-v1.1/sample/videos/front/AL07EJ17_Disassembly_A_001_front.mp4"
    excerpt = output / "real_physical_excerpt.avi"
    writer = cv2.VideoWriter(str(excerpt), cv2.VideoWriter_fourcc(*"MJPG"), 5, (640, 360))
    if not writer.isOpened():
        raise ValueError("Excerpt encoder unavailable")
    count = 0
    try:
        for _, _, frame in sampled_frames(source, 60, 3, 5):
            writer.write(cv2.resize(frame, (640, 360)))
            count += 1
    finally:
        writer.release()
    if count != 15:
        raise ValueError("Expected 15 actual source frames")
    with TestClient(create_app(runtime_root=output / "api_runtime"), base_url="http://127.0.0.1") as client:
        created = client.post("/api/sessions", json={"source_kind": "REPLAY_TAGGED", "consent_recorded": True})
        assert created.status_code == 201, created.text
        data = created.json()
        sid, auth = data["session_id"], {"Authorization": "Bearer " + data["access_token"]}
        with excerpt.open("rb") as stream:
            upload = client.post(f"/api/sessions/{sid}/upload", headers=auth, files={"file": (excerpt.name, stream, "video/avi")})
        assert upload.status_code == 200, upload.text
        assert upload.json()["source_sha256"] == sha256(excerpt)
        started = client.post(f"/api/sessions/{sid}/start", headers=auth, json={"checkpoint_at_end": True})
        assert started.status_code == 200, started.text
        deadline = time.monotonic() + 25
        while time.monotonic() < deadline:
            state = client.get(f"/api/sessions/{sid}", headers=auth).json()
            if state["state"] != "running":
                break
            time.sleep(.05)
        assert state["state"] == "finished", state
        assert state["runtime"]["frames_analyzed"] == 15, state["runtime"]
        assert state["decision"]["status"] == "CALIBRATION_REQUIRED", state["decision"]
        frame = state["latest_frame"]
        original = client.get(f"/api/sessions/{sid}/frames/{frame['frame_id']}?annotated=false", headers=auth)
        assert original.status_code == 200
        assert hashlib.sha256(original.content).hexdigest() == frame["frame_sha256"]
        report = client.get(f"/api/sessions/{sid}/report", headers=auth)
        printable = client.get(f"/api/sessions/{sid}/report?format=html", headers=auth)
        assert report.status_code == printable.status_code == 200
        assert data["access_token"] not in report.text and data["access_token"] not in printable.text
        (output / "report.json").write_bytes(report.content)
        (output / "report.html").write_text(printable.text, encoding="utf-8")
        stopped = client.post(f"/api/sessions/{sid}/stop", headers=auth).json()
        assert stopped["decision"]["status"] == "SOURCE_LOST"
        receipt = {"population": "EXTERNAL_PHYSICAL_UNTAGGED", "test_transport": "isolated FastAPI TestClient; no live browser or physical camera",
                   "source_video_id": source.stem, "original_dataset_video_sha256": sha256(source),
                   "excerpt_sha256": sha256(excerpt), "derivation": "source60s..63s, actual frames at5Hz, resized640x360, MJPEG re-encoding; no generated scene/tags",
                   "frames_analyzed": 15, "upload_http": upload.status_code, "final_status": state["decision"]["status"],
                   "export_json_http": report.status_code, "export_html_http": printable.status_code,
                   "original_frame_hash_verified": True, "tokens_absent_from_exports": True,
                   "stop_status": stopped["decision"]["status"], "camera_opened": False,
                   "local_artifact_directory": str(output.resolve())}
    dump(output / "receipt.json", receipt)
    print(json.dumps(receipt, indent=2))
    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=bootstrap.ROOT / "data/external/impact_v1_1")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run(args.root, args.output)
