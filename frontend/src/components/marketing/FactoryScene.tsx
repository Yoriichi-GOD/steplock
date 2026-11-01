import {useEffect,useLayoutEffect,useMemo,useRef} from 'react';
import type {MutableRefObject} from 'react';
import {Canvas,useFrame,useThree} from '@react-three/fiber';
import {Environment,Lightformer,OrbitControls} from '@react-three/drei';
import {ACESFilmicToneMapping,DirectionalLight,Group,InstancedMesh,Matrix4,Vector3} from 'three';
import {MechanicalPart} from '../assembly/MechanicalPart';
import type {AssemblyPart} from '../assembly/assemblyState';
import type {StoryPose} from './storyState';

const labels=['BASE','SPACER','COVER','FASTENER'];
const zero={lift:0};
interface Props{pose:MutableRefObject<StoryPose>;selected:string;onSelect:(part:string)=>void;onFailure:()=>void;manual:boolean;lowQuality:boolean;onSlow:()=>void;warning:boolean}

function Rollers(){
 const mesh=useRef<InstancedMesh>(null);
 useEffect(()=>{const matrix=new Matrix4();for(let i=0;i<26;i++){matrix.makeRotationZ(Math.PI/2);matrix.setPosition((i-12.5)*.58,-.32,0);mesh.current?.setMatrixAt(i,matrix)}if(mesh.current)mesh.current.instanceMatrix.needsUpdate=true},[]);
 return <instancedMesh ref={mesh} args={[undefined,undefined,26]}><cylinderGeometry args={[.12,.12,3.8,12]}/><meshStandardMaterial color="#515e67" metalness={.8} roughness={.4}/></instancedMesh>
}
function StationGeometry(){return <group>
 <Rollers/>
 {[-2.08,2.08].map(z=><mesh key={z} position={[0,-.4,z]}><boxGeometry args={[16,.32,.13]}/><meshStandardMaterial color="#1c2932" metalness={.82} roughness={.35}/></mesh>)}
 {[-5.5,0,5.5].map((x,i)=><group key={x} position={[x,0,0]}>
  {[-2.6,2.6].map(z=><mesh key={z} position={[0,1.7,z]}><boxGeometry args={[.11,4.6,.11]}/><meshStandardMaterial color="#34424d" metalness={.8} roughness={.35}/></mesh>)}
  <mesh position={[0,4,0]}><boxGeometry args={[.15,.13,5.3]}/><meshStandardMaterial color="#65717b" metalness={.8} roughness={.4}/></mesh>
  <mesh position={[0,3.91,0]}><boxGeometry args={[.08,.03,3.2]}/><meshBasicMaterial color={i===1?'#b59e70':'#718997'}/></mesh>
  <mesh position={[0,-1,0]}><boxGeometry args={[.24,1.3,3.4]}/><meshStandardMaterial color="#1b2730" metalness={.6} roughness={.5}/></mesh>
 </group>)}
 </group>}
