import {Component,lazy,Suspense,useCallback,useEffect,useRef,useState} from 'react';
import type {ReactNode} from 'react';
import Lenis from 'lenis';
import 'lenis/dist/lenis.css';
import {gsap,ScrollTrigger,SplitText,useGSAP} from './motion';
import {storyAct,storyActs,storyPose} from './storyState';
import FactoryDiagram from './FactoryDiagram';
import {RequiemWorld,RequiemDivider} from './RequiemDecorations';
const Scene=lazy(()=>import('./FactoryScene'));

class SceneBoundary extends Component<{children:ReactNode;onFailure:()=>void},{failed:boolean}>{state={failed:false};static getDerivedStateFromError(){return {failed:true}}componentDidCatch(){this.props.onFailure()}render(){return this.state.failed?null:this.props.children}}

export default function CinematicStory(){
 const root=useRef<HTMLElement>(null),stage=useRef<HTMLDivElement>(null),pose=useRef(storyPose(0));
 const [act,setAct]=useState(0),[mode,setMode]=useState<'2d'|'3d'>('2d'),[failed,setFailed]=useState(false),[paused,setPaused]=useState(false),[reduced,setReduced]=useState(false),[selected,setSelected]=useState('COVER'),[manual,setManual]=useState(false),[lowQuality,setLowQuality]=useState(false),[exploded,setExploded]=useState(false);
 const fail=useCallback(()=>{setFailed(true);setMode('2d')},[]);
 const slow=useCallback(()=>{setLowQuality(true);setMode('2d')},[]);
 const manualLift=useRef<number|null>(null);
 useEffect(()=>{const query=matchMedia('(prefers-reduced-motion: reduce)');const update=()=>{setReduced(query.matches);if(query.matches)setMode('2d')};update();query.addEventListener('change',update);
  const timer=setTimeout(()=>{if(query.matches||innerWidth<1000||navigator.hardwareConcurrency<4||(navigator as Navigator&{connection?:{saveData:boolean}}).connection?.saveData)return;try{const canvas=document.createElement('canvas');const gl=canvas.getContext('webgl2');if(gl){gl.getExtension('WEBGL_lose_context')?.loseContext();setMode('3d')}}catch{/* The SVG story is already visible. */}},250);
  return()=>{clearTimeout(timer);query.removeEventListener('change',update)}},[]);
 useGSAP(()=>{
  const node=root.current;if(!node)return;const mm=gsap.matchMedia();let disposed=false;
  mm.add({all:'(min-width: 0px)',desktop:'(min-width: 1000px)',fine:'(pointer: fine)',motion:'(prefers-reduced-motion: no-preference)'},context=>{
   const animate=!!context.conditions?.motion&&!paused;
   let lenis:Lenis|undefined;let tick:((time:number)=>void)|undefined;const splits:SplitText[]=[];
   if(context.conditions?.desktop&&context.conditions?.fine&&animate){lenis=new Lenis({autoRaf:false,anchors:true,duration:1.05,prevent:element=>!!element.closest('dialog,form,[data-lenis-prevent]')});lenis.on('scroll',ScrollTrigger.update);tick=time=>lenis?.raf(time*1000);gsap.ticker.add(tick);gsap.ticker.lagSmoothing(0);node.dataset.scrollController='lenis'}else node.dataset.scrollController='native';
   const playhead={value:0};let current=-1;
   const update=()=>{const index=storyAct(playhead.value);pose.current=storyPose(animate?playhead.value:[.1,.3,.66,1][index]);if(manualLift.current!==null)pose.current.lift=manualLift.current;
    node.dataset.progress=playhead.value.toFixed(3);node.style.setProperty('--story-progress',String(playhead.value));
    node.style.setProperty('--isolation',String(pose.current.isolation));if(index!==current){current=index;setAct(index)}window.dispatchEvent(new Event('steplock-story-frame'))};
   const tl=gsap.timeline({scrollTrigger:{id:'requiem-story',trigger:node,start:'top top',end:'bottom bottom',scrub:animate ? .65 : true,invalidateOnRefresh:true,onRefresh:update},onUpdate:update});
   tl.to(playhead,{value:1,duration:1,ease:'none'});update();
   if(context.conditions?.desktop)ScrollTrigger.create({trigger:node,start:'top top',end:'bottom bottom',pin:stage.current,pinSpacing:false,anticipatePin:1,invalidateOnRefresh:true});
   if(animate){
    node.querySelectorAll<HTMLElement>('[data-split]').forEach((heading,i)=>{splits.push(SplitText.create(heading,{type:'lines',mask:'lines',autoSplit:true,aria:'auto',onSplit(self){return gsap.from(self.lines,{yPercent:110,xPercent:i%2?-4:4,opacity:.25,duration:1.15,stagger:.11,ease:'requiem',scrollTrigger:{trigger:heading,start:'top 90%',once:true}})}}))});
    gsap.from('.factory-intro .story-deck',{y:24,opacity:0,duration:1,delay:.25,ease:'requiem'});
    gsap.from('.factory-intro .story-kicker',{filter:'blur(5px)',opacity:0,duration:1,clearProps:'filter'});
    gsap.from('.knowledge-opposing p:first-child',{x:-60,opacity:0,scrollTrigger:{trigger:'.knowledge-opposing',start:'top 85%',end:'top 45%',scrub:true}});
    gsap.from('.knowledge-opposing p:last-child',{x:60,opacity:0,scrollTrigger:{trigger:'.knowledge-opposing',start:'top 85%',end:'top 45%',scrub:true}});
    const path=node.querySelector<SVGPathElement>('.station-path');const dot=node.querySelector('.station-traveler');
    if(path&&dot){const length=path.getTotalLength();gsap.fromTo(path,{strokeDasharray:length,strokeDashoffset:length},{strokeDashoffset:0,ease:'none',scrollTrigger:{trigger:'#late-feedback',start:'top 70%',end:'bottom 60%',scrub:true}});gsap.to(dot,{motionPath:{path,align:path,alignOrigin:[.5,.5]},ease:'none',scrollTrigger:{trigger:'#late-feedback',start:'top 70%',end:'bottom 60%',scrub:true}})}
   }
   return()=>{splits.forEach(split=>split.revert());if(tick)gsap.ticker.remove(tick);lenis?.off('scroll',ScrollTrigger.update);lenis?.destroy()};
  });
  document.fonts.ready.then(()=>{if(!disposed)ScrollTrigger.refresh()});
  return()=>{disposed=true;mm.revert()};
 },{scope:root,dependencies:[paused,reduced],revertOnUpdate:true});
 function separate(){const next=!exploded;setExploded(next);manualLift.current=next?1:0;pose.current.lift=manualLift.current;window.dispatchEvent(new Event('steplock-story-frame'))}
 return <section ref={root} className="cinematic-story" aria-label="Why STEPLOCK exists" data-act={act+1}>
  <div className="story-stage" ref={stage}><RequiemWorld/>
   <div className="story-visual"><div className="stage-crosshair" aria-hidden="true"/><div className="stage-orbit" aria-hidden="true"/>
    <div className="factory-model">{mode==='3d'&&!failed?<SceneBoundary onFailure={fail}><Suspense fallback={<FactoryDiagram pose={pose} selected={selected}/>}><Scene pose={pose} selected={selected} onSelect={setSelected} onFailure={fail} manual={manual} lowQuality={lowQuality} onSlow={slow} warning={act===1||act===2}/></Suspense></SceneBoundary>:<FactoryDiagram pose={pose} selected={selected}/>}</div>
    <div className="model-annotation"><span>FIG. 01 — FOUR-PART ASSEMBLY</span><b>{selected}</b><i/>{act===1?'A placement can look right. Its timing can be wrong.':act===2?'The distance between action and feedback.':act===3?'Earlier feedback. Retained evidence.':'One object. A whole procedure.'}</div>
    <div className="stage-controls" data-lenis-prevent><div className="mode-switch" aria-label="Assembly display mode"><button aria-pressed={mode==='3d'} disabled={failed||lowQuality} onClick={()=>setMode('3d')}>3D</button><button aria-pressed={mode==='2d'} onClick={()=>setMode('2d')}>2D</button></div><button onClick={separate}>{exploded?'Assemble':'Explode'} illustration ↗</button><button onClick={()=>setManual(!manual)} disabled={mode==='2d'} aria-pressed={manual}>{manual?'Follow story':'Drag to explore'}</button></div>
    <div className="stage-parts" aria-label="Select illustrated component">{['BASE','SPACER','COVER','FASTENER'].map((part,i)=><button key={part} aria-pressed={selected===part} onClick={()=>setSelected(part)}><span>0{i+1}</span>{part}</button>)}</div><div className="stage-disclosure">{failed?'3D unavailable. ':lowQuality?'Simplified for this device. ':''}ILLUSTRATIVE SCENE · NOT FACTORY FOOTAGE OR DETECTOR OUTPUT</div>
   </div>
   <div className="story-instrument"><span>THE INDUSTRIAL REQUIEM</span><div><b>0{act+1}</b><span>/ 07</span><p>{storyActs[act]}</p></div><a href="/demo">Try the prototype ↗</a><button aria-pressed={paused||reduced} disabled={reduced} onClick={()=>setPaused(!paused)}>{reduced?'Reduced motion':paused?'Resume motion':'Pause motion'}</button></div>
  </div>
  <div className="story-pages">
   <section className="story-act factory-intro" id="factory"><div className="story-copy"><span className="story-kicker">01 / A PROBLEM THAT BROUGHT US HERE</span><h1 data-split>Quality shouldn’t<br/>begin <em>at the end.</em></h1><div className="story-deck"><p>In a friend’s family factory, assembly work brought a problem into focus: feedback can arrive after the work has moved on.</p><p className="quiet-copy">The task is immediate. The consequences aren’t always visible.</p><a className="button-gold" href="#knowledge-gap">Experience the problem <span>↓</span></a><a className="story-text-link" href="/demo">Or try the prototype ↗</a></div><span className="origin-note">Founding inspiration. Not a deployed customer or measured factory pilot.</span></div><div className="hero-bottom"><span>SCROLL TO FOLLOW THE ASSEMBLY</span><span>THE SAME OBJECT. A DIFFERENT MOMENT.</span><i>↓</i></div></section>
   <section className="story-act knowledge-act" id="knowledge-gap"><div className="rq-story-divider"><RequiemDivider kind="vine"/></div><div className="story-copy"><span className="story-kicker">02 / THE KNOWLEDGE GAP</span><h2 data-split>The task.<br/>The procedure.<br/><em>The space between.</em></h2><div className="knowledge-opposing"><p>The operator knows the task.</p><span aria-hidden="true">↕</span><p>The supervisor knows the procedure.</p></div><p>Procedural knowledge doesn’t always reach the workstation at the moment it’s needed. A component can arrive before its prerequisite—and the line continues.</p><span className="scene-label">ILLUSTRATED DEVIATION / COVER BEFORE SPACER</span><p className="quiet-copy">Support the people doing the work. Bring the knowledge closer.</p></div></section>
   <section className="story-act late-act" id="late-feedback"><div className="story-copy"><span className="story-kicker">03 / THE COST OF LATE FEEDBACK</span><h2 data-split>The mistake<br/>happened here.<br/><em>Noticed much later.</em></h2><p>More work can happen between an assembly deviation and the inspection that finds it.</p><ul className="consequence-list"><li>Additional work.</li><li>Reinspection.</li><li>Possible rework.</li><li>Material consumption.</li></ul><p className="quiet-copy">Potential consequences—not measured losses or savings.</p></div><div className="station-track" aria-label="Illustrated process: assembly, next operation, inspection"><svg viewBox="0 0 1000 80" aria-hidden="true"><path className="station-base" d="M20 40H980"/><path className="station-path" d="M20 40H980"/><circle className="station-traveler" cx="0" cy="0" r="6"/></svg><div><span>01 / ASSEMBLY<small>The deviation occurs</small></span><span>02 / NEXT OPERATION<small>Work continues</small></span><span>03 / INSPECTION<small>Feedback arrives</small></span></div></div></section>
   <section className="story-act stillness-act"><div className="story-copy"><span className="story-kicker">THE MOMENT WE WANT TO CHANGE</span><h2 data-split>What if the warning<br/>came <em>earlier?</em></h2><p>Before the next operation.<br/>While there’s still a simple next step.</p></div></section>
   <section className="story-act idea-act" id="product"><div className="story-copy"><span className="story-kicker">04 / INTRODUCING STEPLOCK</span><h2 data-split>Catch the<br/>wrong move<br/><em>before the next step.</em></h2><p>We’re building visual procedure assurance: check supported assembly observations against an expected sequence, and preserve the evidence behind each finding.</p><div className="illustrative-diagnostic"><span>PROPOSED WORKFLOW / ILLUSTRATION</span><b>Cover depends on spacer.</b><p>Bring a supported deviation to the point of action. Keep an inspectable record for the supervisor.</p></div><a className="story-text-link" href="#prototype">Now see what actually works ↓</a></div></section>
  </div>
 </section>
}
