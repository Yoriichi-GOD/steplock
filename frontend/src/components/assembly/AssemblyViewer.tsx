import {Component, lazy, Suspense, useEffect, useMemo, useRef, useState} from 'react';
import type {ErrorInfo, ReactNode} from 'react';
import {Box, Check, ChevronRight, CircleHelp, Expand, Eye, Layers3, Pause, Play, RotateCcw, Rotate3D, TriangleAlert} from 'lucide-react';
import {gsap} from 'gsap';
import type {EventRecord, Session, Step} from '../../api/types';
import {human} from '../../api/client';
import {deriveAssemblyParts, recipeOrder} from './assemblyState';
import type {AssemblyPart} from './assemblyState';
import type {MotionValue} from './AssemblyScene';
import './assembly.css';

const Scene = lazy(() => import('./AssemblyScene'));
const knownParts = ['BASE', 'SPACER', 'COVER', 'FASTENER'];
const roles: Record<string, string> = {BASE: 'Foundation plate', SPACER: 'Separation sleeve', COVER: 'Upper cover plate', FASTENER: 'Hex-head fastener'};

class SceneBoundary extends Component<{children: ReactNode; onError: () => void}, {failed: boolean}> {
  state = {failed: false};
  static getDerivedStateFromError() {return {failed: true};}
  componentDidCatch(_error: Error, _info: ErrorInfo) {this.props.onError();}
  render() {return this.state.failed ? null : this.props.children;}
}

