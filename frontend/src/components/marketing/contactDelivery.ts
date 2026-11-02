export interface Inquiry {name:string;email:string;organization:string;message:string;purpose:string;website:string}

// A provider acceptance is not proof of inbox delivery. Keep the user's fields
// after ambiguous failures: a timeout can occur after the provider accepts mail.
export async function submitInquiry(contact:string,inquiry:Inquiry,transport:typeof fetch=fetch){
 if(inquiry.website)throw new Error('Please leave the website field empty.');
 if(!inquiry.name.trim()||!inquiry.message.trim()||!inquiry.email.trim())throw new Error('Please complete the required fields.');
 const controller=new AbortController();
 const timer=setTimeout(()=>controller.abort(),20000);
 try{
  const response=await transport(`https://formsubmit.co/ajax/${encodeURIComponent(contact)}`,{
   method:'POST',headers:{'Content-Type':'application/json',Accept:'application/json'},signal:controller.signal,
   body:JSON.stringify({name:inquiry.name.trim(),email:inquiry.email.trim(),organization:inquiry.organization.trim(),message:inquiry.message.trim(),purpose:inquiry.purpose,_subject:`STEPLOCK — ${inquiry.purpose}`,_template:'table',_url:'https://step-lock.xyz/#early-access',_honey:inquiry.website}),
  });
  if(!response.ok)throw new Error('The form service could not accept your request.');
  const result:unknown=await response.json();
  if(!result||typeof result!=='object'||!('success' in result)||(result.success!==true&&result.success!=='true'))throw new Error('The form service did not confirm acceptance.');
 }finally{clearTimeout(timer)}
}
