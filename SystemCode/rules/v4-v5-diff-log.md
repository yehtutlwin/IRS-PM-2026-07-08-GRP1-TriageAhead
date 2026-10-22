# ESI v4 to v5 diff log

Purpose: the v4 handbook's practice cases are the answer
key for encoding-fidelity testing of our **v5** rulebook ([criteria.yaml](criteria.yaml)). That
shortcut is valid only where v4 and v5 agree. This log records, per rule, whether the underlying
criterion changed between editions, so every practice case can be pre-classified — expected answer
frozen **before** the test run — into:

- **Set 1 (unchanged)**: case touches only `v4=v5` rules → expected answer = the v4 book's answer, verbatim.
- **Set 2 (adjust)**: case touches a `CHANGED` or `V5-ONLY` rule → expected answer re-derived under v5,
  reasoning logged below, frozen before running. If not cleanly re-derivable → excluded, with reason.
- **Out of scope**: cases touching only `SUPPLEMENTED` rules don't exist (those rules aren't ESI);
  supplemented rules are verified against their own cited CDC/NICE pages, never against ESI cases.

Discipline: after this log is frozen, **every test failure is a real failure** (encoding bug or,
rarely, a pre-classification error — both get fixed and logged). No post-hoc "probably an edition
difference" is admissible.

## Tag vocabulary

| tag | meaning | test-set consequence |
| --- | --- | --- |
| `v4=v5` | criterion materially identical in both editions | v4 cases test it directly (Set 1) |
| `CHANGED` | present in both, but thresholds/wording changed materially | v4 cases touching it → Set 2 (re-derive) |
| `V5-ONLY` | no v4 counterpart | no v4 case can test it → non-encoder-authored v5 cases |
| `V4-ONLY-DROPPED` | v4 content removed in v5 (context for case exclusions) | v4 cases resting on it → excluded |
| `SUPPLEMENTED` | not ESI at all (CDC/NICE) | out of scope for ESI cases entirely |

## Page-numbering note (verification hygiene)

The v5 PDF's printed page N = PDF page N+6. **criteria.yaml citations currently MIX the two
schemes** — e.g. A-01 cites "p.12 (Fig 2-2 note)" and GOV-02 cites "p.13 (Ch.2)": both passages
are on *printed* pages 6–7 (PDF 12–13), while B-rule citations like "p.12 (high-risk examples)"
use *printed* page 12 (PDF 18). This log uses **printed** pages for both editions.

## v5 internal inconsistencies found during verification (encoding-review flags)

These are v5-vs-v5 issues surfaced while verifying the v5 column — they affect what "correct
under v5" even means for Set-2 re-derivation:

1. **Pediatric fever, age bands**: Fig 2-2 note (printed p.6) says *1–28 days* → assign at least
   ESI 2 if T > 38°C, and Ch.6 text (p.23) repeats "<28 days". But Table 6-2 (p.24) uses
   **< 90 days** for the same >38°C red flag, and the p.24 text says "younger than 90 days …
   assigned at least ESI level 2". Our D-03 encodes the 90-day version.
2. **Pediatric fever, older-child threshold**: Fig 2-2 note (p.6) says 3 months+ → *consider*
   ESI 2 or 3 if T > **39°C** (or incomplete immunizations, or no obvious source). Table 6-2
   (p.24) says > 3 months → red flag at > **38.5°C**. Our D-03 encodes 38.5.
3. **D-03 effect strength**: the explicit "at least ESI 2" language attaches to the *infant*
   (<28/<90 day) arm only. For the >3 months arm both v5 statements say "consider" / "red flag",
   not an automatic 2 — but D-03 currently applies `effect: at_least_ESI_2` to BOTH arms. The
   >3-months arm is therefore stricter than the source and should be split out as
   `consider`/operationalized (floor-conservative, but it claims `provenance: verbatim`, which
   overstates).

## Per-rule tags

