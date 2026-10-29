# Measured test run

32 synthetic clips, 864 decoded frames. Real staged data NOT_PROVIDED.

| Arm | Final correct | Event P/R/F1 | False PASS | Timely |
|---|---|---|---|---|
| single_frame | 24/32 | 1.0 / 0.5333333333333333 / 0.6956521739130435 | 8/24 | 12/16 |
| stable_only | 28/32 | 1.0 / 0.8 / 0.8888888888888888 | 4/24 | 12/16 |
| steplock | 32/32 | 1.0 / 1.0 / 1.0 | 0/24 | 16/16 |

Vision p50/p95 17.410850035957992/23.487865028437223 ms. Offline throughput 43.43784544263509 fps. Capture-to-visible latency NOT_MEASURED.

Commit 0a00d9958bdc49d5e0874628205afff226f7d585; working tree dirty=True; prediction source clean=True.

- Generated marker boards only. No physical camera or staged-real footage was evaluated.
- Held-out camera transform groups share a deterministic generator and recipe; this does not establish industrial generalization.
- Tag identity can be swapped. White-board emptiness cannot exclude uniform occluders or hidden stacked parts.
- Event F1 scores the four declared mistake classes; uncertainty/quality warnings are counted separately. All raw events are retained.
- False PASS denominator includes all annotated non-PASS clips, including quality/insufficient-evidence cases.
- Throughput is offline shared vision plus all three engines and logging. Capture-to-visible-alert, live CPU overhead and GPU performance were not measured.
- Wilson bounds are descriptive only: generated clips are related and not independent industrial samples.
