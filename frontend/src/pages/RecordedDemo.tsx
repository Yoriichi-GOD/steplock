import {useRef, useState} from 'react';
import {PublicFooter, PublicHeader, REPOSITORY} from '../components/marketing/PublicChrome';
import '../styles/industrial.css';
import '../styles/recorded-demo.css';

const chapters = [
  {title:'Correct sequence', file:'normal', outcome:'PASS at capture', description:'Independent observations support all four placements, then an explicit checkpoint completes the procedure.'},
  {title:'Wrong component', file:'wrong-component', outcome:'HOLD FOR REVIEW at capture', description:'The wrong tagged fastener is detected. The required fastener is still unproven at the checkpoint.'},
  {title:'Correction', file:'correction', outcome:'PASS after correction at capture', description:'A later observation corrects the wrong-component finding. The original event remains in the history.'},
];

export default function RecordedDemo(){
  const [selected,setSelected]=useState(0);
  const [failed,setFailed]=useState(false);
  const video=useRef<HTMLVideoElement>(null);
  const chapter=chapters[selected];
  return <div className="public-page industrial-page recorded-page"><a className="skip-link" href="#walkthrough">Skip to walkthrough</a><PublicHeader demo/>
    <main id="walkthrough" className="recorded-main">
      <span className="kicker">RECORDED SOFTWARE WALKTHROUGH / 02 NOV 2026</span>
      <h1>See the procedure.<br/><em>Inspect the outcome.</em></h1>
      <p className="recorded-intro">A recording of the actual STEPLOCK prototype inspecting generated marker fixtures. Watch a correct sequence, a mistake, and a correction.</p>
      <p className="recorded-notice"><strong>Recorded playback. No live inspection is running.</strong> These are generated software tests, not physical assembly footage or measured factory accuracy.</p>
      <div className="recorded-tabs" aria-label="Recorded examples">{chapters.map((item,i)=><button key={item.file} aria-pressed={i===selected} onClick={()=>{setSelected(i);setFailed(false)}}><span>0{i+1}</span>{item.title}</button>)}</div>
      <section className="recorded-player" aria-label={chapter.title+' recording'}>
        <div className="document-top"><span>ACTUAL APPLICATION CAPTURE / GENERATED FIXTURE</span><span>RECORDED · ADVISORY ONLY</span></div>
        <video key={chapter.file} ref={video} controls playsInline preload="metadata" poster={`/assets/walkthrough/${chapter.file}.jpg`} aria-label={chapter.title+' recorded inspection'} onError={()=>setFailed(true)}>
          <source src={`/assets/walkthrough/${chapter.file}.webm`} type="video/webm"/>
          <track default kind="captions" src={`/assets/walkthrough/${chapter.file}.vtt`} srcLang="en" label="English explanation"/>
          Your browser cannot play this recording. Use the download below.
        </video>
        {failed&&<p role="alert" className="recorded-notice">Playback is unavailable in this browser. Try downloading the recording, or inspect the source and screenshots on GitHub.</p>}
        <div className="recorded-caption"><div><span className="kicker">{chapter.outcome}</span><p>{chapter.description}</p></div><a className="button-outline" href={`/assets/walkthrough/${chapter.file}.webm`} download>Download recording ↗</a></div>
      </section>
      <section className="recorded-context"><div><span className="kicker">WHAT YOU’RE WATCHING</span><h2>Recorded results.<br/><em>Traceable origin.</em></h2></div><div><p>The recording shows the existing OpenCV marker decoder and temporal procedure engine. It preserves the application’s fixture watermark, source times and advisory wording. Silent clips retain their captured timing; the final frame is held for three seconds for reading.</p><p>PASS is a historical result inside the video, not the status of your workstation. This website doesn’t accept a camera, uploads or new inspections. It makes no external AI calls.</p><a href="/assets/walkthrough/provenance.json" className="story-text-link">Recording provenance & file hashes ↗</a><br/><a href={REPOSITORY} target="_blank" rel="noreferrer" className="story-text-link">Run the full prototype locally ↗</a></div></section>
    </main><PublicFooter/></div>;
}
