# Native release receipt — STEPLOCK NVIDIA / Nebius

**Native build and tests verified. Not submitted; STEPLOCK AWS not deployed.**

- Verified implementation commit: `39a25b027fded8db72e4af2a1a8d9cbd0a8617a5`; repository https://github.com/Yoriichi-GOD/steplock . Release docs/assets are committed after this code checkpoint.
- Backend:113passed/0failed in62.06s; frontend:22passed/0failed; production build:PASS. Existing deprecation and large-bundle advisories remain.
- Actual model: `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` served on Nebius Token Factory, strict served-ID check. Five backend-controlled metadata tools per request; not autonomous model-selected function calls.
- Final four-case API HTTP completion:4/4; final-policy revalidation on unchanged outputs:3/4accepted,1normal-case narrative refused. Human narrative accuracy:NOT_SCORED. Failure outputs remain public alongside fixes.
- Final four API round trips:p50=1685.55ms,p95=2049.21ms,n=4. Reported total6788tokens; billed cost:NOT_MEASURED. Neither this latency nor OpenCV latency is browser capture-to-alert.
- Vision regression:32generated clips/864frames,32/32final,TP/FP/FN60/0/0,false PASS0/24,correction4/4. Run `20261029_182255_717473_test`; core engine/vision/calibration/service/evidence-store files unchanged from8931a72.
- Real physical tagged trials:NOT_PROVIDED. Existing IMPACT2,700-frame untagged compatibility/refusal results preserved; native mistake F1 remains NOT_SCORABLE. IndustReal native recognizer remains OS-blocked.
- Browser:actual Chromium1691x930,1280x720,390x844 passed; no horizontal document overflow, no uncaught errors; real model invocation, session-switch clearing, connection-loss stale PASS/advice suppression. Additional static frontend with no backend API passed1280x720startup.
- Silent recording:`runtime/demo_nebius/steplock-nebius-2min.webm`,1920x1080,25FPS,3000frames,exactly120.0s. Raw120.88s retained;0.88s leading edge trimmed; no internal cuts. Actual synthetic module operation and two live model calls, both accepted under final policy when revalidated. No microphone/camera or unlicensed dataset pixels.
- Actual screenshots:`screenshots/nebius/`; hash provenance included. Script:`docs/PHYSICAL_AI_DEMO_RUNBOOK.md`.
- AWS CLI:`reflex-aws` authenticated; original REFLEX stacks UPDATE_COMPLETE and health200/OpenCV5 original build at read-only preflight. No source/resource updates.
- STEPLOCK AWS URL:NOT_DEPLOYED, paid deployment explicitly outside authorization. Local Docker build:NOT_RUN, daemon pipe unavailable. Dockerfile is a candidate only.
- YouTube:NOT_UPLOADED. Devpost:NOT_SUBMITTED. Draft:`docs/DEVPOST_SUBMISSION_COPY.md`. Cutoff30October2026,22:30IST, checked against official rules.
- Credentials:backend-only, Windows-encrypted under ignored runtime on this machine; no secrets bundled/committed, no new paid resources. No automatic restart or schedule.

The local provider integration is real; fallible generated wording remains separate from the authoritative facts and verdict. All success fractions have their populations and limits. The operator still needs narration/public upload and final submission review.
