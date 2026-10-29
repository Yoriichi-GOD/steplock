import {useEffect, useMemo, useRef} from 'react';
import {Canvas, useFrame, useThree} from '@react-three/fiber';
import {Environment, Lightformer, OrbitControls} from '@react-three/drei';
import {Color, Group, MeshStandardMaterial, Shape} from 'three';
import type {AssemblyPart, PartTone} from './assemblyState';

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

const colors: Record<PartTone, string> = {pending: '#a9bbcd', confirmed: '#80e5ae', issue: '#ff526c', uncertain: '#e5b46a'};

function plateShape(width: number, depth: number, centerRadius: number) {
  const shape = new Shape();
  const x = width / 2, y = depth / 2, r = .16;
  shape.moveTo(-x + r, -y);
  shape.lineTo(x - r, -y); shape.quadraticCurveTo(x, -y, x, -y + r);
  shape.lineTo(x, y - r); shape.quadraticCurveTo(x, y, x - r, y);
  shape.lineTo(-x + r, y); shape.quadraticCurveTo(-x, y, -x, y - r);
  shape.lineTo(-x, -y + r); shape.quadraticCurveTo(-x, -y, -x + r, -y);
  for (const [hx, hy, hr] of [[0, 0, centerRadius], [-x + .43, -y + .43, .13], [x - .43, -y + .43, .13], [-x + .43, y - .43, .13], [x - .43, y - .43, .13]]) {
    const hole = new Shape(); hole.absarc(hx, hy, hr, 0, Math.PI * 2, true); shape.holes.push(hole);
  }
  return shape;
}

function MechanicalPart({part, index, motion, selected, onSelect}: {part: AssemblyPart; index: number; motion: MotionValue; selected: boolean; onSelect: SceneProps['onSelect']}) {
  const group = useRef<Group>(null);
  const material = useMemo(() => new MeshStandardMaterial({metalness: .76, roughness: .27}), []);
  const shape = useMemo(() => part.step.part === 'BASE' ? plateShape(3.9, 2.65, .23) : part.step.part === 'COVER' ? plateShape(3.3, 2.1, .24) : null, [part.step.part]);
  const spacer = useMemo(() => {const s = new Shape(); s.absarc(0, 0, .49, 0, Math.PI * 2, false); const hole = new Shape(); hole.absarc(0, 0, .23, 0, Math.PI * 2, true); s.holes.push(hole); return s;}, []);
  const color = useMemo(() => new Color(colors[part.tone]), [part.tone]);
  useEffect(() => () => material.dispose(), [material]);
  useEffect(() => {material.color.copy(color); material.emissive.copy(color); material.emissiveIntensity = part.tone === 'issue' ? .25 : selected ? .12 : .025;}, [material, color, selected, part.tone]);
  useFrame(() => {if (group.current) group.current.position.y = motion.lift * index * 1.03;});
  return <group ref={group} onClick={event => {event.stopPropagation(); onSelect(part.step.part);}} onPointerOver={event => {event.stopPropagation(); document.body.style.cursor = 'pointer';}} onPointerOut={() => {document.body.style.cursor = '';}}>
    {shape && <mesh material={material} castShadow receiveShadow position={[0, part.step.part === 'BASE' ? .3 : 1.44, 0]} rotation={[-Math.PI / 2, 0, 0]}><extrudeGeometry args={[shape, {depth: part.step.part === 'BASE' ? .28 : .19, bevelEnabled: true, bevelSegments: 2, steps: 1, bevelSize: .035, bevelThickness: .025, curveSegments: 28}]}/></mesh>}
    {part.step.part === 'SPACER' && <mesh material={material} castShadow position={[0, .64, 0]} rotation={[-Math.PI / 2, 0, 0]}><extrudeGeometry args={[spacer, {depth: .76, bevelEnabled: true, bevelSize: .025, bevelThickness: .025, bevelSegments: 2, curveSegments: 40}]}/></mesh>}
    {part.step.part === 'FASTENER' && <group>
      <mesh material={material} castShadow position={[0, .99, 0]}><cylinderGeometry args={[.175, .175, 1.55, 32]}/></mesh>
      {Array.from({length: 15}, (_, i) => <mesh key={i} material={material} position={[0, .27 + i * .075, 0]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[.176, .025, 6, 24]}/></mesh>)}
      <mesh material={material} castShadow position={[0, 1.72, 0]} rotation={[0, Math.PI / 6, 0]}><cylinderGeometry args={[.35, .35, .26, 6]}/></mesh>
      <mesh material={material} position={[0, 1.56, 0]} rotation={[Math.PI / 2, 0, 0]}><torusGeometry args={[.29, .055, 10, 40]}/></mesh>
      <mesh position={[0, 1.855, 0]}><cylinderGeometry args={[.135, .135, .006, 6]}/><meshStandardMaterial color="#18232c" metalness={.4} roughness={.5}/></mesh>
    </group>}
    {selected && <mesh position={[0, part.step.part === 'BASE' ? .215 : part.step.part === 'SPACER' ? 1.02 : part.step.part === 'COVER' ? 1.38 : 1.9, 0]} rotation={[-Math.PI / 2, 0, 0]}><ringGeometry args={[part.step.part === 'BASE' || part.step.part === 'COVER' ? 1.98 : .62, part.step.part === 'BASE' || part.step.part === 'COVER' ? 2.005 : .64, 80]}/><meshBasicMaterial color="#d7ff63" transparent opacity={.8} depthWrite={false}/></mesh>}
  </group>;
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
