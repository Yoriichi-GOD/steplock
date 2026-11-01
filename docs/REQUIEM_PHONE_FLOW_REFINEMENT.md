# REQUIEM phone flow refinement

Implemented and inspected in the actual local browser on 2026-11-02. This is a follow-up to [the lower illustration dock and fixed launcher](REQUIEM_MOBILE_DOCK_AND_LOCAL_STARTUP.md).

## Requested behavior and result

| Requirement | Implemented and verified |
| --- | --- |
| Remove the empty space after each phone chapter | Chapters use their content height. Measured copy-to-copy gaps are 60px, or 104px where a decorative divider needs space, at both 390px and 320px. The half-screen spacer is retained once at the end of the story so the last paragraph can clear the dock. |
| Remove the line separating copy and illustration | The chapter instrument has a computed border of 0px. Existing diagram lines and button outlines retain their separate purposes. |
| Open in native 3D | Fresh loads at 390, 320, 1691, 1280 and 1024px selected 3D and initialized the real canvas without a mode click. The former phone-width and device-capability restrictions on automatic 3D selection were removed. |
| Keep the display choice and fallback | Manual 2D/3D switching, explode/assemble and component selection worked. Native phone mode clicks retained the same scroll position. Reduced motion opened in 2D. Forced graphics-context loss displayed the 2D diagram with usable controls and the existing unavailable notice; reload restored native 3D. |
| Keep the lower-half phone dock and natural exit | At 390×844 the illustration starts at y=422 and the chapter bar at y=370. At 320×740 they start at y=370 and y=318. The stage stays bounded by the story and moves above the viewport before the prototype is reached. |
| Remove the closing assembly drawing | The closing section contains no SVG, canvas or final-mechanism element. Its only foreground content is “The next chapter is still being built.” |
| Match the italic caption font | The caption and “Not where we intend to stop.” both compute to Instrument Serif, italic. Desktop and phone compositions were inspected over the existing celestial artwork. |
| Move desktop navigation right | Navigation begins at x=410.9 / 241.0 / 137.2 for 1691 / 1280 / 1024px viewports, with clear separation from the logo and CTA. The header background remains fully transparent. |

The existing React routes, Three.js scene, 2D renderer, state adapter, story poses, inspection engine, evidence and API contracts are unchanged. No artwork or dependency was added. Existing ornamental dividers now follow the shorter phone chapters; the existing closing celestial background is preserved. No new animation system was introduced.

## Browser receipts

Actual captures and DOM measurements are in `screenshots/requiem-phone-flow/`. `browser-audit.json` retains raw measurements, including an early anchor sample taken while smooth scrolling was still moving. Use the explicitly settled sample for anchor positioning. The Studio destination settled at y=100.2px against the existing 100px desktop scroll padding; the desktop invitation settled at y=99.9px.

| Before | After |
| --- | --- |
| [Previous protected chapter spacing](../screenshots/requiem-mobile-dock/late-feedback-390.jpg) | [Continuous chapter flow](../screenshots/requiem-phone-flow/knowledge-tail-390.jpg) |
| [Previous phone entrance](../screenshots/requiem-mobile-dock/entrance-390.jpg) | [First-load native 3D](../screenshots/requiem-phone-flow/first-load-3d-390.jpg) |

Additional captures: [late feedback](../screenshots/requiem-phone-flow/late-feedback-390.jpg), [vertical process steps](../screenshots/requiem-phone-flow/late-tail-390.jpg), [product reveal](../screenshots/requiem-phone-flow/product-3d-390.jpg), [bounded dock exit](../screenshots/requiem-phone-flow/exit-390.jpg), [clear prototype](../screenshots/requiem-phone-flow/after-story-390.jpg), [320px entrance](../screenshots/requiem-phone-flow/first-load-3d-320.jpg), [320px chapter](../screenshots/requiem-phone-flow/knowledge-320.jpg), [reduced motion](../screenshots/requiem-phone-flow/reduced-motion-390.jpg), [graphics failure](../screenshots/requiem-phone-flow/graphics-fallback-390.jpg), [desktop closing caption](../screenshots/requiem-phone-flow/closing-caption-1691.jpg), [phone closing caption](../screenshots/requiem-phone-flow/closing-caption-390.jpg).

Desktop entrance captures: [1691×930](../screenshots/requiem-phone-flow/desktop-1691.jpg), [1280×720](../screenshots/requiem-phone-flow/desktop-1280.jpg), [1024×768](../screenshots/requiem-phone-flow/desktop-1024.jpg). The screenshot manifest records actual raster dimensions and SHA-256 values separately from CSS viewport dimensions; the host display scaling and scrollbar presentation affect the captured raster. No screenshot was edited.

## Regression checks

