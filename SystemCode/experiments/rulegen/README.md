# rulegen: schema-constrained rule extraction (the August 2026 experiment)

The experiment that produced the first drafts of the rulebook, kept as a record. A language model reads one handbook page
(or the whole handbook) and must return rule entries that conform to `rules/criteria.schema.json`; every draft then passes
three mechanical gates: schema validation, the quoted span found verbatim on the cited page, and a match against the
reviewed rulebook of the time. Nothing a drafter produced entered `rules/criteria.yaml` without a human reading of the page.

The rule ids in the outputs are those of August 2026; the rulebook has been reorganised since, so the tables are a record
of the experiment, not a map of the current rules.

| File | What it is |
| --- | --- |
| `rulegen.py` | the per-page and whole-document drafters (Gemini API), with the three gates |
| `agentic.py` | the agentic drafter: a model with tools, in a workspace that holds only the PDF, the page texts, the schema and the instructions |
| `drafters.py`, `backends.py` | the model backends and the drafting prompts |
| `compare.py` | the three-way comparison of the drafts against the reviewed rulebook (`out/comparison.md`) |
| `relate.py` | the relation graph over every drafted rule: identical, same span, same logic, split, related; writes the concept table `out/concepts.md` (the interactive graph it can also draw is not kept in the repository) |
| `build_review.py`, `review.template.html` | the page that showed the drafts beside their handbook page for the first review |
| `out/criteria.draft.*.yaml` | the seven draft rulebooks, one per drafter and mode |
| `out/runs/` | one log per run with its metrics; the per-run workspaces with the handbook page texts and the agents' command transcripts are not kept |
| `out/QWEN-*.md`, `out/qwen-*.md` | the October run of the same pipeline on a small local model (Qwen 3 14B), reported on the evaluation results page |

## Results

**Per-page against whole-document**, same model (Gemini 3.6 Flash), same schema, same gates:

| Mode | Calls | Drafted | Schema-valid | Span found on the page | Re-found of 47 reviewed rules in scope | Novel |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| per-page, with a 600-character overlap across page breaks | 9 | 68 | 68 of 68 | 68 of 68 | 33 | 28 |
| whole document, plain prompt | 1 | 13 | 12 of 13 | 12 of 12 | 10 | 3 |
| whole document, "enumerate, do not summarise" | 1 | 38 | 37 of 38 | 37 of 37 | 25 | 12 |

**Six drafters, one schema, one set of gates:**

| Drafter | Mode | Drafts | Schema-valid | Span found | Re-found of 47 | Invented field names |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Gemini API, 3.6 Flash | per-page | 68 | 68 of 68 | 68 of 68 | 33 | 6 (category labels as facts, rejected) |
| Gemini 3.6 Flash, command-line client | per-page | 75 | 75 of 75 | 75 of 75 | 34 | 0 |
| Gemini 3.1 Pro, command-line client | per-page | 93 | 93 of 93 | 93 of 93 | 39 | 17 (one boolean per complaint, rejected) |
| Gemini 3.6 Flash, agentic | clean workspace | 84 | 84 of 84 | 84 of 84 | 35 | 1 (`vitals.sbp`, legitimate) |
| Gemini 3.1 Pro, agentic | clean workspace | 52 | 52 of 52 | 52 of 52 | 27 | 0 |
| Gemini API, 3.6 Flash | whole document | 37 | 37 of 38 | 37 of 37 | 25 | 0 |

Over all 468 drafts the concept table groups 111 concepts; only 11 criteria were found by a single drafter.

What the runs showed:

1. **The gates hold for every drafter.** Zero span failures across six configurations once a bug in our own id pattern was
   fixed, and the models' page citations were correct in every whole-document and agentic run.
2. **A stronger model finds more and obeys less.** The Pro model re-found the most reviewed rules and produced the most new
   candidates, but invented 17 field names and labelled a third of its drafts "operationalised" without a note. Review load
   grows with capability.
3. **Whole-document extraction under-generates; per-page over-covers; agentic sits between.** The modes' unique finds
   differ: whole-document reading sees the algorithm figure and the fever table that text extraction mangles, per-page
   reading covers the prose. The pipeline is therefore the union of the drafts, de-duplication through the concept table,
   and human review of every draft.
4. **Passing both mechanical gates is not correctness.** A draft can quote the page verbatim and validate, yet drop two
   items of the list the sentence gives; only the human page check catches that.
5. **An agent's self-report is not evidence.** Two agentic runs claimed to have written entries that no file held; the
   run's command transcript, not its summary, is the record.
