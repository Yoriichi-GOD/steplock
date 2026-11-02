import {useEffect,useState} from 'react';
import {api} from '../../api/client';
import {AUTOMATIC_CONTACT,DEMO_LABEL,PUBLIC_CONTACT_EMAIL,RECORDED_PRESENTATION} from '../../publicMode';
import {RequiemChapterOrnaments} from './RequiemDecorations';
import {submitInquiry} from './contactDelivery';

export interface PublicConfig {public_mode:boolean;contact_email:string|null;owner_access_enabled:boolean;owner_authenticated:boolean;demo_population:string;demo_ttl_seconds:number}
export const REPOSITORY='https://github.com/Yoriichi-GOD/steplock';
export function PublicHeader({demo=false}:{demo?:boolean}){return <header className="public-nav"><nav aria-label="Main navigation"><a href="/#factory">Why STEPLOCK</a><a href="/#prototype">Enter the Studio</a><a href="/#how-it-works">The Record</a><a href="/#early-access">Get involved</a></nav><a className="wordmark rq-brand" href="/" aria-label="STEPLOCK home"><img src="/assets/requiem/steplock-ornate-logo.webp" alt="STEPLOCK — visual procedure assurance" width="900" height="450"/></a><a className="button-gold compact" href={demo?'/':'/demo'}>{demo?'Back to the story':DEMO_LABEL}<span>↗</span></a></header>}
export function PublicFooter(){return <footer className="public-footer"><div><a className="wordmark rq-brand" href="/" aria-label="STEPLOCK home"><img src="/assets/requiem/steplock-ornate-logo.webp" width="900" height="450" alt="STEPLOCK" loading="lazy"/></a><p>Visual procedure assurance, in progress.</p></div><nav aria-label="Footer navigation"><a href="/demo">{RECORDED_PRESENTATION?'Watch walkthrough':'Try demo'} ↗</a><a href={REPOSITORY} target="_blank" rel="noreferrer">GitHub ↗</a><a href="/#early-access">Contact / early access</a>{PUBLIC_CONTACT_EMAIL&&<a href={`mailto:${PUBLIC_CONTACT_EMAIL}`}>{PUBLIC_CONTACT_EMAIL} ↗</a>}<a href="/#prototype-notice">Prototype & privacy notice</a></nav><small>An early-stage project. Built for learning, testing, and iteration.</small></footer>}
export function EarlyAccess(){
 const [contact,setContact]=useState<string|null>(PUBLIC_CONTACT_EMAIL||null);const [loaded,setLoaded]=useState(Boolean(PUBLIC_CONTACT_EMAIL));const [purpose,setPurpose]=useState('Request early access');const [name,setName]=useState('');const [email,setEmail]=useState('');const [role,setRole]=useState('');const [message,setMessage]=useState('');
 const [website,setWebsite]=useState('');const [delivery,setDelivery]=useState<'idle'|'sending'|'accepted'|'error'>('idle');
 useEffect(()=>{if(RECORDED_PRESENTATION){setLoaded(true);return}const c=new AbortController();api<PublicConfig>('/api/public/config',{signal:c.signal}).then(r=>setContact(r.contact_email||PUBLIC_CONTACT_EMAIL||null)).catch(()=>{}).finally(()=>setLoaded(true));return()=>c.abort()},[]);
 const body=`Name: ${name}\nEmail: ${email}\nOrganization / role: ${role}\n\nUse case:\n${message}`;
 async function send(){
  if(!contact||delivery==='sending'||delivery==='accepted')return;
  if(!AUTOMATIC_CONTACT){window.location.href=`mailto:${contact}?subject=${encodeURIComponent('STEPLOCK — '+purpose)}&body=${encodeURIComponent(body)}`;return}
  setDelivery('sending');
  try{await submitInquiry(contact,{name,email,organization:role,message,purpose,website});setDelivery('accepted')}
  catch{setDelivery('error')}
 }
 return <section className="early-access chapter" id="early-access"><RequiemChapterOrnaments chapter="invitation"/>
  <div className="rq-invitation-copy"><img className="rq-closing-brand" src="/assets/requiem/steplock-ornate-logo.webp" alt="STEPLOCK" width="900" height="450" loading="lazy"/><span className="kicker">07 / AN OPEN INVITATION</span><h2>We’re building STEPLOCK.<br/><em>Come build with us.</em></h2><p>Work with assembly processes? We’d like to learn what gets missed, what takes too long, and what better evidence would change.</p>{contact&&<p><a className="story-text-link" href={`mailto:${contact}`}>{contact} ↗</a></p>}<div className="contact-options">{['Request early access','Share an idea','Discuss a pilot'].map(text=><button key={text} aria-pressed={purpose===text} onClick={()=>setPurpose(text)} disabled={delivery==='sending'||delivery==='accepted'}>{text} ↗</button>)}</div></div>
  <form onSubmit={e=>{e.preventDefault();void send()}} aria-busy={delivery==='sending'}>
   <fieldset disabled={delivery==='sending'||delivery==='accepted'} className="contact-fields">
    <legend className="sr-only">{purpose}</legend>
    <label>Your name<input name="name" autoComplete="name" required pattern=".*\S.*" value={name} onChange={e=>setName(e.target.value)} maxLength={100}/></label>
    <label>Email<input name="email" autoComplete="email" type="email" required value={email} onChange={e=>setEmail(e.target.value)} maxLength={200}/></label>
    <label>Organization or role<input name="organization" value={role} onChange={e=>setRole(e.target.value)} maxLength={200}/></label>
    <label>What would you use STEPLOCK for?<textarea name="message" required value={message} onChange={e=>setMessage(e.target.value)} rows={3} maxLength={1500}/></label>
    {AUTOMATIC_CONTACT&&<label hidden aria-hidden="true">Leave this empty<input name="_honey" autoComplete="off" tabIndex={-1} value={website} onChange={e=>setWebsite(e.target.value)}/></label>}
    <button className="button-gold" disabled={!contact} type="submit">{delivery==='sending'?'Sending…':delivery==='accepted'?'Request accepted':contact&&!AUTOMATIC_CONTACT?'Open email draft':purpose} ↗</button>
   </fieldset>
   {delivery==='accepted'&&<p className="notice" role="status">Your request was accepted for email delivery. Thank you for getting in touch.</p>}
   {delivery==='error'&&<p className="notice" role="alert">We couldn’t confirm your request. Your entries are still here. Please email <a href={`mailto:${contact}`}>{contact}</a> instead, or retry. A retry may create a duplicate if the first request reached the service.</p>}
   <small>{contact?AUTOMATIC_CONTACT?<>By sending, you share these fields with FormSubmit to email STEPLOCK at {contact}, which forwards to the founder’s inbox. FormSubmit retains submissions for 30 days; STEPLOCK receives an email copy. Please don’t include sensitive information. <a href="https://formsubmit.co/privacy.pdf" target="_blank" rel="noreferrer">Form service privacy</a>.</>:`Opens your email application to ${contact}. Review the populated fields and press Send there. Only sent emails reach us; nothing is stored by this website.`:loaded?'Email contact is not configured yet. You can explore the code on GitHub while the contact channel is being prepared.':'Checking contact availability…'}</small>
  </form></section>
}
