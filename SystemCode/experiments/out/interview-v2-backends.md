# Interview design v2 on three model backends: the same five personas

The five hardest personas of `prototype/personas.yaml` (a fall on a blood thinner that needs the confirmation question; abdominal
pain in pregnancy; stroke signs that have passed; acute gout, which must not set a false floor; the no-pain breathing case)
played through the real web interview by the persona harness, with the interview design as submitted (two stages, dynamic
grouping with at most two yes/no items per question). Rows link to the run reports, which link to every
session transcript. The index of all runs is `RUNS.md`.

## The controlled comparison (15 Oct 2026, evening)

Only the interview model differs between the two rows. The persona player is the local model at temperature 0 in both; the
local interview runs at temperature 0; the Claude API takes no temperature setting, so Claude runs at its fixed default, which
is the one thing that cannot be matched. One run each.

| Interview model | Expected floor reached | Expected rule fired | Facts captured (number 2) | Questions before the report, mean | Questions in all | Re-asks | Cost | Run |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| gemma4:12b, local (Ollama), temperature 0 | 4 of 5 | 5 of 5 | 30 of 35 (86%) | 14.4 | 90 | 25 | GPU time | [v2p](task-i-20261015-2012-v2p-fair-local-interview-local-persona-t0.md) |
| Claude Opus 5.5 (Anthropic API), default sampling | 4 of 5 | 5 of 5 | 29 of 35 (83%) | 10.8 | 79 | 12 | $2.67 interview | [v2q](task-i-20261015-2026-v2q-fair-claude-interview-local-persona-t0.md) |

What the two rows say:

- **Facts captured are the same within one.** The ceiling on these sheets is 33: the gout persona's history of gout and denial of
  injury have no field. Both models also miss the pregnancy persona's denial of fever, and both miss the stroke persona's resolved
  signs when the caregiver volunteers them in the complaint answer (stored as the complaint flag, not as the sign
  fields, and never asked once the floor rule has fired). Claude's one extra miss is that persona's fever question, which its
  shorter interview never reached. The stronger model does not read more facts.
- **Questions and re-asks are where the models differ.** Claude needed 10.8 questions to the report against 14.4, 79 in all against
  90, and re-asked 12 times against 25. The local model's re-asks are first-answer misses, an item of a two-item question not
  written, each costing one question.
- **The floor each missed is a different one, and both are instructive.** The local model set a floor on the breathing persona
  because the player answered yes to whether the breathing was still getting worse, which the sheet leaves open (the sheet expects
  no floor; its purpose is the pain denial). Claude set a floor on the gout persona: asked whether the patient was "more confused,
  more sleepy, or just not like yourself", the player said "not feeling like myself because of this pain, tired and irritable",
  Claude wrote the altered-mental-status field true and rule B-01 fired. The field's definition and question named "not themselves";
  both were tightened the same evening. The local model had phrased the same question as "more confused or
  sleepy" and stored false.
- **The wording audit** flagged one Claude question as addressing the caregiver as the patient; the line is "if you took his
  temperature", a false match of the audit's pattern, not a fault.
- **What a run costs on Claude**: about $0.53 a session for the interview at the list prices of 14 Oct 2026 (no prompt caching: it
  cost more than it saved in a first attempt, because the prompt changes with the open fields every turn).

## Earlier, uncontrolled rows (15 Oct 2026, morning and afternoon)

Kept for the record. The first two rows differ in two things at once, the interview model and the persona player (Claude Sonnet 5.5
played the caregiver in the Claude row), and ran at the backends' default temperatures; the numbers are not a comparison of the
interview models alone.

| Interview model | Persona player | Expected floor reached | Expected rule fired | Facts captured | Questions before the report, mean | Questions in all | Re-asks | Cost | Run |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| gemma4:12b, local (Ollama) | gemma4:12b, local | 5 of 5 | 5 of 5 | 33 of 35 (94%) | 14 | 112 | 33 | GPU time | [v2i](task-i-20261015-0031-v2i-interview-v2-dynamic.md) (the five rows of the ten) |
| Claude Opus 5.5 (Anthropic API) | Claude Sonnet 5.5 | 4 of 5 | 4 of 5 | 33 of 35 (94%) | 11 | 96 | 15 | $3.04 interview + $0.17 persona | [v2j](task-i-20261015-0047-v2j-claude-opus-interview-sonnet-persona.md) |
| Gemini, free tier (gemini-2.5-flash, the only one of six listed models that answered) | gemma4:12b, local | 1 of 1 completed (the run died in the second persona) | 1 of 1 | 9 of 9 on the one persona (3 of 6 in the aborted second) | 10 | 16 | 4 | free | four attempts, 15 Oct: three in the Singapore night got no session out (every model overloaded, then the quota); the one after the 3 pm reset completed the fall persona in 22 minutes and died on the daily quota in the second; sessions in [sessions-task-i-20261015-1523-v2m-gemini-free-tier-interview-local-persona/](sessions-task-i-20261015-1523-v2m-gemini-free-tier-interview-local-persona/) |

What the Gemini row says: the free tier can run the interview, with the same floor and the same nine facts as the other two
backends on the fall persona and the report ready after ten questions, but a session takes twenty minutes at the free tier's
pacing and the day's quota on one key is spent after about a session and a half. For a demo that is one session per key per
afternoon, with the local model as the fallback the backend already supports.

Caveats, as in the evaluation plan: one run per configuration, and the consistency run of the same evening (v2o, five personas
three times on the local model) puts run-to-run variation at one or two facts with the floor unchanged, so a difference of one
fact between rows means nothing; all ten persona sheets are the builder's; the persona player is a model, not a
person, so the sentences it produces are tidier than a real caregiver's.
