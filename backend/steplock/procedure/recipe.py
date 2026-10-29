import hashlib
import json
from pathlib import Path
from typing import Self
from pydantic import BaseModel, ConfigDict, Field, model_validator
import yaml


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


class Part(StrictModel):
    aruco_marker_id: int = Field(ge=0, lt=40)


class Step(StrictModel):
    id: str = Field(min_length=1, max_length=40, pattern=r"^[A-Za-z0-9_-]+$")
    part: str
    zone: str
    requires: tuple[str, ...] = ()


class Recipe(StrictModel):
    recipe_id: str = Field(pattern=r"^[a-zA-Z0-9_-]+$", max_length=80)
    name: str = Field(min_length=1, max_length=160)
    version: int = Field(ge=1)
    advisory_only: bool = True
    dictionary: str = "DICT_4X4_50"
    minimum_supporting_frames: int = Field(default=2, ge=2, le=10)
    minimum_support_gap_ms: int = Field(default=160, ge=120, le=2000)
    maximum_observation_gap_ms: int = Field(default=1800, ge=500, le=10000)
    minimum_focus_variance: float = Field(default=35, ge=0)
    zone_inset: float = Field(default=0.012, ge=0, le=0.04)
    parts: dict[str, Part]
    zones: dict[str, tuple[float, float, float, float]]
    steps: tuple[Step, ...]

    @model_validator(mode="after")
    def validate_graph(self) -> Self:
        if not self.advisory_only or self.dictionary != "DICT_4X4_50":
            raise ValueError("Only advisory DICT_4X4_50 recipes are supported")
        if not self.steps or len(self.steps) > 16:
            raise ValueError("Recipe must contain 1–16 steps")
        ids = [step.id for step in self.steps]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate step IDs")
        tags = [part.aruco_marker_id for part in self.parts.values()]
        if len(tags) != len(set(tags)):
            raise ValueError("Duplicate marker IDs")
        if len({s.part for s in self.steps}) != len(self.steps) or len({s.zone for s in self.steps}) != len(self.steps):
            raise ValueError("Each required part and zone must have a unique step")
        for name, box in self.zones.items():
            x1, y1, x2, y2 = box
            if not (0 <= x1 < x2 <= 1 and 0 <= y1 < y2 <= 1):
                raise ValueError(f"Invalid zone: {name}")
            if min(x2 - x1, y2 - y1) <= self.zone_inset * 2:
                raise ValueError(f"Zone too narrow for inset: {name}")
        zones = list(self.zones.items())
        for i, (name, a) in enumerate(zones):
            for other, b in zones[i + 1:]:
                if min(a[2], b[2]) > max(a[0], b[0]) and min(a[3], b[3]) > max(a[1], b[1]):
                    raise ValueError(f"Overlapping zones: {name}, {other}")
        graph = {s.id: s.requires for s in self.steps}
        for s in self.steps:
            if s.part not in self.parts or s.zone not in self.zones:
                raise ValueError(f"Unknown part/zone in {s.id}")
            if any(r not in graph for r in s.requires):
                raise ValueError(f"Unknown prerequisite in {s.id}")
        visiting, done = set(), set()

        def visit(key):
            if key in visiting:
                raise ValueError("Cyclic prerequisite graph")
            if key in done:
                return
            visiting.add(key)
            for parent in graph[key]:
                visit(parent)
            visiting.remove(key)
            done.add(key)

        for key in graph:
            visit(key)
        return self

    @property
    def sha256(self):
        return hashlib.sha256(json.dumps(self.model_dump(), sort_keys=True).encode()).hexdigest()

    @classmethod
    def load(cls, path: Path):
        # Reject duplicate YAML keys before Pydantic can see an overwritten zone.
        class UniqueLoader(yaml.SafeLoader):
            pass

        def mapping(loader, node, deep=False):
            result = {}
            for key_node, value_node in node.value:
                key = loader.construct_object(key_node, deep=deep)
                if key in result:
                    raise ValueError(f"Duplicate YAML key: {key}")
                result[key] = loader.construct_object(value_node, deep=deep)
            return result

        UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, mapping)
        return cls.model_validate(yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueLoader))
