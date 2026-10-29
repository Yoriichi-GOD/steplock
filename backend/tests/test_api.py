import hashlib
import json
import time
import cv2
import pytest
from fastapi.testclient import TestClient
from backend.app import create_app
from steplock.config import ROOT
from steplock.evidence.store import EvidenceStore
from steplock.procedure.recipe import Recipe
from steplock.service import Session
from steplock.sources.replay import video_frames
from steplock.vision.aruco import Detector
from scripts.fixture_lib import render_board


@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(runtime_root=tmp_path),base_url="http://127.0.0.1") as client:
        yield client


def new_session(client,**kwargs):
    response=client.post("/api/sessions",json={"source_kind":"SYNTHETIC_FIXTURE",**kwargs})
    assert response.status_code==201,response.text
    body=response.json()
    return body["session_id"],{"Authorization":"Bearer "+body["access_token"]}


def test_safe_request_errors_and_explicit_consent(client):
    assert client.post("/api/sessions",json={"source_kind":"INVALID"}).status_code==422
    assert client.post("/api/sessions",json={"recipe_id":"invented"}).status_code==404
    assert client.post("/api/sessions",json={"source_kind":"LIVE_TAGGED"}).status_code==400
    assert client.post("/api/sessions",json={"source_kind":"REPLAY_TAGGED","example_id":"normal"}).status_code==400
    assert client.get("/api/health",headers={"Origin":"https://evil.example"}).status_code==403
    assert client.get("/api/health",headers={"Host":"evil.example"}).status_code==400
    duplicate=client.post("/api/recipes",content='{"recipe_id":"one","recipe_id":"two"}',headers={"Content-Type":"application/json"})
    assert duplicate.status_code==422 and "Duplicate recipe key" in duplicate.json()["detail"]


def test_isolation_tokens_and_empty_checkpoint(client):
    a,auth_a=new_session(client)
    b,auth_b=new_session(client)
    assert client.get(f"/api/sessions/{a}").status_code==403
    assert client.get(f"/api/sessions/{a}",headers=auth_b).status_code==403
    assert client.get(f"/api/sessions/{a}",headers=auth_a).json()["session_id"]==a
    assert client.post(f"/api/sessions/{a}/checkpoint",headers=auth_a).status_code==409
    assert client.get("/api/sessions/does-not-exist",headers=auth_a).status_code==404


def test_bad_upload_content_mime_and_paths_are_not_persisted(client):
    sid,auth=new_session(client,source_kind="REPLAY_TAGGED",consent_recorded=True)
    for name,content,mime,status in [("file.txt",b"bad","text/plain",415),("bad.mp4",b"not video","video/mp4",422),("../../outside.avi",b"bad","video/avi",400)]:
        response=client.post(f"/api/sessions/{sid}/upload",headers=auth,files={"file":(name,content,mime)})
        assert response.status_code==status,response.text
    assert not (client.app.state.manager.sessions[sid].directory/"upload.bin").exists()


def test_actual_upload_replay_events_export_and_stop(client):
    sid,auth=new_session(client,source_kind="SYNTHETIC_FIXTURE")
    path=ROOT/"fixtures/synthetic/fx_00_00.avi"
    with path.open("rb") as file:
        response=client.post(f"/api/sessions/{sid}/upload",headers=auth,files={"file":("consented-test.avi",file,"video/avi")})
    assert response.status_code==200,response.text
    assert response.json()["source_sha256"]==hashlib.sha256(path.read_bytes()).hexdigest()
    start=client.post(f"/api/sessions/{sid}/start",headers=auth,json={"checkpoint_at_end":True})
    assert start.status_code==200,start.text
    second,auth_b=new_session(client,example_id="normal")
    assert client.post(f"/api/sessions/{second}/start",headers=auth_b,json={}).status_code==409
    deadline=time.monotonic()+15
    while time.monotonic()<deadline:
        state=client.get(f"/api/sessions/{sid}",headers=auth).json()
        if state["state"]!="running": break
        time.sleep(.05)
    assert state["state"]=="finished",state
    assert state["decision"]["status"]=="PASS",state["decision"]
    assert state["runtime"]["frames_analyzed"]==30
    assert state["runtime"]["frames_dropped"]==0
    events=client.get(f"/api/sessions/{sid}/events",headers=auth).json()["events"]
    assert events==state["events"]
    fid=state["latest_frame"]["frame_id"]
    original=client.get(f"/api/sessions/{sid}/frames/{fid}?annotated=false",headers=auth)
    assert hashlib.sha256(original.content).hexdigest()==state["latest_frame"]["frame_sha256"]
    report=client.get(f"/api/sessions/{sid}/report",headers=auth)
    assert report.json()["events"]==events
    html=client.get(f"/api/sessions/{sid}/report?format=html",headers=auth)
    assert "ADVISORY ONLY" in html.text and state["source_sha256"] in html.text
    review=client.post(f"/api/sessions/{sid}/review",headers=auth,json={"event_id":events[0]["event_id"]})
    assert review.status_code==200
    assert client.get(f"/api/sessions/{sid}",headers=auth).json()["decision"]["status"]=="PASS"
    stopped=client.post(f"/api/sessions/{sid}/stop",headers=auth).json()
    assert stopped["decision"]["status"]=="SOURCE_LOST"
    assert client.delete(f"/api/sessions/{sid}/upload",headers=auth).json()["temporary_upload_removed"]


