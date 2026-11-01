# Public demonstration contract

The public demo processes only the four checked-in generated examples: Normal,
Wrong Component, Wrong Order and Correction. Catalog hashes and actual media
bytes are checked before exposing an available scenario. The same OpenCV detector,
procedure engine, checkpoint and evidence store process the real fixture pixels.
Ground truth is not read. The React UI does not generate expected verdicts.

## API

- `GET /api/public/config`: public mode, authorized contact configuration and owner
  access availability. It never returns an owner key or provider credential.
- `GET /api/public/demo/scenarios`: four allowlisted catalog records and actual
  file availability; no local paths.
- `POST /api/public/demo/sessions`: `{ "scenario_id": "normal" }` creates and
  immediately runs an example. Returns a random session ID and bearer capability.
- `GET /api/public/demo/sessions/{id}`: actual snapshot; bearer capability required.
- `GET /api/public/demo/sessions/{id}/frames/{frame}?annotated=true|false`: retained
  original/overlay; same-session capability required. No credentials in URLs.
- `DELETE /api/public/demo/sessions/{id}`: stop and remove this temporary session.

Tokens remain in the demo page's memory, not URLs, logs or persisted local storage.
A refresh is deliberately neutral and does not resume an old result. Unknown,
expired and wrong-capability requests return the same generic 404. Network loss
suppresses PASS and confirmed step styling. Evidence errors are explicit.

## Boundaries

Set `STEPLOCK_PUBLIC_MODE=1` for internet exposure. All existing privileged API
routes and API documentation then require a signed, expiring HttpOnly owner cookie.
The full `/app` route provides the owner gate; it does not grant API access itself.
Owner login is unavailable until a 32-character-or-longer backend owner key is
configured. The public image sets public mode and disables the Nebius agent.
The public gateway never invokes the agent, regardless of provider configuration.

Anonymous camera ingestion, arbitrary uploads, recipe editing, the original
session API, benchmark internals and model calls are denied on the server.
JSON bodies in public/owner POST routes are capped at 2 KiB, including chunked
requests. The public mode also sends a camera/microphone-denial permission policy.
Public contact is intentionally not configured by the founder; no email address
or fake submission confirmation is published.

## Bounds, persistence and deployment limits

- One public inference at a time; a competing request receives explicit 409.
- At most 12 retained sessions; ten-minute lifetime; 25-second processing watchdog.
- Cleanup runs every five seconds and on access. Stop must finish before deletion.
- Only owned public-session directories with validated random names are removed.
  Stale orphan directories after a restart are removed after the same retention.
- SQLite transactions retain start counters across process restarts: 16 attempts
  per peer per hour, 64 globally; owner login 5 per peer / 20 globally per 15 minutes.
  Peer keys use a persistent HMAC secret; raw IP addresses are not stored.
- Only narrowly trusted proxies may set the interpreted client IP. Raw caller
  `X-Forwarded-For` is not parsed by the application.
- Exactly one application worker and one deployment task. Sessions are process
  local, and local SQLite is not a distributed quota or global concurrency service.
  Deployment/restart clears live session state. Persistent volumes can preserve
  limits; replacing ephemeral tasks can reset them. The hosted plan must add an
  AWS WAF rate rule on the public session-creation path before arbitrary exposure.

This is a bounded demonstrator, not a multi-tenant production product or a security
certification. Future scale-out requires shared session ownership, distributed
admission controls and an independently reviewed storage/retention design.

Hostnames are explicitly configured. In public mode only fixed, read-only
`GET /api/health` bypasses hostname matching to support ALB target-IP health probes;
it exposes no session IDs or private state. All other routes retain host validation.

## Local production preview

Build `npm --prefix frontend run build`, then launch the existing backend with
`STEPLOCK_PUBLIC_MODE=1`. Open `/demo`. The private/local application is still at
`/app` when public mode is disabled. No cloud credential or camera is needed.

Actual HTTP smoke: `python scripts/smoke_public_demo.py --origin http://127.0.0.1:62401`.
Browser acceptance: `node scripts/prelaunch_browser_qa.cjs`; its isolated Playwright
installation is under ignored `runtime/browser_qa/`. No personal browser profile
or authenticated external website is accessed.
