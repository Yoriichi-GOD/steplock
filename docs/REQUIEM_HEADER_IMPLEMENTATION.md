# Fixed Celestial header and separate Assembly Explorer

> Superseded for current layout by [Compact REQUIEM header](REQUIEM_COMPACT_HEADER.md).
> This document retains the prior full-height implementation and its receipts.

This revision follows the user's 29 October clarification: **show the entire
uncropped Celestial image in a taller proportional header**, keep the header and
background fixed, and scroll only the workspace. That direct choice supersedes
the ZIP's earlier 248px crop requirement. At 1691px, the resulting header is
approximately 576px high. It intentionally leaves a smaller scrolling inspection
area; it is not claimed to match the reference's 248px height.

## Sources and composition

Read the supplied ZIP README, complete implementation/QA prompts, JSON, CSV,
CSS guide and coordinate guide. Inspected the header reference, background master,
header-ready WebP and coordinate image. The earlier seven REQUIEM assets remain
separate decorative files.

- Source ZIP: `STEPLOCK_REQUIEM_HEADER_BACKGROUND_OVERLAY_CODEX.zip`.
- ZIP SHA-256: `c36786c33a5018d49bb1b2501dc16de335c41da32683163eebdf27cc5ef1218d`.
- The latest `Celestial Ruins Beneath a Starlit Sky.png` is byte-identical to
  the ZIP's 2149x732 master. SHA-256:
  `92365e3dff54e471efbe5b5fb36937d2fca16a2c301ac8d53613fc3a7165b4ae`.
- Runtime: `frontend/public/assets/steplock-header/celestial-full.webp`,
  2149x732, 308,896 bytes, WebP quality 90/method 6. Its SHA-256 and the unchanged
  alternate header-ready crop are in that directory's `manifest.json`.
- The **text-containing reference is never deployed**, imported or used behind
  controls. The 1691x248 ready crop is retained as an unused alternate; only the
  full master appears in the live background.

The full image uses `background-size:100% auto` and its original aspect ratio,
without cover cropping, stretching, masking or an opacity fade. The React header
and heading are transparent foreground layers. The full supplied logo replaces
the separate crest plus typed wordmark. Real text remains as a broken-image
fallback, with one accessible brand link. The Procedure Studio artwork is larger
and retains a real accessible h1. The other page titles remain real text.

The shell uses two grid rows: proportional header, then a constrained scrolling
workspace. Navigation stays 110px high; small screens use a scrolling nav row and
a 300px header with the complete background contained at its foot. Every tab
change resets only the workspace scroll. The recipe toolbar starts at the header
boundary. Health and ADVISORY ONLY remain live and visible.

Main surfaces are opaque black, with cyan used for accents. Panel and header
outline borders are removed; controls, warnings and keyboard focus retain their
usable boundaries. Both scenic side panes now appear beside the workbench on
desktop at full opacity. Floral corners have their own reserved lower space on
both rails, so they do not sit behind findings or cover controls. Evidence pixels
and annotations have no decorative filters or art overlays.

## Separate illustration page

All original five tabs remain. **Assembly explorer** is an additional real tab
beside Evidence explorer. It reuses the existing AssemblyViewer and adapter with
the current session/recipe/connection, independent local selection, the same
2D/3D/motion controls and the same evidence-event callback. Studio no longer mounts
an embedded illustration. No backend, API, inference or frozen evaluation changes
were made by this UI revision.

## Validation receipts

Built production frontend, served with the normal auto-port launcher. Initial
restart preview: `http://127.0.0.1:50145`. Both header image response bodies matched
their manifest hashes. Local health reported OpenCV 4.14.0, ArUco available,
advisory-only and camera inactive.

