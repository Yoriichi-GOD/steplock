# Real physical-video experiment: measured outcome

The official IMPACT v1.1 three-execution sample was acquired and processed with
STEPLOCK's unchanged ArUco detector and procedure engine. **Real-video ingestion
and conservative refusal are verified. Untagged industrial mistake recognition
is not implemented or validated.**

| Measured population | Result |
|---|---:|
| Genuine released RGB recordings | 15 videos, five views of three executions |
| Evaluated portions | 45 windows: start/middle/end, 12 seconds each |
| Actual source frames analyzed | 2,700, sampled at approximately 5 Hz |
| Decode or processing failures | 0/45 windows |
| Valid STEPLOCK board calibration | 0/2,700 frames |
| Final capture verdict | CALIBRATION_REQUIRED in 45/45 windows |
| PASS on unsupported windows | 0/45 |
| Frames with isolated decoded IDs | 9/2,700, IDs 17/34/37; no fixture support |
| Offline detector time p50 / p95 | 22.02 / 27.44 ms |
| Offline detector + engine p95 | 28.68 ms |
| Native mistake precision/recall/F1 | NOT_SCORABLE |
| Native false PASS / correction detection | NOT_SCORABLE |
| Marker recall / placement accuracy | NOT_SCORABLE: no compatible physical marker truth |
| Source-time procedural alert delay | NOT_SCORABLE: no native observation adapter |
| Live capture-to-visible-browser latency | NOT_MEASURED |
| Team-recorded tagged tabletop clips | NOT_PROVIDED |

Zero unsupported PASS is a capture-safety result. It is not a zero false-PASS rate
against native IMPACT assembly correctness. The 45 windows and 15 viewpoints are
correlated; they are not 45 or 15 independent physical assembly trials.

## Reproducible evidence

The immutable measured run is
[`20261029_090358_336831_impact_compatibility`](../benchmarks/external_runs/20261029_090358_336831_impact_compatibility/summary.md).
It includes metrics, per-window predictions, processing times, an explicitly
unscored native confusion table, source/code hashes, native annotation inventory,
isolated-ID anomaly receipts, and the API integration receipt.

- Prediction source commit: `c605b6ad6ec4cc7efc2a284086de6c36973c1837`.
- Detector SHA-256: recorded in metrics.json; the production detector was not changed.
- Full observations and event JSONL are local; their hashes are in metrics.json.
- All 45 windows retain original and overlay images, with a local HTML gallery.
- The nine isolated-ID frames retain exact analysis PNGs and overlays. Each PNG
  was independently recovered from the original recording and matched against
  the prediction log's frame hash. Visual inspection of a retained case showed
  a decoded box border; no native tag truth is assumed and no engine tuning was
  performed on these cases.
- A 45-second, 225-frame demonstration montage uses actual sampled dataset
  frames with visible compatibility-only labels. It is not a successful physical
  mistake/correction demonstration and is not a webcam capture.

Raw observations, images, gallery and demonstration AVI remain under ignored
`data/external/impact_v1_1/validation/20261029_090358_336831/`.
They are kept local rather than bundled into the public software repository.
Dataset media are CC BY-NC-SA 4.0; attribution and actual modifications are
recorded. The original source recordings are unchanged. Analysis frames are
resized to a maximum width of 960 pixels and sampled, as declared in the run.

## Acquisition and actual media inspection

The archive is exactly **2,997,108,593 bytes** and matches official SHA-256
`d22f64abfde8797c3d49cf86aea2ceb83e8581c571e6d5d1c3bad53aa2e13cfd`.
The pinned official `verify_release.py` also passed archive structure, duplicate
entry, CRC and published-checksum checks. 320 of 391 archive members were
selectively extracted: RGB video, annotations and metadata. Depth, audio,
eye-tracking and backbone features were not extracted.

Measured RGB properties are MP4 containers (OpenCV FourCC FMP4 or h264),
1280×720 or 1920×1080; 24.917 or 30.0 FPS; durations
115.93–174.14 seconds; views ego/front/left/right/top. Source timestamps used by
this experiment are declared FPS-index fallbacks, not hardware capture clocks.
The original MP4s exceed the app's 120-second upload limit in some cases; the
compatibility evaluator uses bounded windows without changing product limits.

Native annotations are materially different from the fixture recipe:

- ASR describes 17 angle-grinder components, assembly/disassembly workflows and
  frame-indexed state transitions, rather than four tagged placement zones.
