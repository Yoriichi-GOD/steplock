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
const art = new URL('public/steplock-theme/', root);
const css = await readFile(new URL('src/steplock-ui-overrides.css', root), 'utf8');
const parsed = postcss.parse(css);
const tokens = JSON.parse(await readFile(new URL('theme/tokens.json', art), 'utf8')).palettes;
const manifest = JSON.parse(await readFile(new URL('theme/production-assets.json', art), 'utf8'));

test('selected production art retains supplied hashes; reference images and fonts are excluded', async () => {
  for (const item of manifest.files) {
    const bytes = await readFile(new URL(item.path, art));
    assert.equal(createHash('sha256').update(bytes).digest('hex'), item.sha256, item.path);
  }
  const paths = await readdir(art, {recursive: true});
  assert.ok(paths.every(path => !/reference|preview|catalog|\.woff|\.ttf|\.otf|\.zip|master\.md/i.test(path)));
  assert.ok(manifest.files.reduce((sum, item) => sum + item.bytes, 0) < 1024 * 1024);
});

test('decorative vectors contain no embedded labels, remote assets or scripts', async () => {
  for (const item of manifest.files.filter(file => file.path.endsWith('.svg'))) {
    const svg = await readFile(new URL(item.path, art), 'utf8');
    assert.doesNotMatch(svg, /<(?:script|foreignObject|text)\b|\bon\w+\s*=|(?:href|src)=["'](?!#)/i, item.path);
  }
  const crest = await readFile(new URL('branding/steplock-crest-symmetric.svg', art), 'utf8');
  assert.match(crest, /M256 18 L494 256 L256 494 L18 256Z/);
  assert.match(crest, /translate\(512 0\) scale\(-1 1\)/); // Supplied mirrored crane construction.
});

function luminance(hex) {
  const rgb = hex.replace('#', '').match(/../g).map(value => parseInt(value, 16) / 255).map(value => value <= .04045 ? value / 12.92 : ((value + .055) / 1.055) ** 2.4);
  return rgb[0] * .2126 + rgb[1] * .7152 + rgb[2] * .0722;
}
function contrast(a, b) {const values = [luminance(a), luminance(b)].sort((a, b) => b - a); return (values[0] + .05) / (values[1] + .05);}

test('functional text and semantic status palette meet AA contrast on declared surfaces', () => {
  let hoverBackground;
  parsed.walkRules('button.primary:hover', rule => rule.walkDecls('background', declaration => {hoverBackground = declaration.value;}));
  assert.match(hoverBackground, /^#[a-f0-9]{6}$/i);
  const pairs = [[tokens.text, tokens.ink], [tokens.muted, tokens.panel], [tokens.pass, tokens.panel], [tokens.warning, tokens.panel], [tokens.error, tokens.panel], ['#fff5e8', tokens.vermilion], ['#fff5e8', hoverBackground]];
  for (const [foreground, background] of pairs) assert.ok(contrast(foreground, background) >= 4.5, `${foreground} / ${background}: ${contrast(foreground, background).toFixed(2)}`);
  assert.match(css, /--green:\s*#77c9a6/i);
  assert.match(css, /--amber:\s*#f1ba65/i);
  assert.match(css, /--red:\s*#ed706b/i);
});

test('theme leaves evidence pixels alone and decorative layers cannot intercept controls', () => {
  parsed.walkRules(rule => {
    if (rule.selector.includes('::before') || rule.selector.includes('::after')) {
      const declarations = Object.fromEntries((rule.nodes ?? []).filter(node => node.type === 'decl').map(node => [node.prop, node.value]));
      if (declarations.content === '""') assert.equal(declarations['pointer-events'], 'none', rule.selector);
    }
    assert.doesNotMatch(rule.selector, /\.evidence-image|\.video-stage|\.capture-element|\.matrix-correct|\.matrix-error/);
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
  for (const label of ['Procedure studio', 'Evidence explorer', 'Evaluation lab', 'Recipe designer', 'Demo kit']) assert.ok(html.includes(label), label);
  assert.match(html, /aria-label="STEPLOCK — Procedure studio"/);
  assert.match(html, /steplock-mark\.svg" alt="" aria-hidden="true"/);
});

test('stale PASS input renders SOURCE LOST and review status in the actual Studio', async () => {
  const {Studio} = await server.ssrLoadModule('/src/pages/Studio.tsx');
  const step = {id: 'S1', part: 'BASE', zone: 'BASE_SLOT', requires: [], state: 'CONFIRMED', allowed: true};
  const session = {session_id: 'synthetic-html-test', recipe_version: 1, source_kind: 'SYNTHETIC_FIXTURE', state: 'finished', decision: {status: 'PASS', reason: 'Prior machine outcome', reason_codes: []}, quality: {usable: true, flags: [], calibration_id: 'cal-1'}, part_markers: {BASE: 10}, step_states: [step], events: [], next_allowed_steps: [], unresolved_event_ids: [], runtime: {frames_analyzed: 2, frames_dropped: 0}};
  const noop = () => {};
  const html = renderToStaticMarkup(React.createElement(Studio, {session, connected: false, credentials: null, busy: false, onCheckpoint: noop, onStop: noop, onReview: noop, onEvent: noop, onExport: noop, onRun: noop}));
  assert.match(html, /data-testid="decision-status">SOURCE LOST/);
  assert.doesNotMatch(html, /data-testid="decision-status">PASS/);
  assert.match(html, /data-status="uncertain"/);
  assert.match(html, /SYNTHETIC SOFTWARE TEST/);
  assert.match(html, /Human acknowledgement does not override/);
});
