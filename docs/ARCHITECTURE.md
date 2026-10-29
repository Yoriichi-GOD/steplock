# Architecture and trust boundaries

FastAPI serves the built React/TypeScript app and API from one loopback origin.
`scripts/dev.py` reserves a free socket and hands it to Uvicorn, avoiding a port
selection race. It never terminates another service.

## Perception and procedure

`vision/aruco.py` decodes DICT_4X4_50 from actual arrays. Fixed marker centers
40/41/42/43 define normalized board correspondences, explicitly adopted by the kit.
They are not precision physical board corners. Invalid quadrilaterals, small tags,
blur, exposure and missing anchors are gated. Inset zone entry and supported
removal provide temporal hysteresis.

`procedure/recipe.py` validates IDs, tags, zones, references and DAGs. Duplicate YAML
and API JSON keys are rejected. New recipe versions persist locally; an existing
session retains its recipe model and hash.

`procedure/engine.py` requires two independent images spanning 160ms. Exact repeats
HOLD; near repeats add no support. Existing valid evidence has a bounded 1800ms
window. Missing/reversed source history prevents an unsupported order claim.
Only earlier confirmed prerequisites can authorize a later first placement. An
ORDER_VIOLATION needs earlier supported clear-zone evidence; otherwise HOLD_UNCERTAIN.

Correction needs supported removal, replacement or the same unique tag's relocation.
Clearing an invalid old location cannot erase the new valid confirmation. Removing
a valid prerequisite invalidates dependents for re-placement. Only explicit final
checkpoints can PASS. Acknowledgement never overrides evidence.

## Capture, clocks and evidence

One active source per process; separate producer/consumer threads with queue size 2.
Old queued frames are dropped and counted. Camera release is in `finally`; browser
tracks stop on cancel/unmount. Live/replay duration is bounded at 120 seconds.

Replay uses declared FPS-index source timestamps. Browser camera uses a monotonic
session clock; local camera uses process monotonic time. Vision processing uses
`perf_counter`. Cross-clock capture-to-visible latency is NOT_MEASURED. Browser
polling resynchronizes authoritative snapshots; disconnect cannot retain stale PASS.

Local session storage: `source.json`, lossless original PNGs, annotated JPEGs,
`frames.jsonl`, append-only `events.jsonl`, separate `reviews.jsonl`. Frame hashes
refer to saved PNG bytes; overlays have separate hashes. File-source hashes refer
to file bytes. A live hash identifies the source manifest, not an unrecorded video.
CORRECTED references an old immutable event. The store checks historical prefixes.
Local evidence is Git-ignored and not cryptographically signed against filesystem edits.

## API

| Route | Behavior |
|---|---|
| GET `/api/health` | actual CV version and active source |
| GET/POST `/api/recipes` | list or validate/save new version |
| GET `/api/demo/scenarios` | synthetic catalog, no expected verdicts |
| POST `/api/sessions` | opaque ID + capability token |
| POST `/api/sessions/{id}/upload` | MIME/content/size/duration/path checks |
| POST `/api/sessions/{id}/start`, `/stop` | explicit lifecycle |
| POST `/api/sessions/{id}/frame` | bounded browser-camera JPEG |
| POST `/api/sessions/{id}/checkpoint`, `/review` | final check / acknowledgement |
| POST `/api/sessions/{id}/calibration` | brief four-point fallback |
| GET `/api/sessions/{id}`, `/events`, `/frames` | state / ledger / frame index |
| GET `/api/sessions/{id}/frames/{frame_id}` | authorized original/overlay |
| GET `/api/sessions/{id}/report?format=json\|html` | provenance export |
| DELETE `/api/sessions/{id}/upload` | remove stopped temporary upload |
| GET `/api/benchmarks/latest` | measured report or NOT_RUN |

Loopback bind, local Host checks, explicit browser origins and per-session header
tokens protect the local demo boundary. This is not an enterprise/public-hosting
authentication design. No cloud backend or keys are required.
