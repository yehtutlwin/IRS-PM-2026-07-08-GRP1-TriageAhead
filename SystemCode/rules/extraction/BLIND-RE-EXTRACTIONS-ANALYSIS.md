# Four blind re-extractions of the handbook next to the current rules file

Process: extracted from sources. Analysis written by Claude Code (an AI agent); no clinician has read it.
**Applied on 5 Oct 2026** to [criteria.yaml](../criteria.yaml), with two exceptions found while applying (B-29 and B-28 kept
unchanged because the handbook's practice cases support the stronger reading).

A *blind re-extraction* is one model reading the ESI Handbook, fifth edition, and writing rules from it without seeing our rules
file. Four were made, from three providers:

| Blind re-extraction | Provider | How | Coverage | Entries | Quotes found word for word on the page |
| --- | --- | --- | --- | ---: | --- |
| [blind-re-extraction-opus](blind-re-extraction-opus/rules.yaml) | Anthropic (Claude Opus) | agent session | all pages | 415 | all |
| [blind-re-extraction-fable](blind-re-extraction-fable/rules.yaml) | Anthropic (Claude Fable 5.1) | agent session | all pages | 335 | all |
| [blind-re-extraction-gemini](blind-re-extraction-gemini/rules.yaml) | Google (Gemini 3.1 Pro) | [blind_re_extraction_other.py](blind_re_extraction_other.py), 11 calls | all pages | 318 | 211 of 318 |
| [blind-re-extraction-gpt](blind-re-extraction-gpt/rules.yaml) | OpenAI (Codex default model, free account) | [blind_re_extraction_other.py](blind_re_extraction_other.py), 8 calls | printed pages 1 to 20 only; the account's usage limit stopped the run before pages 23 to 30 | 282 | 220 of 282 |

Gemini and GPT often shorten a quote with "..." or copy a table cell, so their quotes fail the word-for-word check more
often; the comparison matches on overlapping words and still places most of them. Gemini returned no fact definitions,
only fact names inside its rules.

The rule-by-rule table is [blind-re-extractions-comparison.md](blind-re-extractions-comparison.md), produced by
[compare_blind_re_extractions.py](compare_blind_re_extractions.py). Matching is by page and overlapping quote, so a cell can pick up the
neighbouring sentence; every finding below was read against the entries themselves.

## What the four blind re-extractions say

**Agreement.** Of our 92 firing rules, 64 have the same effect in every blind re-extraction that has an entry for the sentence.
All level 1 rules, all vital-sign tables, the fever rules for children and the named mechanisms of injury are in this
group. No blind re-extraction found a firing rule we lack, apart from sentences that restate a rule we already have (figure labels,
the appendix summary).

**Agreed by all four blind re-extractions: our rule is stronger than the sentence.**

| Rules | Ours | Blind re-extractions | Why |
| --- | --- | --- | --- |
| B-17, B-18, B-19, B-20 (abdominal pain with pregnancy, sepsis signs, trauma, constant maximal pain) | assign level 2 | consider level 2: 4 of 4 | the handbook lists questions for the nurse to ask; it does not say an answer assigns a level |
| B-21 (abdominal pain with vaginal bleeding) | assign level 2 | consider or context: 3 of 3 | same passage |
| B-23 (penetrating trauma, stable) | assign level 2 | consider level 2: 3 of 3 | "may include" |
| B-29 (child with subtle change in mental state) | assign level 2 | consider: 3 of 4 (Gemini: assign, marked as its own inference) | "investigated as high risk" |

**Agreed by all four blind re-extractions: the sentence is background, not a rule.** B-52 (older adults, vital signs and medication),
B-53 (signs of respiratory distress in children), B-55 (recent COVID), D-04 (beta-blockers), D-05 (immunosuppression),
B-27 (trauma in older adults; one of three keeps it as consider), B-28 (eye complaints; one has an entry).
Every blind re-extraction that has an entry files these as context, definition or usage. They inform how the nurse reads other
findings and do not raise a level on their own.

**Split: needs a clinician.**

| Rule | Ours | Blind re-extractions | The question |
| --- | --- | --- | --- |
| B-35 (severe psychological distress) | consider level 2 | Opus and Gemini: assign; Fable: consider; GPT: the list is examples only | does one listed behaviour (for example an acute grief reaction) by itself put a patient at level 2? |
| B-25 (possible pelvis or femur fracture, dislocation) | consider level 2 | Opus and Fable: consider; GPT and Gemini: no level named | "carefully evaluated and vital signs considered" |
| B-48 (unexplained change in mental state, breathing or heart rate) | consider level 2 | Fable: consider; Opus, GPT, Gemini: no level named, "evaluated as a possible toxic ingestion" | whether the possibility alone is a flag |

**The level is the blind re-extraction's inference, not the handbook's words** (all four mark it so; the effect is not in dispute):
B-16 button battery, B-24, B-26, B-46, B-47 (limb and ingestion emergencies), B-32 thunderclap headache, B-04 to B-07,
B-10, B-12, B-33 (the examples list). These should carry `origin` showing that the level comes from the section they
sit in, not from the sentence.

**Facts, agreed by the two blind re-extractions that defined facts carefully (Opus, Fable) and not contradicted by the other two:**
pregnant and postpartum are separate facts (our single fact widens B-38 and B-39); suicidal and homicidal are separate;
nosebleed (B-15) needs brisk bleeding in every branch.

## What this means for the rules file

1. Change effect to consider: B-17, B-18, B-19, B-20, B-21, B-23, B-29.
2. Move out of the firing rules into context entries: B-27, B-28, B-52, B-53, B-55, D-04, D-05.
3. Ask a clinician: B-35, B-25, B-48.
4. Mark inferred levels on the rules listed above.
5. Split the bundled facts.

Items 1 and 2 lower what the engine asserts. They do not remove information from the nurse report if context entries
are still shown as notes.

## Limits

Three providers, but one handbook text file and one prompt design (written by Claude) for Gemini and GPT; a
shared misreading caused by the prompt would not show. GPT did not read pages 23 to 30 (children, FAQ, appendix).
Agreement between models is evidence about what the text says, not about what is clinically right.
