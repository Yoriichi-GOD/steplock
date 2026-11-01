import {useEffect,useRef} from 'react';
import type {MutableRefObject} from 'react';
import type {StoryPose} from './storyState';
export default function FactoryDiagram({pose,selected}:{pose:MutableRefObject<StoryPose>;selected:string}){
 const root=useRef<SVGSVGElement>(null);
 useEffect(()=>{const update=()=>{const p=pose.current;const svg=root.current;if(!svg)return;
  svg.querySelector('[data-assembly]')?.setAttribute('transform',`translate(${p.travel*95} 0)`);
  svg.querySelectorAll<SVGGElement>('[data-part]').forEach((part,i)=>{part.setAttribute('transform',`translate(0 ${-i*p.lift*50+(i===1?-p.deviation*45:i===2?p.deviation*28:0)})`);part.style.opacity=String(p.isolation>.5&&part.dataset.part!=='COVER'?.1:1)});
  svg.style.setProperty('--factory-opacity',String(Math.max(.08,p.factory)));};update();window.addEventListener('steplock-story-frame',update);return()=>window.removeEventListener('steplock-story-frame',update)},[pose,selected]);
 return <svg ref={root} className="factory-diagram" viewBox="0 0 800 650" role="img" aria-label="Illustrated mechanical assembly moving between assembly, operation and inspection stations. Not camera evidence.">
 <defs><linearGradient id="rq-steel" x2="1" y2="1"><stop stopColor="#d4c39f"/><stop offset=".35" stopColor="#596472"/><stop offset=".7" stopColor="#1c2833"/><stop offset="1" stopColor="#9ba6af"/></linearGradient><pattern id="rq-blueprint" width="38" height="38" patternUnits="userSpaceOnUse"><path d="M38 0H0V38" fill="none" stroke="#567286" strokeWidth=".5"/></pattern></defs>
 <path d="M10 500L330 315L790 500L450 650Z" fill="url(#rq-blueprint)" opacity=".35"/>
 <g className="diagram-factory"><path d="M80 190V490M80 190H690V490M105 220H665M130 200V245M365 200V245M610 200V245" stroke="#5b6973" fill="none"/><path d="M80 490L380 350L740 490L430 625Z" fill="#101b23" stroke="#6e7e85"/><path d="M80 510L430 645L740 510M80 490V550M740 490V550" fill="none" stroke="#485a68"/><path d="M110 470L430 593M190 433L510 554M265 398L585 515M340 363L665 477" fill="none" stroke="#4a5b67" strokeWidth="6"/></g>
 <g data-assembly="" transform="translate(0 0)">
 {['BASE','SPACER','COVER','FASTENER'].map((part,i)=><g data-part={part} key={part} className={selected===part?'diagram-selected':''}>
 <path d={i===3?'M389 210L410 218V340L389 333Z':i===1?'M356 355Q396 326 437 355V393Q397 425 356 393Z':i===0?'M225 440L400 365L560 434L385 512Z':'M244 335L400 266L543 328L387 399Z'} fill="url(#rq-steel)" stroke={selected===part?'#e7cb95':'#9aa9b2'} strokeWidth="1.5"/>
 {(i===0||i===2)&&<path d={i===0?'M225 440V458L385 533L560 455V434M385 512V533':'M244 335V352L387 418L543 346V328M387 399V418'} fill="#293642" stroke="#79878e"/>}
 {i===3&&<path d="M371 205L397 190L426 205V227L399 242L371 227Z" fill="url(#rq-steel)" stroke="#c0b296"/>}
 <path d={`M565 ${441-i*62}H622`} stroke="#a18c65"/><text x="630" y={445-i*62} fill="#b9aa8a" fontSize="22" fontFamily="IBM Plex Mono,monospace">{part}</text></g>)}
 </g></svg>
}
