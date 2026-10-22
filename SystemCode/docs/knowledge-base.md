# The knowledge we engineered

What the team encoded, from which sources, by what method, where it ended up, and whether it has been reviewed. The
design of the whole system is the [architecture document](architecture.md); the files of the knowledge base, one line
each, are listed in [rules/README.md](../rules/README.md). The second half of this page walks through how the program
uses the knowledge, in the order a fact travels.

## What we encoded

Every file is produced by one of three processes: extracted from sources, derived deterministically, or authored with
added insight. Every fact has one name and one definition in `rules/fields.yaml`; what the interview may ask is derived
from the rules into `rules/derived/agenda.yaml`.

| Knowledge | Source | Method | Encoded in |
| --- | --- | --- | --- |
| **1. The triage criteria.** 109 entries, of which 92 are executable conditions: immediate danger (decision point A, 22 rules), high risk (B, 60) and vital-sign thresholds (D, 10); the rest are notes that fire nothing, such as the resource count of decision point C. Each carries its decision point and a provenance class (quoted, operationalised from an imprecise term, supplemented from another guideline). | ESI handbook v5 pages 9 to 24; the CDC field-triage guideline and NICE NG232 for the supplemented rules | Drafted by a language model from the page text under a fixed schema, page and quoted span kept per rule; the span validated on the page; tested against the fourth edition's 187 worked cases | `rules/criteria.yaml` (plus `criteria-candidates.yaml`, drafted and not in the tested set) |
| **2. Bridges.** How everyday signs a caregiver can report map to the clinical fact a rule reads: the stroke signs, the cast and limb warning signs, the handbook's six eye findings (counted), altered mental status from a change against the patient's usual self or from "not responding", heavy bleeding after childbirth; plus three entailments between our own facts. | NHS and CDC stroke pages, AAOS OrthoInfo and two plaster-cast patient pages, ESI v5 pages 12 to 14 | Each bridge is a condition with its kind (signs, count, entails), its cited quote per sign and a one-line reason; `rules/validate.py` checks that every field named exists and matches the field file | `rules/bridges.yaml` (10 entries) |
| **3. The interview: what to ask, in what order, and when.** The fixed order (danger signs, complaint, medications, history, infection screen, identity), the follow-ups that open on a fact (a fall opens the head-strike question; a probable anticoagulant opens a confirmation), and the grouping of fields into one question. | ESI's order (A before B); the AMPLE handover order; each criterion with two inputs (one known, ask the other); the handbook's own question list for abdominal pain (p. 14) | The agenda is derived from the criteria and the field file by `rules/derive.py`; the 57 triggers and each field's everyday wording are authored | `rules/derived/agenda.yaml` (104 fields), `rules/triggers.yaml`, the `ask` wording in `rules/fields.yaml` |
| **4. The fact vocabulary and how facts are recognised.** Which facts exist, their types and allowed values, the complaint categories, and the plain-language definition of when a fact is true ("soaking a pad an hour"). | The inputs the criteria read; the lay instruments above | Authored: every fact has one name and one definition; the extractor's field list is rendered from the field file and the model may write nothing outside it | `rules/fields.yaml` (136 entries), `rules/vocabulary.yaml`, `rules/terms.yaml` |
| **5. The safety and provenance policy.** Every fact carries who said it and how certain (reported, probable, confirmed); safety rules act on confirmed facts only; a confirmation question before use; a later answer may never make a safety fact less urgent; the floor only rises; a diagnosis word from a caregiver is a cue to ask, never a fact. | Team decisions | Decided, then implemented; not derived from a source document | `prototype/engine.py` (status ladder, floor), `webapp/server.py` (safety-critical list, contradiction guard); the `confirmed`-status conditions in `criteria.yaml` |
| **6. Escalation and follow-up.** The only advice the chat may give (call 995) and when; what counts as getting worse in the waiting room; the check-in cadence. | ESI decision point A; team decision on the advice boundary | Decided, then implemented | `webapp/server.py` |
| **7. The nurse's page.** What the report shows and in what order: identity as declared and unverified, the floor with its rule and page, the AMPLE sections with a provenance chip per line, what was not collected, what changed since the last read. | AMPLE and SBAR handover formats; team decisions on provenance display | Layout derived from the facts by fixed program logic | `prototype/report.py`, `webapp/server.py` |

Items 5 to 7 are knowledge that lives in code; moving them into files is future work.