v5 column verified against sources/ESI-Handbook-5th-Edition-3-2023.pdf; v4 column against
sources/ESI-Handbook-v4-2012-AHRQ.pdf (both via text extraction). v4 printed→PDF offset is +9
at the front of the book, shrinking to +6 by the case chapters (blank versos dropped).

### Decision point A (→ ESI 1)

v4 source: Ch.2 printed pp.7–16 (algorithm note A p.8; Table 2-1 lifesaving interventions p.9;
AVPU Table 2-2 p.10; level-1 examples p.11). v4 note A also lists "acute mental status changes"
as a level-1 condition — v5 folds this into the unresponsiveness definition.

| rule | v5 content (verified, printed page) | v4 status | tag |
| --- | --- | --- | --- |
| A-01.unresponsive | nonverbal + not following commands (acutely) OR requires noxious stimulus (P/U on AVPU) — Fig 2-2 note p.6 | Identical two-part definition, verbatim (v4 note A p.8; AVPU p.10). v4 adds explicit carve-out: not for known dementia/developmental delay/aphasia | `v4=v5` |
| A-02.arrest-or-imminent | "Cardiac and/or pulmonary arrest (or appears to be imminent)" p.9 | Cardiac/respiratory arrest in level-1 examples (p.11) | `v4=v5` |
| A-03.apneic-or-intubated | Fig 2-2 note p.6: intubated, unresponsive, pulselessness, apneic, severe respiratory distress | Same condition list, note A p.8 | `v4=v5` |
| A-04.pulseless | p.6/p.9 | note A p.8 | `v4=v5` |
| A-05.severe-respiratory-distress | p.6; p.9 "ineffective respiratory pattern" | note A p.8; examples p.11 (agonal/gasping) | `v4=v5` |
| A-06.occluded-airway | p.9 Ch.3 intro: unresponsiveness, active seizure, occluded airway, ineffective gas exchange | Airway screening questions p.8–9 ("Does this patient have a patent airway?") | `v4=v5` |
| A-07.active-seizure | p.9 | v4 level-1 framing covers actively seizing via airway/responsiveness; note also v4 p.20: "ALL patients with a reported seizure meet ESI level-2 criteria" (v5 p.12 narrows: post-ictal → 2, alert-and-oriented with known seizure history → by resources) | `v4=v5` (active); reported-seizure handling `CHANGED` (context for case grading) |
| A-08.spo2-below-90-with-compromise | p.9: "SpO2 < 90% that is not the patient's norm, with other signs of respiratory compromise" | **CHANGED.** v4 note A: bare "SPO2<90" = level-1 condition — NO "not patient's norm" qualifier, NO "with other signs" qualifier (norm caveat exists in v4 only as a Ch.5 danger-zone example, p.38) | `CHANGED` |
| A-09.anaphylaxis | p.9 | "anaphylactic shock" in examples p.11 | `v4=v5` |
| A-10.hypotension-with-hypoperfusion | p.9 (example: chest pain, SBP 80) | Identical pairing, examples p.11 ("Chest pain, pale, diaphoretic, BP 70/palp") | `v4=v5` |
| A-11.hypoglycemia | Fig 2-2 note p.6 "profound hypotension or hypoglycemia"; Ch.3 list p.9 says bare "Hypoglycemia" | v4 examples p.11: "hypoglycemia with a change in mental status" — v4 requires the MS change; v5 Ch.3 lists bare "Hypoglycemia" (v5 Fig 2-2 says "profound") | `CHANGED` (qualifier moved: v4 needs AMS; v5 needs "profound"/judgment) |
| A-12.severe-brady-or-tachycardia | p.9; Ch.6 p.23 example (alert elderly, HR 32 or 180 → ESI 1 regardless of appearance) | v4 examples p.11: "severe bradycardia or tachycardia WITH signs of hypoperfusion"; but also "weak and dizzy, HR 30" → 1. v5 drops the hypoperfusion qualifier and its p.23 example makes rate alone decisive | `CHANGED` (v5 broader) |
| A-13.flaccid-infant | p.9 | "Baby that is flaccid", examples p.11 | `v4=v5` |
| A-14.penetrating-trauma-unstable | p.9: head/neck/abdomen/chest requiring lifesaving intervention | Substance present (critically injured trauma unresponsive; requires immediate crystalloid/colloid resuscitation, p.11); the explicit body-region phrasing is v5's | `v4=v5` (substance) |

