# System code

The runnable system, its knowledge files, tests and experiments. The installation and user guide is `docs/install-and-user-guide.md` (also Appendix C of the group report).

| Folder | What it holds |
| --- | --- |
| `webapp/` | The web application: the caregiver chat, the staff-only nurse report behind the QR code, the rulebook page. `python webapp/server.py` |
| `prototype/` | The rule engine, interview controller, fact extraction and guard, language-model backends, personas and the practice signal |
| `rules/` | The knowledge base: rules (`criteria.yaml`), fields, bridges, triggers, terms and options, the derived agenda, the validator and the extraction prompts |
| `tests/` | The handbook's practice cases as tests, plus engine, bridge and agenda tests (`python -m pytest tests/`) |
| `experiments/` | Every evaluation number as a script with a fixed seed; outputs and session records under `experiments/out/` |
| `review/` | The team's review site for reading each rule beside its source page |
| `data/` | Scripts for the Yale ED dataset (the dataset itself is downloaded per person; see `data/README.md`) |
| `sources/` | The cited guidelines; `sources/download.sh` fetches the copyrighted handbook per person |
| `guide/` | The setup guide: `python3 guide/start.py` from the repository folder checks what the machine has and shows the next command, section by section |
| `docs/` | The architecture document, the knowledge-base document, the evaluation results page, the installation and user guide and the platform setup notes |

Copy `.env.example` to `.env` and choose a language-model backend before running; no key is needed for the local backend.
