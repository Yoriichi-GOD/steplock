# STEPLOCK / Speedrun SR008 investor deck

## Deliverables

- `STEPLOCK_Speedrun_SR008.pptx`: 14 main slides + 5 appendix slides, native 16:9
  PowerPoint. Text, diagrams, benchmark chart and financial/competitive tables
  remain editable. Original ornamental lettering and genuine screenshots are images.
- `STEPLOCK_Speedrun_SR008.pdf`: static submission/reading version; use this to
  preserve appearance on devices without the locally used fonts.
- `previews/slide-01.png` through `slide-19.png`: 1920x1080 PowerPoint renders.
- `previews/contact-sheet.png`: complete-deck overview.
- `STEPLOCK_Illustrative_Economics.xlsx`: editable hypothetical assumptions/formulas.
- `SOURCE_OF_TRUTH.md`, `SOURCE_LEDGER.md`, `DESIGN_SYSTEM.md`, `STORYBOARD.md`,
  `SPEAKER_NOTES.md`, `QA_REPORT.md` and `DELIVERY_MANIFEST.json`: review/reuse records.

The deck deliberately distinguishes implemented features, generated-test evidence,
real-input compatibility, planned pilots and long-term research. It claims no
customers, revenue, factory accuracy or measured savings. Founder achievements
are attributed to the founder where supporting certificates were not supplied.
YMCA Cypher/Digiweek are not counted as two independently verified awards.

Public demo: https://st-a69b6c98718945778059ba5124767253.ecs.ap-southeast-2.on.aws/demo
The AWS trial is scheduled to end 9 November 2026 at 00:53 IST. GitHub is the
durable fallback: https://github.com/Yoriichi-GOD/steplock

## Local reproduction

Primary authoring engine: **PptxGenJS 4.0.1**, with **Sharp 0.35.5** for lossless
asset-format conversion. Node 24 was used. The slide source is `src/build_deck.cjs`.
No private API, paid service or cloud credential is needed to rebuild the deck.

Install the versions in `package.json` in this folder if the bundled local
dependencies are unavailable. Set `STEPLOCK_NODE_MODULES` to the absolute
`node_modules` directory. Existing frontend Fontsource packages are required for
the private font-conversion step. Python needs Pillow, fonttools and brotli; QA
also uses pypdf and openpyxl for read-only checking.

From the repository root:

```powershell
node pitch-deck/src/prepare_assets.cjs
python pitch-deck/src/prepare_fonts.py
node pitch-deck/src/build_deck.cjs
python pitch-deck/src/finish_package.py
python pitch-deck/src/economics_workbook.py
# Optional bundled verification: node pitch-deck/src/recalculate_workbook.mjs
./pitch-deck/src/render_powerpoint.ps1
python pitch-deck/src/contact_sheet.py
python pitch-deck/src/verify_delivery.py
```

`prepare_fonts.py` writes only to ignored `runtime/pitch-build/fonts`. The renderer
registers those converted existing subsets for its Windows session, opens only
this deck, exports previews/PDF and removes registration afterward. It does not
close unrelated presentations or ship fonts. Microsoft PowerPoint 16 was the
actual rendering/acceptance application. Other renderers can differ.

`finish_package.py` removes orphan master content-type declarations emitted by
the bundled PptxGenJS build. No actual referenced part is removed. The source
normalizes connector extents to avoid invalid OOXML dimensions. Native Fade
transitions are applied by PowerPoint; every slide is complete without motion.

Font fallback and licensing are documented in DESIGN_SYSTEM.md and SOURCE_LEDGER.md.
Do not label generated fixtures or the conceptual mechanical diagrams as real
factory footage. Do not reuse the stock photo as a customer/founder portrait.
