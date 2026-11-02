/* STEPLOCK / Industrial Requiem. Native text, shapes, tables and chart. */
const fs=require('node:fs'),path=require('node:path');
const modules=process.env.STEPLOCK_NODE_MODULES||'C:/Users/nrgen/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
const pptxgen=require(path.join(modules,'pptxgenjs'));
const imageSize=require(path.join(modules,'image-size'));
const pptx=new pptxgen();pptx.defineLayout({name:'REQUIEM',width:13.333333,height:7.5});pptx.layout='REQUIEM';
pptx.author='Saishreek Singh';pptx.subject='STEPLOCK investor pitch — a16z Speedrun SR008';pptx.title='STEPLOCK — Catch the wrong move before the next step';pptx.company='STEPLOCK';pptx.lang='en-IN';
pptx.theme={headFontFace:'Georgia',bodyFontFace:'Geist',lang:'en-IN'};
const D=path.resolve(__dirname,'..'),A=path.join(D,'assets');
const C={bg:'05070B',night:'090D14',panel:'101722',blue:'58A6FF',ice:'76C7FF',line:'23384E',text:'F2F0E9',sub:'B7BEC8',muted:'788594',gold:'B69A66',green:'70B49A',amber:'D9A65A'};
const F={head:'Georgia',ital:'Instrument Serif',body:'Geist',medium:'Geist Medium',mono:'IBM Plex Mono',geo:'Space Grotesk Light Medium'};
const S=pptx.ShapeType,notes=[],layout=[];
const REPO='https://github.com/Yoriichi-GOD/steplock',BASE=REPO+'/blob/cdeeb4e1e0c10b37977e6837452a552acccf58d1/';
const LIVE='https://st-a69b6c98718945778059ba5124767253.ecs.ap-southeast-2.on.aws';
const refs={benchmark:BASE+'docs/PHYSICAL_AI_EVAL.md',raw:BASE+'benchmarks/runs/20261029_182255_717473_test/metrics.json',architecture:BASE+'docs/ARCHITECTURE.md',limits:BASE+'docs/TECHNICAL_LIMITATIONS.md',impact:BASE+'docs/IMPACT_PHYSICAL_RESULTS.md',shots:BASE+'docs/README_SCREENSHOT_PROVENANCE.md',aws:BASE+'docs/AWS_DEPLOYMENT_20261102.md',ramp:'https://ramp.msme.gov.in/ramp/about-us/about-ramp',asuse:'https://mospi.gov.in/sites/default/files/publication_reports/ASUSE_2023_24_Full_Report-L.pdf',tulip:'https://tulip.co/quality/inline-quality-inspection/',cognex:'https://www.cognex.cn/zh-cn/resources/white-papers-articles/zh-cn/library/media/literature/pdf/dl_assembly_verification_guide.pdf',siemens:'https://www.siemens.com/en-us/company/artificial-intelligence/industrial-ai/inspekto-ai-inspection/',photo:'https://www.pexels.com/photo/male-master-working-with-metal-tools-in-garage-3822844/',photoLicense:'https://www.pexels.com/license/',speedrun:'https://speedrun.a16z.com/faq',sequoia:'https://sequoiacap.com/article/writing-a-business-plan'};
function tx(sl,text,x,y,w,h,size=20,color=C.text,opt={}){sl.addText(text,{x,y,w,h,fontFace:F.body,fontSize:size,color,margin:0,breakLine:false,vertAnchor:'mid',paraSpaceAfterPt:0,...opt});layout.push({slide:sl._slideNum,text:typeof text==='string'?text:text.map(r=>r.text).join(''),x,y,w,h,fontSize:size});}
function rect(sl,x,y,w,h,fill=C.panel,line=C.line,opt={}){sl.addShape(S.rect,{x,y,w,h,fill:{color:fill},line:{color:line,width:.75},...opt});}
function line(sl,x1,y1,x2,y2,color=C.line,width=1,opt={}){const dx=x2-x1,dy=y2-y1;if(dx*dy<0){const length=Math.hypot(dx,dy);sl.addShape(S.line,{x:(x1+x2)/2-length/2,y:(y1+y2)/2,w:length,h:0,rotate:(Math.atan2(dy,dx)*180/Math.PI+360)%360,line:{color,width,...opt}});return}const flip=x2<x1||y2<y1;const ends=flip?{beginArrowType:opt.endArrowType||'none',endArrowType:opt.beginArrowType||'none'}:{};sl.addShape(S.line,{x:Math.min(x1,x2),y:Math.min(y1,y2),w:Math.abs(dx),h:Math.abs(dy),line:{color,width,...opt,...ends}});}
function arrow(sl,x1,y1,x2,y2,color=C.blue,width=1.4){line(sl,x1,y1,x2,y2,color,width,{beginArrowType:'none',endArrowType:'triangle'});}
function dot(sl,x,y,r=.06,color=C.blue){sl.addShape(S.ellipse,{x:x-r,y:y-r,w:r*2,h:r*2,line:{color,transparency:100},fill:{color}});}
function label(sl,text,x,y,w=7,color=C.blue,size=11){tx(sl,text,x,y,w,.3,size,color,{fontFace:F.mono,charSpacing:1.3});}
function image(sl,name,x,y,w,h,crop=false,opt={}){const file=path.join(A,name);const m=imageSize(fs.readFileSync(file));const scale=Math.min(w/m.width,h/m.height);const dw=m.width*scale,dh=m.height*scale;sl.addImage({path:file,x:x+(w-dw)/2,y:y+(h-dh)/2,w:dw,h:dh,...opt});}
function foot(sl,text,num){line(sl,.65,6.96,12.68,6.96,C.line,.6);tx(sl,text,.65,7.05,11.35,.23,10,C.muted);tx(sl,String(num).padStart(2,'0'),12.1,7.03,.55,.25,11,C.muted,{fontFace:F.mono,align:'right'});}
function slide(section,title,source,opt={}){const sl=pptx.addSlide();sl.background={color:C.bg};const n=pptx._slides.length;if(section.startsWith('STEPLOCK /'))return sl;label(sl,section.toUpperCase(),.65,.36);if(title)tx(sl,title,.65,.98,opt.titleW||12.0,opt.titleH||1.5,opt.titleSize||38,C.text,{fontFace:F.head,breakLine:false});foot(sl,source||'STEPLOCK / Early-stage technical prototype',n);return sl;}
function note(sl,body,sources=[],kind='A'){const n=pptx._slides.length;const full=`Investor takeaway: ${body}\n\nClaim class: ${kind}\n\nSources:\n${sources.join('\n')}\n\nPrepared 2 November 2026. Scope and limitations are part of the claim.`;sl.addNotes(full);notes.push({slide:n,text:full});}
function row(sl,head,body,x,y,w,accent=C.blue){line(sl,x,y,x+w,y,C.line,.8);tx(sl,head,x,y+.16,w,.42,21,accent,{fontFace:F.medium});tx(sl,body,x,y+.75,w,.9,18,C.sub,{valign:'top'});}
function plate(sl,x,y,w=1.45,color=C.blue,num='',kind='plate'){
 const h=.55;rect(sl,x+.07,y+.12,w,h,'172A3B','37556B');rect(sl,x,y,w,h,'253E52',color,{radius:.02});
 [[.13,.11],[w-.23,.11],[.13,.37],[w-.23,.37]].forEach(([dx,dy])=>{sl.addShape(S.ellipse,{x:x+dx,y:y+dy,w:.1,h:.1,fill:{color:C.bg},line:{color:'738A9A',width:.6}})});
 if(kind==='spacer'){sl.addShape(S.ellipse,{x:x+w/2-.16,y:y+.1,w:.32,h:.32,fill:{color:'87919A'},line:{color:C.ice,width:.8}});sl.addShape(S.ellipse,{x:x+w/2-.08,y:y+.18,w:.16,h:.16,fill:{color:C.bg},line:{color:'182F40',width:.6}});}
 if(num)tx(sl,num,x,y+.65,w,.4,20,color,{fontFace:F.mono,align:'center'});
}
function tag(sl,x,y,size=.26){rect(sl,x,y,size,size,'F2F0E9','F2F0E9');rect(sl,x+.03,y+.03,size-.06,size-.06,'05070B','05070B');rect(sl,x+.07,y+.07,.07,.07,'F2F0E9','F2F0E9');}
function frame(sl,x,y,w,h,head,body,color=C.blue){rect(sl,x,y,w,h,C.night,C.line);line(sl,x,y,x,y+h,color,2);tx(sl,head,x+.22,y+.18,w-.44,.5,20,color,{fontFace:F.medium});tx(sl,body,x+.22,y+.85,w-.44,h-1.0,18,C.sub,{valign:'top'});}
function gear(sl,cx,cy,r){for(let i=0;i<12;i++){const a=i*Math.PI/6;sl.addShape(S.rect,{x:cx+Math.cos(a)*r-.13,y:cy+Math.sin(a)*r-.13,w:.26,h:.26,rotate:i*30,fill:{color:'253D52'},line:{color:C.blue,width:.6}})}sl.addShape(S.ellipse,{x:cx-r,y:cy-r,w:r*2,h:r*2,fill:{color:C.bg},line:{color:C.blue,width:1.1}});sl.addShape(S.ellipse,{x:cx-r*.5,y:cy-r*.5,w:r,h:r,fill:{color:C.night},line:{color:C.gold,width:1}});}
function table(sl,rows,x,y,w,colW,font=16,rowH=.47){sl.addTable(rows,{x,y,w,colW,rowH,border:{type:'solid',pt:.7,color:C.line},fill:C.night,color:C.sub,fontFace:F.body,fontSize:font,margin:[.055,.14,.055,.14],autoPage:false,verbose:false});}

