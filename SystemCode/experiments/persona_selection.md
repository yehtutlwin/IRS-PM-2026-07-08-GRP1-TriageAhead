# How the personas were selected

The evaluation plan asks for 20 to 25 persona answer sheets whose expected level does not come from the system's builder. The ten
personas of 16 October (P1 to P9, with two numbered P6) were written by the builder: five seeded from Yale visits, one from a
handbook practice case and four wholly synthetic. P10 to P19 add five handbook practice cases and five Yale visits. In each,
the expected level comes from an outside source, and the facts that decide it are ones a caregiver can report before
arrival.

## Rules of selection

- **The label comes from outside the team.** For a handbook case it is the book's answer, with its page. For a Yale visit
  it is the level the triage nurse recorded.
- **The deciding facts are reportable before arrival.** A handbook case qualifies only if the rules reach the book's level
  from the case's facts with every vital sign and examination finding removed. A Yale visit qualifies only if the rules
  reach a floor from the record's pre-arrival facts (no vital signs), mapped as in the full Yale run
  ([task_g_full.py](task_g_full.py), history-only arm).
- **Nothing decisive is invented.** Handbook personas state only the case's facts a caregiver can know. Yale personas
  state only what the record holds: age, sex, the recorded complaint, medication classes and history flags. They answer
  "I don't know" to everything else, and "no" to a danger sign only where the record lists no such complaint. Names and
  dates of birth are fictional, and any other filled-in detail is named in the persona's comment.
- **Rules not yet covered, and a spread of ages.** The ten add seven floor rules the first ten do not test, and three
  personas with no floor, to measure false alarms.
- **Arrivals by car or on foot.** The Yale visits arrived by car or walked in, as the product's users do.

## The ten

| Persona | Source | Expected | Rule that sets it |
| --- | --- | --- | --- |
| P10-infant-fever | ESI v4 handbook, chapter 9 case 14 (p.72; answer level 2, p.79) | at least ESI-2 | B-56, infant under 28 days with fever |
| P11-asthma-worsening | ESI v4 handbook, chapter 10 set A case 8 (p.85; answer level 2, p.89); the book's patient came by ambulance | at least ESI-2 | B-12, increasing respiratory effort |
| P12-elderly-confusion-uti | ESI v4 handbook, chapter 9 case 85 (p.77; answer level 2, p.83) | at least ESI-2 | B-01, new altered mental status; B-43, urinary symptoms at 65 or over |
| P13-cast-too-tight | ESI v4 handbook, chapter 9 case 50 (p.74; answer level 2, p.81); age and sex fictional. Sheet restated on 18 Oct 2026 after the first run: the clinical fact replaced by the three limb signs a family can see; expected floor and rule unchanged | at least ESI-2 | B-24, extremity neurovascular compromise |
| P14-child-knee-cut | ESI v4 handbook, chapter 9 case 9 (p.71; answer level 4, p.78) | no floor | none |
| P15-suicidal-thoughts | Yale visit 177748: woman of 31, complaint "suicidal", walked in, nurse's level 2 | at least ESI-2 | B-09, suicidal or homicidal |
| P16-intentional-overdose | Yale visit 166225: man of 20, complaint "overdose-intentional", by car, nurse's level 2 | at least ESI-2 | B-26, suspected toxic ingestion |
| P17-nosebleed-clotting | Yale visit 379598: man of 71, complaint "epistaxis", clotting disorder on record, by car, nurse's level 2 | at least ESI-2 | B-15, high-risk epistaxis |
| P18-fall-no-floor | Yale visit 141814: woman of 58, complaint "fall", no blood thinner on record, by car, nurse's level 4 | no floor | none |
| P19-headache-no-floor | Yale visit 553293: woman of 52, complaint "headache", nurse's level 4 | no floor | none |

Yale visits are rows of `data/yale_ed_visits.parquet` (0-based). The urgent visits were the first found, in a random order
with a fixed seed (42, then 7 for arrivals by car or on foot), among visits rated 1 or 2 whose record facts make exactly the
named rule fire. The two visits with no floor were the first found, with seed 42, among visits rated 4 or 5, aged 18 to 64,
with a single recorded complaint and no floor from the record.

## Before any run

The sheet check ([sheet_check.py](sheet_check.py), output in [out/sheet-check.md](out/sheet-check.md)) runs the rule engine
on each sheet's facts. All ten reach their expected level and rule.

## P20 to P24: the fallback five (18 October 2026, evening)

So that a tested set of 25 existed before the teammates' sheets were complete, five more handbook practice cases were
added by the same rules as P10 to P14: the book's answer is the label, only facts a caregiver
can know are stated, and each adds a rule or a patient type the first 20 do not test. They are the builder's and reported as such; in the
final set a teammate's sheet testing the same rule replaced three of them.

