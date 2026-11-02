# Hosting STEPLOCK throughout the application cycle

Decision, 2 November 2026: **USD 0 hosting; website plus recorded walkthrough.**
The founder selected this option instead of a recurring live-server budget.
Render is excluded. No Supabase, paid container or new database is needed.

## Chosen architecture

- Cloudflare Pages Free hosts the existing REQUIEM story, browser-rendered 3D,
  bundled fonts/artwork, retained evidence and actual prototype recordings.
- GoDaddy remains registrar for the founder-owned `step-lock.xyz`. Nameservers
  change DNS hosting, not domain ownership. Domain renewal remains separate.
- No public inspection backend. `/demo` is explicitly recorded playback. The
  unchanged Python/OpenCV application is available in the repository locally.
- No public contact address or collection. Contact submission remains disabled;
  the static release does not make a configuration API request.

Build with `node scripts/build-static-site.mjs`. The opt-in build leaves the
normal live application behavior intact. See [deployment instructions](../infra/static-pages/README.md)
and the [release receipt](STATIC_RELEASE_20261102.md).

## Evidence boundaries

Recordings show the actual application inspecting generated marker fixtures:
normal sequence, wrong component and correction. They are historical software
examples, not physical footage, industrial accuracy, new benchmarks or current
workstation status. Preserve their watermarks and recording labels.

The first hosted check caught `/demo` redirecting to `/`; native extensionless
HTML route files fixed it. HTTPS checks then returned 200 for `/demo` and `/app`,
and 404 for `/api/health`. Browser checks establish emulated viewport behavior,
not physical-phone performance or universal browser compatibility.

## Migration and cost closure

The tested static preview is https://steplock-xt9.pages.dev. Custom-domain
activation and certificate checks are separate gates. The founder approved
replacing the two old apex forwarding addresses and www target, preserving
verification/DMARC records, and moving delegation to
`agustin.ns.cloudflare.com` and `novalee.ns.cloudflare.com`.

Keep the old AWS trial until custom-domain HTTPS and recording checks pass,
then retire only `steplock-service` and `steplock-foundation` through their
inventoried cleanup path. Do not touch other projects. Retain the expiry
control until deletion is verified. Its fallback expiry remains 9 November
2026 at 00:53:05 IST, with foundation cleanup 30 minutes later. Do not claim
zero ongoing AWS cost until chargeable resources are actually removed.

Free hosting has no running application process to sleep, but is not an uptime
guarantee. Keep the reproducible release and repository. No paid Functions,
Stream, R2 or additional subscription is authorized by this USD 0 decision.

## Sources

- [Static requests](https://developers.cloudflare.com/pages/functions/routing/)
- [Free limits](https://developers.cloudflare.com/pages/platform/limits/)
- [Custom domains](https://developers.cloudflare.com/pages/configuration/custom-domains/)
- [Native route matching](https://developers.cloudflare.com/pages/configuration/serving-pages/)
- [Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/)

The earlier paid-server candidates were not provisioned. This decision
supersedes that planning proposal.
