# Physical AI evaluation

All populations below are separate. No physical-camera accuracy, torque,
industrial safety or deployed STEPLOCK claim is supported.

## Existing vision reproduced

New run: `benchmarks/runs/20261029_182255_717473_test`, 32 generated test clips,
864 frames. STEPLOCK: 32/32 final statuses; scored events TP/FP/FN 60/0/0;
false PASS 0/24; corrections 4/4. Single frame: 24/32, false PASS 8/24. Temporal
stable-only: 28/32, false PASS 4/24. Detector p50/p95 19.36/27.21 ms offline.
Capture-to-visible latency remains NOT_MEASURED. The old result directories were
not edited. Shared rendering and tiny generated corpus limit generalization.

## Agent development runs — actual NVIDIA API calls

Model: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` served by Nebius Token Factory.
Protocol: `benchmarks/nebius_physical_ai/protocol_v1.json`. Four previously
generated vision-test clips: normal, wrong component, wrong order, correction.
They are now reused for agent development and are **not an independent held-out
agent evaluation**. No target truth file or expected human answer enters model
inputs; source and truth hashes are checked and preserved.

The template is valid by construction. The direct model sees event + snapshot;
the tools arm receives five backend evidence reads including recipe/frame and
correction context. This is a metadata intervention, not an architecture-only
comparison. Human narrative quality scores remain null.

Pilot `20261029_182024_295758`: template 4/4 structural acceptance, direct 2/4,
tools 4/4. Review then found one invented tag (14 instead of required 13) and an
order explanation omitting the actual prerequisite. A direct correction response
was truncated by the token cap. These outputs and review notes are retained.
Code changed during this pilot; it is not a frozen release snapshot.

Run `20261029_183507_089037`: source hashes stable throughout eight requests.
Template 4/4 structural acceptance; direct 1/4, with two rejected and one
truncated/unavailable; tools 4/4 under the then-current checks. Tools round-trip
p50/p95: 3,449/4,562 ms (n=4). Direct p50/p95: 3,630/4,334 ms (n=4, including
the failed/truncated response). These small percentiles are descriptive only.

Further review found wrong-component descriptions incorrectly saying “wrong
slot” in two tools outputs. Therefore **4/4 accepted does not mean 4/4 factually
correct**. The release adds authoritative fact display and a categorical
contradiction guard. Prior metrics describe prior checks; they are not silently
rewritten. Final API acceptance is recorded separately after that change.

No independent human scoring of explanation correctness or action usefulness was
provided. Automated acceptance checks citations, policy and selected contradictions;
it cannot prove arbitrary generated prose. No industrial effectiveness percentage
is claimed. Billed API cost is unknown; token usage is recorded where returned.

## Failure and regression tests

Tests cover: unknown/foreign session events and runs, consent/source provenance,
mutated hashes, arbitrary tool/prompt rejection, 2 KiB requests, 401/403/429/500/
503, timeout, model mismatch, output truncation, invalid JSON/citations/actions,
unsafe wording, invented tag IDs, missing prerequisites, categorical mismatch,
concurrent requests, quotas, source changes during inference and stale advice.
Mocks are explicitly unit-test transport fixtures, not live inference evidence.

Full suite before the last categorical test: 109 backend passes; targeted final
fact/policy checks: 31 passes; 22 frontend passes; production build passes.
Final full-suite totals are in the release receipt/checkpoint.

Actual headless Chromium browser acceptance passed at 1691×930, 1280×720 and
390×844 without horizontal document overflow. It invoked a real authenticated
model explanation, cleared it on session switch, hid stale PASS/advice after
connection loss, and started with backend requests refused: disabled run action,
PENDING and explicit offline banner. No uncaught browser errors. The in-app
browser tool timed out; a separate isolated local runner supplied this evidence.

## Real input and infrastructure

No new team-recorded tagged trials: NOT_PROVIDED. Existing IMPACT results remain
45 windows / 2,700 real frames, CALIBRATION_REQUIRED for untagged inputs. They do
not score native physical mistake recognition. The local licensed excerpt is not
sent to the model or bundled in the public demonstration.

Existing REFLEX AWS health: HTTP 200, OpenCV 5.0.0, original real-image build;
both stacks UPDATE_COMPLETE. No REFLEX source/resource mutation. STEPLOCK AWS:
NOT_DEPLOYED by user instruction; no paid resources created. Local Docker image
build: NOT_RUN because daemon was unavailable. Browser/model/native tests do not
prove Docker or hosted deployment.
