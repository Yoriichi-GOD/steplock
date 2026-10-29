# Evaluation protocol and interpretation

Prediction inputs are frame bytes, source timestamps, source mode/hash and a
validated recipe. Evaluator truth is separate and never imported by inference.
Filename/adjacent-label mutation and deterministic-replay regressions verify this.

48 generated clips: eight families × six camera-transform variants. Whole variants
0–1 are development (16 clips); variants 2–5 test (32 clips). Labels, onsets and
boundaries were generated before predictions. These are related synthetic cases,
not independent physical assemblies. No staged-real footage was available.

All three arms receive each exact decoded frame once, the same detections, recipe,
focus/exposure/calibration settings. A: single observation, no temporal or DAG guards.
B: stable temporal support, no DAG. C: stable support, prerequisite history and
correction. Single-frame deliberately bypasses duplicate temporal flags; this is
the ablated mechanism, not a visual input change. Both baselines retain evidence
and current spatial quality checks.

## Metrics

- Event match: one-to-one same class, part and zone. Alert in [onset−200ms,
  onset+2000ms]; checkpoint events ±200ms. Timely means matched before annotated
  boundary. Match class/reason is separate from correct final status.
- Precision TP/(TP+FP), recall TP/(TP+FN), F1 2TP/(2TP+FP+FN). Undefined denominators
  return null, not a fabricated perfect score. Micro and per-class/macro retained.
- False PASS: expected non-PASS clips returned PASS / all expected non-PASS clips.
  Includes insufficient-evidence/quality cases. Every aborted clip stays in denominator.
- False alerts/minute uses scored mistake alerts on annotated normal footage;
  uncertainty/quality warnings are counted separately and all raw events are retained.
- Marker recall includes missed visible marker/anchor opportunities. Occluded markers
  have a separate all-placed recall. Zone accuracy uses all visible part opportunities,
  not only successful detections. Unknown opportunities zero → null, tested separately.
- Vision p50/p95 uses wall-clock per analyzed frame. Throughput is offline processing,
  not live capture/display latency. Capture-to-visible latency is NOT_MEASURED.
- Wilson bounds are descriptive; related generated clips violate a simple independent
  industrial sample interpretation. Report exact denominators before percentages.

`benchmarks/protocol.json` records frozen thresholds. First development failure:
default adaptive threshold missed a tag after resampling. Wider windows selected
on dev recovered it. Encoded frozen frames exposed byte-level differences; a dev-only
near-repeat check prevents them from adding support. Raw recovery regression caught
overly aggressive invalidation; recent proof is retained only within the bounded
window. [Full tuning history](DEVELOPMENT_TUNING.md). Earlier runs are immutable.

First test run `20261029_061625_048928_test` used committed source c14e7f0. Later
wrong-zone/OUTSIDE correction regressions found a stale-pair invalidation bug;
this fix was not selected to improve the held-out corpus. A separate final run
must accompany the final engine commit. No labels are silently changed.

Each run saves config, exact commit, dirty paths, prediction-source cleanliness,
environment, manifest, per-clip outcomes, observations, events, confusion matrix,
latencies, failures and selected source/overlay frames. No run directory is reused.
Stress tests are a separate designed safety grid, not another accuracy benchmark.

Assembly101/HoloAssist/IKEA ASM visual evaluation: NOT_RUN. Assembly101 action labels
do not directly map to the four visible tags, so even an annotation-only score is
NOT_RUN rather than a misleading number.