// 01 / Reveal
{
const sl=slide('STEPLOCK / a16z Speedrun SR008','', 'Saishreek Singh / Sole founder / Technical prototype');
image(sl,'celestial-arches.png',0,0,13.333,7.5,true);rect(sl,0,0,8.3,7.5,C.bg,C.bg,{fill:{color:C.bg,transparency:23},line:{transparency:100}});
image(sl,'steplock-ornate-logo.png',.5,.32,5.4,2.7);
tx(sl,[{text:'Catch the '},{text:'wrong move',options:{fontFace:F.ital,italic:true,color:C.ice}},{text:'\nbefore the next step'}],.72,3.0,10.3,1.7,45,C.text,{fontFace:F.head,breakLine:false});
tx(sl,'Visual procedure verification for smaller manufacturers',.75,5.12,9,.55,21,C.sub);
label(sl,'SAISHREEK SINGH / SOLE FOUNDER',.75,6.42,9,C.ice,12);
label(sl,'SPEEDRUN SR008 / NOVEMBER 2026',.75,.35,10,C.ice,10);
note(sl,'Move verification closer to the moment assembly work happens. STEPLOCK is an early-stage tagged-procedure prototype, with an initial smaller-manufacturer focus.',[refs.architecture,refs.limits],'A + D');
}
// 02 / Clear analogy
{
const sl=slide('01 / The problem','The mistake happens now.\nWe find it later.','Conceptual assembly analogy / Native editable objects / Not factory observations',{titleSize:40});
label(sl,'REQUIRED ORDER',.7,2.92,2,C.muted);label(sl,'OBSERVED ORDER',.7,4.82,2,C.amber);
const xs=[3.3,6.25,9.2];[1,2,3].forEach((n,i)=>{plate(sl,xs[i],2.9,1.55,C.blue,String(n),n===2?'spacer':'plate');if(i<2)arrow(sl,xs[i]+1.75,3.2,xs[i]+2.68,3.2)});
[1,3,2].forEach((n,i)=>{plate(sl,xs[i],4.8,1.55,i===1?C.amber:C.blue,String(n),n===2?'spacer':'plate');if(i<2)arrow(sl,xs[i]+1.75,5.1,xs[i]+2.68,5.1,i===0?C.amber:C.blue)});
line(sl,6.15,4.55,7.9,4.55,C.amber,1.5);tx(sl,'Cover before spacer',7.8,4.18,4,.4,17,C.amber);
tx(sl,'The same parts can produce the wrong procedure.',.7,6.28,11.8,.43,23,C.text);
note(sl,'Sequence is the problem before AI is the solution. A cover installed before a required spacer can conceal the missing prerequisite. The numbered shapes are an explanatory analogy, not measured output.',[refs.architecture],'B / conceptual illustration');
}
// 03 / Editable late-discovery example
{
const sl=slide('02 / Late discovery','Every later step can add\nto the cost of fixing it.','Illustrative wrong-zone housing assembly / Potential rework, not measured cost savings',{titleSize:38});
const xs=[.9,3.25,5.6,7.95,10.3],heads=['Place insert','Wrong zone','Close housing','Final inspection','Reopen + rework'];
line(sl,1.1,3.3,11.9,3.3,C.blue,2);heads.forEach((h,i)=>{dot(sl,xs[i]+.5,3.3,.10,i===1?C.amber:C.blue);label(sl,String(i+1).padStart(2,'0'),xs[i],2.7,1.7,i===1?C.amber:C.muted);tx(sl,h,xs[i]-.2,3.7,2.15,.8,19,i===1?C.amber:C.text,{align:'center'});});
rect(sl,.9,5.0,3.4,1.05,'11202F',C.blue);rect(sl,1.08,5.17,1.25,.68,C.bg,'4F6E86');rect(sl,2.65,5.17,1.25,.68,C.bg,'4F6E86');plate(sl,2.85,5.31,.8,C.amber,'');
tx(sl,'Insert belongs here',.9,6.17,3.3,.32,14,C.ice);arrow(sl,1.6,6.10,1.6,5.86);
tx(sl,'The next operation can hide the error.',5.0,5.0,7.4,.5,25,C.text,{fontFace:F.head});
tx(sl,'An earlier placement check could let the operator correct it before closing the assembly.',5.0,5.72,7.4,.75,20,C.sub);
note(sl,'Example A: an insert enters a neighboring zone, then the housing closes. A compatible tagged recipe could raise WRONG_ZONE before closure. The scenario does not claim inspection of fastening, hidden defects or real industrial outcomes.',[refs.architecture,refs.limits],'B concept + D proposed use');
}
// 04 / Wedge context
{
const sl=slide('03 / The initial customer','Quality control should fit\nthe factory using it.','Sources: Ministry of MSME RAMP; photo Andrea Piacquadio / Pexels, illustrative workshop',{titleSize:38});
tx(sl,'Origin: a friend’s family factory. A few supervisors held the procedural know-how.',.72,2.42,11.9,.36,17,C.ice);
image(sl,'workshop-pexels-3822844.jpg',7.75,2.8,4.9,3.64,true);rect(sl,7.75,2.8,4.9,3.64,C.night,C.night,{fill:{color:C.night,transparency:68},line:{transparency:100}});
label(sl,'RESOURCE-RICH INSTALLATION',.72,2.94,6,C.muted,11);
tx(sl,'Dedicated engineering.\nIntegrated inspection hardware.\nApplication-specific setup.',.72,3.4,6.4,1.15,21,C.sub);
label(sl,'OUR STARTING CUSTOMER / HYPOTHESIS',.72,4.88,6,C.blue,11);
tx(sl,'A repeatable assembly bench.\nA few supervisors.\nA need for manageable setup and cost.',.72,5.25,6.4,1.15,22,C.text);
tx(sl,'Illustrative stock workshop; not the founder’s factory.\nLocation unspecified. No affiliation or endorsement.',7.78,6.48,4.9,.37,10,C.muted);
note(sl,'The founder account concentrates expertise among a few supervisors. This is a customer hypothesis, not a census of all small factories. RAMP documents credit, technology and infrastructure constraints. Large and small manufacturers vary; incumbents can also serve smaller operations. The Pexels photograph illustrates a small workshop, not India or the founder relationship.',[refs.ramp,refs.photo,refs.photoLicense],'D + F');
}
// 05 / Solution and manufacturing example B
{
const sl=slide('04 / The idea','What if the process could\nverify its next step?','Supported prototype: tagged visible placements and explicit temporal rules / Illustration, not a deployed station',{titleSize:38});
const x=.85,y=3.2;rect(sl,x,y,5.15,2.65,'0F1B27','42647C');[[.15,.15],[4.7,.15],[.15,2.15],[4.7,2.15]].forEach(([dx,dy])=>tag(sl,x+dx,y+dy));
line(sl,1.6,4.1,5.3,4.1,C.line);label(sl,'A / SPACER',1.6,3.65,1.6,C.ice,12);label(sl,'B / COVER',3.65,3.65,1.6,C.amber,12);
plate(sl,3.75,4.35,1.45,C.amber,'','plate');tag(sl,4.25,4.47,.24);
sl.addShape(S.rect,{x:2.9,y:2.7,w:.9,h:.34,fill:{color:'526878'},line:{color:C.ice,width:1}});sl.addShape(S.ellipse,{x:3.22,y:2.77,w:.17,h:.17,fill:{color:C.bg},line:{color:C.blue,width:1}});line(sl,3.35,3.04,2.2,3.5,C.blue,.8,{dashType:'dash'});line(sl,3.35,3.04,4.9,3.5,C.blue,.8,{dashType:'dash'});
label(sl,'HOLD / B REQUIRES A',6.65,3.25,5.7,C.amber,14);tx(sl,'Cover before spacer',6.65,3.78,5.7,.53,29,C.text,{fontFace:F.head});tx(sl,'The engine checks earlier supported observations before confirming the next placement.',6.65,4.55,5.7,1.25,21,C.sub);
const steps=['Observe','Verify','Alert','Correct','Keep evidence'];steps.forEach((s,i)=>{const dx=.85+i*2.43;tx(sl,s,dx,6.25,i===4?2.2:1.8,.4,19,i===2?C.amber:C.ice,{fontFace:F.geo});if(i<4)arrow(sl,dx+1.9,6.43,dx+2.25,6.43)});
note(sl,'Example B: the cover requires the spacer. Earlier usable clear-zone history and repeated independent support are required to accuse an order violation. Starting midassembly cannot prove order and must remain uncertain. The physical station is illustrative; current successful recognition examples are generated.',[refs.architecture,refs.limits],'A + B');
}
// 06 / Genuine reveal
{
const sl=slide('05 / The product','', 'Actual application capture / Controlled generated test / Source: README_SCREENSHOT_PROVENANCE.md');
tx(sl,'Meet STEPLOCK',.7,.83,7,.72,42,C.text,{fontFace:F.head});
tx(sl,'Visible placements. Procedure checks. Linked evidence.',.72,1.69,11.7,.46,21,C.sub);
image(sl,'inspection-native.png',.72,2.34,9.95,4.48,false);
line(sl,10.85,2.42,10.85,6.64,C.blue,1.1);label(sl,'ACTUAL UI',11.07,2.49,1.7,C.blue,11);tx(sl,'PASS',11.06,3.06,1.8,.62,29,C.green,{fontFace:F.head});tx(sl,'4 visible\nplacements\nconfirmed',11.06,3.98,1.65,1.1,19,C.text);tx(sl,'Generated fixture.\nNot camera footage.',11.06,5.65,1.65,.65,13,C.sub);
image(sl,'procedure-studio-ornate-title.png',8.8,.68,3.7,1.05);
note(sl,'This is the actual preserved normal-session inspection screenshot, copied unchanged. It contains its own synthetic watermark. Its 25 analyzed / 5 dropped frame UI values are session observations, not throughput/accuracy benchmarks. All original source/provenance labels remain in the uncropped capture. Source image is 1920x1080.',[refs.shots,BASE+'screenshots/readme/inspection-native.png'],'B');
}
// 07 / System architecture
{
const sl=slide('06 / Trust and evidence','Not just a warning.\nAn explanation you can inspect.','Source: architecture, procedure engine and NVIDIA/Nebius integration / Optional advice never owns the verdict',{titleSize:37});
const boxes=[['Camera / video','Source pixels + time'],['Observe + calibrate','Markers, anchors, zones'],['Temporal recipe','Support + prerequisites'],['Current advisory','PASS / HOLD / uncertain']];
boxes.forEach(([h,b],i)=>{const x=.7+i*3.13;rect(sl,x,3.0,2.62,1.3,C.night,C.line);tx(sl,h,x+.15,3.08,2.32,.68,18,C.ice,{fontFace:F.medium});tx(sl,b,x+.15,3.92,2.32,.26,13,C.sub);if(i<3)arrow(sl,x+2.65,3.65,x+3.0,3.65)});
arrow(sl,11.45,4.38,11.45,4.83);rect(sl,7.9,4.95,4.72,1.2,C.night,C.blue);tx(sl,'Linked frames + event history',8.13,5.13,4.25,.45,21,C.ice);tx(sl,'Operator reviews the actual evidence',8.13,5.71,4.25,.3,15,C.sub);
line(sl,6.9,4.32,6.9,5.55,C.muted,1,{dashType:'dash'});line(sl,6.9,5.55,6.35,5.55,C.muted,1,{dashType:'dash'});
rect(sl,.72,4.95,5.61,1.2,C.night,C.line);tx(sl,'Optional NVIDIA / Nebius guidance',.95,5.12,5.13,.45,21,C.sub);tx(sl,'Evidence in → advisory text out; disabled in public demo',.95,5.7,5.13,.32,14,C.muted);
label(sl,'OBSERVED FACTS → EXPLICIT RULES → TRACEABLE DECISION',.72,6.49,11.8,C.blue,11);
note(sl,'The real engine requires independent images and source history, checks calibration and prerequisites, then creates findings. Unusable capture cannot sustain PASS. Source/frame and recipe hashes, event history and correction links support review. The optional LLM reads retained evidence, may be refused, and cannot mutate verdicts or events. Local evidence is not tamper-proof against its filesystem owner.',[refs.architecture,refs.limits,BASE+'docs/NVIDIA_NEBIUS_INTEGRATION.md'],'A with B validation');
}
// 08 / Native editable chart
{
const sl=slide('07 / Controlled technical proof','Built. Tested. Measured.','Source: saved 29 Oct 2026 benchmark / 32 generated test clips / 864 frames / Not industrial accuracy',{titleSize:42,titleH:.9});
label(sl,'CORRECT FINAL STATUS / SAME 32 CLIPS',.8,2.35,7,C.muted,11);
sl.addChart(pptx.ChartType.bar,[{name:'Correct final statuses',labels:['Single frame','Stable only','STEPLOCK'],values:[24,28,32]}],{x:.7,y:2.92,w:7.2,h:3.02,barDir:'bar',grouping:'clustered',catAxisLabelFontFace:F.body,catAxisLabelFontSize:17,catAxisLabelColor:C.sub,valAxisLabelFontFace:F.mono,valAxisLabelFontSize:12,valAxisLabelColor:C.muted,valAxisMinVal:0,valAxisMaxVal:32,valAxisMajorUnit:8,chartColors:[C.blue],showLegend:false,showTitle:false,showValue:true,dataLabelColor:C.text,dataLabelPosition:'outEnd',dataLabelFormatCode:'0" / 32"',dataLabelBkgrdColor:C.bg,dataLabelFontSize:15,showCatName:false,showBorder:false,showCatName:false,showMarker:false,showShadow:false,showValue:true,showCatName:false,catAxisLineShow:false,valAxisLineShow:false,showTitle:false,showLegend:false,showCatName:false,showValue:true,showCatName:false,showValAxisTitle:false,showCatAxisTitle:false,showValAxis:true,showCatAxisLabel:true,showValAxisLabel:true,valGridLine:{color:C.line,width:.5},showCatName:false,invertedColors:[C.blue],layout:{x:.24,y:.04,w:.64,h:.79},showBorder:false,showLegend:false,showTitle:false,chartArea:{fill:{color:C.bg},border:{color:C.bg,transparency:100}},plotArea:{fill:{color:C.bg},border:{color:C.bg,transparency:100}}});
tx(sl,'32/32',8.6,2.65,4.0,1.25,62,C.text,{fontFace:F.head});tx(sl,'correct final statuses',8.64,4.0,4,.45,21,C.sub);
line(sl,8.63,4.7,12.42,4.7,C.line,1);tx(sl,'0/24',8.64,4.94,1.9,.62,31,C.green,{fontFace:F.head});tx(sl,'4/4',10.8,4.94,1.7,.62,31,C.ice,{fontFace:F.head});tx(sl,'false PASS',8.64,5.66,1.95,.36,15,C.sub);tx(sl,'corrections',10.8,5.66,1.9,.36,15,C.sub);
label(sl,'CONTROLLED GENERATED FIXTURES. NOT INDUSTRIAL ACCURACY.',.8,6.36,11.8,C.amber,12);
note(sl,'All three arms use the same frozen generated test split, not different physical factories. Single-frame: 24/32 final statuses, 8/24 false PASS. Stable-only: 28/32, 4/24 false PASS. STEPLOCK: 32/32, 0/24 false PASS, 4/4 supported corrections. 864 decoded frames and TP/FP/FN 60/0/0. Shared renderer, recipe and small corpus limit generalization. The reproduction run records a dirty worktree; source manifests/hashes are retained. Do not imply an independent industrial trial.',[refs.benchmark,refs.raw,BASE+'benchmarks/protocol.json'],'B');
}
// 09 / Founder
{
const sl=slide('08 / The founder','Machines first.\nSoftware next. STEPLOCK now.','Founder-reported background; product/build evidence in public repository / Sole founder',{titleSize:38});
tx(sl,'Saishreek\nSingh',.75,2.9,5.35,1.6,49,C.text,{fontFace:F.head});label(sl,'SOLE FOUNDER / MECHATRONICS',.8,4.8,5.2,C.blue,12);
label(sl,'STEPLOCK / HACKATHON RUNNER-UP*',.8,5.3,5.5,C.muted,10);gear(sl,4.75,5.95,.34);gear(sl,3.95,6.03,.23);
row(sl,'Robotics taught precision','Robotics club president; World Robot Olympiad India gold.',6.65,2.8,5.9);
row(sl,'Software turned it into a product','Independent builds: Peekolitix, Warscythe and SATQuery AI.',6.65,4.55,5.9);
tx(sl,'≈20 hours/week while studying. Ready to build full-time.',.8,6.44,11.6,.37,18,C.sub);
note(sl,'Founder-reported: early interest in machinery including the Big Boy locomotive, robotics club presidency, WRO India gold, current Mechatronics study, independent software products, approximately 20 hours/week and willingness to work full-time/relocate if selected. Independent certificates and portrait were not supplied. Repository demonstrates implemented STEPLOCK software, not WRO credentials. Hackathon runner-up is founder-reported; YMCA Cypher and Digiweek are not counted as two distinct wins without corroboration. Dr. Mylswamy Annadurai is not represented as a STEPLOCK advisor. AI coding assistance was used; sole founder does not imply absence of coding tools or any hackathon collaborators.',[REPO,'Founder instruction supplied 2 November 2026'],'A product + founder-reported biography');
}
// 10 / Market wedge and bottom-up scale
{
const sl=slide('09 / The market wedge','Start where the need is visible.','Market context: MoSPI ASUSE 2023–24 and Ministry of MSME RAMP / Revenue arithmetic is hypothetical',{titleSize:40,titleH:1.0});
label(sl,'WHO WE WOULD QUALIFY FIRST',.8,2.5,7,C.blue,11);
const filters=['Repeatable manual assembly','Tags and a fixed camera are practical','A supervisor owns the procedure','Downstream rework can be measured'];filters.forEach((s,i)=>{tx(sl,String(i+1).padStart(2,'0'),.8,3.03+i*.67,.55,.35,13,C.blue,{fontFace:F.mono});tx(sl,s,1.55,2.98+i*.67,6.4,.47,22,C.text)});
line(sl,8.5,2.52,8.5,5.93,C.line,1);label(sl,'A SCALE SCENARIO / NOT TAM',8.85,2.55,3.65,C.muted,10);
tx(sl,'1,000',8.85,3.02,3.7,.9,45,C.text,{fontFace:F.head});tx(sl,'hypothetical eligible factories',8.87,4.0,3.6,.55,17,C.sub);
tx(sl,'× 2 stations × ₹3,000/month',8.87,4.78,3.6,.65,20,C.ice);tx(sl,'= ₹7.2 crore ARR',8.87,5.57,3.6,.56,26,C.text,{fontFace:F.head});
tx(sl,'The eligible account count, willingness to pay and installation economics still need validation.',.8,6.25,11.8,.47,18,C.sub);
note(sl,'ASUSE measures unincorporated non-agricultural establishments; many are not assembly factories. Do not turn its broad population into an addressable market. Initial discovery targets selected assembly benches with feasible tags/calibration and observable rework. Revenue arithmetic assumes 1,000 eligible factories, two paid stations each and INR 3,000/station/month: INR 72,000,000/year = INR 7.2 crore. All three inputs are unvalidated; this is a scale scenario, not TAM, pipeline or forecast. Manufacturing-cluster channels are proposed rather than existing relationships.',[refs.asuse,refs.ramp],'D + F + hypothetical model');
}
// 11 / Customer path
{
const sl=slide('10 / Customer development','Earn one repeatable deployment.\nThen earn the next.','Planned milestones / No customers, paid deployments or contracted pilots claimed',{titleSize:38});
const steps=[['01','Supervised pilots','One suitable tagged workflow.\nFreeze manual ground truth.'],['02','Measure the station','Misses, false alerts, setup time,\noperator acceptance, rework.'],['03','Package installation','Repeatable recipe, camera setup,\ntraining and support.'],['04','Expand distribution','Manufacturing clusters and\nimplementation partners.']];
steps.forEach(([n,h,b],i)=>{const x=.8+i*3.13;line(sl,x,3.15,x+2.7,3.15,C.blue,1);label(sl,n,x,2.64,1,C.ice,15);tx(sl,h,x,3.48,2.7,.9,24,C.text,{fontFace:F.head});tx(sl,b,x,4.65,2.7,1.25,18,C.sub);});
rect(sl,.8,6.02,11.78,.64,C.night,C.line);tx(sl,'Proposed business model: per-station software subscription + paid setup/support',1.0,6.17,11.38,.32,18,C.ice);
note(sl,'The factory relationship is an origin and discovery route, not a signed pilot. Complete supervised consented camera trials before commercial claims. Measure setup time, false alerts and misses, operator acceptance and independently labeled correction outcomes. Test whether per-station recurring fees plus installation/support can cover field service cost. Pricing and channels are hypotheses. No external users or revenue are established in the supplied account.',[refs.limits,'Founder account supplied in this conversation'],'D');
}
// 12 / Vision
{
const sl=slide('11 / The company we could build','From detecting mistakes\nto anticipating them.','Today is marker-assisted / Every later capability is planned or a research direction',{titleSize:39});
const xs=[.8,3.9,7.0,10.1],stages=[['TODAY','Tagged procedure\nverification','Implemented prototype',C.blue],['NEXT','Factory validation +\nmore workflows','Planned',C.ice],['LATER','Broader observation +\nprocess analytics','Research direction',C.sub],['LONG TERM','Predictive process\nintelligence','Long-term ambition',C.sub]];
line(sl,1.0,3.15,12.2,3.15,C.line,2);stages.forEach(([a,b,c,color],i)=>{dot(sl,xs[i]+.15,3.15,.08,color);label(sl,a,xs[i],2.58,2.55,color,11);tx(sl,b,xs[i],3.65,2.6,1.3,25,C.text,{fontFace:F.head});tx(sl,c,xs[i],5.17,2.6,.5,15,color);});
tx(sl,'A trusted record of what happened could become a foundation for learning what fails next.',.8,6.0,11.7,.85,24,C.text,{fontFace:F.head});
note(sl,'Verification is the entry wedge. Broader observation, analytics and predictive intelligence depend on representative consented factory data, evaluation, deployment economics and customer need. No predictive model, markerless universal recognizer, industrial torque measurement or safety certification is implemented. Avoid implying that collecting more video automatically creates a moat or reliable predictor.',[refs.architecture,refs.limits],'A today + D planned + E ambition');
}
// 13 / Explicit financial scenarios
const inputs=[{name:'Conservative',stations:4,errors:2,rate:.35,minutes:15,weeks:48,labor:200,material:50},{name:'Base',stations:4,errors:4,rate:.50,minutes:30,weeks:48,labor:200,material:100},{name:'Optimistic',stations:4,errors:6,rate:.65,minutes:45,weeks:48,labor:200,material:150}];
const scenarios=inputs.map(v=>{const incidents=v.stations*v.errors*v.rate*v.weeks,hours=incidents*v.minutes/60,labor=hours*v.labor,materials=incidents*v.material;return{...v,hours,incidents,labor_savings:labor,material_savings:materials,gross_savings:labor+materials,subscription:72000,setup:20000,net_first_year:labor+materials-92000}});
{
const sl=slide('12 / Illustrative economics','Earlier correction has an\neconomic mechanism to test.','Hypothetical inputs only / Not measured ROI / Currency INR / Full editable model in companion XLSX',{titleSize:37});
const header=[{text:'Input / annual outcome',options:{color:C.ice,bold:true}},...scenarios.map(s=>({text:s.name,options:{color:C.ice,bold:true}}))];
const rows=[header,['Workstations',...scenarios.map(s=>s.stations)],['Errors / station / week',...scenarios.map(s=>s.errors)],['Detected early (assumed)',...scenarios.map(s=>Math.round(s.rate*100)+'%')],['Rework minutes avoided',...scenarios.map(s=>s.minutes)],['Potential hours saved',...scenarios.map(s=>Math.round(s.hours)+' h')],['Gross annual value',...scenarios.map(s=>'₹'+Math.round(s.gross_savings/1000)+'k')],['First-year net after assumed cost',...scenarios.map(s=>(s.net_first_year<0?'−':'')+'₹'+Math.abs(Math.round(s.net_first_year/1000))+'k')]];
table(sl,rows,.8,2.65,11.75,[4.38,2.45,2.45,2.47],14,.40);
tx(sl,'Hours = stations × weekly errors × early detection × minutes avoided × weeks ÷ 60',.8,6.25,11.8,.33,14,C.ice);
tx(sl,'48 weeks; ₹200/hour; material ₹50/100/150 per early incident; subscription ₹72k/year + ₹20k setup.',.8,6.65,11.8,.22,11,C.sub);
note(sl,'Every input is hypothetical and editable. Shared: 48 operating weeks/year; INR 200/labor-hour; subscription INR 1,500/station/month for four stations (INR 72,000/year); setup INR 20,000; first-year cost INR 92,000. Avoided material per early incident: INR 50/100/150. Early incidents are stations*errors*rate*weeks. Hours add avoided rework time only. Gross value = hours*labor rate + incidents*material amount, assuming no double counting or downstream operational losses. Net = gross - subscription - setup. Conservative and base are negative; preserving those results makes pricing/fit risk visible. No empirical detection rate, willingness-to-pay or realized savings is asserted. The INR 3,000 scale scenario on slide 10 is a different explicit price sensitivity, not a single validated price.',[REPO+'/blob/industrial-requiem/pitch-deck/charts/scenarios.json'],'Hypothetical financial scenarios');
}
// 14 / Close
{
const sl=slide('STEPLOCK / Speedrun SR008','', 'Technical prototype / Application materials / No investor endorsement claimed');
image(sl,'celestial-arches.png',0,0,13.333,7.5,true);rect(sl,0,0,9.4,7.5,C.bg,C.bg,{fill:{color:C.bg,transparency:20},line:{transparency:100}});
image(sl,'steplock-ornate-logo.png',.6,.1,4.7,2.35);
tx(sl,[{text:'Quality shouldn’t begin\n'},{text:'at the end.',options:{fontFace:F.ital,italic:true,color:C.ice}}],.8,2.65,10.5,1.8,49,C.text,{fontFace:F.head});
tx(sl,'Move manufacturing verification to the moment work happens.',.82,4.65,10.1,.9,25,C.sub);
tx(sl,'Saishreek Singh · Sole founder',.83,5.78,8,.43,21,C.text);
tx(sl,'Ready to build full-time and relocate to San Francisco if selected.',.83,6.34,11.7,.4,18,C.ice);
tx(sl,'Open the working demo ↗',.84,7.0,5.5,.25,12,C.ice,{hyperlink:{url:LIVE+'/demo'}});tx(sl,'github.com/Yoriichi-GOD/steplock ↗',7.1,7.0,5.4,.25,12,C.ice,{hyperlink:{url:REPO},align:'right'});
note(sl,'The ask is entry to Speedrun to test a manufacturing verification company through supervised pilots, improve deployment repeatability and learn customer economics. Founder-reported commitment: work full-time and relocate to San Francisco if selected. Public AWS demo verified 2 November 2026; generated examples only; trial teardown scheduled 9 November 2026 at 00:53 IST. The GitHub repository is the durable fallback. No acceptance, funding, endorsement or industrial deployment is implied.',[refs.speedrun,refs.aws,REPO],'A product + D plan + founder commitment');
}
// A1 / Method
{
const sl=slide('Appendix A / Benchmark method','What the 32/32 result means','Saved generated benchmark; reports and historical failures preserved',{titleSize:35,titleH:1});
frame(sl,.8,2.55,5.7,2.0,'Same observations. Three rule sets.','32 test clips; 864 frames.\n16 separate development clips.\nAll arms receive the same frame stream.');
table(sl,[[{text:'Arm',options:{color:C.ice}},{text:'Final status',options:{color:C.ice}},{text:'False PASS',options:{color:C.ice}}],['Single frame','24 / 32','8 / 24'],['Stable only','28 / 32','4 / 24'],['STEPLOCK','32 / 32','0 / 24']],6.9,2.55,5.65,[2.25,1.7,1.7],16,.55);
tx(sl,'The corpus shares a renderer and a four-part recipe. These results establish controlled software behavior; they do not estimate factory accuracy.',.8,5.05,11.75,.95,24,C.text,{fontFace:F.head});
tx(sl,'Corrected outcomes: 4/4. Scored events: TP 60, FP 0, FN 0. Physical capture-to-visible latency remains unmeasured.',.8,6.21,11.75,.58,16,C.sub);
note(sl,'The test split uses transform groups 2–5, development groups 0–1. Truth is evaluator-only and never feeds prediction. Shared construction still limits independence. The saved reproduction run is named 20261029_182255_717473_test and records git_dirty=true; source manifest/hashes are retained. Do not relabel it a clean frozen-commit run. Detector timings are offline processing, not camera-to-browser delay.',[refs.raw,refs.benchmark,BASE+'benchmarks/protocol.json'],'B');
}
// A2 / Physical gap
{
const sl=slide('Appendix B / Physical validation','Real input tested.\nIndustrial recognition still open.','Source: IMPACT physical-video compatibility experiment / No dataset frames redistributed',{titleSize:36});
tx(sl,'2,700',.8,2.8,5.5,1.0,59,C.text,{fontFace:F.head});tx(sl,'real source frames processed',.83,3.96,5.6,.5,22,C.sub);
tx(sl,'45/45',7.0,2.8,5.4,1.0,59,C.amber,{fontFace:F.head});tx(sl,'windows: calibration required',7.03,3.96,5.2,.5,22,C.sub);
line(sl,.8,4.86,12.52,4.86,C.line);tx(sl,'What this proves',.8,5.14,5.3,.43,23,C.ice);tx(sl,'What must come next',7.0,5.14,5.3,.43,23,C.ice);
tx(sl,'Real-video ingestion and safe refusal.\nThree executions; correlated windows.',.8,5.7,5.35,1.2,18,C.sub);
tx(sl,'Consented tagged trials, independent labels,\nmiss/false-alert rates and setup economics.',7.0,5.7,5.35,1.0,18,C.sub);
note(sl,'Official IMPACT three-execution sample: 15 real RGB recordings, five views each; 45 start/middle/end windows of 12 seconds, sampled about 5 Hz. Calibration valid in 0/2700 frames; no processing failure in 45 windows; no unsupported PASS. No native marker/placement truth or semantic adapter means industrial mistake precision/recall/F1 and correction are NOT_SCORABLE. Zero unsupported PASS is a safe-refusal result, not zero native false PASS. Dataset media are CC BY-NC-SA 4.0 and are not included in the investor assets. No staged compatible tagged physical recordings have been supplied.',[refs.impact],'C');
}
// A3 / Fair competition
{
const sl=slide('Appendix C / Alternatives','A narrow entry point in an existing market','Vendor statements checked 2 Nov 2026 / Not a price or head-to-head performance comparison',{titleSize:35,titleH:1.0});
const h=['Approach','Published / typical role','Practical deployment consideration'];
const rows=[h,['Manual inspection','Operator/supervisor reviews work','Timing and coverage depend on the workflow'],['Cognex vision','Visual assembly verification','Application imaging, hardware and configuration'],['Tulip','Guided inspections, work instructions, records','Station apps and configured integrations'],['Siemens Inspekto','Ready-to-use AI visual inspection','Dedicated visual-QA system and application fit'],['STEPLOCK prototype','Tagged temporal rules + linked evidence','Fixed board/tags; physical validation pending']];
table(sl,rows,.8,2.4,11.76,[2.42,4.28,5.06],15,.61);
tx(sl,'Our hypothesis: make a limited class of procedure checks easier to start and review.',.8,6.39,11.7,.33,18,C.ice);
note(sl,'Cognex publishes assembly verification; Tulip already combines guided inspection, instructions and traceability; Siemens describes Inspekto as ready-to-use AI visual inspection. These are real alternatives, not evidence that no one serves SMEs. Their actual setup/cost varies by application. No competitor pricing was inferred and no blanket lack-of-capability checkmarks were invented. STEPLOCK has narrower current capability and lower validation maturity. Its ease/cost wedge is a hypothesis to test.',[refs.cognex,refs.tulip,refs.siemens,refs.architecture],'F + A + D');
}
// A4 / Assumptions
{
const sl=slide('Appendix D / Commercial assumptions','A model to challenge, not a forecast','All STEPLOCK pricing and economic inputs are hypothetical / No customer ROI measured',{titleSize:35,titleH:1});
frame(sl,.8,2.52,5.7,3.6,'Market context is not addressability','≈2.36m unincorporated manufacturing establishments with hired workers (ASUSE 2023–24).\n\nNot an addressable-market estimate.\n\nEligible tagged assembly stations remain uncounted.');
frame(sl,6.83,2.52,5.7,3.6,'Financial model inputs','48 weeks/year; ₹200/hour labor value.\nMaterials avoided: ₹50 / ₹100 / ₹150.\n\nROI model: ₹1,500/station/month + ₹20k setup.\nScale sensitivity: ₹3,000/station/month.');
tx(sl,'Validation gates: willingness to pay · installation time · support burden · measured rework avoided',.8,6.38,11.7,.35,17,C.ice);
note(sl,'ASUSE 2023–24 Table 5, BAC Manufacturing / HWE / Combined, PDF page 100 gives 2,363,672 estimated unincorporated manufacturing establishments with hired workers. This is a broad survey population, not a count of eligible STEPLOCK buyers. Own-account manufacturing is separately 17,782,785 (PDF p103); combined approximately 20.15m, far broader than repeatable assembly. HWE state counts include Tamil Nadu 272,663, Maharashtra 246,885 and Gujarat 235,098; they suggest discovery geography, not demand or partnerships. Scale model: 1,000*2*3000*12 = INR 72 million ARR, entirely hypothetical. ROI model uses four stations, INR 1500/station/month and INR 20000 setup. Total first-year cost INR 92000 excludes camera/hardware and workflow-change labor. Model inputs are unvalidated, and potential savings must not be double counted.',[refs.asuse+'#page=100',refs.ramp,'Companion STEPLOCK_Illustrative_Economics.xlsx'],'Hypothetical + F');
}
// A5 / Sources
{
const sl=slide('Appendix E / References','Sources behind the story','Full claim ledger, asset hashes and speaker notes accompany this deck',{titleSize:36,titleH:1});
const sources=[['01 / Product + evidence','Public code, architecture, limitations, source PNG provenance',refs.architecture],['02 / Technical measurements','Saved benchmark metrics + IMPACT compatibility report',refs.benchmark],['03 / Manufacturing context','MoSPI ASUSE 2023–24 + Ministry of MSME RAMP',refs.asuse],['04 / Alternatives','Cognex, Tulip and Siemens Inspekto official materials',refs.tulip],['05 / Visual assets','Founder-supplied REQUIEM; Andrea Piacquadio / Pexels',refs.photo],['06 / Investor structure','Sequoia business-plan guidance; official Speedrun FAQ',refs.sequoia]];
sources.forEach(([h,b,url],i)=>{const y=2.47+i*.65;tx(sl,h,.8,y,3.5,.35,16,C.ice,{fontFace:F.medium});tx(sl,b,4.2,y,8.25,.39,16,C.sub,{hyperlink:{url}});if(i<5)line(sl,.8,y+.49,12.5,y+.49,C.line,.6)});
tx(sl,'Founder biography is attributed to the founder; no independent award certificates or factory deployment evidence were supplied.',.8,6.43,11.7,.35,13,C.muted);
note(sl,'All URLs, inspected dates, exact claims, categories, artwork conversion/source hashes, stock license and founder-report limitations appear in SOURCE_LEDGER.md and assets/manifest.json. External prose is paraphrased; no long copyrighted source passages are reproduced. Original artwork composition/transparency and source-screen provenance are preserved. Standalone font files are not distributed.',Object.values(refs),'A–F source disclosure');
}