def test_browser_jpeg_transport_with_synthetic_images_and_stale_hold(client):
    # Exercises the live transport with generated pixels. Does not activate a webcam.
    sid,auth=new_session(client,source_kind="LIVE_TAGGED",consent_recorded=True,camera_mode="browser")
    assert client.post(f"/api/sessions/{sid}/start",headers=auth,json={}).status_code==200
    for i in range(3):
        ok,jpg=cv2.imencode(".jpg",render_board([(10,"BASE_SLOT")],seed=i+1))
        response=client.post(f"/api/sessions/{sid}/frame?captured_at_ms={i*200}",headers={**auth,"Content-Type":"image/jpeg"},content=jpg.tobytes())
        assert response.status_code==200,response.text
    session=client.app.state.manager.sessions[sid]
    assert session.snapshot()["step_states"][0]["state"]=="CONFIRMED"
    session.last_frame_wall=time.monotonic()-3
    assert client.get(f"/api/sessions/{sid}",headers=auth).json()["decision"]["status"]=="SOURCE_LOST"


def test_recipe_version_is_frozen_per_session(client):
    sid,auth=new_session(client)
    before=client.get(f"/api/sessions/{sid}",headers=auth).json()["recipe_sha256"]
    data=client.get("/api/recipes").json()[0]
    data.pop("key");data.pop("sha256")
    assert client.post("/api/recipes",json=data).status_code==409
    data["version"]+=1
    data["name"]="Second recipe version"
    assert client.post("/api/recipes",json=data).status_code==201
    assert client.get(f"/api/sessions/{sid}",headers=auth).json()["recipe_sha256"]==before
    data["steps"][0]["requires"]=["S4"]
    assert client.post("/api/recipes",json=data).status_code==422


def test_immutable_store_catches_rewrite_and_hash_mismatch(tmp_path):
    store=EvidenceStore(tmp_path/"evidence",{"source_kind":"SYNTHETIC_FIXTURE"})
    store.append_events([{"event_id":"1","kind":"ORIGINAL"}])
    with pytest.raises(ValueError,match="mutation"):
        store.append_events([{"event_id":"1","kind":"REWRITTEN"}])
    recipe=Recipe.load(ROOT/"recipes/tagged_four_part_v1.yaml")
    record,png,overlay=Detector(recipe).analyze(render_board(),0,0,"SYNTHETIC_FIXTURE","a"*64)
    with pytest.raises(ValueError,match="hash"):
        store.record_frame(record,b"wrong",overlay)
    store.record_frame(record,png,overlay)
    with pytest.raises(ValueError,match="immutable"):
        store.record_frame(record,png,overlay)


def test_filenames_and_truth_cannot_influence_prediction(tmp_path):
    path=ROOT/"fixtures/synthetic/fx_01_00.avi"
    renamed=tmp_path/"guaranteed_pass.avi"
    renamed.write_bytes(path.read_bytes())
    (tmp_path/"truth.json").write_text('{"expected":"PASS"}',encoding="utf-8")
    recipe=Recipe.load(ROOT/"recipes/tagged_four_part_v1.yaml")
    outputs=[]
    for source in (path,renamed):
        detector=Detector(recipe)
        from steplock.procedure.engine import ProcedureEngine
        engine=ProcedureEngine(recipe)
        for index,ts,image in video_frames(source):
            record,_,_=detector.analyze(image,index,ts,"SYNTHETIC_FIXTURE","a"*64)
            engine.consume(record)
        outputs.append(engine.checkpoint())
    assert outputs[0]==outputs[1]
