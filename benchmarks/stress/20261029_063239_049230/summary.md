# Synthetic degradation gates

| Stress | Status | Safety gate |
|---|---|---|
| clean | PASS | True |
| light_minus25 | PASS | True |
| light_minus50 | PASS | True |
| severe_blur | CALIBRATION_REQUIRED | True |
| occlusion | HOLD_FOR_REVIEW | True |
| repeated_pixels | HOLD_FOR_REVIEW | True |
| drop30 | PASS | True |
| extreme_tilt | CALIBRATION_REQUIRED | True |
| wrong_dictionary | CALIBRATION_REQUIRED | True |
| midassembly | HOLD_FOR_REVIEW | True |
| backwards_time | HOLD_FOR_REVIEW | True |
| anchors_lost | CALIBRATION_REQUIRED | True |
| unknown_tag | HOLD_FOR_REVIEW | True |
| source_gap | HOLD_FOR_REVIEW | True |

- Designed synthetic safety checks, not an independent accuracy benchmark.
- Light/drop cases permit abstention; a passing safety gate does not mean successful procedure completion.
- No physical capture, hand recognition or uniform-occluder guarantee.
