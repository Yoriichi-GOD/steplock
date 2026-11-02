# Static application-cycle release

This is a separate, opt-in presentation build. It hosts the REQUIEM website and
actual screen recordings of the prototype on generated marker fixtures. No
Python/OpenCV process, database, Pages Functions, model API or anonymous data
collection is deployed. Normal `npm --prefix frontend run build` retains the live
inspection application and its original backend requirements.

## Rebuild

From the repository root, after `npm --prefix frontend ci`:

```text
node scripts/build-static-site.mjs
```

Upload **the contents of `frontend/static-dist`**, or a ZIP containing those files
at its root, to the Cloudflare Pages project `steplock` (Direct Upload). The
verified project hostname is `steplock-xt9.pages.dev`. This is not a Git-linked
project; a repository push alone does not deploy it. Direct Upload cannot be
converted to Git integration in-place; create another project if that is wanted.

The script enables `VITE_PUBLIC_PRESENTATION=recorded`, clears the API origin,
checks the 25 MiB/file and 20,000-file Free plan limits, and copies the static
headers and routes. It creates `demo.html` and `app.html` as native extensionless
Pages routes. Do not proxy `/demo` to `/index.html`: the host's canonical index
redirect was observed sending that route back to `/` in the first deployment.
The explicit `404.html` ensures `/api/*` and unknown routes do not return a
pretend API or the application shell.

## Recordings

`frontend/public/assets/walkthrough/provenance.json` records capture times,
application commit/image digest, individual capture hashes and final video
hashes. The JPEG posters are authentic source screenshots. The videos are silent
VP9 WebM at 15 fps with English caption tracks, generated from browser CDP
screencasts while the actual engine ran. A three-second final frame hold permits
reading; the correction clip omits one final loading/redraw frame, as recorded
in provenance. Original captures remain in ignored runtime storage.

`encode_walkthrough.py` reproduces the encoding from those private captures.
It requires OpenCV and a full FFmpeg encoder; Playwright's bundled FFmpeg is a
minimal build without the rawvideo input format. A pinned `imageio-ffmpeg==0.6.0`
wheel from PyPI supplied the encoder in this run; it is a build tool, not a
frontend or server dependency.

Recordings are **historical generated software tests**, not factory footage,
new visitor inspections, benchmarks or industrial accuracy. The original engine
and all historical evaluation reports remain unchanged.

## Release gates

- Build the static release and the default live application.
- Run existing frontend regression checks.
- Check `/`, `/demo`, `/app`, unknown paths and `/api/health` over real HTTPS.
- Confirm video decoding, native playback and provenance hashes.
- Check desktop 1280×720 and phone 390×844 / 320×740 widths.
- Verify no inspection API requests or external asset origins.
- Preserve existing verification/DMARC records when moving DNS.
- Verify apex and www HTTPS and recordings before retiring the scoped AWS trial.

Cloudflare Free static hosting introduces no paid compute subscription. The
separately purchased domain still needs normal renewal. Free hosting is not an
uptime guarantee; keep the reproducible release and repository available.

References: [Direct Upload](https://developers.cloudflare.com/pages/get-started/direct-upload/),
[custom domains](https://developers.cloudflare.com/pages/configuration/custom-domains/),
[route matching](https://developers.cloudflare.com/pages/configuration/serving-pages/),
[Free limits](https://developers.cloudflare.com/pages/platform/limits/).
