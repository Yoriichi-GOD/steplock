import {useEffect,useRef} from 'react';
import '../../styles/requiem-landing.css';

const base='/assets/requiem-ornaments/';
function useVisibleArtwork(){
 const root=useRef<HTMLDivElement>(null);
 useEffect(()=>{const node=root.current;if(!node)return;
  const observer=new IntersectionObserver(([entry])=>{node.dataset.visible=String(entry.isIntersecting)});
  observer.observe(node);return()=>observer.disconnect();
 },[]);return root;
}
const ornaments={
 sparkles:['sparkles/celestial-sparkles-cluster.webp',1468,505],
 arch:['fragments/fragment-grand-arch.webp',683,760],
 column:['fragments/fragment-fluted-column.webp',393,459],
 broken:['fragments/fragment-broken-arch.webp',565,344],
 upperLeft:['corners/corner-upper-left.webp',634,512],
 upperRight:['corners/corner-upper-right.webp',598,500],
 lowerLeft:['corners/corner-lower-left.webp',649,481],
 lowerRight:['corners/corner-lower-right.webp',640,467],
 twin:['fragments/fragment-twin-arches.webp',488,402],
 ornateCorner:['fragments/fragment-ornate-upper-corner.webp',464,404],
 halo:['dividers/divider-halo-star.webp',1509,175],
 vine:['dividers/divider-floral-vine.webp',1511,110],
 moon:['dividers/divider-crescent-moon.webp',1663,135],
 mountain:['dividers/divider-mountain-crest.webp',1572,140],
 diamond:['dividers/divider-celestial-diamond.webp',1507,156],
} as const;

/** Artwork lives outside all assembly and evidence renderers. */
export function Ornament({kind,className=''}:{kind:keyof typeof ornaments;className?:string}){
 const [file,width,height]=ornaments[kind];
 return <img className={`rq-ornament ${className}`} src={base+file} width={width} height={height} alt="" aria-hidden="true" loading="lazy" decoding="async"/>;
}
export function RequiemDivider({kind='halo'}:{kind?:'halo'|'vine'|'moon'|'mountain'|'diamond'}){
 return <div className="rq-divider" aria-hidden="true"><Ornament kind={kind}/></div>;
}
export function RequiemWorld(){
 const root=useVisibleArtwork();
 return <div ref={root} className="rq-hero-world" aria-hidden="true"><img className="rq-celestial" src="/assets/steplock-header/celestial-full.webp" width="2149" height="732" alt="" fetchPriority="high"/><Ornament kind="arch" className="rq-hero-arch"/><Ornament kind="sparkles" className="rq-hero-sparkles"/></div>;
}
export function RequiemPortal(){
 return <div className="rq-portal-art" aria-hidden="true"><img className="rq-portal-sky" src="/assets/requiem/celestial-arches.webp" width="1691" height="930" alt="" loading="lazy"/><img className="rq-window rq-window-left" src="/assets/requiem/right-arch-landscape.webp" width="300" height="533" alt="" loading="lazy"/><img className="rq-window rq-window-right" src="/assets/requiem/right-arch-landscape.webp" width="300" height="533" alt="" loading="lazy"/></div>;
}
export function RequiemChapterOrnaments({chapter}:{chapter:'knowledge'|'mistake'|'reveal'|'future'|'invitation'}){
 return <div className={`rq-chapter-art rq-${chapter}-art`} aria-hidden="true">
  {chapter==='knowledge'&&<Ornament kind="column"/>}
  {chapter==='mistake'&&<Ornament kind="broken"/>}
  {chapter==='reveal'&&<Ornament kind="ornateCorner"/>}
  {chapter==='future'&&<Ornament kind="twin"/>}
  {chapter==='invitation'&&<><Ornament kind="upperLeft" className="rq-invitation-upper"/><Ornament kind="lowerRight" className="rq-invitation-lower"/></>}
 </div>;
}
export function RequiemDemoMasthead(){
 return <div className="rq-demo-art" aria-hidden="true"><img src="/assets/steplock-header/BACKGROUND_HEADER_READY_1691x248.webp" width="1691" height="248" alt=""/><Ornament kind="upperLeft" className="rq-demo-corner"/></div>;
}
