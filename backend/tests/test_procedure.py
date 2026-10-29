from copy import deepcopy
import pytest
from steplock.config import ROOT
from steplock.procedure.recipe import Recipe
from steplock.procedure.engine import ProcedureEngine
from steplock.vision.aruco import Detector
from scripts.fixture_lib import scenario_frames, render_board


@pytest.fixture
def recipe():
    return Recipe.load(ROOT/"recipes/tagged_four_part_v1.yaml")


def run_pixels(recipe, family, checkpoint=True, arm="steplock"):
    detector,engine=Detector(recipe),ProcedureEngine(recipe,arm)
    for index,ts,image,_,_ in scenario_frames(family):
        frame,_,_=detector.analyze(image,index,ts,"SYNTHETIC_FIXTURE","a"*64)
        engine.consume(frame)
    return engine, engine.checkpoint() if checkpoint else engine.snapshot()


def test_valid_recipe_and_reject_cycle_missing_overlap_duplicate(recipe,tmp_path):
    Recipe.model_validate(recipe.model_dump())
    for change in ("cycle","missing","overlap","tag","step","unknownpart"):
        data=deepcopy(recipe.model_dump())
        data["steps"]=list(data["steps"])
        if change=="cycle": data["steps"][0]["requires"]=["S4"]
        elif change=="missing": data["steps"][1]["requires"]=["NOPE"]
        elif change=="overlap": data["zones"]["SPACER_SLOT"]=data["zones"]["BASE_SLOT"]
        elif change=="tag": data["parts"]["SPACER"]["aruco_marker_id"]=10
        elif change=="step": data["steps"][1]["id"]="S1"
        else: data["steps"][1]["part"]="INVENTED"
        with pytest.raises(ValueError): Recipe.model_validate(data)
    duplicate=tmp_path/"duplicate.yaml"
    duplicate.write_text("recipe_id: one\nrecipe_id: two\n",encoding="utf-8")
    with pytest.raises(ValueError,match="Duplicate YAML"): Recipe.load(duplicate)


def test_correct_pixels_only_pass_at_explicit_checkpoint(recipe):
    engine,state=run_pixels(recipe,"normal",False)
    assert state["decision"]["status"]=="PENDING"
    assert all(s["state"]=="CONFIRMED" for s in state["step_states"])
    assert engine.checkpoint()["decision"]["status"]=="PASS"


@pytest.mark.parametrize("family,code",[("wrong_component","WRONG_COMPONENT"),("wrong_zone","WRONG_ZONE"),("wrong_order","ORDER_VIOLATION"),("missing_fastener","MISSING_AT_CHECKPOINT")])
def test_errors_have_actual_support(recipe,family,code):
    engine,state=run_pixels(recipe,family)
    assert state["decision"]["status"]=="HOLD_FOR_REVIEW"
    findings=[e for e in engine.events if e["kind"]==code]
    assert findings and all(e["evidence_ids"] and e["frame_sha256"] for e in findings)


def test_missing_only_at_finish(recipe):
    engine,state=run_pixels(recipe,"missing_fastener",False)
    assert state["decision"]["status"]=="PENDING"
    assert not any(e["kind"]=="MISSING_AT_CHECKPOINT" for e in engine.events)
    assert "MISSING_AT_CHECKPOINT" in engine.checkpoint()["decision"]["reason_codes"]


def test_correction_is_append_only_and_resumes(recipe):
    engine,state=run_pixels(recipe,"correction")
    assert state["decision"]["status"]=="PASS"
    original=next(e for e in engine.events if e["kind"]=="WRONG_COMPONENT")
    assert "resolved_at" not in original
    assert any(e["kind"]=="CORRECTED" and e["resolves_event_id"]==original["event_id"] for e in engine.events)


def test_midassembly_does_not_invent_order_violation(recipe):
    detector,engine=Detector(recipe),ProcedureEngine(recipe)
    placements=[(10,"BASE_SLOT"),(11,"SPACER_SLOT"),(12,"COVER_SLOT"),(13,"FASTENER_SLOT")]
    for index in range(5):
        record,_,_=detector.analyze(render_board(placements,seed=index+1),index,index*200,"SYNTHETIC_FIXTURE","a"*64)
        engine.consume(record)
    state=engine.checkpoint()
    assert state["decision"]["status"]!="PASS"
    assert any(e["kind"]=="HOLD_UNCERTAIN" for e in engine.events)
    assert not any(e["kind"]=="ORDER_VIOLATION" for e in engine.events)


def test_duplicate_images_cannot_confirm(recipe):
    engine,state=run_pixels(recipe,"frozen_capture")
    assert not engine.confirmed
    assert state["decision"]["status"]!="PASS"
    assert "DUPLICATE_FRAME" in state["quality"]["flags"]


def test_occluded_confirmed_part_is_not_deleted_or_passed(recipe):
    engine,state=run_pixels(recipe,"occlusion")
    assert state["decision"]["status"]!="PASS"
    assert "S2" in engine.confirmed
    assert not any(e["kind"]=="PLACEMENT_REMOVED" for e in engine.events)


def test_order_fault_requires_remove_and_replace(recipe):
    detector,engine=Detector(recipe),ProcedureEngine(recipe)
    stages=[[],[(10,"BASE_SLOT")],[(10,"BASE_SLOT"),(12,"COVER_SLOT")],
            [(10,"BASE_SLOT"),(11,"SPACER_SLOT"),(12,"COVER_SLOT")],
            [(10,"BASE_SLOT"),(11,"SPACER_SLOT")],
            [(10,"BASE_SLOT"),(11,"SPACER_SLOT"),(12,"COVER_SLOT")],
            [(10,"BASE_SLOT"),(11,"SPACER_SLOT"),(12,"COVER_SLOT"),(13,"FASTENER_SLOT")]]
    before=None
    index=0
    for stage_index,placements in enumerate(stages):
        for _ in range(5):
            record,_,_=detector.analyze(render_board(placements,seed=index+1),index,index*200,"SYNTHETIC_FIXTURE","a"*64)
            engine.consume(record)
            index+=1
        if stage_index==3:
            before=engine.snapshot()
    assert "ORDER_VIOLATION" in before["decision"]["reason_codes"]
    assert engine.checkpoint()["decision"]["status"]=="PASS"
    assert any(e["kind"]=="CORRECTED" for e in engine.events)


def test_timestamp_backwards_and_stale_source_are_safe(recipe):
    engine,state=run_pixels(recipe,"normal")
    record=engine.frame.model_copy(update={"captured_at_ms":1})
    assert engine.consume(record)["decision"]["status"]!="PASS"
    assert "NONMONOTONIC_TIMESTAMP" in engine.quality_flags
    engine.source_lost()
    assert engine.snapshot()["decision"]["status"]=="SOURCE_LOST"


def test_one_frame_not_enough_and_deterministic_replay(recipe):
    detector,engine=Detector(recipe),ProcedureEngine(recipe)
    record,_,_=detector.analyze(render_board([(10,"BASE_SLOT")]),0,0,"SYNTHETIC_FIXTURE","a"*64)
    engine.consume(record)
    assert not engine.confirmed
    a,_=run_pixels(recipe,"wrong_component")
    b,_=run_pixels(recipe,"wrong_component")
    assert a.events==b.events


def test_snapshot_mutation_cannot_change_historical_events(recipe):
    engine,_=run_pixels(recipe,"normal")
    snapshot=engine.snapshot()
    snapshot["events"][0]["kind"]="FAKE"
    assert engine.events[0]["kind"]!="FAKE"
