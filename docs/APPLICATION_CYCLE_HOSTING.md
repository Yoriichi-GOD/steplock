# Hosting STEPLOCK throughout the application cycle

Decision candidate, 2 November 2026. **Not deployed.** The existing seven-day AWS
trial remains unchanged while the recurring budget is selected. Render is excluded.

## What the website actually needs

The pre-launch frontend builds into static HTML, JavaScript, fonts and artwork.
The 3D scene runs in the visitor's browser. Its retained inspection record is a
bundled, explicitly labeled software-test capture. Neither needs a running
Python service. The live `/demo` inspection does need Python/OpenCV, temporary
evidence storage and its process-local session manager.

Verified locally in this preparation:

- TypeScript/Vite production build passed into isolated ignored runtime storage.
- A browser loaded the story and 3D canvas with **no inspection backend**.
- The retained technical record opened with its event, source time and hashes.
- Contact remained truthfully unconfigured; no personal data was submitted.
- This does not establish that a live inspection works without a backend.

No application code, domain records, cloud service or paid subscription was
changed for this preparation. Runtime proof is under `runtime/application-cycle/`.

## Recommended split

| Part | Candidate | Cost basis | Why |
|---|---|---|---|
| Pre-launch website | Cloudflare Pages, static assets only | Free plan within published limits | No application process to sleep; website independent of the demo server |
| Actual inspection backend | One Lightsail Linux instance | 1 GB IPv4 bundle: USD 7/month base; 2 GB: USD 12/month base | Running server, bundled disk and transfer allowance, predictable compute ceiling |
| Database service | None for this stage | No new service | Current demo already has local SQLite and bounded temporary files |

These are base prices, not an unlimited all-in bill. Tax, transfer beyond the
bundle, optional snapshots and other add-ons can cost extra. A 1 GB instance is
a candidate, not a verified capacity result; test the unchanged image at that
limit before selecting it. Do not claim that a free service guarantees perpetual
availability or that an always-running server cannot fail or restart.

Vercel can serve the frontend too. Its Hobby plan restricts use to personal,
non-commercial projects, so review the actual account/plan before using it for
the company website. Supabase is unnecessary for the current frontend and is
not a direct host for this unchanged OpenCV process. Supabase Free projects may
pause after a low-activity seven-day period, conflicting with the stated need.
Railway is another viable container platform, but its USD 5 Hobby amount is a
minimum with usage charges above included credits, not a fixed USD 5 ceiling.

## Migration boundaries before any paid cutover

1. Confirm recurring monthly budget and account access. Preserve the working
   trial and immutable history until the replacement is verified.
2. Publish the static site to a preview URL. For a Cloudflare Pages apex domain,
   migrate authoritative DNS to its free zone while retaining GoDaddy as
   registrar. Copy and verify all existing records, including certificate and
   mail-related records; add project-recommended values, never guessed addresses.
3. Run the existing digest-pinned application as one worker on the selected
   server, with a persistent runtime directory, automatic restart, bounded logs,
   HTTPS and health checks. Keep the internal application port private.
4. Replace the current gateway with verified equivalent body/rate limits and
   exact proxy trust before public exposure. Preserve the private API, camera,
   upload and model-call restrictions. Do not silently discard the current WAF
   boundary just to meet the server price.
5. Configure only the exact website origins and backend hostname. Verify browser
   requests, bearer isolation, all four actual engine examples, correction,
   source loss, restart behavior and desktop/phone views.
6. Simulate backend loss and prove that the website and retained evidence remain
   accessible, while the live demo stays honest about being unavailable.
7. Confirm certificate issuance, root and www behavior, cost settings and restart
   monitoring. Only then change production DNS and retire the old chargeable
   infrastructure through its inventoried cleanup path.

The current service is still scheduled to expire on **9 November 2026 at
00:53:05 IST**. This document does not extend it or authorize a new recurring
payment. A static-only website could continue without a running inspection
server, but its live-demo promise must then be changed explicitly, with consent;
a recorded example must never masquerade as a fresh engine result.

## Sources checked

- [Cloudflare Pages static requests](https://developers.cloudflare.com/pages/functions/routing/)
- [Cloudflare Pages limits](https://developers.cloudflare.com/pages/platform/limits/)
- [Cloudflare apex/custom domains](https://developers.cloudflare.com/pages/configuration/custom-domains/)
- [AWS Lightsail instance bundles](https://docs.aws.amazon.com/lightsail/latest/userguide/amazon-lightsail-bundles.html)
- [Vercel Hobby eligibility](https://vercel.com/docs/plans/hobby)
- [Supabase project pausing](https://supabase.com/docs/guides/platform/free-project-pausing)
- [Railway pricing](https://railway.com/pricing)
