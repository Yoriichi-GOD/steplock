import type {EventRecord, Session, Step} from '../../api/types';

export type PartTone = 'pending' | 'confirmed' | 'issue' | 'uncertain';
export interface AssemblyPart {
  step: Step;
  tone: PartTone;
  label: string;
  finding: EventRecord | undefined;
  evidence: EventRecord | undefined;
}

const violations = new Set(['WRONG_COMPONENT', 'WRONG_ZONE', 'ORDER_VIOLATION', 'MISSING_AT_CHECKPOINT', 'UNKNOWN_COMPONENT']);

// Match an observed part first. Unexpected identities can map to the expected slot,
// but a finding without either identifier must never be assigned to an arbitrary mesh.
export function findingTargets(event: EventRecord, step: Step, steps: Step[]): boolean {
  if (steps.some(candidate => candidate.part === event.part_id)) return event.part_id === step.part;
  return event.zone_id !== null && event.zone_id === step.zone;
}

export function deriveAssemblyParts(steps: Step[], session: Session | null, connected: boolean): AssemblyPart[] {
  const unresolved = new Set(session?.unresolved_event_ids ?? []);
  const findings = session?.events.filter(event => unresolved.has(event.event_id)) ?? [];
  const trusted = !!session && connected && session.quality.usable && session.quality.flags.length === 0
    && !!session.quality.calibration_id && !session.error
    && !['SOURCE_LOST', 'CALIBRATION_REQUIRED'].includes(session.decision.status)
    && !findings.some(event => !steps.some(step => findingTargets(event, step, steps)))
    && !findings.some(event => ['HOLD_UNCERTAIN', 'ORDER_REVALIDATION_REQUIRED'].includes(event.kind));
  return steps.map(step => {
    const finding = findings.find(event => findingTargets(event, step, steps));
    const evidence = finding ?? session?.events.slice().reverse().find(event => event.part_id === step.part && event.kind === 'STEP_CONFIRMED');
    if (finding && violations.has(finding.kind)) return {step, tone: 'issue', label: finding.kind.replaceAll('_', ' ').toLowerCase(), finding, evidence};
    if (session && !connected) return {step, tone: 'uncertain', label: 'source disconnected · stale', finding, evidence};
    if (session && (!trusted || finding)) return {step, tone: 'uncertain', label: finding ? 'order needs review' : 'capture needs review', finding, evidence};
    if (trusted && step.state === 'CONFIRMED') return {step, tone: 'confirmed', label: 'visible placement confirmed', finding, evidence};
    return {step, tone: 'pending', label: session ? 'placement not yet proven' : 'awaiting inspection', finding, evidence};
  });
}

export function recipeOrder(steps: Step[]): Step[] {
  const remaining = [...steps];
  const ordered: Step[] = [];
  while (remaining.length) {
    const index = remaining.findIndex(step => step.requires.every(id => ordered.some(parent => parent.id === id)));
    if (index < 0) return []; // Invalid/cyclic recipes must not get a fabricated sequence.
    ordered.push(...remaining.splice(index, 1));
  }
  return ordered;
}
