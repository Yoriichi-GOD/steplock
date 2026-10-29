# Supplied artwork integration

This changes the existing React/Vite frontend's appearance. All five views,
session controls, evidence pixels, procedure decisions, benchmarks and optional
3D explorer remain in the tested application.

## Artwork and provenance

Source: user-supplied `ui/STEPLOCK_UI_COMPLETE_ASSET_PACK.zip` in the canonical
checkout. ZIP SHA-256:
`8675ad78523c0d4d00ec7b6a1e816a81ebd284e6d9d6dcb966567dae121dc94e`.

Eight selected files under `frontend/public/steplock-theme/` total 212,432 bytes:

| Asset | Actual role |
| --- | --- |
| `branding/steplock-mark.svg` | Header mark and favicon |
| `branding/steplock-crest-symmetric.svg` | One large crest in Demo Kit |
| `backgrounds/header-landscape-no-text.webp` | Restrained title-area landscape |
| `backgrounds/ink-grain-tile.png` | Global grain at 2.5% opacity |
| `overlays/header-sakura-overlay.svg` | Independent header branches |
| `overlays/footer-sakura-wave-overlay.svg` | Independent footer waves/flowers |
| `ornaments/precision-divider.svg` | Demo Kit title divider |
| `theme/tokens.json` | Supplied palette and attribution metadata |

`theme/production-assets.json` records the selected files' original SHA-256 hashes.
All copies match the supplied manifest. The pack credits generated decorative
imagery and constructed SVG vectors. The supplied crest retains its diamond
outline and mirrored crane construction; it receives no extra CSS rotation.
The artwork is decorative and is never represented as assembly evidence.
The scoped `.gitattributes` rule preserves asset bytes through Windows checkouts;
Git line-ending conversion must not invalidate the supplied hashes.

The full private brief, ZIP, reference mockups, art atlas, previews, optional
unused artwork and font payloads are excluded from public assets and Git staging.
The optional footer raster was inspected and left unused because it contains
stamp-like glyphs; the standalone SVG supplies the footer instead.

## Source changes

- `frontend/src/steplock-ui-overrides.css`: adapts the supplied starter theme;
  independent non-interactive artwork layers, palette, focus, responsive rules,
  semantic status colors and reduced motion.
- `frontend/src/main.tsx`: imports that layer after the original stylesheet.
- `frontend/src/App.tsx`: replaces only the brand icon/wordmark markup and adds
  an accessible brand-link label. All existing action/state code is retained.
- `frontend/src/pages/GettingStarted.tsx`: replaces the decorative shield with
  the supplied full crest. Setup instructions and downloads are retained.
- `frontend/index.html`: compact SVG favicon and ink theme color.
- `frontend/src/theme/theme.test.mjs`, `frontend/package.json`: six focused
  artwork/contrast/HTML regressions alongside the existing ten assembly tests.

UI font stack: Inter, Plus Jakarta Sans, Segoe UI, system-ui, sans-serif.
Logo-only stack: Reggae One, Yuji Boku, Georgia, serif. These are local font
preferences; no font download, remote font request or font installation occurs.
Existing monospace data/ID styles remain intact.

PASS/confirmed stays green, warnings amber, and errors red. Vermilion is the
brand action color. The supplied hover color failed the 4.5:1 text contrast
gate (4.35:1); the shipped hover uses `#BD4035` with `#FFF5E8` text instead.
Evidence images and plot cells receive no decorative styles or filters.
Header engine/advisory indicators remain visible at small widths; only the
navigation row scrolls locally when space is limited.

## Verified scope

| Check | Result |
| --- | --- |
| `npm test` | 16/16 passed: existing 10 + six theme tests |
| `npm run build` | Passed; existing lazy 3D bundle size advisory remains |
| Build with `/steplock-preview/` base | Passed; all five CSS artwork URLs and favicon correctly prefixed |
| Asset provenance | Eight source hashes match; no reference/font/ZIP payload in production |
| SVG safety | No scripts, embedded labels or remote asset references in selected vectors |
| Declared text/status palette contrast | Seven pairs meet 4.5:1 or higher |
| Real App HTML, rendered without a browser | All five tab labels, accessible brand link, offline alert and disabled Run remain |
| Real Studio HTML with stale PASS input | SOURCE LOST and uncertain part status; synthetic disclosure remains |
| Application logic preservation | App action/state code and existing action attributes unchanged |
| Functional source preservation | 12 protected source files match pre-theme `e740dca`, ignoring line endings |
| Canonical checkout | Same 16 tests and production build passed after local synchronization |
| Existing local service | `http://127.0.0.1:63847` serves the new index/CSS and all eight exact asset hashes; engine healthy, camera inactive |
| Theme browser/screenshots | **BLOCKED: local browser use disabled in Work settings** |
| Responsive visual QA | **NOT_RUN** at 320, 360x800, 768x1024, 1366x768, 1920x1080 |
| Camera/upload, pointer/keyboard interaction under the new theme | **NOT_RUN in browser**; source handlers and existing tests preserved |

HTML rendering is a semantic regression check, not browser layout or interaction
verification. No new theme screenshot is claimed. Existing `screenshots/studio-*`
and `assembly-*` files predate this theme and must not be used as final theme QA.
The supplied mockups also remain references only.

Local verification receipts are ignored under `runtime/ui-theme-*.json`; public
source assertions and palette/asset checks are reproducible through `npm test`.
Browser follow-up must check actual healthy/normal, source-lost, Demo Kit, all
five tabs, keyboard focus, source controls and the listed viewport sizes before
the visual acceptance gate can be closed. Real camera validation remains a
separate NOT_PROVIDED gate.

## Delivery

Theme-only Git/push receipts are in [UI_THEME_CHECKPOINTS.md](UI_THEME_CHECKPOINTS.md).
The canonical launcher retains `http://127.0.0.1:63847`; no port is
prescribed or reconfigured for this styling task. Refresh the application after
its production assets are synchronized.