| Check | Result |
| --- | --- |
| TypeScript and production build | PASS; Vite build 8.02s. Existing shared 3D bundle-size advisory remains. |
| Existing frontend tests | 26 passed, 0 failed. |
| Existing launcher and public-demo tests | 15 passed in 37.58s. One existing Starlette/httpx deprecation warning. |
| Actual HTTP demo examples | Normal PASS; wrong component HOLD_FOR_REVIEW; wrong order HOLD_FOR_REVIEW; correction PASS with retained CORRECTED event. All source-frame retrieval and reset checks passed. Generated fixture population; zero provider calls. |
| Actual browser demo | Normal completed with PASS, 30 analyzed frames and 10 ledger events. Reset returned PENDING. The rendered evidence image filter remained `none`; see `demo-audit.json` and [the generated frame capture](../screenshots/requiem-phone-flow/demo-normal-frame-390.jpg). |
| Fixed-address startup | Preview started at 127.0.0.1:62401 and a repeated launcher invocation reused it without creating another server. |
| Rendered responsive layout | Actual 390×844 and 320×740 phone views plus 1691×930, 1280×720 and 1024×768 desktop views inspected. No measured document horizontal overflow. |
| Frozen checkpoint | `day1-final` remains unchanged. Unrelated `docs/judging/` work excluded. |

Commands:

```text
cd frontend
npm run build
npm test
cd ..
.venv/Scripts/python.exe -m pytest backend/tests/test_launcher.py backend/tests/test_public_demo.py -q --basetemp=C:/Users/nrgen/AppData/Local/Temp/steplock-phone-flow-20261102 -o faulthandler_timeout=45
.venv/Scripts/python.exe scripts/smoke_public_demo.py --origin http://127.0.0.1:62401
```

The restarted Codex session initially launched a network-restricted process, which was stopped and replaced by the normal approved local preview process on the same port. An initial smoke attempt also exposed an incorrect launch environment variable: `STEPLOCK_PUBLIC_DEMO` is not the public-mode setting. Restarting with the existing `STEPLOCK_PUBLIC_MODE=1` corrected the test environment; the complete smoke then passed. Neither diagnosis required application changes. The preview runtime resolves to the external Codex LocalCache directory documented in the preceding report.

The portable launcher-test follow-up `095f4814ffd0194271a15ed1fbc0f8159ec74eef` has [green GitHub CI](https://github.com/Yoriichi-GOD/steplock/actions/runs/41336884113). The complete phone implementation is pushed as **`e773bef24db4c8aefa8df6b7f2338a090f85ee65`**, with [its own green CI](https://github.com/Yoriichi-GOD/steplock/actions/runs/41339222928). Frontend regression/build, full backend regression, Linux production image and actual-container HTTP smoke all passed for that exact implementation commit. The local and remote branch SHAs matched; `day1-final` still resolves to `dd056687dcfa4f179519132378137d80d3d21570`.

## Independent review

The architecture owner independently accepted implementation commit `e773bef` after a separate review. Fresh 390/320px phone browsers and reduced-motion 390px confirmed the dock bounds, 60/104px chapter gaps, borderless bar, controls, natural exit and caption-only italic closing. All four desktop navigation links settled at the existing 100px scroll offset: 100.00, 100.33, 99.58 and 100.38px. Desktop 1691/1280/1024px had native initial 3D, separated navigation/logo/CTA and no horizontal overflow. Normal and context-loss review sessions recorded no page errors. The reviewer also reran 26 frontend and 7 launcher tests and verified the 19 primary screenshot hashes.

The reviewer separately launched **fresh Chromium with `--disable-webgl`**, confirmed `webglAvailable: false`, and verified that initial startup reaches the existing 2D fallback with the unavailable notice and usable explode/assemble controls. This is distinct from the primary session's successful `WEBGL_lose_context` test after 3D initialization.

Exact unedited independent receipts are preserved in `screenshots/requiem-phone-flow/independent-review/`: [phone/navigation review JSON](../screenshots/requiem-phone-flow/independent-review/review.json), [desktop/startup JSON](../screenshots/requiem-phone-flow/independent-review/desktop-startup.json), [native 1280px capture](../screenshots/requiem-phone-flow/independent-review/desktop-native-1280.png), and [startup without WebGL](../screenshots/requiem-phone-flow/independent-review/startup-without-webgl.png). Its separate manifest records each file's SHA-256 and the PNG dimensions. The copies were checked byte-for-byte against the ignored runtime originals. This documentation-only follow-up introduces no application changes and does not restart the preview.

## Exact modified implementation files

- `frontend/src/components/marketing/CinematicStory.tsx`: native 3D initial selection, while retaining reduced-motion and failure handling.
- `frontend/src/pages/LandingPage.tsx`: replace the closing schematic with the real caption text and remove the unused import.
- `frontend/src/styles/requiem-landing.css`: content-height phone chapters, divider clearance, borderless dock bar, italic closing caption and desktop navigation offsets.

This report, the follow-up link in the preceding report, and browser screenshot/audit files document the change. The architecture-owning chat held shared files and port 62401 during implementation and was given the final review handoff.

## Verification limits

Phone dimensions were emulated in actual browsers, not tested on physical phone hardware. Reduced motion, actual graphics-context loss and independently tested startup without WebGL passed. The primary in-app browser could not perform its requested initialization override; the independent Chromium launch described above closed that startup verification gap. The existing performance fallback was preserved but was not forced through a slow-device benchmark. No physical-camera, uploaded-video or industrial accuracy claim is made by these UI checks.
