# Contact and inquiry delivery

Public address: **founder@step-lock.xyz**. The founder explicitly authorized this
alias and automatic form delivery on 2 November 2026. Keep its forwarding
destination private; it belongs only in ImprovMX, never in frontend code.

## Where submissions go

1. A visitor selects Request early access, Share an idea or Discuss a pilot,
   completes the fields and presses the send button.
2. The browser posts the name, email, organization/role, message and purpose to
   FormSubmit over HTTPS. No email application is needed.
3. FormSubmit emails `founder@step-lock.xyz`. ImprovMX forwards it to the existing
   destination inbox configured by the founder.
4. Find messages with subjects such as **STEPLOCK — Request early access** or
   **STEPLOCK — Discuss a pilot**. Check Spam as well as Inbox. An optional Gmail
   filter `from:submissions@formsubmit.co subject:STEPLOCK` can apply a STEPLOCK
   label; no inbox filter was created automatically.

The `email` field lets FormSubmit set Reply-To to the visitor. Review the actual
recipient before replying. Receiving/forwarding does not configure outbound
sending as `founder@step-lock.xyz`; replies otherwise use the sending account's
normal address. No outbound SMTP credentials or paid email plan were created.

There is no STEPLOCK submissions database, CRM or admin dashboard. The email
copies are the working record. FormSubmit documents a 30-day submission archive
and a separate authenticated archive API; no archive credential is bundled or
archive integration claimed. Do not treat ImprovMX transport logs as a permanent
customer-record database.

## DNS and setup

Cloudflare manages DNS; GoDaddy remains the registrar. Existing DMARC,
domain-connect and ACM verification records were preserved.

| Record | Name | Value | Priority |
| --- | --- | --- | --- |
| MX | @ | mx1.improvmx.com | 10 |
| MX | @ | mx2.improvmx.com | 20 |
| TXT | @ | v=spf1 include:spf.improvmx.com ~all | — |

ImprovMX shows all three records valid. The founder activated FormSubmit after
receiving its verification email. If changing the receiving address or adding a
new form origin, verify activation and actual delivery again.

## Failure and privacy behavior

The interface says Request accepted only after an explicit provider success
response. This confirms acceptance for delivery, not that a person read it or
that it landed in Inbox rather than Spam. In-flight requests disable duplicate
clicks. A timeout, malformed/negative response or HTTP failure retains the fields
and shows direct email as a fallback. A retry may duplicate a request accepted
before a connection failure. Required fields, length limits and a hidden
honeypot are present; the provider's normal anti-spam behavior is retained. No
CAPTCHA protection was explicitly disabled. Spam elimination is not claimed.

The form discloses third-party processing, FormSubmit's 30-day retention and the
email copy before sending. It asks visitors not to include sensitive information.
No attachments, auto-response emails, private destination or credential are
included. Only the FormSubmit origin was added to CSP connect-src; other site
restrictions remain. Page loads do not submit form fields.

## Verified on 2 November 2026

- ImprovMX alias test entered queue at 19:25:54 IST and Gmail accepted it at
  19:25:57 IST (3 seconds).
- The first browser form test returned `success:false` / activation required.
  The UI retained its fields and displayed an unconfirmed request. Its activation
  email was forwarded in 5 seconds. The founder then activated the form.
- Post-activation browser submission returned HTTP 200 and `success:true`.
  ImprovMX shows **STEPLOCK — Request early access** queued at 19:38:53 IST and
  delivered at 19:38:55 IST (2 seconds), with Gmail's `2.0.0 OK` response.
  These are mail-forwarding queue durations, not overall web-request latency.
- Static and default production builds passed; all 28 frontend regression tests
  passed, including explicit success/failure parsing, payload fields, empty and
  honeypot rejection, stale PASS and original unconfigured-contact behavior.
- The 102-file public package contains only the authorized email address. Its
  ZIP SHA-256 is `0974c9417ca2a65afbbb419d74d43a579c08e524cbd1e363aa4b6e2f5ef1446f`.
- Normal DNS / validated HTTPS checks now pass for apex and www. Earlier public
  DNS diagnostic checks are labeled separately; no TLS protection was bypassed.
- Both production hostnames serve the tested contact JavaScript and styles
  byte-for-byte. HTTP OPTIONS checks allow the form's POST and Content-Type for
  both origins. These are network checks, not a replacement for a phone render.
- The production-domain endpoint initially requested its own activation. The
  founder activated `https://step-lock.xyz/`; a subsequent endpoint request with
  production Origin/Referer returned HTTP 200 / `success:true`. The founder
  confirmed receiving the complete **STEPLOCK — Discuss a pilot** test containing
  **CUSTOM DOMAIN TEST 2026-11-02**. This is recipient-confirmed production
  delivery, separate from the earlier preview browser submission.
- The `www.step-lock.xyz` origin was separately tested and requested its own
  activation. The founder activated it; the subsequent www-origin request
  returned HTTP 200 / `success:true`. Do not assume the provider's activation is
  shared across hostnames. The root test body is recipient-confirmed; the www
  test is provider-accepted, not independently inbox-inspected.

Limits: forwarding acceptance does not prove inbox placement or reading. The
Reply-To was not independently inspected; ImprovMX's message-download attempt
timed out, and the connected Gmail account returned no matching test. The founder
confirmed the complete production test in the actual forwarding inbox.
The final phone-layout pass and custom-domain browser render were blocked when
local browser access was disabled. Existing earlier responsive receipts do not
prove the new form's phone layout. AWS retirement remains a separate gate.

## Rebuild and publish

`node scripts/build-static-site.mjs` opts into the public alias and FormSubmit.
Default live builds retain their existing opt-in configuration. To customize a
future release, set `VITE_PUBLIC_CONTACT_EMAIL` to an authorized public alias.
The direct-upload Pages project still needs an actual upload after each build;
a Git push alone does not deploy it. Preserve the private runtime logs outside
Git; they contain the forwarding destination and download tokens.

Sources: [ImprovMX Cloudflare setup](https://improvmx.com/guides/cloudflare/),
[forwarding versus sending](https://improvmx.com/guides/forwarding-vs-smtp/),
[FormSubmit documentation](https://formsubmit.co/documentation),
[activation help](https://formsubmit.co/help),
[FormSubmit privacy](https://formsubmit.co/privacy.pdf).
