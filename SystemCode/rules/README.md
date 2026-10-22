# rules/ — the knowledge base

The files the system reads to decide what to ask and what the answers mean. How each file was made and reviewed is in [docs/knowledge-base.md](../docs/knowledge-base.md).

| File | What it holds |
| --- | --- |
| `criteria.yaml` | The triage criteria: each ESI decision-point condition with its page, quoted span and provenance class. Validated by `validate.py`. |
| `criteria.schema.json` | What a rule entry may contain. |
| `fields.yaml` | Every fact the interview can hold: name, meaning, everyday wording, ask policy. |
| `bridges.yaml` | How everyday signs a caregiver reports map to the clinical fact a rule reads, with citations. |
| `triggers.yaml` | The authored condition under which a question is asked (a fall height only after a fall). |
| `terms.yaml` | The number, band or list the system assigns to a word the handbook uses without one. |
| `vocabulary.yaml` | The controlled vocabularies: every tag a rule or fact carries, with its meaning. |
| `derived/` | `fields-index.yaml` and `agenda.yaml`, computed from the files above by `derive.py` and never edited (`derive.py --check` fails when stale). |
| `validate.py` | Checks the rulebook: schema, unique ids, every quoted span found on its cited handbook page. |
| `extraction/` | The complete reading pass of the handbook and the four blind re-extractions compared against the rulebook. |
| `criteria-candidates.yaml` | Rules drafted from the CDC and NICE sources, not reviewed and not in the tested set. |
| `v4-v5-diff-log.md` | Where the two handbook editions differ and what was done about it. |
| `criteria.v1-spike.yaml`, `criteria.v1-2026-08-29.yaml` | Earlier versions kept for comparison. |
