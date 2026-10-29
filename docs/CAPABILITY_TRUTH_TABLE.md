# Capability truth table

| Capability | Implemented | Evidence | Measured result | Limit |
|---|---|---|---|---|
| Pixel-based replay | Yes | vision/API tests, run_demo.py, saved observations | normal replay 30 analyzed frames → PASS | generated imagery |
| Live input | Yes | browser JPEG transport/API tests; camera adapter | transport verified with synthetic JPEGs | physical webcam NOT_TESTED |
| Board placement | Yes | homography/zone/perspective tests | movement changes actual decoded zone | normalized 2D tag anchors, no mm/3D |
| Wrong component/zone | Yes | engine/API tests, benchmark events | supported HOLD with frame IDs | label identity, not intrinsic part |
| Wrong order | Yes | full history vs midassembly tests | early cover HOLD; uncertain history abstains | staged recipe only |
| Correction | Yes | wrong type, order, wrong zone, OUTSIDE tests | retained fault + new CORRECTED; eventual checkpoint PASS | visibility/unique-tag assumptions |
| Benchmarks | Yes | benchmarks/runs/20261029_065156_263419_test | final test: 32/32 final, 60/60 events, 0/24 false PASS | synthetic only; related generator |
| Three baselines | Yes | same-frame evaluator | naive 8/24 false PASS; stable-only 4/24 | controlled ablation, no trained-model comparison |
| Degradation | Yes | benchmarks/stress | 14/14 designed safe gates | not physical accuracy |
| Browser Studio | Yes | frontend build, screenshots, browser checks | normal/fault/offline verified | some final browser follow-ups pending settings access |
| Recipe/evidence tools | Yes | API tests | version hash frozen; original hashes; JSON/HTML | local demo security boundary |
| Optional 3D illustration | Yes | UI_COORDINATION.md, 10 production-adapter tests | selection/orbit/explode; red/green from real snapshot; offline no green | illustration; startup-no-WebGL follow-up unverified |
| Public research data | Inventory only | ASSEMBLY101_INVENTORY.json | 328 CSVs / 3,964 rows | no justified mapping; score NOT_RUN |
| Authentic GitHub cadence | Yes through recorded checkpoints | DEVELOPMENT_LOG.md + git log | meaningful pushes <45 minutes during active build | latest push receipt verified separately |
| Real staged dataset | No | fixtures/recorded/manifest.csv | NOT_PROVIDED | human capture/consent needed |
| Industrial safety | No claim | TECHNICAL_LIMITATIONS.md | NOT_VALIDATED | advisory demonstration only |
