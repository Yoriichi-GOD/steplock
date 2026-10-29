# Judge walkthrough

## 90 seconds

0–10s: “STEPLOCK checks visible tagged placements against a recipe and asks for
correction. It is a local advisory prototype, not a certified interlock.”

10–25s: Show actual source frame, marker corners, IDs, calibrated regions and source
clock. Say “This example is synthetic software imagery; physical capture remains
untested unless the team supplies footage.” With a real jig, identify fixed anchors.

25–40s: Run Normal. Observe BASE → SPACER → COVER → FASTENER confirm, then final
checkpoint PASS. One isolated image cannot produce a STEPLOCK PASS.

40–60s: Run Wrong Component or Wrong Order. Show exact supported finding and frame.
An early cover only gets an order accusation when earlier empty-zone evidence exists.
If a clip starts midassembly, STEPLOCK requests evidence rather than inventing history.

60–75s: Run Correction. Wrong fastener removed; correct fastener appears; CORRECTED
references retained old evidence. Acknowledgement does not clear a machine finding.

75–90s: Evaluation Lab: same frames / three arms / exact counts / retained failures.
Show commit cadence and physical validation gap. Optional assembly illustration is
explicitly separate from perception; animation cannot change evidence or verdict.

## 30-second fallback

Run Normal, then Wrong Component. Open its event and show source hash + original/
overlay. State the synthetic/marker-assisted limits. Use headless `run_demo.py` if
browser/camera is unavailable; never call a JSON-only run a physical demonstration.

## Questions

- Tag identity vs general AI? Tags are the sensor; the contribution is temporal
  prerequisites, abstention, correction and traceable evidence, not markerless recognition.
- Missing camera visibility? HOLD/uncertainty, not fabricated absence or PASS.
- Can it stop machinery? No. Real interlock engineering and certification are separate.
- What validates it? Generated software regression/benchmarks here. Consented physical
  task clips are still required for real capture evidence; no public-video score claimed.
