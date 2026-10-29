import {readFile} from 'node:fs/promises';
import assert from 'node:assert/strict';
import {test} from 'node:test';
import ts from 'typescript';

// Exercise the production state adapter without a browser or synthetic UI fixtures.
const source = await readFile(new URL('./assemblyState.ts', import.meta.url), 'utf8');
const {outputText} = ts.transpileModule(source, {compilerOptions: {module: ts.ModuleKind.ESNext, target: ts.ScriptTarget.ES2022}});
const {deriveAssemblyParts, recipeOrder} = await import(`data:text/javascript;base64,${Buffer.from(outputText).toString('base64')}`);
const steps = ['BASE', 'SPACER', 'COVER', 'FASTENER'].map((part, i) => ({id: `S${i + 1}`, part, zone: `${part}_SLOT`, requires: i ? [`S${i}`] : [], state: 'CONFIRMED'}));
const event = (kind, part = 'FASTENER', zone = 'FASTENER_SLOT', id = 'finding-1') => ({event_id: id, kind, part_id: part, zone_id: zone, reason: kind});
const session = (overrides = {}) => ({events: [], unresolved_event_ids: [], error: null, quality: {usable: true, flags: [], calibration_id: 'cal-1'}, decision: {status: 'PASS'}, ...overrides});

test('no session claims no confirmations even if recipe carries states', () => {
  assert.deepEqual(deriveAssemblyParts(steps, null, false).map(part => part.tone), ['pending', 'pending', 'pending', 'pending']);
});
test('a connected usable calibrated session can show actual confirmations', () => {
  assert.ok(deriveAssemblyParts(steps, session(), true).every(part => part.tone === 'confirmed'));
});
test('offline, unusable, uncalibrated and error sessions never stay green', () => {
  const cases = [session(), session({quality: {usable: false, flags: ['LOW_FOCUS'], calibration_id: 'c'}}), session({quality: {usable: true, flags: [], calibration_id: null}}), session({error: 'capture failed'}), session({decision: {status: 'SOURCE_LOST'}})];
  cases.forEach((value, index) => assert.ok(deriveAssemblyParts(steps, value, index !== 0).every(part => part.tone !== 'confirmed')));
});
test('unexpected identity maps to its recipe slot without inventing a part identity', () => {
  const bad = event('WRONG_COMPONENT', 'WRONG_FASTENER');
  const parts = deriveAssemblyParts(steps, session({events: [bad], unresolved_event_ids: [bad.event_id]}), true);
  assert.equal(parts[3].tone, 'issue'); assert.equal(parts[3].finding.part_id, 'WRONG_FASTENER');
  assert.ok(parts.slice(0, 3).every(part => part.tone === 'confirmed'));
});
test('known wrong-zone part highlights itself instead of blaming the destination part', () => {
  const bad = event('WRONG_ZONE', 'SPACER', 'BASE_SLOT');
  const parts = deriveAssemblyParts(steps, session({events: [bad], unresolved_event_ids: [bad.event_id]}), true);
  assert.equal(parts[1].tone, 'issue'); assert.equal(parts[0].tone, 'confirmed');
});
test('historical corrected violations cannot leave a mesh red', () => {
  const bad = event('WRONG_COMPONENT', 'WRONG_FASTENER');
  const corrected = {...event('CORRECTED'), resolves_event_id: bad.event_id};
  assert.equal(deriveAssemblyParts(steps, session({events: [bad, corrected]}), true)[3].tone, 'confirmed');
});
test('acknowledgement does not remove an unresolved finding', () => {
  const bad = event('MISSING_AT_CHECKPOINT');
  const value = session({events: [bad], unresolved_event_ids: [bad.event_id], human_reviews: [{event_id: bad.event_id}]});
  assert.equal(deriveAssemblyParts(steps, value, true)[3].tone, 'issue');
});
test('uncertain order suppresses green across the illustration', () => {
  const bad = event('HOLD_UNCERTAIN');
  const parts = deriveAssemblyParts(steps, session({events: [bad], unresolved_event_ids: [bad.event_id]}), true);
  assert.ok(parts.every(part => part.tone === 'uncertain'));
});
test('unmapped findings never color an arbitrary component red', () => {
  const bad = event('UNKNOWN_COMPONENT', 'UNKNOWN', null);
  assert.ok(deriveAssemblyParts(steps, session({events: [bad], unresolved_event_ids: [bad.event_id]}), true).every(part => part.tone === 'uncertain'));
});
test('sequence follows dependency order even when recipe array is rearranged', () => {
  assert.deepEqual(recipeOrder([...steps].reverse()).map(step => step.id), ['S1', 'S2', 'S3', 'S4']);
  assert.deepEqual(recipeOrder([{...steps[0], requires: ['S4']}, ...steps.slice(1)]), []);
});
