# Static release — 2 November 2026

Status: **CUSTOM_DOMAINS_HTTP_VERIFIED / AUTOMATIC_CONTACT_VERIFIED_ON_PREVIEW / AWS_RETAINED**.

Update at 14:45 UTC: Cloudflare reports apex and www Active / SSL enabled. Both
hostnames now pass normal system-DNS HTTPS checks for the static routes, three
recordings, hashes and captions. New receipts are under
`docs/verification/contact-20261102/`. The earlier failures below are historical.

The founder subsequently authorized a public contact alias and automatic form
delivery. `founder@step-lock.xyz` appears in the invitation and footer. The
FormSubmit form was activated by the founder; an actual browser submission was
accepted and ImprovMX reports forwarding to Gmail accepted in two seconds.
This supersedes the earlier unconfigured-contact state below. See
[contact operations](CONTACT_AND_INQUIRIES.md) for privacy, failure behavior and
verification limits. No private forwarding destination is published.

The founder selected USD 0 hosting with a recorded walkthrough. The public
preview is [STEPLOCK](https://steplock-xt9.pages.dev) and its
[recorded walkthrough](https://steplock-xt9.pages.dev/demo).

## Verified implementation

- Opt-in `VITE_PUBLIC_PRESENTATION=recorded` selects recorded `/demo`, a local
  workbench explanation at `/app`, truthful navigation and no contact API call.
- Default builds retain the original live inspection application.
- Both TypeScript/Vite production builds pass. All 26 existing frontend
  regression checks pass, including stale PASS and unavailable evidence checks.
- Three videos fully decode: normal 158 frames, wrong component 157 frames,
  correction 177 frames, all at 15 fps. Browser native playback reached the
  end of all three recordings without a media error.
- Actual live-engine captures showed normal PASS (30 analyzed frames),
  wrong-component HOLD (30), and corrected PASS (42). This is generated fixture
  demonstration evidence, not a new physical or benchmark evaluation.
- Hosted walkthrough requests stayed on the site origin with no `/api/` calls.
  The landing story rendered its 3D canvas and kept contact unconfigured.
- Hosted walkthrough has no horizontal overflow at 1280, 390 and 320 CSS pixels.
  A first attempted phone override stayed at 1280; it was rejected as phone
  evidence and replaced with a verified tab-scoped viewport override.
- HTTPS `/demo` and `/app` returned 200; `/api/health` returned 404 with no
  backend. Content-type, frame, camera/microphone and CSP headers are present.

## Failures retained and corrected

The first hosted `/demo` returned 308 to `/` because proxying to `index.html`
triggered the host's canonical index redirect. Native `demo.html` and `app.html`
route files fixed this. The original backend and results were not modified.

Python urllib was rejected with Cloudflare Browser Integrity Check error 1010.
The installed curl client and the browser passed with their ordinary identities;
no protection or TLS validation was disabled. The host ignores byte-range
requests and returns each complete video (under 280 KB). Full files and hashes
matched, and native playback completed. Partial network seeking is not claimed.

Playwright's minimal FFmpeg lacked the rawvideo input format; a pinned
`imageio-ffmpeg==0.6.0` PyPI tool encoded the actual captures instead. The original
failed attempt is not counted as a completed recording.

Browser control was disabled during preparation and later restored by the
founder. Automatic approval review blocked deleting an old apex A record;
the founder then explicitly approved the exact DNS replacements and confirmed
that the existing GoDaddy ownership should be retained.

## DNS and outstanding gates

GoDaddy saved custom nameservers `agustin.ns.cloudflare.com` and
`novalee.ns.cloudflare.com`. The public registry independently reports those
nameservers and `delegationSigned: false`; no DNSSEC setting was disabled.
The Cloudflare zone preserves `_dmarc`, `_domainconnect` and the ACM verification
CNAME. Only apex web-forwarding records and www target were replaced.

Cloudflare domain activation, apex Pages binding, www activation and both HTTPS
hostnames still require final confirmation. Public resolver caches may retain
the earlier GoDaddy delegation. The preview is independently available.

Follow-up diagnosis at 13:25–13:29 UTC (18:55–18:59 IST): a normal HTTPS GET
to the root returned 301 to `https://www.step-lock.xyz`, which returned 200.
Browser rendering confirmed that this is still the original AWS application,
not the static release. The GoDaddy forwarding service returns 405 for HEAD;
that response alone must not be interpreted as a failed homepage GET.

The registry RDAP database records the new nameservers and a last-changed time
of 13:11:19 UTC, but direct DNS queries to two IANA-listed `.xyz` servers
(`x.nic.xyz` and `y.nic.xyz`) still returned `ns29.domaincontrol.com` and
`ns30.domaincontrol.com`. The latter query was explicitly non-recursive. This
identifies incomplete parent-zone publication, not merely a browser cache.
Local direct TCP DNS could not connect, so the independent queries used the
public diagnostic interface recommended by Cloudflare. No security setting,
domain lock or DNSSEC protection was changed during this follow-up.

A fresh Cloudflare activation check was requested. Its dashboard still reports
pending nameserver publication, and attempting the root binding still leads to
the DNS-management prerequisite. Do not repeatedly re-save nameservers or claim
the migration complete on the basis of the registrar panel or RDAP alone.
Cloudflare's [pending-zone troubleshooting procedure](https://developers.cloudflare.com/dns/zone-setups/troubleshooting/pending-nameservers/)
identifies the parent DNS response as the decisive check.

The original AWS service and foundation remain running while those gates are
open. The seven-day fallback cleanup schedule is unchanged. No new paid service
was created. A USD 0 static replacement is not evidence that old AWS charges
have stopped; scoped deletion must be verified before making that claim.

## Provenance and limitations

Recordings and their per-frame/video hashes are in
`frontend/public/assets/walkthrough/provenance.json`. They were captured from the
actual digest-pinned application built from `c8577af`; generated fixture
watermarks remain visible. The final correction redraw frame was omitted,
explicitly recorded in the ledger. A three-second final frame hold is editorial
reading time, not measured engine latency.

No new users, customers, physical accuracy, industrial deployments or savings are
claimed. No email address is published. Engine code, historical benchmark
reports and the immutable `day1-final` tag remain unchanged. Unrelated untracked
`docs/judging/` work is excluded from this release.

Rebuild/publish steps: [static hosting guide](../infra/static-pages/README.md).
