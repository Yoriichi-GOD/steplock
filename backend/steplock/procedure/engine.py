"""Conservative visible-placement state machine shared by the app and evaluator.

Events are append-only. Resolution is a new event, never a mutation of a finding.
An image without a decoded marker is NOT automatically evidence of empty space.
"""
from collections import OrderedDict, deque
from copy import deepcopy
from dataclasses import dataclass, field


@dataclass
class Track:
    first_ms: float
    support: deque = field(default_factory=lambda: deque(maxlen=12))


class ProcedureEngine:
    def __init__(self, recipe, arm="steplock"):
        if arm not in {"single_frame", "stable_only", "steplock"}:
            raise ValueError("Unknown experimental arm")
        self.recipe, self.arm = recipe, arm
        self.events = []
        self.active_faults = {}
        self.confirmed = {}  # step -> confirmation time, strictly before a later placement begins
        self.support_ids = {}
        self.tracks, self.absences, self.empty_tracks = {}, {}, {}
        self.present = set()
        self.current_pairs = set()
        self.seen = OrderedDict()
        self.frame = None
        self.last_ms = None
        self.quality_flags = ["AWAITING_SOURCE"]
        self.history_broken = False
        self.checkpointed = False
        self.revision = 0
        self.by_part = {step.part: step for step in recipe.steps}
        self.by_id = {step.id: step for step in recipe.steps}

    def _emit(self, kind, reason, *, pair=None, support=(), resolves=None):
        frame = self.frame
        event = {"event_id": f"evt-{len(self.events)+1:05d}", "kind": kind,
                 "source_time_ms": frame.captured_at_ms if frame else 0,
                 "frame_id": frame.frame_id if frame else None,
                 "frame_sha256": frame.frame_sha256 if frame else None,
                 "source_sha256": frame.source_sha256 if frame else None,
                 "reason": reason, "part_id": pair[0] if pair else None,
                 "zone_id": pair[1] if pair else None, "evidence_ids": list(support),
                 "resolves_event_id": resolves}
        self.events.append(event)
        self.revision += 1
        return event

    def _fault(self, code, pair, reason, support):
        key = (code, *pair)
        if key not in self.active_faults:
            event = self._emit(code, reason, pair=pair, support=support)
            self.active_faults[key] = event
            self.checkpointed = False

    def _resolve_pair(self, pair, support):
        for key, old in list(self.active_faults.items()):
            if key[1:] == pair:
                self._emit("CORRECTED", f"Visible arrangement corrected: {old['kind']}. Recheck the recipe before proceeding.",
                           pair=pair, support=support, resolves=old["event_id"])
                del self.active_faults[key]

    def _push(self, history, key, frame, observation_id=None):
        track = history.get(key)
        if track is None or (track.support and frame.captured_at_ms-track.support[-1][0] > self.recipe.maximum_observation_gap_ms):
            track = history[key] = Track(frame.captured_at_ms)
        if not track.support or track.support[-1][1] != frame.frame_sha256:
            track.support.append((frame.captured_at_ms, frame.frame_sha256, observation_id or frame.frame_id))
        return track

    def _stable(self, track):
        if not track or not track.support:
            return False
        if self.arm == "single_frame":
            return True
        return len(track.support) >= self.recipe.minimum_supporting_frames and track.support[-1][0]-track.support[0][0] >= self.recipe.minimum_support_gap_ms

    @staticmethod
    def _ids(track):
        return [s[2] for s in track.support]

    def _quality(self, flags):
        flags = sorted(set(flags))
        if flags != self.quality_flags:
            if flags:
                self._emit("QUALITY_HOLD", ", ".join(flags))
            elif self.quality_flags:
                self._emit("SOURCE_USABLE", "Fresh frame and current calibration are usable.")
        self.quality_flags = flags

    def consume(self, frame):
        self.frame = frame
        flags = list(frame.quality_flags)
        if self.last_ms is not None and frame.captured_at_ms <= self.last_ms:
            flags.append("NONMONOTONIC_TIMESTAMP")
            self.history_broken = True
        if self.last_ms is not None and frame.captured_at_ms-self.last_ms > self.recipe.maximum_observation_gap_ms:
            flags.append("SOURCE_GAP")
            self.history_broken = True
        self.last_ms = max(self.last_ms or 0, frame.captured_at_ms)
        if frame.frame_sha256 in self.seen and self.arm != "single_frame":
            flags.append("DUPLICATE_FRAME")
        self.seen[frame.frame_sha256] = True
        if len(self.seen) > 4096:
            self.seen.popitem(last=False)
        if self.history_broken and self.arm == "steplock":
            flags.append("HISTORY_GAP_RESTART_REQUIRED")
        if not frame.usable or flags:
            self._quality(flags or ["UNUSABLE_FRAME"])
            return self.snapshot()
        pairs = {(ob.part_id, ob.zone_id or "OUTSIDE"): ob for ob in frame.observations}
        # Duplicate visible IDs are a perception quality error, never collapsed into proof.
        self.current_pairs = set(pairs)
        for zone in self.recipe.zones:
            if zone in frame.clear_empty_zones:
                self._push(self.empty_tracks, zone, frame)
            else:
                self.empty_tracks.pop(zone, None)
        for pair, ob in pairs.items():
            self._push(self.tracks, pair, frame, ob.observation_id)
            self.absences.pop(pair, None)
        # A removal requires supported clear space OR a stable, visibly different tag
        # replacing that location. Hidden stacked tags are outside this demo's guarantee.
        for pair in list(self.present):
            if pair in pairs:
                continue
            replacement = any(p[1] == pair[1] and self._stable(self.tracks.get(p)) for p in pairs)
            clear = pair[1] in frame.clear_empty_zones or replacement
            if clear:
                absence = self._push(self.absences, pair, frame)
                if self._stable(absence):
                    self._remove(pair, self._ids(absence))
            else:
                self.absences.pop(pair, None)
        # Unconfirmed candidate disappears into a proven clear slot: reset its onset.
        for pair in list(self.tracks):
            if pair not in pairs and pair not in self.present and pair[1] in frame.clear_empty_zones:
                self.tracks.pop(pair, None)
        for pair in sorted(pairs):
            track = self.tracks[pair]
            if pair not in self.present and self._stable(track):
                self.present.add(pair)
                self.checkpointed = False
                self._placement(pair, track)
        # Current visibility is mandatory even for historically confirmed components.
        if any((s.part, s.zone) not in pairs for s in self.recipe.steps if s.id in self.confirmed):
            self._quality(["CONFIRMED_COMPONENT_NOT_CURRENTLY_VISIBLE"])
        else:
            self._quality([])
        return self.snapshot()

    def _placement(self, pair, track):
        part, zone = pair
        evidence = self._ids(track)
        step = self.by_part.get(part)
        self._emit("PLACEMENT_OBSERVED", f"Stable visible tag {part} in {zone}.", pair=pair, support=evidence)
        if step is None:
            code = "UNKNOWN_COMPONENT" if part == "UNKNOWN" else "WRONG_COMPONENT"
            self._fault(code, pair, f"{part} is not a required component here. Remove it and use the recipe's tagged component.", evidence)
            return
        if step.zone != zone:
            self._fault("WRONG_ZONE", pair, f"{part} belongs in {step.zone}; observed in {zone}.", evidence)
            return
        if self.arm == "steplock":
            unmet = [parent for parent in step.requires if parent not in self.confirmed or self.confirmed[parent] >= track.first_ms]
            if unmet:
                proven_empty = True
                absence_ids = []
                for parent in unmet:
                    previous = self.empty_tracks.get(self.by_id[parent].zone)
                    qualifying = [] if previous is None else [s for s in previous.support if s[0] <= track.first_ms]
                    if len(qualifying) < self.recipe.minimum_supporting_frames or qualifying[-1][0]-qualifying[0][0] < self.recipe.minimum_support_gap_ms or track.first_ms-qualifying[-1][0] > self.recipe.maximum_observation_gap_ms:
                        proven_empty = False
                    absence_ids.extend(s[2] for s in qualifying)
                code = "ORDER_VIOLATION" if proven_empty else "HOLD_UNCERTAIN"
                reason = (f"{part} appeared before prerequisites {', '.join(unmet)} were completed; prior clear-zone frames support the order finding."
                          if proven_empty else f"Cannot prove the order of {part}: prerequisites {', '.join(unmet)} lack earlier completion evidence. Remove/re-place it after prerequisites, or restart from an empty board.")
                self._fault(code, pair, reason, evidence+absence_ids)
                return
        self.confirmed[step.id] = self.frame.captured_at_ms
        self.support_ids[step.id] = evidence
        self._emit("STEP_CONFIRMED", f"{step.id}: {part} visibly placed in {zone}; supported by independent observations.", pair=pair, support=evidence)
        missing_key = ("MISSING_AT_CHECKPOINT", *pair)
        if missing_key in self.active_faults:
            old = self.active_faults.pop(missing_key)
            self._emit("CORRECTED", f"Previously missing {part} is now visually confirmed.", pair=pair, support=evidence, resolves=old["event_id"])

    def _remove(self, pair, support):
        self.present.discard(pair)
        self.tracks.pop(pair, None)
        self.absences.pop(pair, None)
        self._resolve_pair(pair, support)
        self._emit("PLACEMENT_REMOVED", f"Supported visible removal/replacement of {pair[0]} from {pair[1]}.", pair=pair, support=support)
        self.checkpointed = False
        step = self.by_part.get(pair[0])
        if step and step.id in self.confirmed:
            del self.confirmed[step.id]
            affected = {step.id}
            for _ in self.recipe.steps:
                for other in self.recipe.steps:
                    if any(parent in affected for parent in other.requires):
                        affected.add(other.id)
            for sid in affected-{step.id}:
                if sid in self.confirmed:
                    del self.confirmed[sid]
                    other=self.by_id[sid]
                    self._fault("ORDER_REVALIDATION_REQUIRED", (other.part,other.zone),
                                f"Prerequisite {step.id} was removed. Re-place {other.part} after its prerequisite is proven again.",support)

    def checkpoint(self):
        self._emit("CHECKPOINT", "Operator requested final visible-placement inspection.")
        for step in self.recipe.steps:
            if step.id not in self.confirmed:
                self._fault("MISSING_AT_CHECKPOINT", (step.part,step.zone),
                            f"{step.part} is not proven at the explicit final checkpoint. Observe/re-place it correctly and check again.",
                            [self.frame.frame_id] if self.frame else [])
        self.checkpointed = True
        return self.snapshot()

    def source_lost(self, reason="Source stopped or stopped delivering fresh frames."):
        self._quality(["SOURCE_LOST"])
        self.checkpointed = False
        self._emit("SOURCE_LOST", reason)

    def snapshot(self):
        codes = sorted({key[0] for key in self.active_faults})
        all_proven = len(self.confirmed) == len(self.recipe.steps)
        if self.quality_flags:
            status = "SOURCE_LOST" if "SOURCE_LOST" in self.quality_flags else "CALIBRATION_REQUIRED" if any("CALIBRATION" in f for f in self.quality_flags) else "HOLD_FOR_REVIEW"
            reason = "Capture needs review: " + ", ".join(self.quality_flags)
        elif self.active_faults:
            status, reason = "HOLD_FOR_REVIEW", next(iter(self.active_faults.values()))["reason"]
        elif self.checkpointed and all_proven:
            status, reason = "PASS", "All required visible placements, order and current evidence satisfy this recipe. Advisory only."
        else:
            status = "PENDING"
            reason = "All placements confirmed. Request the final checkpoint." if all_proven else "Waiting for the next permitted visible placement."
        states = []
        for step in self.recipe.steps:
            pair = (step.part,step.zone)
            fault = any(k[1:] == pair for k in self.active_faults)
            state = "CONFIRMED" if step.id in self.confirmed else "BLOCKED" if fault else "OBSERVED_CANDIDATE" if pair in self.tracks else "NOT_STARTED"
            states.append({**step.model_dump(), "state":state, "confirmed_at_ms":self.confirmed.get(step.id),
                           "evidence_ids":self.support_ids.get(step.id,[]),
                           "allowed":all(p in self.confirmed for p in step.requires)})
        next_steps = [s for s in states if s["state"] != "CONFIRMED" and s["allowed"]]
        return {"decision":{"status":status,"reason":reason,"reason_codes":codes + self.quality_flags,
                            "advisory_only":True},
                "step_states":states, "events":deepcopy(self.events),
                "unresolved_event_ids":[e["event_id"] for e in self.active_faults.values()],
                "quality":{"usable":not self.quality_flags,"flags":list(self.quality_flags),
                           "calibration_id":self.frame.calibration_id if self.frame else None},
                "next_allowed_steps":[s["id"] for s in next_steps],"checkpoint_requested":self.checkpointed,
                "revision":self.revision}
