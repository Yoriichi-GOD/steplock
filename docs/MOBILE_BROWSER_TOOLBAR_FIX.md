# Phone browser-toolbar dock — 2 November 2026

Status: **IMPLEMENTED / BROWSER_EMULATION_VERIFIED / DEPLOYED**.

Production deployment `db5df9cb-a99c-4b85-90f0-e43f087002ed` was created at
15:31 UTC / 21:01 IST. Cloudflare displayed Success. Both apex and www now serve
the tested `/assets/index-wUle5PYK.js` entry and byte-identical phone stylesheet
`PublicChrome-TsNZAnVR.css` (SHA-256
`7ab7defafab84a29cc71139cbe1636c99dedfd9f17e68d4233d03492beec162d`).
The toolbar difference was explicitly reapplied after the production reload;
native 3D initialized and the live 390px dock ended at y=844 with gap 0.
Live 724 → 844 → 724px resize checks also had gap 0 and a stable reading position.

The founder reported a gap below the lower illustration when a phone browser's
bottom toolbar retracts. This was reproduced on the existing public release:
with a 390×844 visible viewport and a simulated 120-pixel small/large viewport
difference, the sticky stage and dock ended at y=724, exposing later chapter
content in the remaining 120 pixels.

## Final implementation

Only `frontend/src/styles/requiem-landing.css` changes application behavior,
inside its existing phone breakpoint (maximum 767 CSS pixels).

- The stage uses `100dvh`, with `100vh` as a compatibility fallback. Its negative
  flow overlap uses the same unit, keeping reading content aligned.
- The illustration occupies the lower half of that stage using percentage
  positioning. Its instrument bar is anchored to the same halfway boundary.
- Final-chapter clearance and anchor clearance follow the dynamic height.
- Bottom controls and the source disclosure account for `safe-area-inset-bottom`.
- The stage remains bounded by the story and scrolls away before the prototype.

No JavaScript resize loop, new dependency, artwork, detection change, backend,
model call or paid hosting is added. Contact delivery and recorded evidence are
preserved. Desktop rules are unchanged.

## Verification

| Check | Observed result |
| --- | --- |
| Existing live release, 390×844, 120px toolbar difference | 120px gap reproduced; native 3D |
| Final local candidate, same conditions | Stage/dock bottom 844; gap 0; readable 3D view |
| 390×724 → 390×784 → 390×844 → 390×724 | Gap 0 throughout; reading paragraph top stayed 90.2396px |
| 320×640 / 320×740 | Gap 0; no document horizontal overflow |
| 430×812 / 430×932 | Gap 0; no document horizontal overflow |
| Simulated 34px bottom safe area at 320×740 | Controls/disclosure remain above the safe area; panel still reaches y=740 |
| 2D, component selection, explode/assemble | Controls responded with the expected pressed states and button label |
| Story exit | Stage bottom moved above viewport with the story; prototype remained unobstructed |
| Desktop 1280×720 | Native 3D and existing composition inspected; no measured document horizontal overflow |
| Console | No captured browser error entries in the local candidate session |
| Frontend regression suite | 28 passed, 0 failed |
| Static and default live production builds | Both passed; existing shared 3D chunk-size advisory remains |
| Production identity | Entry script and stylesheet match the tested release on apex and www |
| Live phone emulation | Native 3D, 0px gap with 120px viewport difference, and repeated toolbar-size changes verified |

Measurements are in [browser geometry](verification/mobile-toolbar-20261102/browser-geometry.json).
The eight explicit resize cases reapply Chrome's small-viewport override after
each size change. This matters: a page reload can clear the small-viewport
difference. A post-reload zero gap alone is not accepted as proof of the fix.

## Rejected attempts and deployment gates

The first grid-overlap candidate closed the geometric gap, but its local 3D
render hid reading text. It was discarded. The final implementation retains
the existing normal-flow overlap with matched dynamic height. The rejected
capture remains in ignored runtime storage; early candidate measurements remain
labeled in the audit and are not counted as final visual acceptance.

The first attempted production upload returned to an enabled Save and deploy
button without a success confirmation. A premature public-browser zero-gap
sample was invalid because the viewport-difference override had reset on reload.
An independent HTML/asset check correctly found the old entry script and a 404
for the new stylesheet. Publication is complete only after the exact new assets
are served and the toolbar simulation is explicitly reapplied on the public site.
The repeated upload then completed successfully. Its creation response initially
records a queued stage; that is a creation snapshot, not the final serving state.
The dashboard confirmation, exact asset checks and final public rendering close
the publication gate. Earlier invalid samples and prepublication smoke receipts
are retained with their limitations rather than counted as final release proof.

## Evidence and limits

Unedited PNGs: [before](../screenshots/mobile-toolbar-20261102/before-gap-390.png),
[local final 3D](../screenshots/mobile-toolbar-20261102/after-docked-390.png),
[narrow safe area / 2D](../screenshots/mobile-toolbar-20261102/safe-area-320.png),
[story exit](../screenshots/mobile-toolbar-20261102/story-exit-390.png),
[desktop](../screenshots/mobile-toolbar-20261102/desktop-1280.png),
[verified public 3D view](../screenshots/mobile-toolbar-20261102/production-docked-390.png).
The screenshot manifest records native PNG dimensions and hashes. No image was
edited. The accepted 3D captures were taken after initialization and native
scrolling; transient background-compositor samples are not final visual proof.

This is real Chromium rendering with its documented viewport-difference and
safe-area emulation. It is not an Android Chrome or iOS Safari hardware test.
Physical-phone toolbar animation and older-browser fallback behavior remain
untested. Browser engines may update dynamic viewport units in steps during
toolbar animation; a continuous hardware animation guarantee is not claimed.
Old responsive receipts are preserved and do not prove this toolbar behavior.

Sources: [viewport length units](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/length#relative_length_units_based_on_viewport),
[safe-area variables](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Values/env),
[Chrome viewport emulation definitions](https://github.com/ChromeDevTools/devtools-protocol/blob/master/pdl/domains/Emulation.pdl).
