"""Bounded real-provider ablation. Truth files are checked, never model inputs."""
import bootstrap
from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import time
import numpy as np
from steplock.config import ROOT
from steplock.agent.schemas import AgentConfig, ExplainRequest
from steplock.agent.orchestrator import AgentService, SYSTEM
from steplock.agent.nebius_client import NebiusClient, ProviderFailure
from steplock.agent.evidence_tools import gather
from steplock.agent.safety_policy import allowed_actions, rule_ids, validate
from steplock.procedure.recipe import Recipe
from steplock.service import Session
from steplock.sources.replay import video_frames, inspect_video


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path,value):path.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')


def prepare(clip,directory):
    video=ROOT/clip['relative_path']
    if sha(video)!=clip['source_sha256'] or sha(ROOT/clip['truth_path'])!=clip['truth_sha256']:
        raise ValueError('Frozen source/truth hash mismatch')
    session=Session(Recipe.load(ROOT/'recipes/tagged_four_part_v1.yaml'),'SYNTHETIC_FIXTURE',False,inspect_video(video),directory)
    for index,ts,image in video_frames(video):
        session.stats['frames_in']+=1;session.process(index,ts,image)
    session.engine.checkpoint();session.store.append_events(session.engine.events);session.state='finished'
    return session


def main():
    config=AgentConfig.from_env()
    if not config.configured:raise SystemExit('Agent not enabled/configured; no fake live evaluation')
    protocol_path=ROOT/'benchmarks/nebius_physical_ai/protocol_v1.json'
    protocol=json.loads(protocol_path.read_text())
    manifest=json.loads((ROOT/'fixtures/synthetic/manifest.json').read_text())
    now=datetime.now(timezone.utc);run_id=now.strftime('%Y%m%d_%H%M%S_%f')
    directory=ROOT/'benchmarks/nebius_physical_ai'/run_id;directory.mkdir()
    internal=ROOT/'runtime/agent_eval'/run_id;internal.mkdir(parents=True)
    dump(directory/'protocol.json',protocol)
    source_hashes={path.relative_to(ROOT).as_posix():sha(path) for path in sorted((ROOT/'backend/steplock/agent').glob('*.py'))}
    source_hashes['scripts/run_agent_eval.py']=sha(Path(__file__).resolve())
    dump(directory/'source_hashes_at_start.json',source_hashes)
    client=NebiusClient(config);service=AgentService(config,client)
    rows=[];metadata=[]
    for case in protocol['cases']:
        clip=next(x for x in manifest['clips'] if x['clip_id']==case['clip_id'] and x['split']=='test')
        session=prepare(clip,internal/case['name']);before=deepcopy(session.snapshot())
        packet,trace,_=gather(session,None,case['purpose'])
        ids=[packet['event']['event_id']]
        if packet['event']['kind']=='CORRECTED':ids.append(packet['event']['resolves_event_id'])
        template={'action':allowed_actions(packet)[0],'summary':'Review the retained tag evidence and the applicable recipe prerequisites.','steps':['Inspect the linked source frame before requesting another checkpoint.'],'evidence_event_ids':ids,'rule_ids':rule_ids(packet)[:1]}
        if packet['event']['kind']=='ORDER_VIOLATION':
            blocked=[s for s in packet['recipe']['steps'] if s['id'] in rule_ids(packet)]
            template['summary']+=' Recheck prerequisite '+', '.join(key for step in blocked for key in step['requires'])+'.'
        validate(json.dumps(template),packet)
        rows.append({'case':case['name'],'clip_id':clip['clip_id'],'arm':'deterministic_template','state':'ADVISED','advice':template,'model_calls':0,'human_quality_score':None})
        # Limited direct arm: same selected event and current state; no full recipe,
        # original/correction chain or frame metadata. This difference is disclosed.
        direct={'event':packet['event'],'snapshot':packet['snapshot'],'allowed_actions':['EXPLAIN','CHECK_TAG','REPOSITION','REMOVE_AND_REPLACE','RECAPTURE','ESCALATE_TO_HUMAN'],'allowed_rule_ids':rule_ids(packet)}
        direct_row={'case':case['name'],'clip_id':clip['clip_id'],'arm':'nemotron_direct','state':'UNAVAILABLE','advice':None,'model_calls':1,'tool_reads_in_model_context':2,'human_quality_score':None}
        try:
            result=client.complete([{'role':'system','content':SYSTEM},{'role':'user','content':json.dumps(direct)}]);raw=result.pop('content');direct_row['provider']=result;direct_row['raw_model_content']=raw
            try:direct_row.update(state='ADVISED',advice=validate(raw,packet).model_dump())
            except ValueError:direct_row.update(state='REJECTED',reason='SCHEMA_OR_POLICY_OR_CITATION')
        except ProviderFailure as error:direct_row.update(state='DEFERRED' if error.deferred else 'UNAVAILABLE',reason=error.code,provider=error.metadata)
        rows.append(direct_row);dump(directory/'partial_results.json',rows)
        request=ExplainRequest(purpose=case['purpose'],event_id=packet['event']['event_id'])
        result=service.explain(session,request)
        rows.append({'case':case['name'],'clip_id':clip['clip_id'],'arm':'nemotron_with_evidence_tools','model_calls':1,'tool_reads_in_model_context':5,'human_quality_score':None,**result})
        after=session.snapshot()
        unchanged=before['decision']==after['decision'] and before['events']==after['events']
        if not unchanged:raise AssertionError('Agent changed authoritative engine state')
        if sha(ROOT/clip['truth_path'])!=clip['truth_sha256']:raise AssertionError('Truth mutated')
        metadata.append({'case':case['name'],'clip_id':clip['clip_id'],'source_sha256':clip['source_sha256'],'truth_sha256':clip['truth_sha256'],'recipe_sha256':session.recipe.sha256,'engine_decision':after['decision']['status'],'selected_event_kind':packet['event']['kind'],'engine_unchanged':unchanged})
        dump(directory/'partial_results.json',rows)
        print('CASE',case['name'],'direct',direct_row['state'],'tools',result['state'],result.get('reason_code',''),'engine',after['decision']['status'],flush=True)
    metrics={}
    for arm in protocol['arms']:
        subset=[r for r in rows if r['arm']==arm];times=[r['provider']['round_trip_ms'] for r in subset if r.get('provider')]
        metrics[arm]={'cases':len(subset),'policy_and_citation_accepted':sum(r['state']=='ADVISED' for r in subset),'rejected':sum(r['state']=='REJECTED' for r in subset),'unavailable_or_deferred':sum(r['state'] in ['UNAVAILABLE','DEFERRED'] for r in subset),'measured_responses':len(times),'round_trip_p50_ms':float(np.percentile(times,50)) if times else None,'round_trip_p95_ms':float(np.percentile(times,95)) if times else None,'human_explanation_correctness':None}
    stable=all(sha(ROOT/path)==digest for path,digest in source_hashes.items())
    report={'run_id':run_id,'created_at':now.isoformat(),'git_commit':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'git_dirty':True,'source_stable_during_run':stable,'source_hashes':source_hashes,'model':config.model,'protocol_sha256':sha(protocol_path),'population':protocol['population'],'actual_model_requests':sum(r['model_calls'] for r in rows),'billed_cost':None,'metrics':metrics,'source_receipts':metadata,'limitations':protocol['caveats'],'results':rows}
    dump(directory/'results.json',report)
    print('RESULTS',directory, json.dumps(metrics),flush=True)


if __name__=='__main__':main()
