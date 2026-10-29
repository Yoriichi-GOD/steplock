# UI coordination

UI chat: `01a1864c-a044-7e02-8a95-834392d0f2ff`.
Engine owner: `01a18606-cee2-72c2-a257-995e04574dd5`.

## Ownership

UI work owns new `frontend/src/components/assembly/` files, integration in
`frontend/src/pages/Studio.tsx`, and frontend package files. Existing global CSS,
App source/camera controls, backend, benchmark runs and frozen evidence are not
part of this change. Engine owner retains commit/push ownership.

## Definition of Done

- Procedural metallic parts; 360 degree orbit; select a part by mesh or keyboard button.
- Animated explode, reassemble, distance slider and recipe-order sequence.
- Labels and engine statuses derive from the active session recipe and append-only findings.
- Red means an unresolved engine finding mapped to that part. Green means a confirmed
  placement on a connected, usable capture. A stale source never remains green.
- Animation cannot submit a checkpoint, clear a finding or change the procedure state.
- Procedural illustration and source-frame evidence remain visibly separate.
- Existing camera/replay/checkpoint/evidence paths preserved; responsive browser QA,
  fallback behavior, production build and focused state mapping regressions pass.

## Baseline and progress

- Baseline frontend production build passed before edits (2026-10-29).
- Existing backend/benchmark changes were already present and remain owned by the engine agent.
- UI implementation frozen after production build and 10/10 focused adapter regressions.
- Browser verified: exploded/assembled geometry; all parts fit; direct mesh selection;
  orbit drag; component buttons; separation; recipe sequence; fullscreen exit;
  collapse/restore; actual finding-to-evidence navigation.
- Actual wrong-component synthetic replay: HOLD; fastener red; confirmed other parts
  green. Recipe animation reassembled the model without clearing HOLD/red.
- Actual correction replay: PASS, 4/4 confirmed, retained CORRECTED history.
- Mobile 390 x 844 and desktop 1280 x 900: no horizontal overflow; parts fit.
  Reduced motion disabled sequence/rotation and retained immediate separation.
- Forced graphics-context loss: usable 2D fallback; one-click 3D recovery verified.
  Manual 2D/3D switching did not falsely report a graphics failure.
- Browser offline emulation: PASS became SOURCE LOST; all four mesh states became
  uncertain. Network/media emulation restored after testing.
- Fresh actual API replays after the annotation fix: normal PASS (30 frames, 4/4),
  wrong component HOLD (30 frames, 3/4, two open findings), correction PASS
  (42 frames, 4/4, one retained CORRECTED event). All three actual snapshots passed
  the production frontend state adapter check, including no green when disconnected.
- Direct inspection of fresh annotated evidence confirms the correction frame now
  says `NO NEW TEMPORAL SUPPORT / NEAR-REPEATED IMAGE`; it does not issue a HOLD verdict.
- Browser-only startup with WebGL entirely unavailable remains UNVERIFIED because
  local browser use was disabled in Work settings after earlier successful QA.
  The user reported enabling it, but a retry still returned disabled. No alternate
  browser-control path was used. Context-loss fallback and recovery DID pass earlier.
- The UI source is ready for the engine owner's integration commit, with this
  verification limit retained. No further feature expansion is needed for this slice.

## Exact UI handoff files

- `frontend/package.json`, `frontend/package-lock.json`
- `frontend/src/pages/Studio.tsx` (two integration lines)
- `frontend/src/components/assembly/AssemblyViewer.tsx`
- `frontend/src/components/assembly/AssemblyScene.tsx`
- `frontend/src/components/assembly/assemblyState.ts`
- `frontend/src/components/assembly/assemblyState.test.mjs`
- `frontend/src/components/assembly/assembly.css`
- `docs/ASSEMBLY_VIEWER.md`, `docs/UI_COORDINATION.md`
- `screenshots/assembly-*.jpg` (browser screenshots are JPEG)
- `screenshots/assembly-*-annotated-final.jpg` (actual source evidence, not browser UI)

Commands: `npm test` (10 passing), `npm run build` (passed).
The 3D bundle emits Vite's >500 kB size advisory; it is lazy loaded and about
275.5 kB compressed. No type/build failure remains.

## Resolved integration finding

On staging correction session `4403efd9`, the final summary was PASS but the
latest image overlay said `HOLD: NEAR_DUPLICATE_FRAME`. Original evidence:
`screenshots/assembly-corrected-inspection.jpg`. The engine agent reports a fix:
annotation now describes frame quality / lack of new temporal support without
claiming a separate decision. Fresh API replays and direct final-frame inspection
verified this fix. The original contradictory screenshot is retained as failed
evidence and must not be presented as the current final screen.
The assembly is read-only and mirrors the session summary; no UI decision is invented.
No physical camera, upload, or real footage validation was performed by this UI chat.

Fresh replay artifacts (ignored local evidence):
`runtime/ui-verification/20261029T065056Z/`.
The earlier `20261029T064847Z` TestClient attempt stalled before creating a session
and was stopped. A live local API replay method succeeded; no app code was added
to work around the test harness.

## Model scope

This is a locally generated illustration of the four recipe placements, not CAD,
pose reconstruction, fastening/torque detection or physical assembly validation.
No remote fonts, model files or environment textures will be required at runtime.

Engine-owner integration receipt: final annotated frame files were renamed from
`.png` to `.jpg` after byte-signature inspection; SHA-256 before/after matched.
No source image or historical screenshot was retouched.