| Check | Actual result |
| --- | --- |
| Frontend | 20 checks passed; includes separate explorer stale-state adapter, true header asset hashes, offline HTML, no-source art and existing 10 assembly regressions |
| Production build | Passed; existing optional Three.js chunk warning remains |
| Existing backend suite | 45 passed, one upstream Starlette/httpx deprecation warning; core agent separately added and verified its own validation tests |
| 1691x930 | Header 576.10px, nav110px, body354px; toolbar at576.10px; no horizontal page/body overflow |
| 1440x900 | Header490.49px, body410px; toolbar at490.49px; no horizontal overflow |
| 1280x720 | Header435.99px, body284px; toolbar at435.99px; no horizontal overflow |
| 1024x768 | Header348.79px, body419px; toolbar at348.79px; no horizontal overflow |
| 390x844 | Header300px, body544px; all six tabs clicked, no page/body overflow; tab changes reset workspace scroll |
| 320x760 | Header300px, body460px; no page/body overflow; controls remain reachable |
| Fixed scrolling | With workspace scroll414.67px, header remained at top0; source scrub changed to frame0 and original-frame alt remained truthful |
| Normal inspection | Real synthetic run reached PASS; checkpoint, original/overlay and scrub/Current worked |
| Wrong component | Actual HOLD, linked Wrong Component evidence; acknowledgement retained HOLD |
| Header actions | Setup Guide opened Demo Kit; HTML report downloaded successfully from the actual session |
| Consent | Camera start disabled before consent; recording upload disabled without file/consent; no camera activated |
| Assembly page | 2D switch and separation slider reached100%; Studio has no embedded AssemblyViewer |
| Stale PASS | Stopped only the temporary backend after real PASS: ENGINE OFFLINE, SOURCE LOST, STALE EVIDENCE, disabled checkpoint, no flower. Assembly page also changed to Source Disconnected / Stale |
| Fresh offline startup | Served the built frontend without any API at an auto-selected local port. At1280x720: ENGINE OFFLINE, visible API error, PENDING, disabled Run/camera/upload/checkpoint, no horizontal overflow; screenshot retained |

The first browser comparison found an inherited auto margin allowing the body to
outgrow its grid row, and an oversized implicit nav row from the logo. Both were
fixed and remeasured. A later tab-switch check found inherited scroll position;
the workspace now resets to top on page changes. These are browser-proven fixes,
not assumptions from a successful compile.

Final tablet handoff inspection also found an inherited breakpoint leaving an
empty third column at1024px. Moved the source-first tablet layout threshold to
1100px, retaining full-width camera evidence above the two working rails.
The browser recheck measured the source at957.81px across the957.81px workspace
content, with no horizontal overflow. `screenshots/requiem-header/tablet-1024.png`
records the correction;1280x720 retained its435.99px header/toolbar boundary.
The final original checkout also passed20 frontend checks,58 combined backend
checks and its production build before this CSS-only breakpoint correction.

Real screenshots are in `screenshots/requiem-header/`. They are untouched browser
captures. The reference remains in the ignored/private source pack only.

The first attempt to simulate disconnection with browser networking commands
timed out. Resetting the browser control session restored access. The confirmed
failure receipt above instead stopped the owned temporary backend, and the fresh
startup used a frontend-only static server. Both temporary servers were used only
for verification; neither touched the teammate's live source or core state.

Physical camera operation is outside this visual validation; no camera was opened.
No physical-world accuracy is inferred from these synthetic inspection checks.

## Exact implementation scope

Implementation commit `df9b28528b3df9fc90851c9f5028e7e6df3030f6`, pushed to `main`.
`git show --name-only df9b285` lists these19 intentional files:

```text
.gitattributes
docs/REQUIEM_HEADER_IMPLEMENTATION.md
docs/REQUIEM_UI_IMPLEMENTATION.md
docs/REQUIEM_UI_PROGRESS.md
frontend/public/assets/steplock-header/BACKGROUND_HEADER_READY_1691x248.webp
frontend/public/assets/steplock-header/celestial-full.webp
frontend/public/assets/steplock-header/manifest.json
frontend/src/App.tsx
frontend/src/pages/AssemblyExplorer.tsx
frontend/src/pages/Studio.tsx
frontend/src/theme/requiem.css
frontend/src/theme/theme.test.mjs
screenshots/requiem-header/body-scroll-1691.png
screenshots/requiem-header/desktop-1280.png
screenshots/requiem-header/desktop-1691.png
screenshots/requiem-header/fresh-offline-1280.png
screenshots/requiem-header/laptop-hold.png
screenshots/requiem-header/mobile-390.png
screenshots/requiem-header/source-lost-1691.png
```

The README's small UI usage update is coordinated with the core agent's separate
physical-validation reviewer update, so it is included in that agent's checkpoint
instead of sweeping their changes into this UI commit. Historical source ZIPs,
raw UI assets, existing stashes and frozen evaluation runs are preserved.