**Not part of the knowledge we engineered:** the trained classifier behind the practice signal
(`prototype/models/practice-signal.json` and `.joblib`). It is learned from the Yale visits and belongs to knowledge
discovery; it is evaluated, not reviewed. Likewise the test knowledge that judges the program rather than steering it:
`tests/v4_cases.yaml` and `tests/v4_posttest_cases.yaml` (the handbook's cases as facts), `prototype/personas.yaml`.

**How the seven connect.** Fields are the shared vocabulary: a question (3) fills fields (4), a bridge (2) derives a
field from fields, a criterion (1) reads fields, the page (7) shows fields, the policy (5) says which fields are
safety-critical. Those relations make the knowledge base a graph with fields as nodes; `rules/validate.py` checks that
every field a rule or bridge names is defined, and `rules/derive.py` computes the index of who reads and supplies each field.

## Every file of the knowledge engineering

Listed by role, whether or not the program reads it. A file is here if a person authored, transcribed, derived or
reviewed knowledge in it.

| Role | Files |
| --- | --- |
| **Extracted from sources** (a model reads the source and writes each entry with its page and quote; several runs or models compared; the quote checked mechanically) | `rules/criteria.yaml` (109 entries, 92 firing rules; every entry lists its supporting `statements` and `origin`), `rules/criteria-candidates.yaml`, `rules/bridges.yaml`, `rules/extraction/v5-complete-pass.yaml` (the complete reading pass: 137 statements with page and quote), the four blind re-extractions and their comparison in `rules/extraction/` |
| **Derived deterministically** (a fixed procedure computes it from the files above; never edited; `rules/derive.py --check` fails when stale) | `rules/derived/fields-index.yaml` (for each fact: which rules read it, who can supply it, bridges), `rules/derived/agenda.yaml` (what the interview may ask: 104 fields with priority, policy and gates), the field section of the extraction prompt (`prototype/extraction.py`, rendered at call time) |
| **Authored with added insight** (a choice no source makes) | `rules/fields.yaml` (every fact's name, meaning, everyday wording `ask`, ask policy), `rules/triggers.yaml` (the condition under which a question is asked, with its reason), `rules/terms.yaml` (the number, band or list behind a word the handbook uses without one), `prototype/extract_instructions.txt` (how to extract: true only when stated, false only when denied, deduced values probable); items 5 to 7 above, in code |
| **Schema and validation of the knowledge** | `rules/vocabulary.yaml` (the controlled vocabularies: every tag a rule or fact carries, each value with its meaning, what the program does with it, and an example), `rules/criteria.schema.json` (what a rule may contain; its enumerations must match the vocabulary), `rules/validate.py` (schema check, vocabulary check, quoted-span-on-page check) |
| **Sources the knowledge is taken from** | `sources/README.md` (the registry: what each source is, edition, how obtained), the guideline PDFs in `sources/`, `sources/download.sh` for the copyrighted handbook |
| **Rationale and provenance records** | the `why` line of each bridge in `rules/bridges.yaml`, `rules/v4-v5-diff-log.md` (where the two handbook editions differ and what we did), `rules/README.md` |
| **Review of the knowledge** | the review app `review/` and its design decisions `review/adr/`; the rulebook renderer `prototype/inspector.py` |
| **How the knowledge was extracted** (the experiment) | `experiments/rulegen/`: the drafters and modes, the seven draft rulebooks `out/criteria.draft.*.yaml`, the comparison `out/comparison.md` and the concept table `out/concepts.md` (drawn in August 2026 against the rulebook of that time; rule ids have been reorganised since, so the table is a record of the experiment, not a map of the current rules) |
| **Encoded test material** (transcribed by us from sources) | `tests/v4_cases.yaml` (the handbook's worked cases as facts and expected outcomes), `tests/v4_posttest_cases.yaml` (the Appendix A post-test questions, same format), `tests/test_v4_cases.py`, `tests/test_lay_bridges.py`, `prototype/personas.yaml`, `data/yale-persona-seeds.json` |
| **Mapping of the knowledge onto the data** | `data/yale-schema.md` (Yale columns to our fields, tiers of confidence), the mapping table in `experiments/task_g_full.py`, `experiments/task_g_coverage.py` |
| **Earlier versions kept for comparison** | `rules/criteria.v1-spike.yaml` (the August draft), `rules/criteria.v1-2026-08-29.yaml` (the first consolidated rulebook) |

**Review.** The review app covers the extracted files (1 and 2) and shows, per rule, each fact's meaning and where the
interview gets it; the other items are team decisions. The field file's everyday wordings have not had a nurse's read.

## Vocabulary

Terms are defined once, here; other documents use them without redefining them. The values a rule's tags may take
(decision point, assessed via, provenance, effect override) and the fact-status ladder are defined, with what the program
does with each value, in `rules/vocabulary.yaml`, which the validator enforces.

| Term | Meaning | Defined in |
| --- | --- | --- |
| **Field** | A named thing the fact store can hold. The prefix says its area: `danger_signs.`, `complaint.`, `E.` (events), `M.` (medications), `A.` (allergies), `history.`, `L.` (last meal), `infection.`, `stroke.`, `limb.`, `identity.`, `patient.`; `obs.`, `vitals.`, `resources.` can only come from a nurse. | `rules/fields.yaml` |
| **Fact** | A field with a value and its provenance: `status` (reported, probable, confirmed, unknown), `who`, `turn`, `ts`. | `prototype/engine.py` (`Facts`) |
| **Bridge** | A derivation from everyday-sign fields to the fact a rule reads, with a citation (`signs`), a count of such signs (`count`), or an entailment between two of our own facts (`entails`). | `rules/bridges.yaml` |
| **Rule (criterion)** | A condition over fields tagged with an ESI decision point, with page and quoted span. | `rules/criteria.yaml` |
| **Decision point** | A, B, C, D: the four steps of the ESI algorithm. A rule belongs to one; it does not produce one. | ESI handbook v5 |
| **Trigger** | The authored condition under which a question is asked (a fall opens the head-strike question). | `rules/triggers.yaml` |
| **Agenda** | The derived list of every field a caregiver can answer, with its priority, ask policy and gates; the interview control reads it. | `rules/derived/agenda.yaml` |

## 1. Extraction: answer to facts

Reads the caregiver's text and the question that was asked. Writes facts in the fixed schema rendered from the field
file; nothing outside that list can be written. Complaint details are attached to a complaint record (`about:` category)
so several complaints in one answer do not overwrite each other. *Neural; writes only the fields offered, with a quote;
decides nothing about the level or what is open.* `prototype/extraction.py`: the authored instructions in
`extract_instructions.txt` plus a field section rendered from `rules/fields.yaml` for the fields asked, open, always
allowed or volunteered-only this turn. A deduced value ("not pregnant" because the patient is 60) comes back with status
`probable`.

Post-processing in the intake app (`webapp/server.py`): invented categories collapsed onto the enumeration;
`E.mechanism=none` derived for non-injury complaints; a blanket "no" fills every field of the asked question; "I don't
know" closes the asked fields the answer did not fill as `unknown`; relative times ("10 mins ago") resolved to a timestamp
anchored on when it was said (`prototype/engine.py`, `resolve_relative_time`).

## 2. Fact store: write, derive, guard

- **Write** adds or replaces a fact with provenance. `complaint.pain_rating` also keeps a `pain_latest` trend copy.
  `engine.Facts.write`, `write_complaint`.
- **Derive** runs the bridges after every write: any stroke sign true gives `complaint.stroke_signs`; two eye findings give
  `complaint.atso_elements_count` = 2; a known anticoagulant name gives `M.anticoagulant confirmed`; age from the date of
  birth. `engine.derive`.
- **Safety guard** (intake app): a later answer that would make a safety-critical fact *less* urgent is not applied; the
  earlier value is kept and a "conflicting report" note goes on the report. A confirmed anticoagulant cannot be
  un-confirmed by a vaguer answer. `webapp/server.py` (`contradiction_guard`, `SAFETY_BOOL`).
- **Status ladder**: reported, probable, confirmed. Rules with safety consequences read `.status == confirmed` explicitly
  (for example B-30). A rule that needs `confirmed` gives the agenda a confirmation entry, asked alone while the status is
  `probable`. Fields with `alias_of` mirror each other; a named anticoagulant confirms `M.anticoagulant` whatever the
  extractor wrote.

## 3. Question selection: which field next

Deterministic, no model involved. The unit is the field, not a question. On every turn `engine.open_fields` walks the
derived agenda (`rules/derived/agenda.yaml`, one entry per field a caregiver can answer, in order) and keeps a field when:

1. it is not stored yet and has been asked fewer than three times;
2. its **ask policy** allows it: `always` (23 fields: the four danger signs, the complaint, age, sex, medicines, allergies,
   conditions, immune status, last meal, the infection screen, identity), `when_applicable` (its gate holds), or never for
   `volunteered_only` (16 fields such as sexual assault or an oxygen reading, written only if the caregiver brings them up);
3. its **trigger** holds: an authored condition in `rules/triggers.yaml` (fall height only after a fall; pregnancy only for a
   patient not known to be male, aged 10 to 59), or, where the field file gives none, a rule gate derived from the rules
   that read it (the field opens when such a rule is still possible and another of its facts is known).

Priority comes from the rules: 0 the danger screen; 1 a field three or more other fields' gates wait on (complaint, age,
sex, fever, mechanism); 2 a field some rule assigns a level on; 3 a field only consider flags or context notes read;
4 history and identity. Within a priority, more wanting rules first, then field-file order; `asked_with` places a
companion (date of birth after name, postpartum after pregnant) right after its anchor. A confirmation entry (a rule
needs the fact `confirmed`) is due while the status is `probable` and is asked alone. A model-free check of what the gates
let through, for every handbook case, is `experiments/reachability.py`.

## 4. Phrasing: fields to one question

Two modes, same selection. **Static**: the program bundles the top open field with the fields asked with it or of the same
topic and priority (up to four), and the language model words them in one plain sentence. **Dynamic** (`INTERVIEW_MODE=dynamic`,
the submitted setting): the model is given the top-ranked open fields with each field's everyday wording (`ask` in the field
file) and the known facts, and chooses which to bundle and how to say it; the top field is always included, and at most two
yes/no items go in one question; a confirmation or a re-ask is asked alone. The `ask` text is the reference wording of what a
field asks, not a script: the model writes its own question. Never assess, reassure or advise. *Neural; chooses the grouping
among the top-ranked open fields and the words; never what is open, never the level.* `engine.static_bundle`,
`webapp/server.py` (`pick_and_ask`, `pick_and_ask_dynamic`, `DYN_SYSTEM`).

## 5. Rule evaluation: facts to floor, indicators, flags

After every write, every rule is evaluated against the facts (`holds`: true, false, or not evaluable because a field is
missing). Outcome by decision point:

| Rule kind | Outcome |
| --- | --- |
| A (22 rules) | an **ESI-1 indicator** (immediate danger) |
| B (60) | the **floor** "at least ESI-2"; the same floor whether one or five fire |
| any rule with `effect_override: consider` (19) | a **consider flag** for the nurse's judgement; never moves the floor |
| D (10) | **pending**: vital-sign thresholds, which do not exist before arrival |

`engine.evaluate_tree` returns `{floor, fired, esi1_indicators, consider, pending}`. The floor only rises as facts arrive;
a corrected fact triggers a full re-evaluation.

## 6. Escalation and phases (intake app)

- **Escalation advice**: the only advice the chat may give. Fires once, on any ESI-1 indicator or when the caregiver reports
  the patient is not responding: "call 995 now if you are not already with paramedics". `esc_advice`.
- **Phases**: `enroute` until the family presses "We've arrived"; then `waiting`. That press also records a **baseline**
  (pain, floor, indicators, number of complaints). `do_arrived`. Opening the report changes nothing in the chat.
- **Check-ins**: in the waiting phase the chat asks "how is the patient now" every `CHECKIN_SECONDS`; stops after three
  unanswered, resumes when the family writes. `do_checkin`.
- **Worsening**: higher pain than baseline, a floor or indicator change, or a new complaint: a banner at the top of the
  report, and the family is asked to tell the counter staff. `worsening_check`.

## 7. Report rendering: facts to the nurse's page

Fixed program logic; the layout is derived from the facts, never designed per case.

- Identity as declared, marked not verified.
- Floor card: floor, fired rules with page and provenance class, pending decision points.
- **Practice signal** (learned lane): the pre-arrival classifier reads the same facts and gives one sentence about similar
  past visits; computed at render time, writes nothing to the engine. `prototype/practice_signal.py`.
- Consider flags; complaints in order reported; pain trend; AMPLE sections with a provenance chip per line; "not
  collected"; **changed since last opened** (facts written after the previous staff read).
- AI summary: one paragraph from the stored facts, shown only if every number in it appears in a stored fact.
  `webapp/server.py` (`render_html_report`, `summary_grounded`), `prototype/report.py` (text version).
