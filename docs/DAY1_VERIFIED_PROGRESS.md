# Day 1 verified progress — 30 October 2026

This closes the STEPLOCK work at the team-authorized Rule T4 checkpoint. The
project has prior public history; this checkpoint does not represent that older
work as newly created for a different event.

## Application and evidence

The implementation remains the tested NVIDIA/Nebius release. Its code checkpoint
is `39a25b027fded8db72e4af2a1a8d9cbd0a8617a5`; release documentation and assets are
at `2ef83d46f570767274f03262e637409ee7acdf99`. Existing source, UI and benchmark
results are preserved. See [release receipt](FINAL_RELEASE_RECEIPT.md) and
[evaluation with retained failures](PHYSICAL_AI_EVAL.md).

The recorded release passed 113 backend tests, 22 frontend tests and the frontend
production build. The generated vision regression retained 32/32 final outcomes
on 32 clips / 864 frames, event TP/FP/FN 60/0/0, false PASS 0/24 and correction
4/4. These are generated software-test populations, not physical accuracy.

Actual NVIDIA Nemotron-3-Nano-30B-A3B calls ran on Nebius Token Factory. The final
four development API calls completed; final-policy revalidation accepted 3/4
unchanged replies and refused one incorrect normal narrative. Human narrative
accuracy was not independently scored. The deterministic engine owns PASS/HOLD.

The fresh checkpoint rerun passed **113 backend tests in 67.27 seconds**, all
**22 frontend tests**, and the frontend production build in 6.02 seconds.
The existing httpx/Starlette deprecation warning and large-bundle advisory remain.
The command made zero cloud calls or deployments. See the
[checkpoint validation receipt](DAY1_VALIDATION.json). No fresh browser,
physical-camera or live-provider result is inferred from this regression rerun.

## Devpost attachment completed

`STEPLOCK_Devpost_Submission.zip` is 20,899,836 bytes (20.90 decimal MB), under the
35 MB upload limit. It contains source, the built frontend, setup instructions,
actual screenshots, historical/current reports, `START_HERE.md`, and a per-file
SHA-256 manifest. Its frozen source baseline is `2ef83d46`, before these checkpoint
documentation files. The attachment is not silently replaced by this checkpoint.

SHA-256:
`1e549023300b5d331c95e6ee98b5260e3827bf7079a898d5a4397f064e231f3f`.

Verification passed archive CRC and final byte/hash checks for 478 payload files,
460 tracked files against Git (307 using Git's Windows line-ending filters),
15 included built-frontend files and nine statically identified build asset
references. Credentials, runtime sessions, third-party dataset media and model
weights are excluded. These packaging checks are not a new application benchmark.
See [package verification receipt](DEVPOST_PACKAGE_VERIFICATION.json) and
[judge guide](SUBMISSION_START_HERE.md).

## Submission state and remaining work

During the last browser-editing session, project overview and the project-details
draft were saved, including the story, technologies, repository link, thumbnail
and two captioned application screenshots. Organizer technical answers were
entered but not yet confirmed saved. Computer Use then stopped because it could
not reliably verify the browser URL. This historical editing record is not a
current portal-state check or a final submission receipt.

The YouTube field was intentionally left to the submitter. Personal eligibility
answers were not invented. Tavily was explicitly deferred; no Tavily runtime call
or Tavily prize qualification is claimed. There is no verified final Devpost or
organizer SHA-submission receipt in this checkpoint.

Real tagged camera trials remain unavailable. Untagged IMPACT results remain
compatibility/refusal evidence, not native mistake accuracy. STEPLOCK AWS remains
undeployed; no paid deployment was authorized. The Docker candidate was not built
or run. No robot, machine actuation, torque validation or industrial safety
certification is claimed.

## History and worktree boundaries

Only the reviewed Rule T4 document and these submission/checkpoint records are
added. Existing untracked `docs/judging/` and `ui/` are preserved and excluded.
No application or historical result file is modified. The exact checkpoint
identity is the immutable annotated `day1-final` tag and its full target commit
SHA, recorded in the tag message and local organizer handoff receipt.
