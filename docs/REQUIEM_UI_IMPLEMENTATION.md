# REQUIEM UI implementation

> Updated header, black surfaces and separate Assembly Explorer:
> [current header implementation](REQUIEM_HEADER_IMPLEMENTATION.md). The receipts
> below describe the first REQUIEM integration and remain historical evidence.

The rejected sakura/vermilion theme has been removed from the running frontend.
The existing React application now uses the supplied celestial-arch artwork,
ivory serif headings, cyan navigation, parchment actions and neutral inspection
surfaces. No API, procedure engine, inference, benchmark or recipe changes are
part of this integration.

## Review and run

Use the normal launcher in the [README](../README.md#run-locally). It prints an
available loopback URL; no fixed port is required. The current UI verification
used `http://127.0.0.1:55520`, selected by that launcher on 29 October 2026.
The final handoff runs from the original checkout at `http://127.0.0.1:61795`.

All five existing tabs and their callbacks remain. The inspection workbench now
precedes the existing optional assembly explorer, so the real source and advisory
lead the screen. The explorer retains its 3D, 2D, motion, selection and collapse
controls. Its geometry remains an illustration, never reconstructed evidence.

## Asset provenance and placement

The entire supplied brief was read. All seven master images and seven supplied
WebP variants, the reference mockup, catalog, manifest and starter tokens were
inspected. The reference image is guidance, never a runtime background.

Source archive: `STEPLOCK_REQUIEM_UI_ASSETS_AND_CODEX.zip`, SHA-256
`078739888fb88fb44bd14b83de415f6157c14e3b8cd67b6206ee06c636edcbaf`.
Originals remain in the user's local `ui/` source archive and the ignored
`runtime/requiem-assets/078739888fb8/STEPLOCK_REQUIEM_UI_ASSET_PACK/` inspection
directory. The private brief, reference mockup, ZIP and heavy masters are not
published as product assets.

| Production file under `frontend/public/assets/requiem/` | Use |
| --- | --- |
| `celestial-arches.webp` | Upper-right hero; dark negative space behind live text |
| `steplock-crest-compact.webp` | Small header crest beside the real STEPLOCK name |
| `procedure-studio-ornate-title.webp` | Desktop-only title with a real accessible h1; text fallback on error |
| `steplock-ornate-logo.webp` | Demo Kit introduction, lazy loaded |
| `floating-flower.webp` | Studio only, before any session/source; never loading, failed or stale evidence |
| `corner-florals.webp` | Bottom 100px of procedure rail, opacity 0.10 |
| `right-arch-landscape.webp` | Separate 78px decorative margin only at widths >=1800px |

The seven production images total **796,298 bytes**. Their source master hashes,
output hashes, dimensions and conversion settings are recorded in
[`manifest.json`](../frontend/public/assets/requiem/manifest.json).
[`prepare_requiem_assets.py`](../scripts/prepare_requiem_assets.py) verifies source
hashes and generates WebP derivatives with Pillow/LANCZOS, quality 85, method 6.
The normal build does not require Pillow. No font files or remote font services
are used; Georgia/Segoe UI/Consolas fallbacks work offline.

Decorative images cannot intercept controls. Artwork never filters, recolors,
textures or transforms source frames, calibration annotations or numerical plots.
Broken ornament images are hidden while functional text remains. A failed evidence
image displays an explicit evidence-unavailable message. A disconnected source
keeps historical pixels but labels them STALE EVIDENCE and changes the current
advisory to SOURCE LOST.

## Definition of Done and receipts

Browser checks used the built production app and the actual FastAPI/OpenCV backend.
No screenshot was retouched; files in [screenshots/requiem](../screenshots/requiem/)
come directly from the browser. Source images shown there are visibly synthetic.

| Requirement | Evidence / result |
| --- | --- |
| Typecheck and production build | `npm run build`: passed; existing optional 3D chunk-size warning remains |
| Frontend regression checks | `npm test`: 18 passed; includes 10 existing assembly-state checks, asset hashes, declared text contrast, no evidence styling, actual offline/stale component HTML and empty benchmarks |
| Existing backend regression suite | `.venv/Scripts/python.exe -m pytest -q --basetemp=runtime/pytest-requiem-live`: 45 passed, one upstream Starlette/httpx deprecation warning |
| Normal synthetic run | Browser reached real PASS; original/overlay toggle, first-frame scrub and Current worked |
| Wrong component | Actual HOLD, WRONG_FASTENER explanation and linked timestamped original/overlay evidence |
| Acknowledgement | Browser acknowledgement retained HOLD; notice explicitly says machine evidence governs |
| Checkpoint and exports | Explicit checkpoint worked; real JSON and HTML files downloaded and inspected locally |
| Upload | Real file chooser uploaded `fx_00_00.avi` as SYNTHETIC_FIXTURE; remained PENDING before explicit checkpoint, then PASS |
| Camera controls | Consent gate disabled capture initially; injected `getUserMedia` permission rejection showed the upload recovery message; injection removed by reload |
| Physical camera / OS permission prompt | NOT_TESTED; no physical camera opened and no new camera access granted |
| Disconnected after PASS | Browser network interruption produced ENGINE OFFLINE + SOURCE LOST, disabled checkpoint, no flower or stale PASS |
| Fresh offline startup | API requests blocked in a separate fresh tab: ENGINE OFFLINE, alert, disabled run and PENDING; no false PASS. A narrow-laptop verdict wrap found here was corrected and rechecked |
| Failed evidence request | Blocked frame request produced explicit evidence-unavailable fallback; request blocking then removed |
| Missing art | All REQUIEM image URLs blocked: real title/name, source controls and evidence remained usable; blocking removed |
| Five tabs | Studio, Evidence Explorer, Evaluation Lab, Recipe Designer and Demo Kit opened with real state |
| Recipe UI | Selected existing v2 then restored v1; invalid JSON disabled save; restored draft without persisting a new recipe |
| Evaluation | Existing 32-clip synthetic results and denominator text preserved; missing data also covered by component regression |
| Responsive | 1920x1080, 1600x1000, 1280x900, 820x1180, 390x844 and 320x760 inspected; no page-wide overflow in checked Studio views or any of the five tabs at 390px |
| Reduced motion / explorer | Reduced-motion disabled sequence playback; 2D switch, separation to 100%, reassembly and collapse worked |
| Original checkout | Its 18 frontend tests and production build passed; all seven served assets matched the manifest; startup, no-source state and Stop source checked in browser |
| Subpath assets | Separate `/steplock/` build passed; CSS backgrounds, favicon and client asset base contain the required prefix |

The first restricted backend test process stalled at local API access and was
stopped. Rerunning with permitted local connections produced the 45/45 receipt.
The first restored preview had the same local socket restriction; the successful
preview used the normal launcher with local connection permission.
The existing Three.js explorer also emits a `THREE.Clock` deprecation warning;
this predates the theme. No new dependency or renderer was introduced.

## Intentional differences from the reference

The supplied ornate title is gold rather than the mockup's ivory typesetting.
The header uses the supplied compact crest with real text. Panels remain opaque
and source pixels retain their actual ungraded appearance. No fake part thumbnails,
case IDs, timings or screenshot metrics were recreated. The existing event timeline
and optional 3D explorer remain available beneath the inspection area. Tablet and
mobile stack the source before the decision and procedure sections.

## One-minute judge walkthrough

1. Open Procedure Studio and run **Normal**. Identify the synthetic watermark.
2. Point to the source frame and ordered confirmations: "We verify what was
   observed and when."
3. Run **Wrong Component**, inspect HOLD, then click its timestamped evidence.
4. Explain that acknowledgement does not override the machine finding.
5. Open Evaluation Lab and describe its actual 32-clip synthetic scope.
6. Close: "See the component. Know the step. Show the evidence."

Git publication and exact checkpoint receipts are in
[`REQUIEM_UI_PROGRESS.md`](REQUIEM_UI_PROGRESS.md). Historical theme reports are
retained and explicitly marked superseded.
The exact source, asset, screenshot and removed-file inventory is in
[`REQUIEM_CHANGED_FILES.txt`](REQUIEM_CHANGED_FILES.txt).
