# Devpost draft — operator review required

Status: not submitted. Deadline checked against official rules: 30 October 2026,
22:30 IST. Public YouTube URL and submission receipt are NOT_PROVIDED.

## Project name
STEPLOCK — Physical Procedure Assurance with a Nemotron Evidence Agent

## Tagline
See the wrong move. Keep the evidence. Prove the correction.

## Inspiration
Assembly mistakes are temporal: the right part in the final image does not prove
that prerequisites were followed. We wanted an inspection workflow that retains
the evidence behind a decision, and a language model that helps explain the
finding without becoming the authority that approves the work.

## What it does
STEPLOCK decodes ArUco markers, calibrates a four-anchor board, requires distinct
timed observations and checks a versioned four-part recipe. It records visible
placement, wrong component/zone, order and correction events. An explicit NVIDIA
Nemotron action reads five scoped evidence tools, produces advisory operator
guidance through Nebius Token Factory and links the original source events.
Unsafe, stale or unsupported outputs are refused. The deterministic engine owns
PASS/HOLD throughout.

## How we built it
Python/FastAPI, OpenCV contrib 4, Pydantic, React/TypeScript/Vite and NVIDIA's
`nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` served on Nebius Token Factory. Source
images and vision processing stay local; only structured evidence metadata is
sent to Nebius. Tool selection is backend-controlled and bounded, not claimed
as autonomous model-selected function calling. Credentials stay backend-only.
AWS CLI is authorized, but STEPLOCK was not deployed to AWS; the existing REFLEX
service was used as a read-only architecture reference and left unchanged.

## Physical AI scope
Track: Physical AI. This submission demonstrates actual perception and procedure
modules operating on visibly generated marker fixtures. No robot or tested
physical tagged camera workflow is claimed. Existing real IMPACT footage tests
the compatibility boundary: missing fixture anchors produce calibration refusal.
It does not establish native untagged assembly recognition. No torque, machinery
interlock or industrial safety certification.

## What was new for this hackathon
After the original STEPLOCK build, we added actual NVIDIA/Nebius runtime calls,
five scoped evidence reads, strict advisory/action/citation validation, source
revision binding, explicit provider-failure states, token/concurrency limits,
the UI guidance panel, live API/browser evaluation and retained model failures.
Meaningful commits and dated result directories are public; earlier benchmark
reports remain preserved. The project began within the contest submission period.

## Challenges and what we learned
Valid citations do not guarantee factual prose. Development calls invented a tag
number, mislabeled a part, omitted a prerequisite and confused a wrong component
with a wrong slot. We retained those outputs, added explicit authoritative facts
and rejection checks, and still label generated wording unverified. Reasoning
also exhausted a bounded output budget; a documented reasoning-off request
improved completion without silently raising the token cap. This is why model
guidance must remain outside the approval path.

## Validation
The original generated benchmark reproduced 32/32 final outcomes, 60/0/0 scored
event TP/FP/FN and 0/24 false PASS on 864 frames. Full regression totals and live
model-policy acceptance denominators are in `docs/FINAL_RELEASE_RECEIPT.md` and
`docs/PHYSICAL_AI_EVAL.md`; do not describe structural acceptance as human-rated
explanation accuracy. Actual provider model, timings, usage and failed outputs
are retained. Physical tagged trials and independent human narrative scoring
remain unavailable.

## NVIDIA / Nebius feedback draft
The authenticated model catalog and OpenAI-compatible API made it practical to
verify the exact served NVIDIA model and retain request/usage receipts. Bounded
output can be exhausted by reasoning before useful JSON is returned. The
documented reasoning-off control helped the short advisory workflow; callers
still need explicit truncation checks, failure handling and semantic validation.
Token Factory inference works independently of where the rest of the app runs.

## Links to enter
- Repository: https://github.com/Yoriichi-GOD/steplock
- Hosted STEPLOCK URL: NOT_DEPLOYED; reproducible local build supplied.
- Public YouTube demonstration: NOT_PROVIDED — upload and verify before entry.
- Devpost project/submission receipt: NOT_PROVIDED.
- Team names/roles: operator must confirm; do not infer.

This is copy for the user to review and submit, not a claim that Devpost fields
have been filled or the entry has been accepted.