- ATR declares six error categories. This sample contains 142 unique annotated
  anomaly segments after deduplicating repeated split membership; observed label
  occurrences are 73 temporal, 62 spatial and 16 handling. Multi-label segments
  mean these counts do not sum to 142. The 568 split-file rows are not independent
  anomaly events or predictions.
- PPR supplies NORMAL/ANOMALY/RECOVERY mappings. The sample's per-hand frame labels
  observed here include NORMAL and ANOMALY; no RECOVERY-labeled frames were found
  in those files. Availability of a recovery mapping does not prove sample coverage.
- Anomaly start/end values are source **frame indices**, not milliseconds.

These inventories are annotation analysis after inference. They are not counted
as detector predictions and never enter the production engine.

## Why no native recognition adapter was added

| Native task family | What STEPLOCK can currently test | Missing independent evidence |
|---|---|---|
| TAS/action segmentation and forecasting | Decode source frames and preserve timing/provenance | Untagged action recognizer and official task protocol |
| ASR, 17-component assembly state | Safe refusal when fixture calibration is absent | Native part identity/state observations and geometry |
| PSR/procedure completion | Existing four-part temporal engine remains intact | Valid native recipe/graph plus independent native observations |
| PPR anomaly/recovery | Ingestion and capture-quality behavior | Native visual phase/anomaly predictions |
| ATR temporal/spatial/handling/etc. | Raw detector behavior on real scenes | Independently validated semantic error recognizer |

Converting annotation labels into marker observations would feed ground truth
into inference. Pasting digital tags onto footage would create synthetic evidence.
Neither was done. Training/tuning a new native recognizer on three executions
would require separate development data, a defensible held-out protocol, model
provenance and new validation. That is an additional research workstream, not a
valid shortcut to physical accuracy in this experiment.

## Actual app-route verification with real video

A declared 60–63 second excerpt from the real front-view disassembly recording
was sampled at 5 Hz, resized to 640×360 and re-encoded as MJPEG for the existing
upload limits. In an isolated FastAPI TestClient, without interfering with the
UI preview:

- Session creation succeeded; upload returned 200 and matched the excerpt hash.
- The actual source, detector and engine processed all 15 excerpt frames.
- The final verdict was CALIBRATION_REQUIRED, as expected for unsupported footage.
- Original frame PNG hash verified against the engine's evidence record.
- JSON and HTML exports both returned 200; neither included the access token.
- Stopping the source changed the verdict to SOURCE_LOST.

This is app-route integration evidence, not a new live-browser or camera test.

## Controlled tagged physical validation is prepared

`scripts/prepare_physical_validation.py` produces printable board/tags, a
20-recording trial plan (five scenarios × four recordings, two setups), an
independent manual-label template and step-by-step recording/registration guide.
`scripts/run_physical_eval.py` requires consented registered original clips and
frozen manual labels; it rejects pending/synthetic/empty populations and source
hash/path violations. It records the recipe, source code, manifest and manual
truth hashes and preserves failures in a separate REAL_STAGED run.

No team camera was opened and no staged footage was invented. Marker recall,
placement accuracy, actual mistake precision/recall, correction and source-time
alert delay can be measured once compatible physical clips and independent labels
exist. Live capture-to-visible-browser latency additionally requires a validated
shared timing method; offline processing speed is not that measurement.

## Preservation and verification

The production backend, recipe, frozen synthetic benchmark runs and stress runs
have no diff from the pre-workstream baseline `04c79f5`. New scripts, reports and
tests are isolated from the UI workstream. The existing synthetic 32/32 result
remains a separate historical claim with its original provenance and limitations.
The full backend suite passed 58/58 after final output-path hardening (45 existing
and 13 new regressions, 19.36 seconds). Exact push receipts are recorded in PHYSICAL_VALIDATION.md.
The coordinated UI workstream closed exact 1280×720, frontend-only offline startup
and actual backend-loss-after-PASS checks with screenshots at `df9b285`.
[Browser receipts](REQUIEM_HEADER_IMPLEMENTATION.md) retain the scope of those
synthetic-procedure UI checks; physical recognition is not inferred from them.

Sources: [official IMPACT release](https://github.com/Kratos-Wen/IMPACT/blob/4fed5faa5f05f7aece55712e458defa1f372b248/docs/DATA_RELEASE.md),
[official dataset](https://huggingface.co/datasets/KratosWen/IMPACT/tree/628d3ad7a366879f3fdab37648d5df271317c9c0),
[dataset license](https://github.com/Kratos-Wen/IMPACT/blob/4fed5faa5f05f7aece55712e458defa1f372b248/LICENSE-DATA).
