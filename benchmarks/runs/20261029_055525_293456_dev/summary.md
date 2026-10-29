# Measured dev run

16 synthetic clips, 432 decoded frames. Real staged data NOT_PROVIDED.

| Arm | Final correct | Event P/R/F1 | False PASS | Timely |
|---|---|---|---|---|
| single_frame | 11/16 | 1.0 / 0.5333333333333333 / 0.6956521739130435 | 4/12 | 6/8 |
| stable_only | 13/16 | 1.0 / 0.5333333333333333 / 0.6956521739130435 | 2/12 | 6/8 |
| steplock | 15/16 | 1.0 / 0.9333333333333333 / 0.9655172413793104 | 0/12 | 8/8 |

Vision p50/p95 12.424/15.455 ms. Offline throughput 60.21 fps. Capture-to-visible latency NOT_MEASURED.

Commit 3af5a9bc4c543cee054ac4272766502c7d9b41f5; working tree dirty=True.

- Generated marker boards only. No physical camera or staged-real footage was evaluated.
- Held-out camera transform groups share a deterministic generator and recipe; this does not establish industrial generalization.
- Tag identity can be swapped. White-board emptiness cannot exclude uniform occluders or hidden stacked parts.
- Event F1 scores the four declared mistake classes; uncertainty/quality warnings are counted separately. All raw events are retained.
- False PASS denominator includes all annotated non-PASS clips, including quality/insufficient-evidence cases.
- Throughput is offline shared vision plus all three engines and logging. Capture-to-visible-alert, live CPU overhead and GPU performance were not measured.
- Wilson bounds are descriptive only: generated clips are related and not independent industrial samples.
