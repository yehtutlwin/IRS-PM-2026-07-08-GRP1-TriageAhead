# Source documents

Every document that any rule in `rules/` cites must be listed here (source-registry
closure), and so must the source of every question the interview asks. Two are committed to the repo (US federal publications — public domain);
the rest are copyrighted and must be fetched by each person: run

```bash
bash sources/download.sh
```

| File | What it is | Why we need it | Redistribution |
| --- | --- | --- | --- |
| `ESI-Handbook-5th-Edition-3-2023.pdf` | Emergency Severity Index v5 Implementation Handbook (ENA, 2023) — the triage algorithm we encode | **Primary standard**: all verbatim/operationalized rules cite its pages. Contains the algorithm but **no practice cases** | © ENA — not committed; script downloads from the California ENA chapter's public copy |
| `ESI-Handbook-v4-2012-AHRQ.pdf` | ESI v4 Implementation Handbook (AHRQ, 2012, 114 pp) | Contains the **practice cases** missing from v5 — our encoding-fidelity **test set** (with a logged v4→v5 delta check) | US federal (AHRQ) publication, public domain — **committed** |
| `CDC-Field-Triage-2011-MMWR.pdf` | CDC Guidelines for Field Triage of Injured Patients (MMWR 2012) — paramedics' trauma transport-destination protocol | Supplemented-class source: anticoagulated-trauma (B-30) and several candidate rules cite it. NOTE: it governs *transport destination*, not triage acuity — see the coverage caveat in `rules/criteria-candidates.yaml` | US federal (CDC) publication, public domain — **committed** |
| `NICE-NG232-main-guideline.pdf` | NICE NG232 Head Injury guideline (2023) — who needs a CT and how fast | Supplemented-class source: dual citation partner for B-30 and the B-31..B-36 candidates | © NICE — not committed; script downloads the NCBI Bookshelf mirror (nice.org.uk blocks command-line clients) |
| NICE NG232 evidence reviews I (anticoagulants) & J (concussion) | Underlying evidence reviews for the recommendations we cite | Background/verification reading only — no rule cites them directly | © NICE — not committed and **not scripted**: nice.org.uk blocks curl/wget. Download manually in a browser from <https://www.nice.org.uk/guidance/ng232/evidence> |

## Lay-instrument sources (web pages, not PDFs)

Cited by the bridges in `rules/bridges.yaml` (everyday signs a caregiver can report, mapped to the fact a rule reads).
Public patient-facing pages: cited by name, URL, the page's own review date and our access date, with the quoted
sentence per sign in the bridge; nothing to download or commit.

| Source | Used for | URL | Status |
| --- | --- | --- | --- |
| NHS — Stroke: symptoms | bridge BR-05 (stroke signs; "even if they've now stopped") | <https://www.nhs.uk/conditions/stroke/symptoms/> | page reviewed 12 Sep 2024; quoted 13 Oct 2026 |
| CDC — Stroke signs and symptoms | bridge BR-05 (the sudden signs; a transient ischemic attack) | <https://www.cdc.gov/stroke/signs-symptoms/index.html> | last reviewed 19 May 2026; quoted 13 Oct 2026 |
| American Stroke Association — B.E. F.A.S.T. stroke warning signs | bridge BR-05, the page first used | <https://www.stroke.org/en/about-stroke/stroke-symptoms> | verified by eye 24 Aug 2026; refuses automated fetches, so the quotes come from the NHS and CDC pages |
| AAOS OrthoInfo — Care of Casts and Splints, "Warning signs" | bridge BR-24 (numbness and tingling, too tight, cannot move) | <https://www.orthoinfo.org/en/recovery/care-of-casts-and-splints/> (the orthoinfo.aaos.org address redirects here) | quoted 13 Oct 2026 |
| Royal Children's Hospital Melbourne — Plaster cast care | bridge BR-24 (pale or bluish, cool to touch) | <https://www.rch.org.au/kidsinfo/fact_sheets/plaster_cast_care/> | reviewed Dec 2023; quoted 13 Oct 2026 |
| NHS — Broken arm or wrist | bridge BR-24 (turn blue or white) | <https://www.nhs.uk/conditions/broken-arm-or-wrist/> | page reviewed 2 Oct 2026; quoted 13 Oct 2026 |

Not used: the NIMH suicide-screening questions, the poison-control, nosebleed and hip-fracture pages considered earlier.
Those facts carry their everyday wording in the field's own `ask` in `rules/fields.yaml` (authored), with no
bridge; the handbook's own words were enough.

## History-format sources (what the interview collects for the nurse, not for the level)

