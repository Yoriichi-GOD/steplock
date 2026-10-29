import pytest
from scripts.fixture_lib import render_board
from steplock.config import ROOT
from steplock.procedure.recipe import Recipe
from steplock.procedure.engine import ProcedureEngine
from steplock.vision.aruco import Detector


@pytest.mark.parametrize("wrong_location",["COVER_SLOT",(.49,.9)])
def test_wrong_zone_and_outside_recovery_preserve_new_valid_confirmation(wrong_location):
    recipe=Recipe.load(ROOT/"recipes/tagged_four_part_v1.yaml")
    detector,engine=Detector(recipe),ProcedureEngine(recipe)
    b=(10,"BASE_SLOT");s=(11,"SPACER_SLOT");c=(12,"COVER_SLOT");f=(13,"FASTENER_SLOT")
    stages=[[],[b],[b,(11,wrong_location)],[b,s],[b,s,c],[b,s,c,f]]
    index=0
    for placements in stages:
        for _ in range(6):
            record,_,_=detector.analyze(render_board(placements,seed=index+1),index,index*200,"SYNTHETIC_FIXTURE","a"*64)
            engine.consume(record);index+=1
    state=engine.checkpoint()
    assert state["decision"]["status"]=="PASS",state["decision"]
    original=next(e for e in engine.events if e["kind"]=="WRONG_ZONE")
    assert any(e["kind"]=="CORRECTED" and e["resolves_event_id"]==original["event_id"] for e in engine.events)
    assert all(s["state"]=="CONFIRMED" for s in state["step_states"])
