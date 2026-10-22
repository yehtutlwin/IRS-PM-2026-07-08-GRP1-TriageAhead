# B-30 anticoagulated-trauma: standard vs practice on Yale (one-rule divergence analysis)

Rows with a nurse ESI: 558,029 · trauma-flagged: 45,704 · anticoagulated among them: 1,348 (**B-30 condition holds, coarse mapping**)


## Nurse ESI where B-30 fires (our floor: at least ESI-2)

| nurse ESI | n | share |
| --- | --- | --- |
| 1 | 17 | 1.3% |
| 2 | 750 | 55.6% |
| 3 | 531 | 39.4% |
| 4 | 45 | 3.3% |
| 5 | 5 | 0.4% |

**Below our floor (ESI 3-5): 581 = 43.1%** of B-30 cases.


## Outcome arbitration: admission rate among nurse-ESI 3-5 trauma patients

| group | n | admitted |
| --- | --- | --- |
| trauma + anticoagulated (B-30 fired, nurse below floor) | 581 | 75.4% |
| trauma, NOT anticoagulated, same nurse levels (control) | 34,015 | 13.7% |

Admission ratio (B-30 group / control): **5.5×**


## By mechanism (B-30 fired)

| mechanism | n fired | nurse below floor | admitted among below-floor |
| --- | --- | --- | --- |
| fall | 1,294 | 42.4% | 77.6% (n=549) |
| road_accident | 50 | 64.0% | 40.6% (n=32) |
| assault | 5 | 20.0% | 0.0% (n=1) |

## Reading it

- The rule's condition is common on real data (not an exotic textbook case).
- A large share of those patients were triaged below the floor the CDC/NICE-derived criterion implies - a real *divergence* between the encoded criterion and practice.
- Outcome arbitration points in the floor's direction, with the treatment-paradox caveat: admission-for-observation is partly *caused by* the anticoagulant, so this supports 'the criterion identifies a group clinicians take seriously', not 'nurses under-triaged'.
- This is the under-triage safety-net analysis in miniature; a fuller version would use a critical-outcome composite (ICU/death/immediate intervention - MIMIC), sensitivity vs alarm-rate curves, and rule-class attribution.

## Caveats

- Treatment paradox on admission (see above).
- Coarse mapping: cc_fall etc. don't confirm head strike / mechanism detail; head-injury-specific rows would be a tighter test.
- Supplemented-class rule: a claim about the external criterion vs practice, not about ESI.
- Pattern-level only; never individual adjudication.