function useReducedMotion() {
  const [reduced, setReduced] = useState(() => window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  useEffect(() => {const query = window.matchMedia('(prefers-reduced-motion: reduce)'); const change = () => setReduced(query.matches); query.addEventListener('change', change); return () => query.removeEventListener('change', change);}, []);
  return reduced;
}

function Diagram({parts, motion, selected}: {parts: AssemblyPart[]; motion: Record<string, MotionValue>; selected: string}) {
  const fills = {pending: '#8c9bab', confirmed: '#8ce2b6', issue: '#ff8190', uncertain: '#ffc870'};
  return <svg className="assembly-diagram" viewBox="0 0 600 390" role="img" aria-label="Static schematic of the recipe parts; select a part using the component buttons">
    <defs><pattern id="assembly-grid" width="30" height="30" patternUnits="userSpaceOnUse"><path d="M 30 0 L 0 0 0 30" fill="none" stroke="#334352" strokeWidth=".5"/></pattern></defs>
    <rect width="600" height="390" fill="url(#assembly-grid)" opacity=".6"/>
    <path d="M300 55V345" stroke="#778d9a" strokeDasharray="4 8"/>
    {parts.map((part, i) => {const y = 290 - i * (18 + (motion[part.step.part]?.lift ?? 0) * 54); return <g key={part.step.id} transform={`translate(300 ${y})`}>
      <path d="M-130 -15L35 -50L130 -15L-35 20Z" fill={fills[part.tone]} fillOpacity=".18" stroke={selected === part.step.part ? '#d7ff63' : fills[part.tone]} strokeWidth="2"/>
      <path d="M-130 -15V0L-35 35L130 0V-15M-35 20V35" fill="none" stroke={fills[part.tone]}/>
      <path d="M140 -10H170" stroke={fills[part.tone]}/><text x="178" y="-7" fill={fills[part.tone]} fontSize="12" fontFamily="monospace">{part.step.id}</text>
    </g>;})}
  </svg>;
}

interface Props {steps: Step[]; session: Session | null; connected: boolean; selectedPart: string; onSelectPart: (part: string) => void; onEvent: (event: EventRecord) => void}

export function AssemblyViewer({steps, session, connected, selectedPart, onSelectPart, onEvent}: Props) {
  const parts = deriveAssemblyParts(steps, session, connected);
  const signature = steps.map(step => step.part).join('|');
  const motion = useMemo<Record<string, MotionValue>>(() => Object.fromEntries(steps.map(step => [step.part, {lift: 0}])), [signature]);
  const reduced = useReducedMotion();
  const [distance, setDistance] = useState(0);
  const [open, setOpen] = useState(true);
  const [fullscreen, setFullscreen] = useState(false);
  const [rotating, setRotating] = useState(false);
  const [reset, setReset] = useState(0);
  const [diagram, setDiagram] = useState(false);
  const [failed, setFailed] = useState(false);
  const [sequenceStep, setSequenceStep] = useState<string | null>(null);
  const timeline = useRef<gsap.core.Animation | null>(null);
  const root = useRef<HTMLElement>(null);
  const supported = parts.length === 4 && knownParts.every(name => parts.some(part => part.step.part === name));
  const schematic = diagram || failed || !supported;
  const selected = parts.find(part => part.step.part === selectedPart) ?? parts.at(-1);
  const order = recipeOrder(steps);
  useEffect(() => {const change = () => setFullscreen(!!document.fullscreenElement); document.addEventListener('fullscreenchange', change); return () => document.removeEventListener('fullscreenchange', change);}, []);
  const findings = parts.filter(part => part.finding);
  const activeFindings = session?.unresolved_event_ids.length ?? 0;
  const current = sequenceStep ? steps.find(step => step.id === sequenceStep) : null;

  function update() {
    const values = Object.values(motion);
    setDistance(values.length ? Math.round(values.reduce((sum, value) => sum + value.lift, 0) / values.length * 100) : 0);
    window.dispatchEvent(new Event('steplock-assembly-frame'));
  }
  function stop() {timeline.current?.kill(); timeline.current = null; setSequenceStep(null);}
  function move(amount: number, instant = false) {
    stop();
    timeline.current = gsap.to(Object.values(motion), {lift: amount, duration: reduced || instant ? 0 : 1.05, ease: 'power3.inOut', onUpdate: update, onComplete: update});
  }
  function sequence() {
    stop(); setRotating(false);
    const animation = gsap.timeline({onUpdate: update, onComplete: () => {setSequenceStep(null); update();}});
    timeline.current = animation;
    animation.to(Object.values(motion), {lift: 1, duration: .65, ease: 'power2.inOut'});
    order.forEach(step => animation.call(() => {setSequenceStep(step.id); onSelectPart(step.part);}).to(motion[step.part], {lift: 0, duration: .65, ease: 'power2.inOut'}).to({}, {duration: .2}));
  }
  useEffect(() => {timeline.current?.kill(); setSequenceStep(null); Object.values(motion).forEach(value => {value.lift = 0;}); setDistance(0); window.dispatchEvent(new Event('steplock-assembly-frame')); return () => {timeline.current?.kill();};}, [motion, session?.session_id]);
  useEffect(() => {if (reduced) {timeline.current?.kill(); setSequenceStep(null); setRotating(false);}}, [reduced]);

  return <section ref={root} className="panel assembly-panel" aria-label="Assembly illustration">
    <div className="assembly-heading"><div><span className="eyebrow"><Box size={13}/> ASSEMBLY EXPLORER <span className="assembly-version">01 / FOUR-PART FIXTURE</span></span><h2>Every part. In its place<span>.</span></h2><p>Explore the mechanism. Follow the procedure.</p></div><div className="assembly-heading-actions"><span className="assembly-illustration-tag"><CircleHelp size={12}/> PROCEDURAL ILLUSTRATION</span><button className="assembly-collapse" aria-expanded={open} onClick={() => {stop(); setRotating(false); setOpen(!open);}}>{open ? 'Hide explorer' : 'Show explorer'}</button><button className="icon-button" aria-label={fullscreen ? 'Exit assembly presentation' : 'Expand assembly explorer'} onClick={() => {if (document.fullscreenElement) document.exitFullscreen().catch(() => {}); else root.current?.requestFullscreen().catch(() => {});}}><Expand size={15}/></button></div></div>
    <div className="assembly-content" hidden={!open}><div className="assembly-body"><div className="assembly-visual">
      <div className="assembly-view-badges"><span><i/>{session?.source_kind === 'SYNTHETIC_FIXTURE' ? 'SYNTHETIC TEST · ' : session ? human(session.source_kind).toUpperCase() + ' · ' : ''}{schematic ? '2D SCHEMATIC' : 'INTERACTIVE 3D'}</span><span>{sequenceStep ? `ILLUSTRATING ${sequenceStep}` : distance === 0 ? 'ASSEMBLED' : distance === 100 ? 'EXPLODED' : 'PARTIALLY EXPLODED'}</span></div>
      <div className="assembly-canvas" data-testid="assembly-canvas">{!open ? null : schematic ? <Diagram parts={parts} motion={motion} selected={selected?.step.part ?? ''}/> : <SceneBoundary onError={() => setFailed(true)}><Suspense fallback={<div className="assembly-loading"><Box size={24}/><span>Preparing the mechanism…</span></div>}><Scene parts={parts} motion={motion} selected={selected?.step.part ?? ''} onSelect={onSelectPart} rotate={rotating && !reduced} reset={reset} onFailure={() => setFailed(true)}/></Suspense></SceneBoundary>}</div>
      <div className="assembly-scene-caption"><span>{schematic ? failed ? '3D unavailable · diagram remains usable' : !supported ? 'Recipe diagram · no matching 3D model' : 'Schematic view' : 'DRAG TO ORBIT · SCROLL TO ZOOM · CLICK TO INSPECT'}</span><div><button aria-label="Reset assembly camera" title="Reset view" disabled={schematic} onClick={() => {setRotating(false); setReset(value => value + 1);}}><RotateCcw size={13}/></button><button aria-label={rotating ? 'Pause assembly rotation' : 'Rotate assembly'} aria-pressed={rotating} disabled={schematic || reduced} onClick={() => setRotating(!rotating)}><Rotate3D size={14}/></button><button onClick={() => {setDiagram(!schematic); setFailed(false);}} disabled={!supported}>{schematic ? 'Use 3D view' : 'Use 2D diagram'}</button></div></div>
      <div className="assembly-motion"><div className="assembly-motion-buttons"><button className={distance > 0 ? '' : 'primary'} onClick={() => move(distance > 0 ? 0 : 1)}><Layers3 size={15}/>{distance > 0 ? 'Reassemble' : 'Explode assembly'}</button><button onClick={sequenceStep ? stop : sequence} disabled={reduced || order.length === 0}>{sequenceStep ? <Pause size={14}/> : <Play size={14}/>} {sequenceStep ? 'Pause sequence' : activeFindings ? 'Show correct order' : 'Play assembly'}</button></div><label className="assembly-distance">SEPARATION <input aria-label="Assembly separation" type="range" min="0" max="100" value={distance} onChange={event => move(Number(event.target.value) / 100, true)}/><output>{distance}%</output></label></div>
    </div><aside className="assembly-inspector"><div className="assembly-inspector-heading"><span className="eyebrow">COMPONENT INSPECTOR</span><span className="mono">{selected?.step.id ?? '—'} / {String(parts.length).padStart(2, '0')}</span></div>
      <div className="assembly-selected"><span className="assembly-part-icon"><Box size={25}/></span><div><span className="eyebrow">{selected ? roles[selected.step.part] ?? 'Recipe component' : 'No recipe'}</span><h3>{selected ? human(selected.step.part) : 'Select a recipe'}</h3></div></div>
      <div className={`assembly-part-status ${selected?.tone ?? 'pending'}`} data-testid="assembly-part-status">{selected?.tone === 'confirmed' ? <Check size={13}/> : selected?.tone === 'issue' || selected?.tone === 'uncertain' ? <TriangleAlert size={13}/> : <Eye size={13}/>} {selected?.label ?? 'awaiting recipe'}</div>
      <dl className="assembly-specs"><div><dt>Procedure step</dt><dd>{selected?.step.id ?? '—'}</dd></div><div><dt>Required zone</dt><dd>{selected ? human(selected.step.zone) : '—'}</dd></div><div><dt>Tag identity</dt><dd>{selected && session?.part_markers[selected.step.part] != null ? `#${session.part_markers[selected.step.part]}` : session ? 'not mapped' : 'awaiting session'}</dd></div><div><dt>Prerequisites</dt><dd>{selected?.step.requires.join(', ') || 'None · start here'}</dd></div></dl>
      <div className={`assembly-guidance ${selected?.finding ? 'has-finding' : ''}`}><span className="eyebrow">{current ? 'RECIPE WALKTHROUGH' : selected?.finding ? 'ENGINE FINDING' : 'PLACEMENT GUIDANCE'}</span><p>{current ? `Illustrating ${current.id}: place ${human(current.part)} after ${current.requires.join(', ') || 'the empty-board check'}.` : selected?.finding?.reason ?? (selected ? `Place ${human(selected.step.part)} in ${human(selected.step.zone)}${selected.step.requires.length ? ` after ${selected.step.requires.join(', ')} is proven` : ' first'}. Keep its tag visible for independent observations.` : 'Load a validated recipe to inspect the required parts.')}</p>{selected?.evidence && <button className="text-button" onClick={() => onEvent(selected.evidence!)}>Inspect source evidence <ChevronRight size={13}/></button>}</div>
      <p className="assembly-animation-note">{reduced ? 'Reduced motion is on. Use separation to inspect a static configuration.' : 'Animation explains the recipe. Only source evidence can confirm a correction.'}</p>
    </aside></div>
    <div className="assembly-components" aria-label="Select illustrated component">{parts.map((part, index) => <button key={part.step.id} className={`assembly-component ${part.tone} ${selected?.step.part === part.step.part ? 'selected' : ''}`} aria-label={`Inspect ${human(part.step.part)}`} aria-pressed={selected?.step.part === part.step.part} data-part={part.step.part} data-status={part.tone} onClick={() => onSelectPart(part.step.part)}><span className="assembly-component-order">{String(index + 1).padStart(2, '0')}</span><span><strong>{human(part.step.part)}</strong><small>{part.label}</small></span><i/></button>)}</div>
    <div className="assembly-footer"><span><i className="confirmed"/> Confirmed placement <i className="issue"/> Open finding <i className="uncertain"/> Needs review</span><span>{activeFindings > findings.length ? `${activeFindings - findings.length} further finding(s) · see decision panel` : 'Illustrated geometry · not reconstructed from camera'}</span></div>
    </div></section>;
}
