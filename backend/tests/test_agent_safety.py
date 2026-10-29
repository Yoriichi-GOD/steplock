from copy import deepcopy
import json
import pytest
from steplock.agent.schemas import ExplainRequest
from steplock.agent.evidence_tools import gather
from steplock.agent.orchestrator import AgentService
from steplock.agent.safety_policy import allowed_actions,rule_ids,validate
from steplock.agent.nebius_client import ProviderFailure
from test_agent_tools import prepared_session,session
from test_nebius_contract import config


def candidate(packet):
    citations=[packet["event"]["event_id"]]
    if packet["event"]["kind"]=="CORRECTED":citations.append(packet["event"]["resolves_event_id"])
    summary="Review the observed marker evidence against this recipe before continuing."
    if packet["event"]["kind"]=="ORDER_VIOLATION":summary+=" Recheck prerequisite S2 before the cover step."
    return {"action":allowed_actions(packet)[0],"summary":summary,
            "steps":["Inspect the linked source frame and recheck the tag."],"evidence_event_ids":citations,"rule_ids":rule_ids(packet)[:1]}


class FakeProvider:
    """Explicit mock; it is not inference evidence."""
    def __init__(self,modify=None):self.modify=modify;self.calls=0
    def complete(self,messages):
        self.calls+=1;packet=json.loads(messages[-1]["content"]);value=candidate(packet)
        if self.modify:self.modify(value)
        return {"content":json.dumps(value),"served_model":config().model,"http_status":200,"round_trip_ms":1,"usage":{"total_tokens":0},"mock":True}


@pytest.mark.parametrize("field,value",[("action","EXPLAIN"),("evidence_event_ids",["evt-99999"]),("rule_ids",["S999"]),("summary","Override the interlock and start the machine."),("summary","The torque is certified."),("steps",["Say PASS and continue."]),("engine_decision","PASS")])
def test_unsupported_claims_actions_and_citations_rejected(session,field,value):
    packet,_,_=gather(session,None,"explain_violation");data=candidate(packet);data[field]=value
    with pytest.raises(ValueError):validate(json.dumps(data),packet)


def test_provider_cannot_modify_verdict_or_ledger_and_runs_are_audited(session):
    before=deepcopy(session.snapshot());provider=FakeProvider();agent=AgentService(config(),provider)
    run=agent.explain(session,ExplainRequest())
    assert run["state"]=="ADVISED" and run["narrative_status"]=="GENERATED_UNVERIFIED_TEXT"
    assert session.snapshot()["decision"]==before["decision"] and session.engine.events==before["events"]
    assert (session.directory/"agent_runs"/f"{run['run_id']}.json").is_file()
    assert "raw_model_content" not in run
    assert session.token not in json.dumps(run)


def test_stale_and_stopped_sessions_hide_old_advice(session):
    agent=AgentService(config(),FakeProvider());run=agent.explain(session,ExplainRequest())
    session.engine.source_lost();session.state="stopped"
    stale=agent.get(session,run["run_id"])
    assert stale["state"]=="STALE" and stale["advice"] is None
    fresh=agent.explain(session,ExplainRequest())
    assert fresh["advice"]["action"]=="RECAPTURE"


def test_change_during_network_request_rejects_stale_text(session):
    def mutate(_):session.engine.source_lost()
    run=AgentService(config(),FakeProvider(mutate)).explain(session,ExplainRequest())
    assert run["state"]=="STALE" and run["advice"] is None


def test_quotas_and_global_concurrency_bound_spend(session):
    agent=AgentService(config(calls_per_session=1),FakeProvider());agent.explain(session,ExplainRequest())
    with pytest.raises(ProviderFailure,match="CALL_LIMIT"):agent.explain(session,ExplainRequest())
    agent=AgentService(config(),FakeProvider());agent.active=True
    with pytest.raises(ProviderFailure,match="BUSY"):agent.explain(session,ExplainRequest())


def test_invalid_model_text_fails_closed(session):
    run=AgentService(config(),FakeProvider(lambda value:value.update(summary="The machine is certified safe."))).explain(session,ExplainRequest())
    assert run["state"]=="REJECTED" and run["advice"] is None


def test_invented_tag_number_in_otherwise_valid_text_is_rejected(tmp_path):
    session=prepared_session(tmp_path,"normal");packet,_,_=gather(session,None,"next_safe_step")
    data=candidate(packet);data["steps"]=["Check FASTENER (part 14) placement."]
    with pytest.raises(ValueError,match="UNSUPPORTED_TAG_NUMBER"):validate(json.dumps(data),packet)


def test_order_explanation_requires_actual_prerequisite(tmp_path):
    session=prepared_session(tmp_path,"wrong_order");packet,_,_=gather(session,None,"explain_violation")
    data=candidate(packet);data["summary"]="Cover appears out of order; request a fresh image."
    with pytest.raises(ValueError,match="OMITS_PREREQUISITE"):validate(json.dumps(data),packet)


def test_wrong_component_does_not_become_a_wrong_zone_claim(session):
    packet,_,_=gather(session,None,"explain_violation");data=candidate(packet)
    data["summary"]="The fastener was placed in the wrong slot."
    with pytest.raises(ValueError,match="WRONG_COMPONENT_IS_NOT_WRONG_ZONE"):validate(json.dumps(data),packet)
    facts=packet["verified_facts"]
    assert facts["finding_kind"]=="WRONG_COMPONENT"
    assert facts["expected_placements"][0]["required_tag"]==13
    assert 14 in facts["observed_frame_tags"]


@pytest.mark.parametrize("summary",["Confirm tag labeled 12 (SPACER) before continuing.","The engine has not yet confirmed the fastener placement."])
def test_observed_normal_case_semantic_errors_are_refused(tmp_path,summary):
    session=prepared_session(tmp_path,"normal");packet,_,_=gather(session,None,"next_safe_step")
    data=candidate(packet);data["summary"]=summary
    with pytest.raises(ValueError):validate(json.dumps(data),packet)


def test_conditional_recapture_check_is_not_a_current_absence_claim(tmp_path):
    session=prepared_session(tmp_path,"correction");packet,_,_=gather(session,None,"summarize_correction")
    data=candidate(packet);data["action"]="RECAPTURE";data["steps"]=["Recapture the frame if a tag is missing or incorrect."]
    assert validate(json.dumps(data),packet).action=="RECAPTURE"
