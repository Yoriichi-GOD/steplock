import {useEffect,useMemo,useRef} from 'react';
import {useFrame} from '@react-three/fiber';
import {Color,Group,MeshStandardMaterial,Shape} from 'three';
import type {AssemblyPart,PartTone} from './assemblyState';
import type {MotionValue,SceneProps} from './AssemblyScene';

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

export function MechanicalPart({part, index, motion, selected, onSelect,industrial=false}: {part: AssemblyPart; index: number; motion: MotionValue; selected: boolean; onSelect: SceneProps['onSelect'];industrial?:boolean}) {
  const group = useRef<Group>(null);
  const material = useMemo(() => new MeshStandardMaterial({metalness: industrial ? .88 : .76, roughness: industrial ? .31 : .27}), [industrial]);
  const shape = useMemo(() => part.step.part === 'BASE' ? plateShape(3.9, 2.65, .23) : part.step.part === 'COVER' ? plateShape(3.3, 2.1, .24) : null, [part.step.part]);
  const spacer = useMemo(() => {const s = new Shape(); s.absarc(0, 0, .49, 0, Math.PI * 2, false); const hole = new Shape(); hole.absarc(0, 0, .23, 0, Math.PI * 2, true); s.holes.push(hole); return s;}, []);
  const color = useMemo(() => new Color(industrial?(part.tone==='uncertain'?'#bca16d':part.step.part==='FASTENER'?'#b5a07b':'#8a9ba8'):colors[part.tone]), [part.tone,industrial,part.step.part]);
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
    {selected && <mesh position={[0, part.step.part === 'BASE' ? .215 : part.step.part === 'SPACER' ? 1.02 : part.step.part === 'COVER' ? 1.38 : 1.9, 0]} rotation={[-Math.PI / 2, 0, 0]}><ringGeometry args={[part.step.part === 'BASE' || part.step.part === 'COVER' ? 1.98 : .62, part.step.part === 'BASE' || part.step.part === 'COVER' ? 2.005 : .64, 80]}/><meshBasicMaterial color={industrial?'#ddc491':'#d7ff63'} transparent opacity={.8} depthWrite={false}/></mesh>}
  </group>;
}

