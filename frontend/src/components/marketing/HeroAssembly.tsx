import {Component,lazy,Suspense,useEffect,useMemo,useRef,useState} from 'react';
import type {ReactNode} from 'react';
import {gsap} from 'gsap';
import type {AssemblyPart} from '../assembly/assemblyState';
import type {MotionValue} from '../assembly/AssemblyScene';

import {TechnicalAssembly} from './TechnicalAssembly';
const Scene=lazy(()=>import('../assembly/AssemblyScene'));
const labels=['BASE','SPACER','COVER','FASTENER'];
class SceneBoundary extends Component<{children:ReactNode;onFailure:()=>void},{failed:boolean}>{state={failed:false};static getDerivedStateFromError(){return {failed:true}}componentDidCatch(){this.props.onFailure()}render(){return this.state.failed?null:this.props.children}}


export default function HeroAssembly(){
 const root=useRef<HTMLDivElement>(null);const [selected,setSelected]=useState('COVER');const [separation,setSeparation]=useState(.25);const [mode,setMode]=useState<'3d'|'2d'>('2d');const [ready,setReady]=useState(false);const [failed,setFailed]=useState(false);const [paused,setPaused]=useState(false);const [reduced,setReduced]=useState(false);const userControlled=useRef(false);
 const parts=useMemo<AssemblyPart[]>(()=>labels.map((part,i)=>({step:{id:`S${i+1}`,part,zone:`${part}_SLOT`,requires:i?[`S${i}`]:[],state:'PENDING'},tone:'pending',label:'Illustration',finding:undefined,evidence:undefined})),[]);
 const motion=useMemo<Record<string,MotionValue>>(()=>Object.fromEntries(labels.map(part=>[part,{lift:.25}])),[]);
 useEffect(()=>{const query=matchMedia('(prefers-reduced-motion: reduce)');const update=()=>{setReduced(query.matches);if(query.matches){setPaused(true);setMode('2d')}};update();query.addEventListener('change',update);const supported=()=>{try{const canvas=document.createElement('canvas');const gl=canvas.getContext('webgl2');if(!gl)return false;gl.getExtension('WEBGL_lose_context')?.loseContext();return true}catch{return false}};const timer=setTimeout(()=>{setReady(true);if(!query.matches&&innerWidth>=768&&supported())setMode('3d')},350);return()=>{clearTimeout(timer);query.removeEventListener('change',update)}},[]);
 useEffect(()=>{const animation=gsap.to(Object.values(motion),{lift:separation,duration:reduced?0:.8,ease:'power2.inOut',onUpdate:()=>window.dispatchEvent(new Event('steplock-assembly-frame'))});return()=>{animation.kill()}},[motion,separation,reduced]);
 useEffect(()=>{let tick=0;const scroll=()=>{cancelAnimationFrame(tick);tick=requestAnimationFrame(()=>{if(!userControlled.current&&!reduced)setSeparation(Math.min(1,.25+scrollY/850))})};window.addEventListener('scroll',scroll,{passive:true});return()=>{window.removeEventListener('scroll',scroll);cancelAnimationFrame(tick)}},[reduced]);
 useEffect(()=>{const observer=new IntersectionObserver(entries=>setPaused(p=>entries[0].isIntersecting?p:true));if(root.current)observer.observe(root.current);return()=>observer.disconnect()},[]);
 const schematic=mode==='2d'||failed||!ready;
 return <div className="hero-assembly" ref={root}><div className="assembly-topline"><span>FIG. 01 / PROCEDURE STUDY</span><div className="mode-switch" aria-label="Assembly display mode"><button aria-pressed={mode==='3d'&&!failed} disabled={failed} onClick={()=>{setMode('3d');setReady(true)}}>3D</button><button aria-pressed={schematic} onClick={()=>setMode('2d')}>2D</button></div></div><div className="hero-model">{schematic?<TechnicalAssembly separation={separation} selected={selected} onSelect={setSelected}/>:<SceneBoundary onFailure={()=>setFailed(true)}><Suspense fallback={<TechnicalAssembly separation={separation} selected={selected}/>}><Scene parts={parts} motion={motion} selected={selected} onSelect={setSelected} rotate={!paused&&!reduced} reset={0} onFailure={()=>setFailed(true)}/></Suspense></SceneBoundary>}<span className="model-axis axis-x">X / Y / Z</span><span className="model-coordinate">{String(labels.indexOf(selected)+1).padStart(2,'0')} / {selected}</span></div><div className="model-controls"><button onClick={()=>{userControlled.current=true;setSeparation(separation>.5?0:1)}}>{separation>.5?'Assemble':'Explode'} illustration <span>↗</span></button><button onClick={()=>setPaused(!paused)} disabled={reduced||schematic}>{paused?'Resume motion':'Pause motion'}</button></div><div className="model-parts">{labels.map((part,i)=><button key={part} aria-pressed={selected===part} onClick={()=>setSelected(part)}><span>0{i+1}</span>{part}</button>)}</div><p className="model-disclosure">{failed?'3D unavailable · technical 2D mode. ':''}Interactive illustration. Not reconstructed from inspection footage.</p></div>
}
