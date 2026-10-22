# Reviewed rulebook vs rulegen per-page vs rulegen whole-document

Reviewed (spike) rule entries: 88 (79 on the pages the per-page mode covered: [9, 11, 12, 13, 14, 15, 23, 24]).
Same schema and gates for both rulegen modes; same model. 'Re-found' uses a loose criterion-identity matcher (same decision point + span overlap ≥0.35 or shared fields) — still an undercount.

| mode | drafts | re-found of all reviewed rules | re-found of in-scope reviewed rules | novel (not in reviewed) | provenance labels |
| --- | --- | --- | --- | --- | --- |
| per-page (api gemini-3.6-flash) | 68 | 61/88 | 60/79 | 4 | {'verbatim': 58, 'operationalized': 10} |
| per-page (agy.gemini-3.1-pro-high) | 93 | 72/88 | 70/79 | 14 | {'verbatim': 59, 'operationalized': 34} |
| per-page (agy.gemini-3.6-flash-medium) | 75 | 60/88 | 59/79 | 10 | {'verbatim': 70, 'operationalized': 5} |
| whole (whole-exhaustive) | 37 | 36/88 | 31/79 | 5 | {'verbatim': 37} |
| whole (whole) | 12 | 15/88 | 7/79 | 0 | {'verbatim': 12} |
| agentic (gemini-3.1-pro-high) | 52 | 44/88 | 42/79 | 3 | {'operationalized': 12, 'verbatim': 40} |
| agentic (gemini-3.6-flash-medium) | 84 | 51/88 | 50/79 | 24 | {'verbatim': 43, 'operationalized': 41} |

## Agreement between per-page and the fuller whole-document run (same model, different context)

- criteria found by **both**: 37
- **per-page only**: 31
- **whole-document only**: 8

Per-page only (first 12):
  - A-61.active-seizure (p.9) — active seizure
  - A-62.ineffective-airway-clearance (p.9) — Ineffective airway clearance
  - A-66.hypotension-hypoperfusion (p.9) — Hypotension with signs of hypoperfusion
  - A-68.extreme-heart-rate (p.9) — Severe bradycardia or tachycardia
  - A-71.penetrating-trauma-lifesaving (p.9) — Penetrating trauma of head, neck, abdomen, chest requiring  
a lifesaving interv
  - A-72.severe-respiratory-distress-lifesaving (p.13) — Patients in severe respiratory distress who require immediate lifesaving interve
  - A-73.unstable-chest-pain-lifesaving (p.13) — Patients with chest pain who are physiologically unstable and require immediate 
  - A-74.pregnant-postpartum-hemodynamic-instability-lifesaving-intervention (p.14) — Any pregnancy-capable patient, whether pregnant or postpartum, who presents with
  - B-101.toxic-ingestion-unexplained-changes (p.15) — Patients who present with alterations in mental status, difficulty breathing, ch
  - B-103.transplant-list (p.15) — Patients who are on a transplant list are also usually considered high-risk.
  - B-105.infant-under-28-days-fever (p.23) — An infant less than 28 days old with a fever is considered high risk and is assi
  - B-106.fever-infant-under-90-days (p.24) — Temperature greater than 38°C (100.4°F) in an infant younger than 90 days old is

Whole-document only (first 12):
  - A-61.intubated (p.6) — intubated
  - A-63.pulselessness (p.6) — pulselessness
  - A-65.severe-respiratory-distress (p.6) — severe respiratory distress
  - A-66.profound-hypotension (p.6) — profound hypotension
  - B-73.thunderclap-headache (p.12) — Most concerning is the “thunderclap headache” (a severe, rapid-onset headache), 
  - D-61.fever-neonate (p.6) — 1-28 days of age: Assign at least ESI 2 if T > 38° C (100.4 ° F)
  - D-62.fever-1-3-months (p.6) — 1-3 months: Consider assigning ESI 2 if T > 38 ° C (100.4 ° F)
  - D-63.fever-3-months-plus-temp (p.6) — 3 months and older: Consider assigning ESI 2 or 3 if: 1. T > 39°C (102.2°F) or <

## per-page API flash vs per-page agy.gemini-3.1-pro-high: found by both 67 · api-only 1 · agy.gemini-3.1-pro-high-only 24

## per-page API flash vs per-page agy.gemini-3.6-flash-medium: found by both 66 · api-only 2 · agy.gemini-3.6-flash-medium-only 8

## per-page API flash vs agentic gemini-3.1-pro-high: found by both 48 · api-only 20 · agentic-only 3

## per-page API flash vs agentic gemini-3.6-flash-medium: found by both 50 · api-only 18 · agentic-only 27

## Reviewed rules no drafter re-found (7)

  - B-27.geriatric-trauma-caution (p.15) — Occult hypoperfusion with normal vital signs is associated with age greater than
  - B-28.ocular-high-risk-constellation (p.13) — with more symptoms in constellation predicting a more emergent problem
  - B-53.pediatric-respiratory-distress-signs-consider (p.13) — Grunting, belly breathing, and retractions suggest respiratory distress
  - B-54.respiratory-distress-signs-consider (p.13) — Signs of distress can include tachypnea, tachycardia, tripoding, speaking in sho
  - B-55.recent-covid-cardiac-risk-consider (p.13) — A recent Covid-19 infection increases cardiac risk (Boukhris et al., 2020) regar
  - D-04.context-beta-blockers-consider (p.23) — Medications that affect tachycardic compensation for hypotension, such as beta b
  - D-05.context-immunosuppression-consider (p.23) — Medications that blunt a robust immune response, such as corticosteroids, must a