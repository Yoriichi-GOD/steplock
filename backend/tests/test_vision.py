import hashlib
import cv2
import numpy as np
import pytest
from steplock.config import ROOT
from steplock.procedure.recipe import Recipe
from steplock.vision.aruco import Detector
from steplock.vision.calibration import calibrate
from scripts.fixture_lib import render_board


@pytest.fixture
def detector():
    return Detector(Recipe.load(ROOT/"recipes/tagged_four_part_v1.yaml"))


def inspect(detector, placements=(), **kwargs):
    return detector.analyze(render_board(placements, **kwargs),0,0,"SYNTHETIC_FIXTURE","a"*64)


def test_decode_pixels_and_zone_motion(detector):
    frame,png,_=inspect(detector,[(10,"BASE_SLOT")])
    assert frame.usable
    assert frame.frame_sha256==hashlib.sha256(png).hexdigest()
    assert frame.observations[0].part_id=="BASE"
    assert frame.observations[0].zone_id=="BASE_SLOT"
    moved,_,_=inspect(detector,[(10,"SPACER_SLOT")])
    assert moved.observations[0].zone_id=="SPACER_SLOT"


@pytest.mark.parametrize("variant",[0,1,3,5])
def test_perspective_anchors_and_identity(detector,variant):
    frame,_,_=inspect(detector,[(11,"SPACER_SLOT")],variant=variant,seed=42)
    assert frame.usable
    assert frame.observations[0].marker_id==11
    assert frame.observations[0].zone_id=="SPACER_SLOT"


def test_missing_anchors_cannot_calibrate(detector):
    frame,_,_=inspect(detector,[(10,"BASE_SLOT")],anchors=False)
    assert not frame.usable
    assert frame.calibration_id is None
    assert "CALIBRATION_REQUIRED" in frame.quality_flags


def test_unknown_never_becomes_known(detector):
    frame,_,_=inspect(detector,[(30,"BASE_SLOT")])
    assert frame.observations[0].part_id=="UNKNOWN"


def test_occlusion_not_empty(detector):
    frame,_,_=inspect(detector,occluded="SPACER_SLOT")
    assert "SPACER_SLOT" not in frame.clear_empty_zones


def test_blur_does_not_produce_usable_calibration(detector):
    frame,_,_=inspect(detector,[(10,"BASE_SLOT")],blur=41)
    assert not frame.usable


def test_invalid_calibrations():
    for points in ([[0,0]]*4,[[1,1],[1,400],[900,400],[900,1]],[[0,0],[20,0],[20,20],[0,20]]):
        with pytest.raises(ValueError):
            calibrate(points,(600,960,3))