fs.writeFileSync(path.join(D,'SPEAKER_NOTES.md'),'# STEPLOCK — speaker notes\n\n'+notes.map(n=>`## Slide ${n.slide}\n\n${n.text}\n`).join('\n'));
fs.writeFileSync(path.join(D,'charts/scenarios.json'),JSON.stringify({status:'HYPOTHETICAL_NOT_MEASURED',scenarios},null,2)+'\n');
fs.writeFileSync(path.join(D,'charts/scenarios.csv'),'scenario,stations,weekly_errors_per_station,early_detection_rate,minutes_avoided,weeks,labor_value_inr_hour,material_value_inr_incident,hours_saved,gross_annual_value_inr,first_year_net_inr\n'+scenarios.map(s=>[s.name,s.stations,s.errors,s.rate,s.minutes,s.weeks,s.labor,s.material,s.hours,s.gross_savings,s.net_first_year].join(',')).join('\n')+'\n');
fs.writeFileSync(path.join(D,'src/layout-ledger.json'),JSON.stringify(layout,null,2)+'\n');
fs.writeFileSync(path.join(D,'src/references.json'),JSON.stringify(refs,null,2)+'\n');
pptx.writeFile({fileName:path.join(D,'STEPLOCK_Speedrun_SR008.pptx'),compression:true}).then(()=>console.log(JSON.stringify({slides:pptx._slides.length,file:'STEPLOCK_Speedrun_SR008.pptx'})));
