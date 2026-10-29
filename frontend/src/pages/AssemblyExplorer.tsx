import {useState} from 'react';
import type {EventRecord,Recipe,Session} from '../api/types';
import {AssemblyViewer} from '../components/assembly/AssemblyViewer';

export function AssemblyExplorer({session,recipe,connected,onEvent}:{session:Session|null;recipe:Recipe|undefined;connected:boolean;onEvent:(event:EventRecord)=>void}){
  const [selectedPart,setSelectedPart]=useState('');
  const steps=session?.step_states||recipe?.steps.map((step,index)=>({...step,state:'NOT_STARTED',allowed:index===0}))||[];
  return <AssemblyViewer steps={steps} session={session} connected={connected} selectedPart={selectedPart} onSelectPart={setSelectedPart} onEvent={onEvent}/>;
}
