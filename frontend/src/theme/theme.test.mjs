import {after, test} from 'node:test';
import assert from 'node:assert/strict';
import {readFile, readdir} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {fileURLToPath} from 'node:url';
import {createServer} from 'vite';
import postcss from 'postcss';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';

const root = new URL('../../', import.meta.url);
const art = new URL('public/assets/requiem/', root);
const css = await readFile(new URL('src/theme/requiem.css', root), 'utf8');
const parsed = postcss.parse(css);
const tokens = Object.fromEntries([...css.matchAll(/--rq-([a-z]+):\s*(#[a-f0-9]{6})/gi)].map(match=>[match[1],match[2]]));
const manifest = JSON.parse(await readFile(new URL('manifest.json', art), 'utf8'));

test('selected production art retains supplied hashes; reference images and fonts are excluded', async () => {
  assert.equal(manifest.files.length, 7);
  for (const item of manifest.files) {
    const bytes = await readFile(new URL(item.path, art));
    assert.equal(createHash('sha256').update(bytes).digest('hex'), item.sha256, item.path);
  }
  const paths = await readdir(art, {recursive: true});
  assert.ok(paths.every(path => !/reference|preview|catalog|\.woff|\.ttf|\.otf|\.zip|master\.md/i.test(path)));
  assert.ok(manifest.files.reduce((sum, item) => sum + item.bytes, 0) < 1024 * 1024);
});

test('production artwork is local optimized WebP with traceable source masters', () => {
  for (const file of manifest.files) {
    assert.match(file.path, /^[a-z-]+\.webp$/);
    assert.match(file.source_sha256, /^[a-f0-9]{64}$/);
    assert.ok(file.size_px[0] <= file.source_size_px[0]);
    assert.ok(file.size_px[1] <= file.source_size_px[1]);
  }
  assert.doesNotMatch(css, /https?:|@import|@font-face/);
});

function luminance(hex) {
  const rgb = hex.replace('#', '').match(/../g).map(value => parseInt(value, 16) / 255).map(value => value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4);
  return rgb[0] * .2126 + rgb[1] * .7152 + rgb[2] * .0722;
}
function contrast(a, b) {const values = [luminance(a), luminance(b)].sort((a, b) => b - a); return (values[0] + .05) / (values[1] + .05);}

test('functional text and semantic status palette meet AA contrast on declared surfaces', () => {
  const pairs = [[tokens.ivory,tokens.bg],[tokens.muted,tokens.panel],[tokens.good,tokens.panel],[tokens.warning,tokens.panel],[tokens.danger,tokens.panel],['#101923',tokens.parchment],['#101923','#efe0bf'],[tokens.blue,tokens.night]];
  for (const [foreground, background] of pairs) assert.ok(contrast(foreground, background) >= 4.5, `${foreground} / ${background}: ${contrast(foreground, background).toFixed(2)}`);

});

test('theme leaves evidence pixels alone and decorative layers cannot intercept controls', () => {
  parsed.walkRules(rule => {
    if (rule.selector.includes('::before') || rule.selector.includes('::after')) {
      const declarations = Object.fromEntries((rule.nodes ?? []).filter(node => node.type === 'decl').map(node => [node.prop, node.value]));
      if (declarations.content === '""') assert.equal(declarations['pointer-events'], 'none', rule.selector);
    }
    if (/\.evidence-image|\.video-stage|\.capture-element|\.matrix-correct|\.matrix-error/.test(rule.selector)) rule.walkDecls(decl=>assert.ok(!/filter|transform|opacity|background/.test(decl.prop), decl.toString()));
    if (/error-banner|notice-banner|connection|decision-status/.test(rule.selector)) {
      rule.walkDecls(decl => assert.ok(!(decl.prop === 'display' && decl.value === 'none') && !(decl.prop === 'visibility' && decl.value === 'hidden') && !(decl.prop === 'opacity' && Number(decl.value) === 0), `${rule.selector}: ${decl.toString()}`));
    }
  });
});

// Render the real components without a browser. This checks HTML semantics,
// not CSS layout, clicking, camera capture or screenshots.
const originalWindow = globalThis.window;
globalThis.window = {matchMedia: () => ({matches: false})};
const server = await createServer({root: fileURLToPath(root), configFile: false, server: {middlewareMode: true, watch: null}, appType: 'custom', logLevel: 'error'});
after(async () => {await server.close(); if (originalWindow === undefined) delete globalThis.window; else globalThis.window = originalWindow;});

test('real app HTML retains truthful offline alert, disabled run action and all five tabs', async () => {
  const {default: App} = await server.ssrLoadModule('/src/App.tsx');
  const html = renderToStaticMarkup(React.createElement(App));
  assert.match(html, /ENGINE OFFLINE/);
  assert.match(html, /role="alert"/);
  assert.match(html, /Local engine unavailable/);
  assert.match(html, /<button class="primary" disabled=""><[^>]+>[\s\S]*?Run example<\/button>/);
  for (const label of ['Procedure studio', 'Evidence explorer', 'Assembly explorer', 'Evaluation lab', 'Recipe designer', 'Demo kit']) assert.ok(html.includes(label), label);
  assert.match(html, /aria-label="STEPLOCK — Procedure studio"/);
  assert.match(html, /steplock-ornate-logo\.webp" alt="STEPLOCK — Visual procedure assurance"/);
});

test('stale PASS input renders SOURCE LOST and review status in the actual Studio', async () => {
  const {Studio} = await server.ssrLoadModule('/src/pages/Studio.tsx');
  const step = {id: 'S1', part: 'BASE', zone: 'BASE_SLOT', requires: [], state: 'CONFIRMED', allowed: true};
  const session = {session_id: 'synthetic-html-test', recipe_version: 1, source_kind: 'SYNTHETIC_FIXTURE', state: 'finished', decision: {status: 'PASS', reason: 'Prior machine outcome', reason_codes: []}, quality: {usable: true, flags: [], calibration_id: 'cal-1'}, part_markers: {BASE: 10}, step_states: [step], events: [], next_allowed_steps: [], unresolved_event_ids: [], runtime: {frames_analyzed: 2, frames_dropped: 0}};
  const noop = () => {};
  const html = renderToStaticMarkup(React.createElement(Studio, {session, connected: false, credentials: null, busy: false, onCheckpoint: noop, onStop: noop, onReview: noop, onEvent: noop, onExport: noop, onRun: noop}));
  assert.match(html, /data-testid="decision-status">SOURCE LOST/);
  assert.match(html, /STALE EVIDENCE/);
  assert.doesNotMatch(html, /data-testid="decision-status">PASS/);
  assert.doesNotMatch(html, /aria-label="Assembly illustration"/);
  assert.match(html, /SYNTHETIC SOFTWARE TEST/);
  assert.match(html, /Human acknowledgement does not override/);
});

test('flower is exclusive to the genuine zero-source Studio state', async () => {
  const {FrameImage} = await server.ssrLoadModule('/src/components/FrameImage.tsx');
  const render = props => renderToStaticMarkup(React.createElement(FrameImage, {credentials:null,frameId:null,...props}));
  assert.match(render({awaitingSource:true}), /Awaiting an inspection source/);
  assert.match(render({awaitingSource:true}), /floating-flower.webp/);
  assert.doesNotMatch(render({}), /floating-flower.webp/);
  assert.doesNotMatch(render({awaitingSource:true,frameId:'prior-frame'}), /floating-flower.webp/);
  assert.match(render({frameId:'new-frame'}), /Loading evidence/);
  assert.doesNotMatch(render({awaitingSource:true,credentials:{session_id:'active'}}), /floating-flower.webp/);
});

test('missing benchmark data never becomes invented metrics', async () => {
  const {Benchmarks} = await server.ssrLoadModule('/src/pages/Benchmarks.tsx');
  const html = renderToStaticMarkup(React.createElement(Benchmarks, {data:null}));
  assert.match(html, /No completed benchmark run is available yet/);
  assert.doesNotMatch(html, /100\.0%|metric-grid/);
});

test('assembly is a separate page and conservatively reflects stale sessions', async () => {
 const {AssemblyExplorer}=await server.ssrLoadModule('/src/pages/AssemblyExplorer.tsx');
 const noop=()=>{};
 const step={id:'S1',part:'BASE',zone:'BASE_SLOT',requires:[],state:'CONFIRMED',allowed:true};
 const session={session_id:'stale',step_states:[step],source_kind:'SYNTHETIC_FIXTURE',decision:{status:'PASS',reason_codes:[]},quality:{usable:true,flags:[],calibration_id:'old'},events:[],unresolved_event_ids:[],part_markers:{BASE:10}};
 const html=renderToStaticMarkup(React.createElement(AssemblyExplorer,{session,connected:false,onEvent:noop}));
 assert.match(html,/aria-label="Assembly illustration"/);
 assert.match(html,/data-status="uncertain"/);
});

test('header uses the exact crop while only navigation remains fixed', async () => {
 const headerArt=new URL('public/assets/steplock-header/',root);
 const record=JSON.parse(await readFile(new URL('manifest.json',headerArt),'utf8'));
 for(const item of record.files){
  assert.equal(createHash('sha256').update(await readFile(new URL(item.path,headerArt))).digest('hex'),item.sha256);
 }
 assert.match(css,/celestial-full\.webp/);
 assert.match(css,/BACKGROUND_HEADER_READY_1691x248\.webp/);
 assert.match(css,/\.rq-header-stage \{[^}]*height:248px/);
 assert.doesNotMatch(css,/02_REFERENCE|REFERENCE_FULL_UI/);
 assert.match(css,/\.app-header \{[^}]*position:absolute/);
 assert.match(css,/\.rq-page-scroll \{[^}]*overflow-y:auto/);
 assert.match(css,/\.workspace \{[^}]*celestial-full\.webp/);
});