| Persona | Source | Expected | Rule that sets it | What it adds |
| --- | --- | --- | --- | --- |
| P20-cancer-pain | ESI v4 handbook, chapter 10 set A case 4 (p.85; answer level 2, p.88) | at least ESI-2 | B-03, severe pain from a systemic cause | a rule not yet tested; the patient answers for herself |
| P21-child-shunt-not-right | chapter 10 set A case 17 (p.86; answer level 2, p.89) | at least ESI-2 | B-29, a child's subtle change in mental status; B-01 | a rule not yet tested; a 4-year-old with a shunt |
| P22-teen-threatening-family | chapter 9 case 93 (p.77; answer level 2, p.84) | at least ESI-2 | B-09, suicidal or homicidal | the homicidal side of B-09; an adolescent |
| P23-sawdust-in-eye | chapter 9 case 39 (p.73; answer level 4, p.80) | no floor | none | an eye complaint; a walk-in false-alarm check |
| P24-bug-in-ear | chapter 10 set B case 7 (p.87; answer level 4, p.90) | no floor | none | an ear complaint; a walk-in false-alarm check |

The 25 then test 15 of the 60 floor rules, with 17 personas expecting a floor and 8 expecting none (one of the eight is
the builder's synthetic gout case). Ages run from a newborn to 87. No persona tests an ESI-1 rule from an outside source: the
handbook's level-1 cases rest on a clinician's findings, which the interview cannot ask for.

## The final set of 27 (19 October 2026)

On 19 October two teammates' sheets became complete as posted (expected floor with its basis, current fields, `say` lines):
six sheets from one teammate and the ten floor sheets among another teammate's 35. Each was run once as posted, separately from the set
([the six-sheet run](out/task-i-20261019-1205-v2y-newtondai-6-sheets-as-posted-sheet-player-local-t0.md),
[the 35-sheet run](out/task-i-20261019-0327-v2x-chernhaw-35-sheets-as-posted-sheet-player-local-t0.md); the posted files are
kept beside the reports). The rule for the final set: a teammate's sheet is taken exactly as
posted, with only a prefix for its author added to its id; where a teammate's sheet tests the same rule as a builder sheet, the
teammate's replaces it; a sheet is left out only when its label is debatable, its facts cannot be reached by the interview, or it
duplicates another teammate's. A sheet that exposes a gap in the interview is kept: that is what the set is for.

| Origin | Personas | Count |
| --- | --- | --- |
| Yale visits, nurse's level, written by the builder | P1, P2, P4, P15, P16, P17, P18, P19 | 8 |
| ESI v4 handbook practice cases, the book's answer, written by the builder | P10, P12, P13, P14, P20, P21 | 6 |
| Synthetic, the builder's judgement | P6-acute-gout, P7-heat-stroke, P8-decompensated-liver-disease, P9-breathing-no-pain | 4 |
| Teammates' sheets, invented cases with the handbook page cited | ND-P20, ND-P23, ND-P27, ND-P28, ND-P29, CH-I29-03, CH-I29-04, CH-I29-08, CH-I29-09 | 9 |

Withdrawn from the earlier 25: P3 and P6-stroke-resolved (replaced by ND-P29 and ND-P27), P5 and P11 (replaced by CH-I29-04 and
CH-I29-09), and the builder's fallback P22, P23 and P24 (replaced by ND-P20, ND-P23 and ND-P28). Not taken: a teammate's P22
(its label rests on reading "thoughts of hurting themselves" as "actively suicidal"; P15 carries the same rule with a nurse's
level), the other teammate's I29-02, I29-15 and I29-18 (duplicates), I29-11 and I29-17 (not reachable by our rules), and the 25 no-floor
sheets (no basis stated for the absence of a floor).

The 27: 21 expect a floor, 6 none; 19 distinct floor rules; 9 sheets not written by the builder; labels from outside the team on
23 (8 nurse levels, 6 book answers, 9 teammate citations). Sheet check: 25 of 27 agree, the two synthetic disagreements as before.

**Result on the final set of 27** (19 October 2026, the code as submitted): expected floor reached in 20 of 27, expected rule in 17 of
27, facts captured 159 of 196 (148 of 169 outside the synthetic three), no danger sign missed; arm B of number 4 on the same sheets 10 of
27 with the handbook only and 13 of 27 with the handbook and our rules. The seven floors not reached: the synthetic heat-stroke case,
two builder sheets whose deciding question came one past the run's sixteen-answer limit (P17, P20), and four teammate sheets that each
exposed a recorded gap in the interview (ND-P28, ND-P29, CH-I29-04, CH-I29-08; each explained on the evaluation results page). None is a wrong floor.
