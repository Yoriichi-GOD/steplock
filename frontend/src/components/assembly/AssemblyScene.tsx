import {useEffect, useMemo, useRef} from 'react';
import {Canvas, useFrame, useThree} from '@react-three/fiber';
import {Environment, Lightformer, OrbitControls} from '@react-three/drei';
import type {AssemblyPart} from './assemblyState';
import {MechanicalPart} from './MechanicalPart';

export interface MotionValue {lift: number}
export interface SceneProps {
  parts: AssemblyPart[];
  motion: Record<string, MotionValue>;
  selected: string;
  onSelect: (part: string) => void;
  rotate: boolean;
  reset: number;
  onFailure: () => void;
}

function Model(props: SceneProps) {
  const invalidate = useThree(state => state.invalidate);
  const gl = useThree(state => state.gl);
  const controls = useRef<React.ComponentRef<typeof OrbitControls>>(null);
  const lastReset = useRef(props.reset);
  const lastLift = useRef(-1);
  useEffect(() => {if (lastReset.current !== props.reset) {controls.current?.reset(); lastLift.current = -1; lastReset.current = props.reset; invalidate();}}, [props.reset, invalidate]);
  useFrame(() => {
    const lift = Math.max(0, ...Object.values(props.motion).map(value => value.lift));
    if (controls.current && lift !== lastLift.current) {
      controls.current.target.set(0, 1.05 + lift * 1.85, 0);
      controls.current.update();
      lastLift.current = lift;
    }
  });
  // The demand loop sleeps at rest. GSAP invalidates it while parts move.
  useEffect(() => {const refresh = () => invalidate(); window.addEventListener('steplock-assembly-frame', refresh); return () => window.removeEventListener('steplock-assembly-frame', refresh);}, [invalidate]);
  useEffect(() => {const lost = (event: Event) => {event.preventDefault(); props.onFailure();}; gl.domElement.addEventListener('webglcontextlost', lost); return () => gl.domElement.removeEventListener('webglcontextlost', lost);}, [gl, props.onFailure]);
  useEffect(() => () => {document.body.style.cursor = '';}, []);
  return <>
    <ambientLight intensity={.65}/><directionalLight position={[3, 8, 4]} intensity={3.2}/><directionalLight position={[-4, 3, -2]} intensity={2} color="#b6d7ff"/>
    <Environment resolution={128} frames={1}>
      <Lightformer form="rect" intensity={4} position={[0, 5, -5]} scale={[8, 5, 1]} color="#d6e7ff"/>
      <Lightformer form="rect" intensity={3} position={[-5, 2, 2]} rotation={[0, Math.PI / 2, 0]} scale={[4, 8, 1]}/>
      <Lightformer form="rect" intensity={2} position={[5, 3, 0]} rotation={[0, -Math.PI / 2, 0]} scale={[4, 6, 1]} color="#d7ffb0"/>
    </Environment>
    <group position={[0, -.2, 0]}>{props.parts.map(part => <MechanicalPart key={part.step.part} part={part} index={{BASE: 0, SPACER: 1, COVER: 2, FASTENER: 3.75}[part.step.part] ?? 0} motion={props.motion[part.step.part]} selected={props.selected === part.step.part} onSelect={props.onSelect}/>)}</group>
    <gridHelper args={[20, 40, '#344453', '#1d2b36']} position={[0, -.02, 0]}/>
    <OrbitControls ref={controls} makeDefault target={[0, 1.05, 0]} enablePan={false} minDistance={7} maxDistance={19} minPolarAngle={.15} maxPolarAngle={Math.PI / 2.03} autoRotate={props.rotate} autoRotateSpeed={.7} enableDamping dampingFactor={.08}/>
  </>;
}

export default function AssemblyScene(props: SceneProps) {
  return <Canvas aria-label="Interactive illustrated mechanical assembly. Drag to rotate; select components with the buttons below." frameloop="demand" dpr={[1, 1.5]} camera={{position: [7, 6.2, 9], fov: 38}} gl={{antialias: true, alpha: true}}><Model {...props}/></Canvas>;
}
