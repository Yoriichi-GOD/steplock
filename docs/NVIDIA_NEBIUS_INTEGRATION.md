# NVIDIA Nemotron evidence guidance

STEPLOCK's OpenCV 4 detector and deterministic recipe engine still own every
verdict. An optional NVIDIA Nemotron model on Nebius explains retained evidence
and proposes one bounded operator action. It cannot change events, recipe state,
checkpoints, source pixels or machine controls. There is no machine actuation.

## Run locally

Install/build using the existing `python scripts/dev.py --setup` path. Provide
backend environment variables from `.env.example`: `ENABLE_NEBIUS_AGENT=1`,
`NEBIUS_API_KEY`, the official `NEBIUS_BASE_URL`, and
`NEBIUS_NVIDIA_MODEL=nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`. The launcher does not
automatically load `.env`; set variables through the shell or a secret manager.
Never place the key in a `VITE_` variable or frontend file.

This machine has an ignored, Windows-encrypted credential and launcher under
`runtime/cloud_access/`. Its `with_cloud_access.py -- <command>` wrapper sets the
key in the child process only. A fresh clone needs its own authorized credential.
`python scripts/verify_nebius.py` makes a read-only authenticated catalog check;
it does not pretend to be an application inference check.

Run a generated example, wait until the replay finishes, scroll below the
evidence timeline, optionally select an event and click **Explain finding**.
The default selects a specific component/order finding before a generic missing
checkpoint event. Select a CORRECTED event to summarize its original/new link.
The original four-case workflow and eight generated example choices remain.

## Actual orchestration

The backend makes five independent, allowlisted reads: recipe, current snapshot,
selected event, retained frame metadata, and correction links. These are real
application reads with output hashes and timings, orchestrated by the backend.
This is **not a claim that the model autonomously selected native function calls**.
No source images, review notes, arbitrary filenames, URLs, raw user instructions
or credentials are included in the model packet. Only structured evidence goes
to Nebius; vision and retained pixels remain in the local process/filesystem.

The packet includes authoritative finding categories, required tag IDs, observed
frame tags, prerequisites and source hashes. A real provider request generates
JSON with one action, short prose, event citations and rule IDs. The backend
validates schema, same-session citations, recipe rules, action policy, known tag
numbers, prerequisite references and selected unsafe/contradictory wording.
Authoritative fields are constructed from the application, never accepted from
the model. Raw model content is retained only in local agent audit files.

**Prose is still generated, unverified text.** Citation and action validation do
not establish complete natural-language factual correctness. The UI separates
**Verified by STEPLOCK** facts from **Generated guidance — operator review
required**. Development runs found real semantic errors; these are retained in
the evaluation report. This layer is advisory, not safety certification.

## Bounds and failures

- Feature off by default; only two official Nebius endpoint hosts are accepted.
- Session capability token required for POST explain and GET run. No arbitrary
  prompt, tool, path or URL input. Request body capped at 2 KiB.
- Only finished/stopped evidence can be queried; running capture must complete
  first. Unusable/stopped capture restricts actions to recapture or human review.
- One active model request per server process, four requests per session, forty
  per server lifetime; each request is capped at 1,100 completion tokens and a
  20-second provider timeout. These are in-process demo bounds, not distributed
  public-service quotas. Restarting resets counts.
- Exactly one provider attempt. 401/403 never retry. 429/503 preserve Retry-After
  and defer to an explicit operator action; no automatic retry or credit burn.
- Timeout/network error, invalid JSON, truncated output, incorrect model identity,
  unsupported citations/actions/text all refuse guidance. Vision continues.
- Advice binds to session, recipe hash, source frame and engine revision. A changed
  frame, verdict, session or connection suppresses stale advice immediately.
  Historical run retrieval also rechecks the fingerprint.
- Audit files live separately under `runtime/sessions/<id>/agent_runs/`; the
  original append-only frame/event ledger is untouched. Local session persistence
  is not production archival storage.

## API

`GET /api/agent/health` reports configuration and the last runtime probe. Configured
does not mean inference has succeeded. No provider call occurs during polling.

`POST /api/sessions/{id}/agent/explain` accepts only purpose and optional event ID.
`GET /api/sessions/{id}/agent/runs/{run_id}` is scoped to the same session token.
Replies distinguish ADVISED, REJECTED, UNAVAILABLE, DEFERRED and STALE. Provider
receipts include actual served model, request/completion ID, round trip and token
usage when returned. Cost is not invented from token counts.

## Verified scope

Real NVIDIA calls have run through the production service and authenticated API,
not just the connection script. Existing generated benchmark reproduced 32/32
final outcomes and 0/24 false PASS on 864 frames. External IMPACT remains an
untagged compatibility/refusal test; no new physical tagged footage exists.
See [evaluation](PHYSICAL_AI_EVAL.md) for denominators and known failures.

AWS is authenticated for read-only preflight. **STEPLOCK is NOT_DEPLOYED**:
the user stopped before paid AWS deployment. REFLEX remains separate and healthy.
Local Docker CLI exists but its daemon is unavailable, so the Dockerfile is an
untested container candidate, not a verified image. Native local operation is
the tested delivery path.