### Decision point B (→ ESI 2)

v4 source: Ch.2 pp.11–13 (examples list), Ch.3 pp.17–28 (topic sections + Table 3-1 vignettes).
v4's framing device ("a patient you would put in your last open bed") has no v5 counterpart but
changes no criterion.

| rule | v5 content (verified, printed page) | v4 status | tag |
| --- | --- | --- | --- |
| B-01.new-altered-mental-status | p.12: history unknown + confused/lethargic/disoriented → assume new, assign 2 | Identical incl. the unknown-history default (v4 p.26); chronic dementia/confusion excluded in both | `v4=v5` |
| B-02.severe-pain-consider | p.12: ≥7/10 "considered for" level 2; explicit warning not all ≥7 are level 2 | Identical: ≥7/10 "may… but is not required" (v4 pp.8, 12); bolded caveat p.26; "can I do anything at triage to decrease the pain?" heuristic | `v4=v5` |
| B-03.severe-pain-systemic-cause | p.12: systemic disruption (renal colic, cancer, sickle cell crisis) → level 2 | Identical trio: "not possible to manage pain at triage for renal colic, cancer, or sickle cell crisis… ESI level 2" (v4 p.26) | `v4=v5` |
| B-04.chest-pain-acs-suspect | p.12 examples list | Near-verbatim example (v4 p.12); Ch.3 p.19 adds the needs-an-ECG heuristic | `v4=v5` |
| B-05.stroke-signs | p.12 examples list | v4 p.12 + p.20 (sudden speech deficit/motor weakness → 2; fibrinolytic time window) | `v4=v5` |
| B-06.possible-ectopic-stable | p.12 examples list | v4 p.12 ("rule-out ectopic, hemodynamically stable"); Table 3-1 p.24 | `v4=v5` |
| B-07.immunocompromised-fever | p.12: chemo + fever | Verbatim same example (v4 p.12; p.20) | `v4=v5` |
| B-08.transplant-fever-or-infection | p.12 examples list ("Transplant recipient presenting with a fever or other indication of infection"); p.15 Transplant section (adds "or rejection", transplant-listed) | Substance present (v4 p.22: "ill" post-transplant = immunocompromised, high-risk; transplant-listed high-risk verbatim in both). Explicit fever pairing is v5's | `v4=v5` (substance) |
| B-09.suicidal-or-homicidal | p.12 examples; p.15 adds psychotic, violent | v4 p.12, p.20 (adds elopement risk; intoxication alone ≠ high risk) | `v4=v5` |
| B-10.needle-stick-hcw | p.12 examples list | v4 p.12 (without the PEP time-sensitivity gloss) | `v4=v5` |
| B-11.sexual-assault | p.12 examples list; p.15 (mechanism list includes sexual assault) | Present, but filed under severe DISTRESS (v4 p.13, p.27) rather than high-risk; same level-2 outcome | `v4=v5` (substance) |
| B-12.increasing-respiratory-effort | p.12 examples list | v4 respiratory section: distress with potential to rapidly deteriorate (asthma, PE, pneumothorax…) | `v4=v5` (substance) |
| B-13.postpartum-hemorrhage | p.12 examples list; p.14 OB section (heavy bleeding definitions) | v4 p.20: postpartum heavy vaginal bleeding → 2; instability → 1 | `v4=v5` |
| B-14.stridor-or-secretions | p.13 ENT: cannot manage secretions and/or stridor → 2 | **CHANGED (direction).** v4 p.19: drooling/stridor = impending airway loss, "meet level-1 criteria" when in immediate danger (epiglottitis, peritonsillar abscess). v5 files stridor/secretions at 2 | `CHANGED` |
| B-15.high-risk-epistaxis | p.13: posterior/brisk, thrombocytopenia, clotting dyscrasias, warfarin/other anticoagulants → 2 | Near-verbatim (v4 p.19: posterior bleed or warfarin/other anticoagulant → 2); v5 ADDS thrombocytopenia/clotting dyscrasias | `CHANGED` (minor; v5 broader) |
| B-16.button-battery-or-magnet-ingestion | p.13 peds note (<6y, >20mm); p.14 (earth magnet) | **NOT IN V4** (zero occurrences of "battery"; closest: esophageal foreign body as airway risk, p.19) | `V5-ONLY` |
| B-17.abdo-pain-pregnant-or-postpartum | p.14 assessment question | **CHANGED.** v4 p.20 is narrower and gestation-gated: localized pain / bleeding / discharge at ≥14–20 weeks → 2; "generalized cramping and bleeding with stable vital signs do not meet level-2 criteria". v5 asks broadly "pregnant or postpartum?" | `CHANGED` |
| B-18.abdo-pain-sepsis-or-hypoperfusion | p.14 assessment questions | Substance present (sepsis/urosepsis high-risk throughout v4); the abdo-pain question formulation is v5's | `v4=v5` (substance) |
| B-19.abdo-pain-trauma | p.14 assessment question | Substance present in v4 trauma section (blunt/penetrating abdominal trauma high-risk) | `v4=v5` (substance) |
| B-20.abdo-pain-refractory-constant-maximal | p.14 assessment question | No v4 counterpart found (refractory/constant/maximal-on-onset formulation) | `V5-ONLY` (formulation) |
| B-21.abdo-pain-vaginal-bleeding | p.14 OB/GYN note (ectopic) | **CHANGED.** v4 gates on ≥14–20 wks + localized (see B-17); v5's ectopic-suspicion framing is broader | `CHANGED` |
| B-22.trauma-mechanism-high-energy | p.15: falls ≥20 ft (6 m), vehicle ejection, mechanical extrication (list also includes sexual assault → B-11) | **CHANGED.** v4 p.22 is qualitative: "Any mechanism of injury associated with a high risk of injury → ESI level 2" (fall distance, vehicle speed as factors, NO numbers). The 20-ft/ejection/extrication numerics are v5's | `CHANGED` (v4 broader, v5 numeric) |
| B-23.penetrating-trauma-stable | p.15: head/neck/chest/abdomen without hemodynamic instability | Substance present (v4 p.22: GSW head/neck/chest/abdomen/groin → trauma team; stab groin → high risk, Table 3-1 p.25). v4 includes groin | `v4=v5` (substance) |
| B-24.extremity-neurovascular-compromise | p.15 ortho: neurovascular compromise, compartment syndrome, partial/complete amputation | Identical trio (v4 p.21) | `v4=v5` |
| B-25.pelvis-femur-fracture-consider | p.15: "carefully evaluated and vital signs considered" (consider-flag is faithful) | v4 p.21: pelvis/femur/hip fractures need careful evaluation (blood loss) — same careful-evaluation stance | `v4=v5` |
| B-26.suspected-toxic-ingestion | p.15 Ingestions: unexplained AMS/breathing/rhythm changes → evaluate as possible ingestion | v4 p.22 broader/stronger: "all other admitted overdoses should be considered ESI level 2" (level 1 if lifesaving needed) | `v4=v5` (substance; v4 stronger) |
| B-27.geriatric-trauma-caution | p.15: occult hypoperfusion, age > 55, "careful assessment" | **NOT IN V4** — no numeric-age geriatric trauma caution anywhere ("age of the patient" is a bare bullet in the trauma detail list; elderly flagged only for medical complaints like abdo pain, p.18) | `V5-ONLY` |
| B-28.ocular-high-risk-constellation | p.13 ATSO elements; "more symptoms in constellation" (≥2 threshold is OUR operationalization) | **NOT IN V4** (no ATSO; v4's own ocular list p.21 differs: chemical splash → immediate irrigation, CRAO, glaucoma, retinal detachment, vision loss → 2) | `V5-ONLY` |
| B-29.pediatric-subtle-ams | p.13 peds note: subtle mental-status change → high risk | Substance present (v4 p.21: inconsolable or withdrawn child = high risk; p.12: 3-month-old "sleeping all the time") | `v4=v5` (substance) |
| B-30.anticoagulated-trauma | NOT in v5 (v5 anticoagulant mention: epistaxis only, p.13) | NOT a v4 criterion either — BUT v4 practice case 25 (87M head strike on warfarin) is answered ESI-2: "Patients taking warfarin who fall are at high risk of internal bleeding… needs a prompt evaluation and a head CT" (p.76). The ESI answer key endorses the supplemented rule's behavior without codifying it — strong corroboration for B-30's review file | `SUPPLEMENTED` |

### Decision point C (→ ESI 3/4/5)

v4 source: Ch.4 printed pp.29–33; Table 4-1 p.30 (= Table 2-3 p.14 = Appendix B algorithm box).

| rule | v5 content (verified, printed page) | v4 status | tag |
| --- | --- | --- | --- |
| C-BAND.resource-count-to-level | p.19: 2+ → 3, one → 4, none → 5 | Identical (v4 p.30). v4 adds an explicit "stop counting at two" note (p.30) — same semantics | `v4=v5` |
| C-COUNT.types-not-tests | p.19: count different TYPES; worked micro-examples (CBC+lytes=1, CBC+CXR=2, c-spine+head CT=2) | Identical incl. the same worked micro-examples (v4 p.31; "x ray" for "radiograph") | `v4=v5` |
| C-LIST.resources | Table 5-1 p.20: labs; ECG/radiographs; CT/MRI/US/angio; IV fluids; IV/IM/neb meds; specialty consult; simple procedure=1; complex procedure=2 | Identical row-for-row (v4 Table 4-1 p.30; "conscious sedation" for "procedural sedation", "Foley cath" for "urinary catheter"). v4 FAQ pp.A-4–A-6 adds clarifying rulings (eye irrigation, transfusion = resources; cardiac monitoring, pre-formed splints = not; ED-made splint = resource; constant observer = resource) — useful for case grading, not encoded | `v4=v5` |
| C-LIST.not-resources | Table 5-1 p.20: H&P (incl. pelvic); POC testing; saline/heparin lock; oral meds; tetanus; refills; call to PCP; simple wound care; crutches/splints/slings | Identical row-for-row (v4 Table 4-1 p.30) | `v4=v5` |

### Decision point D (vitals → reconsider)

v4 source: Ch.5 printed pp.35–40; danger-zone box in Appendix B algorithm. v4 effect wording matches v5:
"**consider** up-triage to ESI 2 if any vital sign criterion is exceeded" (v4 algorithm note D; FAQ p.A-7
confirms "considered rather than automatic") — so our `reassess_uptriage_consider` effect is faithful to BOTH editions.

**v4 danger-zone table (4 bands)**: <3mo HR>180 RR>50 · 3mo–3y HR>160 RR>40 · 3–8y HR>140 RR>30 ·
>8y HR>100 RR>20 · SaO2<92% (single criterion, all ages). Temperature and BP are NOT in either edition's
danger-zone table (v4 p.37 explicit: "blood pressure is not included in the ESI algorithm" — relevant to
the ML comparator's SBP/DBP tree-only classification).

| rule | v5 content (verified, printed page) | v4 status | tag |
| --- | --- | --- | --- |
| D-01.adult-danger-zone | Fig 6-1 p.23: >18y HR>100, RR>20; SpO2<92% (all ages); effect = "Reassess acuity decision" | v4 ">8y": same numbers (HR>100, RR>20, sat<92%) but the band starts at 8y, not 18y. For ADULT cases: identical. For patients 8–18y: v4 applies 100/20 where v5 applies 120/30 (8–12y) or 100/20 (12–18y) | `v4=v5` (adults) / `CHANGED` (8–12y) |
| D-02.pediatric-danger-zone | Fig 6-1 p.23 bands: <1mo 190/60; 1-12mo 180/55; 1-3y 140/40; 3-5y 120/35; 5-12y 120/30; 12-18y 100/20; SpO2<92% | **CHANGED — the headline v4→v5 delta.** v4 4 bands vs v5 7. Numeric shifts: v5 adds neonatal <1mo 190/60; <3mo→1-12mo RR 50→55; 1–3y HR 160→140; 3–5y HR 140→120 RR 30→35; 5–8y HR 140→120; 8–12y HR 100→120 RR 20→30 (v5 LOOSER here — a rare direction). SpO2 <92% unchanged | `CHANGED` |
| D-03.pediatric-temperature-red-flags | Table 6-2 p.24 (<90d: >38 or <36; >3mo: >38.5 or <36) — but see v5 internal inconsistencies #1–3 above | **CHANGED.** v4 (Table 5-1 p.37 + note D): 1–28d >38.0 → assign at least 2; 1–3mo >38.0 → "consider 2"; 3–36mo >39.0 → "consider 3". v5 hardens: mandatory band widens 28d→90d; older-child threshold 39.0→38.5 (Table 6-2; Fig 2-2 note still says 39). Hypothermia: v4 only as level-2 example, <90d <36.5°C (p.47); v5 <36.0°C any age | `CHANGED` |
| D-04.context-beta-blockers | p.23: beta blockers mask tachycardic compensation | Present but weaker: one FAQ mention (p.A-7) "vital signs may be affected by… chronic drug therapy (e.g., beta-blockers)" — no masking rationale | `v4=v5` (substance; v5 elaborates) |
| D-05.context-immunosuppression | p.23 + worked example five p.25 (steroids blunt immune response) | **NOT IN V4** as a vitals-masking concept (v4 has immunocompromised+fever as high-risk = our B-07, but no "steroids blunt the response" note) | `V5-ONLY` |
| GOV-01.acuity-changes-up-only | Appendix A p.27: before provider, only increase, documented; never after provider | **NOT IN V4** — no increase-only/never-decrease statement anywhere; v4 also declines to set reassessment times (p.55) | `V5-ONLY` |
| GOV-02.environment-independence | p.7 Ch.2 (NOT p.13 as cited): acuity reflects patient risk, not ED conditions; also not for metrics manipulation | Same position, stated as under-triage-under-crowding warnings (Ch.3 p.17), not as an explicit rule. v4 adds: arrival by ambulance is NOT a criterion (p.15) — direct standard-side support for the ML comparator's "ambulance must never become a rule" note | `v4=v5` (position; v5 makes it explicit) |

## v4 practice-case inventory (the answer key)

All sets are self-keyed inside the v4 handbook (no separate answer appendix); cases and answers
match by number. v4 printed→PDF page offset is NOT constant (blank versos dropped): +9 at the
front shrinking to +6 by the case chapters.

| set | where (printed) | count | format |
| --- | --- | --- | --- |
| Ch.9 Practice Cases | cases pp.71–78, answers pp.78–84 | **100** | vignette (age/sex, complaint, history, usually vitals) → "ESI level N: criterion" + rationale |
| Ch.10 Competency Set A | pp.85–86, answers pp.88–90 | **25** | same; case A7 has an official dual answer ("4 or 5 — an example of variation") |
| Ch.10 Competency Set B | pp.87–88, answers pp.90–91 | **25** | same |
| Appendix A post-tests (Ch.2–7) | pp.A-1–A-11 | **46 questions** | mixed: assign-a-level one-liners; 15 yes/no "meets level-2 criteria?"; 11 T/F resource-counting; 6 vitals-panel vignettes; 5 pediatric one-liners; 3 implementation questions (not cases) |

Ch.9 official answer distribution: L1=16, L2=27, L3=26, L4=15, L5=16.
The cases themselves are encoded as tests in `tests/v4_cases.yaml` and `tests/v4_posttest_cases.yaml`.
