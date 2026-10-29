# IndustReal real-video integration attempt — 29 October 2026

**Outcome: acquisition succeeded; fresh recognition is blocked by Windows
Application Control. No real-video PASS has been verified.** The existing marker
application, synthetic benchmark reports and IMPACT results are unchanged.

## What was actually obtained

The [official IndustReal repository](https://github.com/TimSchoonbeek/IndustReal/tree/ad86a35d4b5125739e24af677e5d7b55c74af945)
points to 4TU for its data and recognition weights. Its desired-behaviour example
is `03_assy_0_1` ([authors' demonstration](https://youtu.be/S-o6MHxvY5c)).
Requests to the official dataset landing page and documented v2/v3 metadata
endpoints timed out during this attempt. Original authors' weights were not
obtained. The authors' demonstration has not been reproduced locally.

A bounded fallback acquired only one video from a
[public mirror](https://huggingface.co/datasets/Zzitang/IndustReal/tree/c408f6effaa96512bd4eb5036c871bb7601ddc3e),
plus a separate course project's research model. The mirror does not contain
`03_assy_0_1`. The selected `25_assy_0_1.mp4` is its smallest nominal normal
assembly recording; selection was by filename and size, before model inference.
Visual inspection shows camera-recorded tabletop assembly of a construction-toy
car. This is not industrial deployment evidence.

| Asset | Measured bytes | SHA-256 |
| --- | ---: | --- |
| `25_assy_0_1.mp4` | 37,472,124 | `9771261256d8995ea9c1144deb6dab31c14fb6f457fb16eb744c9607090f34a1` |
| Third-party `best.pt` | 6,230,378 | `53739cf329e5e3fb08b8584957cf81caf79ce8073c892437cb155e15fee735ce` |

The video member passed the ZIP directory CRC32 (`009522f6`), byte count and
pinned local SHA-256 check. Only its compressed member and the ZIP directory were
transferred; the complete 2.51 GB mirror archive was not downloaded. The mirror
has **not** been matched against the official archive, so provenance remains
`EXTERNAL_PHYSICAL_MIRROR_UNVERIFIED`. The recording's train/test split and any
overlap with model training are unknown. No held-out claim is supported.

Video decoding measured 1,798 frames, 10 FPS, 1280 × 720, 179.8 seconds. Timing is
the declared frame-index/FPS fallback, not hardware capture timestamps. Six
inspection images are retained locally under ignored `runtime/`; none contain
recognizer output.

The model comes from
[321thijs123/IndustReal-YOLO-VLM](https://github.com/321thijs123/IndustReal-YOLO-VLM/tree/5fac256e7d29de2626a2b08e973a449fe6ea98a9),
**not the original IndustReal authors**. Its Git blob SHA-1 was checked against
`94de3b63687bc6a0c570b405c6706c158f5e1e8a`. Static checkpoint inspection found 24
native assembly-state categories, Ultralytics version 8.3.148 metadata, and an
embedded AGPL-3.0 notice. No publisher license file was found. Weights and media
remain ignored local assets and are not redistributed in this repository.

## Where execution stopped

An isolated environment under `runtime/industreal_env/` installed CPU PyTorch
2.15.0, torchvision 0.29.2 and Ultralytics 8.4.192. STEPLOCK's original `.venv`
continues using OpenCV 4.14.0; its dependencies were not replaced.

Two initialization attempts stopped before model loading or frame predictions:

```text
OSError: [WinError 4551] An Application Control policy has blocked this file.
Error loading torch/lib/torch.dll or one of its dependencies.
```

No security policy was changed. A search did not locate a published compatible
IndustReal ONNX checkpoint for the existing OpenCV runtime. The experimental
native runner remains under ignored `runtime/`; it is not shipped as a working
recognition adapter.

| Requested result | Verified outcome |
| --- | --- |
| Fresh pixel predictions | Not executed; empty prediction list |
| Native recognition latency | Not measured; `null` |
| Mistake precision, recall, F1 | Not measured; `null` |
| False PASS / correction detection | Not evaluated; `null` |
| STEPLOCK real assembly → PASS | Not established |
| Original ArUco engine | Unchanged; untagged video is incompatible |

The original authors' CPU PSR example consumes precomputed detections. Replaying
that output would be a reference demonstration, not fresh STEPLOCK inference.
No annotations, generated markers, manual state vectors or third-party PASS
labels were passed to STEPLOCK's procedure engine.

## Reproduction and next prerequisite

Run `python scripts/acquire_industreal_candidate.py` from the repository root.
It obtains the pinned ZIP directory, selects only the named member, checks its
CRC and SHA-256, and obtains the pinned third-party checkpoint. Existing local
assets are rechecked before reuse. Nothing is added to the demo catalog.

The next prerequisite is an approved environment able to run recognition and,
for an authenticated evaluation, the official model, original clip and untouched
annotations. Fresh predictions, temporal sequence checks, failure cases and
measured latency must precede UI integration or any real PASS claim. A final
assembly-state classification alone does not establish correct assembly order.

Machine-readable acquisition and failure evidence is in
[`benchmarks/external_runs/20261029_industreal_attempt/status.json`](../benchmarks/external_runs/20261029_industreal_attempt/status.json).
There is no new accuracy benchmark or confusion matrix because inference did not
execute.

## Regression check

The first full backend run produced 64 passes and one failed assertion: under
concurrent runtime installation, the real replay analyzed 58 of 60 frames. The
existing bounded queue intentionally drops stale frames. Its test previously
assumed zero queue drops. The corrected check requires all source frames to be
decoded, `analyzed + dropped == frames_in`, the last source frame to be retained,
and no unsupported PASS throughout. No application behavior was relaxed.

Follow-up verification: **68 backend tests passed** in 36.72 seconds, including
the local real-video test and three acquisition integrity tests. **20 frontend
tests passed**, and the production build passed. One existing FastAPI/httpx
deprecation warning and the existing frontend bundle-size advisory remain.