function RenderBudget({onSlow}:{onSlow:()=>void}){
 const samples=useRef<number[]>([]);
 // Measure submission work, not time between demand frames (which includes idle
 // time). This is a CPU-side fallback signal, never a claimed GPU benchmark.
 useFrame(({gl,scene,camera})=>{const start=performance.now();gl.render(scene,camera);const elapsed=performance.now()-start;
  gl.domElement.dataset.drawCalls=String(gl.info.render.calls);gl.domElement.dataset.geometries=String(gl.info.memory.geometries);
  if(samples.current.length<90){samples.current.push(elapsed);if(samples.current.length===90){const mean=samples.current.reduce((a,b)=>a+b,0)/90;gl.domElement.dataset.renderCpuMeanMs=mean.toFixed(1);if(mean>65)onSlow()}}
 },1);
 return null;
}
function World(props:Props){
 const {camera,gl,invalidate}=useThree();const group=useRef<Group>(null);const factory=useRef<Group>(null);const covers=useRef<(Group|null)[]>([]);const grid=useRef<Group>(null);const keyLight=useRef<DirectionalLight>(null);
 const parts=useMemo<AssemblyPart[]>(()=>labels.map((part,i)=>({step:{id:`S${i+1}`,part,zone:`${part}_SLOT`,requires:i?[`S${i}`]:[]},tone:props.warning&&part==='COVER'?'uncertain':'pending',label:'Illustration',finding:undefined,evidence:undefined})),[props.warning]);
 const cameraTarget=useMemo(()=>new Vector3(),[]);
 useEffect(()=>{const refresh=()=>invalidate();window.addEventListener('steplock-story-frame',refresh);invalidate();return()=>{window.removeEventListener('steplock-story-frame',refresh);document.body.style.cursor=''}},[gl,invalidate]);
 useFrame(()=>{
  const p=props.pose.current;
  if(group.current){group.current.position.set(p.travel*3.4,0,0);group.current.rotation.y=p.turn}
  covers.current.forEach((node,i)=>{if(node){node.position.y=p.lift*i*.78+(i===1?p.deviation*.8:i===2?-p.deviation*.5:0);node.visible=p.isolation<.6||i===2;if(i===2)node.position.x=p.deviation*.25}});
  if(keyLight.current){keyLight.current.intensity=3.8*p.light;keyLight.current.position.x=3+p.turn*5}
  if(factory.current){factory.current.visible=p.factory>.1;factory.current.position.y=-(1-p.factory)*2.5}
  if(grid.current)grid.current.visible=p.isolation<.6;
  if(!props.manual){camera.position.set(8.5-p.turn*3,6.2+p.lift*.7,10.7-p.travel*1.7);cameraTarget.set(p.travel*2.2,1.1+p.lift*.8,0);camera.lookAt(cameraTarget)}
 });
 return <>
 <fog attach="fog" args={['#080e14',13,32]}/><ambientLight intensity={.4}/><directionalLight ref={keyLight} color="#e6cf9d" position={[3,8,4]} intensity={3.8} castShadow={!props.lowQuality} shadow-mapSize={[512,512]} shadow-camera-left={-8} shadow-camera-right={8} shadow-camera-top={8} shadow-camera-bottom={-8}/><directionalLight color="#83a8c5" intensity={2.3} position={[-5,3,-3]}/>
 <Environment resolution={props.lowQuality?64:128} frames={1}><Lightformer form="rect" intensity={4} position={[0,6,-3]} scale={[7,4,1]} color="#e6d2a7"/><Lightformer form="rect" intensity={3} position={[-5,3,2]} rotation={[0,Math.PI/2,0]} scale={[3,8,1]} color="#afc5d5"/></Environment>
 <group ref={factory}><StationGeometry/></group>
 <group ref={group}>{parts.map((part,i)=><group ref={node=>{covers.current[i]=node}} key={part.step.part}><MechanicalPart part={part} motion={zero} index={0} selected={props.selected===part.step.part} onSelect={props.onSelect} industrial/></group>)}</group>
 <group ref={grid}><gridHelper args={[40,60,'#324655','#152531']} position={[0,-.7,0]}/><mesh rotation={[-Math.PI/2,0,0]} position={[0,-.72,0]} receiveShadow><planeGeometry args={[60,60]}/><shadowMaterial opacity={.22}/></mesh></group>
 {props.manual&&<OrbitControls target={[0,1.4,0]} enablePan={false} enableZoom={false} minPolarAngle={.25} maxPolarAngle={1.5} enableDamping/>}
 <RenderBudget onSlow={props.onSlow}/>
 </>
}
export default function FactoryScene(props:Props){
 const cleanup=useRef<(()=>void)|null>(null);
 // Fiber intentionally loses its context during disposal. That is not a graphics
 // failure: detach our listener before unmounting or changing to the 2D mode.
 useLayoutEffect(()=>()=>cleanup.current?.(),[]);
 return <Canvas className="factory-canvas" aria-label="Interactive mechanical factory illustration, not camera evidence" frameloop="demand" shadows={!props.lowQuality} dpr={props.lowQuality?1:[1,1.25]} camera={{position:[8.5,6.2,10.7],fov:39}} onCreated={({gl})=>{const lost=(event:Event)=>{if(gl.domElement.isConnected){event.preventDefault();props.onFailure()}};gl.domElement.addEventListener('webglcontextlost',lost);cleanup.current=()=>gl.domElement.removeEventListener('webglcontextlost',lost);gl.domElement.dataset.ready='true'}} gl={{alpha:true,antialias:true,toneMapping:ACESFilmicToneMapping}}><World {...props}/></Canvas>
}
