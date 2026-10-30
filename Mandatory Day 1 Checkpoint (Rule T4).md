# Mandatory Day 1 Checkpoint (Rule T4)

> At the official Day 1 checkpoint, commit and push all verified progress, create
> and push the Git tag `day1-final` on that exact commit, record its full SHA for
> submission to the organizers, and continue Day 2 development without altering
> or rewriting the Day 1 history.

Rule text supplied by the team. On 30 October 2026 the submitter explicitly
confirmed: **"This is the checkpoint—create the tag now."** This records that
instruction; no independent organizer schedule or reuse-eligibility ruling is
asserted. Existing STEPLOCK history remains visible, including the prior baseline
`2ef83d46f570767274f03262e637409ee7acdf99`.

## Checkpoint contents

- The existing application, NVIDIA/Nebius integration, historical benchmarks,
  retained model failures and release evidence remain preserved.
- [Verified progress and open items](docs/DAY1_VERIFIED_PROGRESS.md).
- [Verified Devpost package receipt](docs/DEVPOST_PACKAGE_VERIFICATION.json).
- [Judge attachment guide](docs/SUBMISSION_START_HERE.md).

All changes in this checkpoint are documentation and artifact receipts. No new
physical trial, model call, Tavily integration or cloud deployment is claimed.
Untracked `docs/judging/` and `ui/` are pre-existing work outside this verified
checkpoint and must not be swept into a blanket `git add .`.

## Execute the freeze once

Run from the repository root in PowerShell, after the documented checks pass:

```powershell
git status --short
# Stage only the reviewed checkpoint files; preserve unrelated work.
git diff --cached --check
git commit -m "docs: freeze verified Day 1 progress and Rule T4 checkpoint"
git push origin main
$checkpointSha = git rev-parse HEAD
git tag -a day1-final $checkpointSha -m "Rule T4 Day 1 checkpoint: $checkpointSha"
git push origin refs/tags/day1-final
git rev-parse 'day1-final^{commit}'
git ls-remote origin refs/heads/main refs/tags/day1-final 'refs/tags/day1-final^{}'
```

Check for an existing local and remote `day1-final` **before** creating it. If it
already exists, preserve it and verify its target; do not delete, move or force
push it. If the branch or reviewed files change during verification, review the
new state before choosing the frozen commit.

The organizer submission value is the full **40-character commit SHA** resolved
by `git rev-parse 'day1-final^{commit}'`, not the annotated tag object's SHA.
The annotated tag message records this full commit SHA. A separate local
`day1-checkpoint-receipt.json` records the verified remote references for copying
to the organizers. It is generated after the commit, so the frozen document does
not attempt to contain its own commit hash.

## Continue Day 2 without rewriting Day 1

Create ordinary new commits after the frozen commit, on the current branch or
an explicitly chosen Day 2 branch. Keep `day1-final` fixed. Do not amend, rebase,
squash, reset away, backdate, force push or retag the Day 1 history. Keep Day 2
measurements separate and preserve all Day 1 evidence and failed runs.

The checkpoint is closed only when the local tag target, remote peeled tag target
and submitted full commit SHA all identify the same reviewed commit. Organizer
receipt is a separate human submission step; creating a Git tag does not prove
the SHA was submitted to the organizers.
