# Measured dev run

16 synthetic clips, 432 decoded frames. Real staged data NOT_PROVIDED.

| Arm | Final correct | Event P/R/F1 | False PASS | Timely |
|---|---|---|---|---|
| single_frame | 12/16 | 1.0 / 0.5333333333333333 / 0.6956521739130435 | 4/12 | 6/8 |
| stable_only | 14/16 | 1.0 / 0.8 / 0.8888888888888888 | 2/12 | 6/8 |
| steplock | 16/16 | 1.0 / 1.0 / 1.0 | 0/12 | 8/8 |

Vision p50/p95 17.805449984734878/23.627009979099963 ms. Offline throughput 42.4318911172698 fps. Capture-to-visible latency NOT_MEASURED.

Commit f692b8d2ba2b57e1d203f78ef5dee30c6cbf70d7; working tree dirty=True; prediction source clean=False.

- Generated marker boards only. No physical camera or staged-real footage was evaluated.
- Held-out camera transform groups share a deterministic generator and recipe; this does not establish industrial generalization.
- Tag identity can be swapped. White-board emptiness cannot exclude uniform occluders or hidden stacked parts.
- Event F1 scores the four declared mistake classes; uncertainty/quality warnings are counted separately. All raw events are retained.
- False PASS denominator includes all annotated non-PASS clips, including quality/insufficient-evidence cases.
- Throughput is offline shared vision plus all three engines and logging. Capture-to-visible-alert, live CPU overhead and GPU performance were not measured.
- Wilson bounds are descriptive only: generated clips are related and not independent industrial samples.
