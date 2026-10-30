# STEPLOCK - Devpost judge attachment

Physical Procedure Assurance with NVIDIA Nemotron on Nebius Token Factory

Public repository: https://github.com/Yoriichi-GOD/steplock
Release source: 2ef83d46f570767274f03262e637409ee7acdf99
Verified implementation: 39a25b027fded8db72e4af2a1a8d9cbd0a8617a5
License: MIT (see LICENSE).

## Run the application

1. Extract this ZIP into a normal local folder. Open a terminal in the extracted
   folder containing README.md and scripts/.
2. Install Python 3.12+ and current Node LTS. The verified native environment used
   Windows, Python 3.14.6, Node 24.18.0 and OpenCV contrib 4.14. Other operating
   systems and the Docker candidate have not been validated.
3. Run: `python scripts/dev.py --setup`
4. Open http://127.0.0.1:62327/ and keep the server terminal open.
   Initial dependency installation needs internet. Subsequent local launch is
   `python scripts/dev.py`. The built frontend is also included in frontend/dist/.
5. Choose Run example > Normal to inspect a generated-marker example reaching
   engine-owned PASS. Choose Wrong Component / Wrong Order for a finding and
   Correction to follow the original finding to its correction evidence.
   Source frames are visibly labeled generated test fixtures.

No camera starts automatically. If the default port belongs to an unrelated
application, use the launcher's documented --port override. Do not stop unrelated
services. Full setup and example instructions are in README.md.

## Enable actual NVIDIA inference

The vision/procedure examples run without a cloud key. The optional Explain
finding action requires the judge's own authorized Nebius Token Factory key.
Set the backend variables ENABLE_NEBIUS_AGENT=1, NEBIUS_API_KEY, NEBIUS_BASE_URL
and NEBIUS_NVIDIA_MODEL as documented in docs/NVIDIA_NEBIUS_INTEGRATION.md and
.env.example, then start the backend. The launcher does not automatically load
a .env file. Never expose the key through a VITE_ variable or frontend file.

The verified model is nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B. Five real evidence
reads are controlled by the backend, not autonomously selected by the model.
Only structured metadata is sent; source images stay local. Generated wording
is advisory, fallible and subject to refusal. The deterministic procedure engine
owns PASS/HOLD. No credential or encrypted credential is included in this ZIP.

## Evidence to review

- docs/FINAL_RELEASE_RECEIPT.md: tested release and exact scope.
- docs/PHYSICAL_AI_EVAL.md: live API results, retained failures and denominators.
- docs/NVIDIA_NEBIUS_INTEGRATION.md: architecture, controls and setup.
- docs/PHYSICAL_AI_DEMO_RUNBOOK.md: two-minute demonstration walkthrough.
- screenshots/nebius/: actual application screenshots.
- benchmarks/: preserved historical and current evaluation outputs.
- SUBMISSION_MANIFEST.json: SHA-256 for every payload file, including this guide.
  The manifest excludes itself; the companion .sha256 file hashes the entire ZIP.

## What has been proved, and what remains open

The recorded release checks passed 113 backend tests, 22 frontend tests and the
production frontend build. The generated vision regression scored 32/32 final
outcomes on 32 clips / 864 frames, false PASS 0/24 and correction detection 4/4.
These are small, shared-renderer software tests, not industrial physical accuracy.

Four final development API calls completed. The final policy accepted 3/4 saved
replies and refused one incorrect narrative in post-hoc revalidation. Human-rated
explanation accuracy was not independently scored. The four API round trips had
p50 1.686 s / p95 2.049 s; camera-to-visible-alert latency remains unmeasured.

Real tagged camera trials were not supplied. The separate IMPACT compatibility
test processed 2,700 untagged real frames and required calibration; native mistake
accuracy was not scorable. External dataset footage and pretrained third-party
weights are excluded from this attachment. STEPLOCK has no claimed hosted service,
paid AWS deployment, tested robot, machine actuation or safety certification.

The YouTube demonstration is supplied separately by the submitter. This attachment
does not assert that the Devpost entry has been finalized. Packaging performs no
model calls, deployment or new application benchmark; the release receipts above
record the tests previously run. Existing source and historical reports are intact.
