"""Validate the model's action/citations. Generated wording remains advisory."""
import json
import re
from .schemas import ModelAdvice


def allowed_actions(packet):
    snapshot, event = packet["snapshot"], packet["event"]
    if not snapshot["quality"]["usable"] or snapshot["state"] in {"stopped", "source_lost", "error", "stopping"}:
        return ["RECAPTURE", "ESCALATE_TO_HUMAN"]
    return {"WRONG_COMPONENT": ["CHECK_TAG", "REMOVE_AND_REPLACE", "ESCALATE_TO_HUMAN"],
            "UNKNOWN_COMPONENT": ["CHECK_TAG", "ESCALATE_TO_HUMAN"],
            "WRONG_ZONE": ["REPOSITION", "ESCALATE_TO_HUMAN"],
            "ORDER_VIOLATION": ["REPOSITION", "RECAPTURE", "ESCALATE_TO_HUMAN"],
            "HOLD_UNCERTAIN": ["RECAPTURE", "ESCALATE_TO_HUMAN"],
            "MISSING_AT_CHECKPOINT": ["CHECK_TAG", "RECAPTURE", "ESCALATE_TO_HUMAN"],
            "CORRECTED": ["EXPLAIN", "RECAPTURE"],
            "PASS": ["EXPLAIN"]}.get(event["kind"], ["EXPLAIN", "RECAPTURE"])


def rule_ids(packet):
    event = packet["event"]
    matching = [s["id"] for s in packet["recipe"]["steps"] if s["part"] == event["part_id"] or s["zone"] == event["zone_id"]]
    return matching or [s["id"] for s in packet["recipe"]["steps"]]


def validate(content, packet):
    advice = ModelAdvice.model_validate(json.loads(content))
    event_ids = {e["event_id"] for e in packet["corrections"]["links"]}
    if packet["event"]["event_id"] not in advice.evidence_event_ids or not set(advice.evidence_event_ids) <= event_ids:
        raise ValueError("UNSUPPORTED_EVENT_CITATION")
    if packet["event"]["kind"] == "CORRECTED" and packet["event"]["resolves_event_id"] not in advice.evidence_event_ids:
        raise ValueError("CORRECTION_REQUIRES_ORIGINAL_CITATION")
    if not set(advice.rule_ids) <= set(rule_ids(packet)):
        raise ValueError("UNSUPPORTED_RULE_CITATION")
    if advice.action not in allowed_actions(packet):
        raise ValueError("UNSUPPORTED_ACTION")
    if any(not 5 <= len(step) <= 400 for step in advice.steps):
        raise ValueError("INVALID_STEP_LENGTH")
    text = " ".join([advice.summary, *advice.steps])
    # Conservative filters are a secondary guard, not proof of semantic truth.
    banned = r"\b(pass|certif\w*|torqu\w*|guarante\w*|actuat\w*|plc|energiz\w*|start\s+(?:the\s+)?machine|disable\s+(?:the\s+)?(?:alert|interlock)|override|intrinsic|accident\w*)\b|https?://|<[^>]+>|\b(?:api[_ -]?key|access[_ -]?token)\b"
    if re.search(banned, text, re.I):
        raise ValueError("UNSUPPORTED_OR_UNSAFE_NARRATIVE")
    known_tags = set(packet["recipe"]["parts"].values()) | set(packet["frame"]["marker_ids"])
    claimed_tags = re.findall(r"\b(?:part|marker|tag|tagged)(?:\s+(?:id|as))?\s*[#:=]?\s*(\d+)\b", text, re.I)
    if any(int(tag) not in known_tags for tag in claimed_tags):
        raise ValueError("UNSUPPORTED_TAG_NUMBER")
    for part, expected_tag in packet["recipe"]["parts"].items():
        forward = re.findall(r"\b" + re.escape(part) + r"\s*\(\s*(?:part|marker|tag)\s*(\d+)\s*\)", text, re.I)
        reverse = re.findall(r"\b(?:part|marker|tag)(?:\s+(?:id|labeled|labelled))?\s*(\d+)\s*\(\s*" + re.escape(part) + r"\s*\)", text, re.I)
        if any(int(tag) != expected_tag for tag in forward + reverse):
            raise ValueError("PART_TAG_BINDING_CONTRADICTION")
    if packet["snapshot"]["engine_decision"] == "PASS" and re.search(r"\b(?:not\s+(?:yet\s+)?confirmed|has\s+not\s+(?:yet\s+)?confirmed|missing|not\s+(?:yet\s+)?present)\b", text, re.I):
        raise ValueError("NARRATIVE_CONTRADICTS_CONFIRMED_ENGINE_STATE")
    category = packet["event"]["kind"]
    if category == "CORRECTED":
        category = next((e["kind"] for e in packet["corrections"]["links"] if e["event_id"] == packet["event"]["resolves_event_id"]), category)
    if category == "WRONG_COMPONENT" and re.search(r"\bwrong\s+(?:slot|zone)\b", text, re.I):
        raise ValueError("WRONG_COMPONENT_IS_NOT_WRONG_ZONE")
    if packet["event"]["kind"] == "ORDER_VIOLATION":
        steps = packet["recipe"]["steps"]
        blocked = [s for s in steps if s["id"] in rule_ids(packet)]
        required = {key for step in blocked for key in step["requires"]}
        labels = required | {s["part"] for s in steps if s["id"] in required}
        if labels and not any(re.search(r"\b" + re.escape(label) + r"\b", text, re.I) for label in labels):
            raise ValueError("ORDER_EXPLANATION_OMITS_PREREQUISITE")
    return advice
