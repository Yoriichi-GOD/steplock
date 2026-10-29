# Physical-video validation workstream

This workstream preserves the application, UI, inference engine, recipes and all
historical synthetic reports. Public physical recordings are a separate population;
the existing 32/32 synthetic result is not a physical accuracy claim.

## Definition of Done

| Requirement | Evidence required | Current state |
|---|---|---|
| Acquire official IMPACT three-execution sample | Pinned revision, published size and SHA-256, local acquisition receipt | Download in progress; do not claim acquired until verified |
| Inspect RGB media and native annotations | Source hashes, codecs/FPS/dimensions, views, native annotation schemas | Evaluator implemented; awaiting verified extraction |
| Run untouched inference on real pixels | Per-window observations, original/overlay gallery, append-only events, predictions | Implemented; execution pending acquisition |
| Report compatibility honestly | Calibration/decoded tags, unsupported-input gate, explicit semantic scoring limits | Implemented; no fabricated observations or task mapping |
| Prepare real staged recording workflow | 20-trial plan, printable board/tags, existing recording/registration commands | Kit generated locally; no camera opened |
| Score consented tagged recordings | Frozen reviewed manual labels, original source hashes, separate REAL_STAGED run | Runner implemented; real staged recordings NOT_PROVIDED |
| Verify regressions | Existing suite plus meaningful research-tool tests | 12 new tests pass; full suite being rerun |
| Browser acceptance | 1280×720, fresh offline startup, stale PASS invalidation | Owned by concurrent UI workstream; require actual receipts |

## Commands

From the repository root, using the existing environment:

```powershell
.venv\Scripts\python.exe scripts/acquire_impact.py
.venv\Scripts\python.exe scripts/inspect_external_video.py --seconds 12 --sample-hz 5
.venv\Scripts\python.exe scripts/prepare_physical_validation.py --output runtime/physical_kit
.venv\Scripts\python.exe scripts/register_recording.py --help
.venv\Scripts\python.exe scripts/run_physical_eval.py --annotations data/physical_labels.json
```

The acquisition script downloads **only** the official 2,997,108,593-byte sample,
checks the pinned official SHA-256, and selectively extracts RGB video plus task
annotations and metadata. The archive contains audio/depth/eye tracking/features,
but those are not extracted or needed. A partial download can resume after an app
restart. Raw media and upstream download/verification scripts stay under ignored
`data/external/impact_v1_1/`; no whole-dataset or model download occurs.

The compatibility experiment analyzes start/middle/end windows from all 15 RGB
videos (five correlated views of three executions), using actual decoded frames
at approximately 5 Hz with deterministic FPS-index source timestamps. Analysis
resizing, sampling and the lack of preceding window history are declared. Each
window gets a fresh detector and engine; no synthetic marker, manual calibration,
native truth label or fabricated observation is introduced into inference.

`REPLAY_TAGGED` is the existing transport enum; the experiment explicitly records
population `EXTERNAL_PHYSICAL_UNTAGGED`. The legacy transport name is not evidence
that tags were found. Native anomaly/state/action classes cannot be treated as
four-part fixture marker labels. A calibration refusal is useful evidence of safe
unsupported-input handling, **not** a true-positive assembly mistake. Native
mistake precision/recall/F1, correction detection and false PASS remain unscored
unless an independently validated observation adapter exists. Marker recall and
placement accuracy also require compatible manual reference annotations.

Reports and per-window prediction CSVs go into a new immutable
`benchmarks/external_runs/` directory. Full decoded-frame observations, source
images/overlays, event ledger, gallery and actual-video demonstration remain local
under the acquisition directory. Processing latency is measured on real decoded
frames; live capture-to-visible-browser latency is not inferred from offline timing.

The staged evaluator requires a registered consented recording manifest and
independently reviewed `FROZEN` manual labels with source/recipe hashes. It rejects
synthetic/pending/empty populations, modified sources and escaped media paths.
It never invents recordings or annotations. Source provenance is operator-declared,
not forensically authenticated. Physical clips, labels, failures and results remain
local by default, separate from frozen synthetic results.

## Provenance and license

- Official source: https://github.com/Kratos-Wen/IMPACT
- Repository revision: `4fed5faa5f05f7aece55712e458defa1f372b248`
- Official data: https://huggingface.co/datasets/KratosWen/IMPACT
- Data revision: `628d3ad7a366879f3fdab37648d5df271317c9c0`
- Release: `v1.1/sample/IMPACT-v1.1-sample.zip`
- Published SHA-256: `d22f64abfde8797c3d49cf86aea2ceb83e8581c571e6d5d1c3bad53aa2e13cfd`
- Dataset terms: CC BY-NC-SA 4.0, as stated in official LICENSE-DATA and dataset card.
- Attribution: IMPACT authors, *IMPACT: A Dataset for Multi-Granularity Human
  Procedural Action Understanding in Industrial Assembly*. Use the official
  repository citation metadata; publication status is not assumed.

The other supplied sources (IndustReal, Assembly101, ATA, HoloAssist) remain
research alternatives. No gated access request, university affiliation claim,
full collection download, paid inference or retraining is part of this workstream.

## Execution notes

- Initial acquisition was interrupted by a Codex restart; the verified-source
  resume began from 494,927,872 bytes. This is not an integrity-verified archive yet.
- An unprivileged full backend test attempt stalled inside Python's loopback
  socket-pair setup for the async test client, before app test execution. The
  captured faulthandler stack identifies an environment/network restriction;
  rerun with normal local networking rather than editing product code to mask it.
- Concurrent UI files are excluded from this workstream's commits. Shared Git
  index/commit/push operations are coordinated explicitly with the UI chat.
