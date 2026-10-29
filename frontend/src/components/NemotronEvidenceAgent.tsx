import {useEffect,useRef,useState} from 'react';
import {ArrowUpRight,BrainCircuit,Loader2} from 'lucide-react';
import {api,human} from '../api/client';
import type {Credentials,EventRecord,Session} from '../api/types';

export interface AgentHealth {configured:boolean;state:string;model:string;last_runtime_probe?:{state:string}|null}
export interface AgentRun {run_id:string;session_id:string;state:string;reason_code?:string;engine_decision:string;recipe_sha256:string;selected_event_id:string;frame_id:string;frame_sha256:string;nvidia_model_id:string;source_population:string;advice:null|{action:string;summary:string;steps:string[];evidence_event_ids:string[];rule_ids:string[]};provider:null|{served_model:string;round_trip_ms:number;completion_id:string;usage?:{total_tokens?:number}};tool_trace:{tool:string;elapsed_ms:number;output_sha256:string}[];limitations:string[]}

export function guidanceIsCurrent(run:AgentRun|null,session:Session|null,connected:boolean){
  return !!(run&&session&&connected&&run.session_id===session.session_id&&run.recipe_sha256===session.recipe_sha256&&run.evidence_revision===session.revision&&run.evidence_latest_frame_id===session.latest_frame?.frame_id&&run.engine_decision===session.decision.status&&run.state==='ADVISED'&&run.advice&&session.state==='finished');
}

export interface AgentRun {evidence_revision:number;evidence_latest_frame_id:string}
export interface AgentRun {verified_evidence?:{finding_kind:string;original_finding_kind:string|null;expected_placements:{step:string;part:string;zone:string;required_tag:number;requires:string[]}[];observed_frame_tags:number[]}}

