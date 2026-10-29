"""Four bounded real model calls through the production authenticated API."""
import bootstrap
from copy import deepcopy
from datetime import datetime, timezone
import json
from pathlib import Path
import hashlib
from fastapi.testclient import TestClient
from backend.app import create_app
from steplock.config import ROOT
from steplock.agent.schemas import AgentConfig
from scripts.run_agent_eval import prepare, dump, sha


def main():
    config=AgentConfig.from_env()
    if not config.configured:raise SystemExit('Enable authorized agent environment first; no mock substitute.')
    protocol=json.loads((ROOT/'benchmarks/nebius_physical_ai/protocol_v1.json').read_text())
    manifest=json.loads((ROOT/'fixtures/synthetic/manifest.json').read_text())
    run_id=datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')+'_api_acceptance'
    out=ROOT/'benchmarks/nebius_physical_ai'/run_id;out.mkdir()
    runtime=ROOT/'runtime/agent_api_acceptance'/run_id
    hashes={p.relative_to(ROOT).as_posix():sha(p) for p in sorted((ROOT/'backend/steplock/agent').glob('*.py'))}
    hashes['backend/app.py']=sha(ROOT/'backend/app.py')
    app=create_app(runtime_root=runtime,agent_config=config);rows=[]
    with TestClient(app,base_url='http://127.0.0.1') as client:
        for case in protocol['cases']:
            clip=next(x for x in manifest['clips'] if x['clip_id']==case['clip_id'] and x['split']=='test')
            session=prepare(clip,runtime/case['name']);app.state.manager.sessions[session.id]=session
            before=deepcopy(session.snapshot())
            response=client.post(f'/api/sessions/{session.id}/agent/explain',headers={'Authorization':'Bearer '+session.token},json={'purpose':case['purpose']})
            run=response.json();unchanged=before['events']==session.engine.events and before['decision']==session.snapshot()['decision']
            row={'case':case['name'],'clip_id':clip['clip_id'],'http_status':response.status_code,'engine_unchanged':unchanged,'source_sha256':clip['source_sha256'],'truth_sha256':clip['truth_sha256'],'result':run}
            if session.token in json.dumps(row):raise AssertionError('Session credential leaked')
            if not unchanged:raise AssertionError('Engine changed')
            rows.append(row);dump(out/'results.json',{'population':'SYNTHETIC_EXISTING_TEST_SPLIT_DEVELOPMENT_ACCEPTANCE','actual_model_requests':len(rows),'source_hashes':hashes,'source_stable':all(sha(ROOT/p)==s for p,s in hashes.items()),'human_narrative_accuracy':None,'rows':rows})
            print('API_CASE',case['name'],response.status_code,run.get('state'),run.get('reason_code',''),flush=True)
    print('API_ACCEPTANCE',out,'accepted',sum(r['result'].get('state')=='ADVISED' for r in rows),'/',len(rows),flush=True)


if __name__=='__main__':main()
