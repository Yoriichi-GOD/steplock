import time
import cv2
from fastapi.testclient import TestClient
from backend.app import create_app
from steplock.config import ROOT
from steplock.procedure.recipe import Recipe
from steplock.service import Session
from steplock.sources.replay import video_frames
from scripts.fixture_lib import render_board


def test_development_regression_missed_spacer_is_decoded():
    from steplock.vision.aruco import Detector
    detector=Detector(Recipe.load(ROOT/"recipes/tagged_four_part_v1.yaml"))
    image=cv2.imread(str(ROOT/"fixtures/synthetic/dev_regression_spacer.png"))
    last=detector.analyze(image,41,8200,"SYNTHETIC_FIXTURE","a"*64)[0]
    # Exact failed development pixels; no predicted-label oracle.
    assert {10,11,12,13}.issubset(last.marker_ids)


def test_saved_recipe_versions_survive_restart(tmp_path):
    with TestClient(create_app(runtime_root=tmp_path)) as client:
        recipe=client.get("/api/recipes").json()[0]
        recipe.pop("key");recipe.pop("sha256");recipe["version"]=2
        saved=client.post("/api/recipes",json=recipe).json()
    with TestClient(create_app(runtime_root=tmp_path)) as client:
        versions=client.get("/api/recipes").json()
        assert any(r["sha256"]==saved["sha256"] for r in versions)


def test_recorded_camera_requires_consent(tmp_path):
    with TestClient(create_app(runtime_root=tmp_path)) as client:
        assert client.post("/api/sessions",json={"source_kind":"REPLAY_TAGGED"}).status_code==400


def test_mjpeg_repeated_picture_does_not_confirm_any_step():
    from steplock.vision.aruco import Detector
    from steplock.procedure.engine import ProcedureEngine
    recipe=Recipe.load(ROOT/"recipes/tagged_four_part_v1.yaml")
    detector,engine=Detector(recipe),ProcedureEngine(recipe)
    for index,ts,image in video_frames(ROOT/"fixtures/synthetic/fx_07_00.avi"):
        record,_,_=detector.analyze(image,index,ts,"SYNTHETIC_FIXTURE","a"*64)
        engine.consume(record)
    assert not engine.confirmed
    assert engine.checkpoint()["decision"]["status"]!="PASS"
    naive=ProcedureEngine(recipe,"single_frame")
    detector=Detector(recipe)
    for index,ts,image in video_frames(ROOT/"fixtures/synthetic/fx_07_00.avi"):
        record,_,_=detector.analyze(image,index,ts,"SYNTHETIC_FIXTURE","a"*64)
        naive.consume(record)
    assert naive.checkpoint()["decision"]["status"]=="PASS"


def test_manual_calibration_expires_without_anchors(tmp_path):
    recipe=Recipe.load(ROOT/"recipes/tagged_four_part_v1.yaml")
    session=Session(recipe,"SYNTHETIC_FIXTURE",False,directory=tmp_path/"session")
    session.manual_points=[[60,70],[900,70],[900,470],[60,470]]
    session.manual_calibrated_at_ms=0
    image=render_board(anchors=False)
    session.process(0,200,image)
    assert session.latest.calibration_mode=="MANUAL_FOUR_POINT"
    session.process(1,2000,render_board(anchors=False,seed=12))
    assert session.latest.calibration_id is None
    assert "CALIBRATION_REQUIRED" in session.latest.quality_flags