export function NemotronEvidenceAgent({session,credentials,connected,onEvent}:{session:Session|null;credentials:Credentials|null;connected:boolean;onEvent:(event:EventRecord)=>void}){
  const [health,setHealth]=useState<AgentHealth|null>(null);const [run,setRun]=useState<AgentRun|null>(null);const [busy,setBusy]=useState(false);const [error,setError]=useState('');const [eventId,setEventId]=useState('');
  const request=useRef<AbortController|null>(null);const generation=useRef(0);
  const signature=[session?.session_id,session?.revision,session?.state,session?.latest_frame?.frame_id,session?.decision.status,connected].join(':');
  useEffect(()=>{const c=new AbortController();api<AgentHealth>('/api/agent/health',{signal:c.signal}).then(setHealth).catch(()=>setHealth(null));return()=>c.abort()},[]);
  useEffect(()=>{generation.current++;request.current?.abort();setRun(null);setError('');setBusy(false)},[signature]);
  useEffect(()=>setEventId(''),[session?.session_id]);
  useEffect(()=>()=>request.current?.abort(),[]);
  async function explain(){
    if(!session||!credentials||!connected)return;
    const mine=++generation.current;const c=new AbortController();request.current?.abort();request.current=c;setBusy(true);setRun(null);setError('');
    const event=session.events.find(e=>e.event_id===eventId);const purpose=event?.kind==='CORRECTED'?'summarize_correction':'explain_violation';
    const timeout=setTimeout(()=>c.abort(),30000);
    try{
      const result=await api<AgentRun>(`/api/sessions/${session.session_id}/agent/explain`,{method:'POST',body:JSON.stringify({purpose,...(eventId?{event_id:eventId}:{})}),signal:c.signal},credentials);
      if(mine===generation.current)setRun(result);
    }catch(e){if(mine===generation.current)setError(e instanceof Error&&e.name!=='AbortError'?e.message:'Provider request timed out or was cancelled. Vision verdict unchanged.')}
    finally{clearTimeout(timeout);if(mine===generation.current)setBusy(false)}
  }
  const current=guidanceIsCurrent(run,session,connected);const canRun=!!(health?.configured&&session?.state==='finished'&&session.events.length&&connected&&credentials&&!busy);
  const state=!connected&&session?'UNAVAILABLE':busy?'WORKING':run?.state||((health?.configured)?'AVAILABLE':'UNAVAILABLE');
  const choices=session?.events.filter(e=>['WRONG_COMPONENT','WRONG_ZONE','ORDER_VIOLATION','MISSING_AT_CHECKPOINT','UNKNOWN_COMPONENT','CORRECTED','PASS','QUALITY_HOLD'].includes(e.kind))||[];
  return <section className="panel nemotron-panel" aria-label="NVIDIA Nemotron evidence guidance">
    <div className="panel-heading"><span><BrainCircuit size={16}/> NVIDIA NEMOTRON <span className="tiny-pill">{state}</span></span><span>POWERED BY NEBIUS TOKEN FACTORY</span></div>
    <div className="nemotron-controls"><div><strong>Explain the evidence. Keep the verdict.</strong><p>Optional cloud guidance from structured metadata. Source images stay here; STEPLOCK owns the decision.</p></div><select aria-label="Evidence event for Nemotron" value={eventId} onChange={e=>{setEventId(e.target.value);setRun(null)}} disabled={!session||busy}><option value="">Current finding · automatic</option>{choices.map(e=><option key={e.event_id} value={e.event_id}>{human(e.kind)} · {e.event_id}</option>)}</select><button className="primary" disabled={!canRun} onClick={explain}>{busy?<Loader2 size={15} className="spin"/>:<BrainCircuit size={15}/>} Explain finding</button></div>
    {!health?.configured&&<p className="nemotron-status">Agent unavailable. Enable the backend with a Nebius key; inspection works independently.</p>}
    {session?.state==='running'&&<p className="nemotron-status">Wait for this replay to finish before requesting guidance.</p>}
    {error&&<p className="nemotron-status" role="alert">{error}</p>}
    {run?.verified_evidence&&connected&&session?.state==='finished'&&run.session_id===session.session_id&&run.evidence_revision===session.revision&&run.evidence_latest_frame_id===session.latest_frame?.frame_id&&<div className="nemotron-status"><b>VERIFIED BY STEPLOCK: {human(run.verified_evidence.finding_kind)}</b>{run.verified_evidence.expected_placements.map(p=><span key={p.step}> · {p.step}: {p.part}, required tag {p.required_tag}, {p.zone}</span>)}<span> · Observed frame tags: {run.verified_evidence.observed_frame_tags.join(', ')}</span></div>}
    {run&&!current&&<p className="nemotron-status" role="status">{run.state==='ADVISED'?'STALE — evidence or connection changed. Request fresh guidance.':`${run.state} · ${human(run.reason_code||'No verified guidance available')}`}. Vision verdict unchanged.</p>}
    {current&&run?.advice&&<div className="nemotron-advice"><div><span className="eyebrow">GENERATED GUIDANCE · OPERATOR REVIEW REQUIRED</span><h3>{human(run.advice.action)}</h3><p>{run.advice.summary}</p><ol>{run.advice.steps.map((step,i)=><li key={i}>{step}</li>)}</ol><div className="nemotron-links">{run.advice.evidence_event_ids.map(id=><button key={id} className="text-button" onClick={()=>{const e=session?.events.find(x=>x.event_id===id);if(e)onEvent(e)}}>{id}<ArrowUpRight size={13}/></button>)}<span>Rules {run.advice.rule_ids.join(', ')} · frame {run.frame_sha256.slice(0,12)}</span></div></div><details><summary>View actual model and evidence trace</summary><p>{run.provider?.served_model} · {run.provider?.round_trip_ms} ms · {run.provider?.usage?.total_tokens??'Unknown'} tokens</p><p>Run {run.run_id} · {run.source_population}</p><p>Source links and action policy checked; generated wording is not independently verified.</p><ol>{run.tool_trace.map((tool,i)=><li key={i}>{tool.tool} · {tool.elapsed_ms} ms · {tool.output_sha256.slice(0,10)}</li>)}</ol>{run.limitations.map((text,i)=><p key={i}>{text}</p>)}</details></div>}
  </section>;
}
