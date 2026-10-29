from typing import Literal
from pydantic import BaseModel, ConfigDict, Field

SourceKind = Literal["LIVE_TAGGED", "REPLAY_TAGGED", "SYNTHETIC_FIXTURE"]


class Observation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    observation_id: str
    marker_id: int = Field(ge=0, le=49)
    part_id: str
    board_xy: tuple[float, float] | None
    zone_id: str | None
    corners: list[list[float]]
    area_px2: float = Field(ge=0)
    quality_score: float = Field(ge=0, le=1)
    detection_kind: Literal["ARUCO_TAG_ASSISTED"] = "ARUCO_TAG_ASSISTED"


class FrameObservation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    frame_id: str
    frame_index: int = Field(ge=0)
    captured_at_ms: float = Field(ge=0)
    source_kind: SourceKind
    source_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    frame_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    width: int = Field(ge=80, le=4096)
    height: int = Field(ge=80, le=4096)
    cv_version: str
    usable: bool
    quality_flags: list[str]
    calibration_id: str | None
    calibration_points: list[list[float]]
    calibration_mode: str | None = None
    focus_variance: float
    mean_luminance: float
    saturated_fraction: float
    observations: list[Observation]
    clear_empty_zones: list[str]
    zones_pixels: dict[str, list[list[float]]]
    marker_ids: list[int]
    rejected_candidates: int
    frame_change_mean: float | None = None
    frame_change_fraction: float | None = None
    independent_visual_support: bool = True
    vision_ms: float = Field(ge=0)