The history and screening questions (allergies, medicines, past history, last meal, what happened; the infection screen;
identity) are not rules. Each such field in `rules/fields.yaml` carries a `purpose` and either a `source` with the quoted
`span`, or an `authored` reason; `rules/validate.py` fails when one has neither. Two properties are kept apart: whether a
question is asked at all is always the team's decision (AMPLE as the handover format, identity as declared and the sex
question were all team decisions); where its content comes from is what
the label says: *transcribed* when a document can be checked against the quote, *authored* when only the reason exists. They are reviewed on the review site as the
set "history questions".

| Source | Used for | Reference and URL | Status |
| --- | --- | --- | --- |
| **AMPLE history**, as described in *Trauma Secondary Survey* (StatPearls) | allergies (A), medicines (M), past history (P), last meal (L), how the injury happened (E) | Zemaitis MR, Planas JH, Waseem M. *Trauma Secondary Survey.* In: StatPearls. Treasure Island (FL): StatPearls Publishing; updated 2023. PMID 28722931, Bookshelf ID NBK441902. <https://www.ncbi.nlm.nih.gov/books/NBK441902/> | verified 4 Oct 2026: section "AMPLE History", quoted below (the page sits behind a human check since; the quote is as read then) |
| Advanced Trauma Life Support (ATLS) Student Course Manual, American College of Surgeons | the origin of the AMPLE format (secondary survey); the chapter above describes it | not held; copyrighted | not held; cited through the chapter above |
| ESI v4 handbook (AHRQ 2012), PDF page 22 | that the handbook expects this history at triage: "Considering the patient's brief subjective and objective assessment, past medical history, allergies, medications, age, and gender, how many different resources will be used" | `ESI-Handbook-v4-2012-AHRQ.pdf` (committed) | verified 13 Oct 2026; recorded in the fields' notes |
| ESI v5 handbook p.14 (abdominal pain) | when the problem started (`complaint.onset`): "onset, accompanying symptoms and current vital signs are important elements in determining the presence or absence of a high-risk situation" | `ESI-Handbook-5th-Edition-3-2023.pdf` | verified 13 Oct 2026 |
| ESI v5 handbook p.23 (pediatric fever) | the rash question (`infection.rash`): "The patient presenting with a fever, non-petechial rash, and incomplete immunizations should prompt the triage nurse to consider isolation." | `ESI-Handbook-5th-Edition-3-2023.pdf` | verified 13 Oct 2026 |
| Mount Sinai Health System, *Infectious Diseases Screening Tool for Patients at Triage/Registration* (updated 25 Mar 2025) | the infection screen (`infection.rash`, `infection.travel_14d`, `infection.contacts`): a hospital system's triage screening form, quoted question by question | <https://www.mountsinai.org/files/MSHealth/Assets/HS/About/Coronavirus/MSHS-Infectious-Diseases-Screening-Tool.pdf> | quoted 13 Oct 2026; our two-week window differs from its three weeks (flagged in the fields' notes for the nurse's read) |
| CDC, *Core Infection Prevention and Control Practices*, section 5e (last reviewed 12 Apr 2024) | why an infection screen is asked at triage at all: "early detection and management ... of potentially infectious persons at initial points of patient encounter in outpatient settings (e.g., triage areas, emergency departments ...)" | <https://www.cdc.gov/infection-control/hcp/core-practices/index.html> | quoted 13 Oct 2026 |

Quoted span (section "AMPLE History"): "This mnemonic device can be used for obtaining a quick, focused history:
Allergy; Medications; Previous medical history or illness/pregnancy; Last Meal; Events/environment related to injury"
(the source sets the five items as a list, one letter each).

| ESI v5 handbook p.6 and p.12; ESI v4 PDF page 18 (Table 2-1) | the four danger-sign questions (`danger_signs.*`): our lay reading of decision point A, labelled *operationalized*; each quotes the handbook criterion it stands for (unresponsiveness, severe respiratory distress, active chest pain suspicious for acute coronary syndrome, the hemodynamic lifesaving interventions / control of major bleeding) | the two handbooks in this folder | verified 13 Oct 2026 |
| NICE NG232 Head injury (2023), recommendation 1.2.3 (remote advice services) | head strike and loss of consciousness after an injury (`E.head_strike`, `E.loc`): the guideline's own list of what a remote advice service asks before referring a head injury to an emergency department | `NICE-NG232-main-guideline.pdf` (not committed; see above) | verified 13 Oct 2026 |

Authored, with the reason on the field: the problem in the caregiver's own words (`complaint.text`), identity as declared
(`identity.name`, `identity.dob`) and the patient's sex.

## Notes

- The rules cite these documents by page; verification means opening the cited page
  and finding the quoted span. That's the whole review protocol.
- Handbook text must never be republished wholesale in our deliverables: we encode the
  logic with citations, quoting only short spans for verification.
