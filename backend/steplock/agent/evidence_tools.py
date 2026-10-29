"""Backend-controlled, allowlisted reads. No pixels, arbitrary paths, or URLs."""
from copy import deepcopy
import hashlib
import json
import re
import time


def safe_id(value):
    return value if isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_-]{1,80}", value) else "UNTRUSTED_LABEL_OMITTED"


def fingerprint(session):
    snapshot = session.snapshot()
    value = {key: snapshot[key] for key in ["session_id", "recipe_sha256", "revision", "state", "decision", "unresolved_event_ids"]}
    value["frame_id"] = snapshot["latest_frame"]["frame_id"] if snapshot["latest_frame"] else None
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


class EvidenceTools:
    def __init__(self, session):
        self.session = session
        self.trace = []

    def read(self, name, argument=None):
        if len(self.trace) >= 5:
            raise ValueError("TOOL_LIMIT_EXCEEDED")
        started = time.perf_counter()
        session = self.session
        if name == "read_recipe":
            recipe = session.recipe
            result = {"recipe_id": recipe.recipe_id, "version": recipe.version, "sha256": recipe.sha256,
                      "parts": {safe_id(s.part): recipe.parts[s.part].aruco_marker_id for s in recipe.steps},
                      "steps": [{"id": s.id, "part": safe_id(s.part), "zone": safe_id(s.zone), "requires": list(s.requires)} for s in recipe.steps]}
        elif name == "read_session_snapshot":
            snapshot = session.snapshot()
            result = {"session_id": session.id, "engine_decision": snapshot["decision"]["status"], "state": snapshot["state"],
                      "revision": snapshot["revision"], "latest_frame_id": snapshot["latest_frame"]["frame_id"] if snapshot["latest_frame"] else None,
                      "source_kind": session.source_kind, "population": safe_id(session.source_metadata.get("population", session.source_kind)),
                      "quality": {"usable": snapshot["quality"]["usable"], "flags": snapshot["quality"]["flags"]},
                      "unresolved_event_ids": snapshot["unresolved_event_ids"], "next_allowed_steps": snapshot["next_allowed_steps"],
                      "steps": [{"id": s["id"], "state": s["state"]} for s in snapshot["step_states"]]}
        elif name == "read_event":
            event = next((e for e in session.engine.events if e["event_id"] == argument), None)
            if event is None:
                raise KeyError("EVENT_NOT_IN_SESSION")
            result = {key: deepcopy(event[key]) for key in ["event_id", "kind", "source_time_ms", "frame_id", "frame_sha256", "source_sha256", "resolves_event_id"]}
            result.update({"part_id": safe_id(event["part_id"]) if event["part_id"] else None,
                           "zone_id": safe_id(event["zone_id"]) if event["zone_id"] else None})
        elif name == "read_evidence_frame_metadata":
            frame = session.store.frame_records.get(argument) if session.store else None
            if frame is None:
                raise KeyError("FRAME_NOT_IN_SESSION")
            result = {key: deepcopy(frame[key]) for key in ["frame_id", "captured_at_ms", "frame_sha256", "source_sha256", "width", "height", "marker_ids", "usable", "quality_flags", "calibration_id"]}
        elif name == "read_correction_links":
            events = session.engine.events
            event = next((e for e in events if e["event_id"] == argument), None)
            if event is None:
                raise KeyError("EVENT_NOT_IN_SESSION")
            ids = {event["event_id"], event["resolves_event_id"]}
            ids.update(e["event_id"] for e in events if e["resolves_event_id"] == argument)
            result = {"links": [{"event_id": e["event_id"], "kind": e["kind"], "resolves_event_id": e["resolves_event_id"],
                                  "frame_id": e["frame_id"], "frame_sha256": e["frame_sha256"]} for e in events if e["event_id"] in ids]}
        else:
            raise ValueError("TOOL_NOT_ALLOWED")
        self.trace.append({"tool": name, "argument": argument, "output_sha256": hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest(),
                           "elapsed_ms": round((time.perf_counter() - started) * 1000, 3), "result": result})
        return result


def gather(session, event_id, purpose):
    with session.lock:
        snapshot = session.snapshot()
        if not snapshot["events"] or session.latest is None:
            raise ValueError("NO_RETAINED_EVENT")
        if snapshot["state"] == "running":
            raise ValueError("FINISH_OR_STOP_SOURCE_BEFORE_GUIDANCE")
        if event_id is None:
            candidates = snapshot["events"]
            if purpose == "summarize_correction":
                candidates = [e for e in candidates if e["kind"] == "CORRECTED"]
            elif snapshot["unresolved_event_ids"]:
                candidates = [e for e in candidates if e["event_id"] in snapshot["unresolved_event_ids"]]
            if not candidates:
                raise ValueError("NO_MATCHING_EVENT")
            explicit = [e for e in candidates if e["kind"] in {"WRONG_COMPONENT", "UNKNOWN_COMPONENT", "WRONG_ZONE", "ORDER_VIOLATION"}]
            event_id = (explicit or candidates)[-1]["event_id"]
        tools = EvidenceTools(session)
        packet = {"recipe": tools.read("read_recipe"), "snapshot": tools.read("read_session_snapshot"),
                  "event": tools.read("read_event", event_id)}
        event = packet["event"]
        if not event["frame_id"]:
            raise ValueError("EVENT_HAS_NO_SOURCE_FRAME")
        packet["frame"] = tools.read("read_evidence_frame_metadata", event["frame_id"])
        if event["frame_sha256"] != packet["frame"]["frame_sha256"] or event["source_sha256"] != session.source_hash:
            raise ValueError("SOURCE_PROVENANCE_MISMATCH")
        packet["corrections"] = tools.read("read_correction_links", event_id)
        matching = [s for s in packet["recipe"]["steps"] if s["part"] == event["part_id"] or s["zone"] == event["zone_id"]]
        original = next((e for e in packet["corrections"]["links"] if e["event_id"] == event["resolves_event_id"]), None)
        packet["verified_facts"] = {"finding_kind": event["kind"], "original_finding_kind": original["kind"] if original else None,
                                    "expected_placements": [{"step": s["id"], "part": s["part"], "zone": s["zone"], "required_tag": packet["recipe"]["parts"][s["part"]], "requires": s["requires"]} for s in matching],
                                    "observed_frame_tags": packet["frame"]["marker_ids"],
                                    "identity_limit": "Decoded tags, not intrinsic component identity or fastening."}
        if purpose == "summarize_correction" and event["kind"] != "CORRECTED":
            raise ValueError("NOT_A_CORRECTION_EVENT")
        return packet, tools.trace, fingerprint(session)
