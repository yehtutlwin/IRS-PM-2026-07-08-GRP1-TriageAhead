# Installation and user guide

Everything runs locally on Linux, macOS, or Windows via WSL2 (see
[platform-setup.md](platform-setup.md) for the platform part). Python 3.10+. All commands are run from the `SystemCode` folder of the submission repository.

## 1. Install (once)

```bash
cd SystemCode
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
bash sources/download.sh          # the copyrighted handbook PDF, fetched per person
cp .env.example .env              # then choose a language-model backend (below)
```

Language-model backend - one of three (`LLM_BACKEND` in `.env`; the same interview runs on each, see
[experiments/out/interview-v2-backends.md](../experiments/out/interview-v2-backends.md) for how they compare):

- **Gemini free tier** (recommended; no GPU needed): a key from <https://aistudio.google.com/apikey> as `GEMINI_API_KEY` in `.env`. What we measured
  on 15 Oct 2026: the backend walks a list of models and switches when one is overloaded or at its daily limit;
  a session takes about twenty minutes at the free tier's pacing, one key gives about a session and a half a day, and in
  the Singapore night nothing answered. Good for one demo session in the afternoon, not for testing.
- **Local, no quota** (the alternative, for a machine with a GPU): install [Ollama](https://ollama.com/download), run `ollama pull gemma4:12b`
  (about 7 GB to download; needs about 8 GB of GPU memory, or 16 GB of unified memory on a Mac; on a CPU alone it runs
  but a turn takes a minute or more), and put `LLM_BACKEND=ollama` in `.env`. A turn takes five to ten seconds on a
  desktop GPU.
- **Claude** (Anthropic API, paid): `LLM_BACKEND=claude` and `ANTHROPIC_API_KEY` in `.env` (`CLAUDE_MODEL`, default
  `claude-opus-5-5`). About $0.50 to $0.60 a session; the fastest and the most complete reading of short answers in our runs.

## 2. The intake app (caregiver chat + nurse report)

```bash
.venv/bin/python webapp/server.py        # -> http://localhost:8090
bash webapp/run.sh                       # the same, plus a public https address so a phone can scan the QR code
```

The script opens a Cloudflare "quick tunnel" to your machine: no account, no key, a fresh random https address every start. It
needs only the [cloudflared](https://github.com/cloudflare/cloudflared/releases) binary (macOS `brew install cloudflared`; Debian/Ubuntu,
and Windows under WSL2, the amd64 .deb from that page). It prints the address and a QR code of it in the terminal. The app builds every link and QR code from the address the browser used, so nothing else is
configured. Ctrl-C stops the app and the tunnel. Anyone with the address can open the chat while it runs, so stop it after the test.

| Who | Open | What happens |
| --- | --- | --- |
| Caregiver | `/` | The gate question ("Is an ambulance on the way, or are you already heading to the ED?"). *Yes* creates a ticket (e.g. `LION-3407`) and opens the chat. |
| Caregiver | `/chat/<TICKET>` | Answer in free text in any language, as short as you like. The only advice the app ever gives is to call 995. As soon as the questions that settle the urgency floor are answered (about a dozen), it says the hospital team has enough and a header button shows the ticket, the QR code and the report link; a few more questions for the nurse follow. The floating button "We've arrived at the hospital" starts the waiting-room check-ins. |
| Nurse / doctor | `/r/<TICKET>` (scan the QR) | The one-page report: declared identity (unverified), the urgency floor with the cited rules, complaints, AMPLE sections with who-said-what chips, an AI summary written from the stored facts only. Opening it changes nothing in the chat. |
| Team | `/rules` | The rulebook, human-readable. |

After the family presses "We've arrived" the chat checks in every fifteen minutes ("How is the patient doing right now
compared to when you arrived?"); a worsening answer puts a banner on the report and asks the family to tell the counter.
Opening the report changes nothing in the chat.

Sessions are written to `prototype/out/sessions-local/` as three files per ticket: `<TICKET>.transcript.txt`, `<TICKET>.log.jsonl`
(the event log) and `<TICKET>.json` (the state). The folder is ignored by git.

Command-line equivalent, same engine: `cd prototype && python3 cli.py chat mysession`;
`python3 run.py dry` runs the engine-only demo without any language model.

## 3. The rule review app

```bash
.venv/bin/python review/app.py           # -> http://localhost:8091
```

Type your name once. For each rule: read the handbook page rendered on the right (the
quoted span is highlighted where found), pick accept / edit / reject / unsure, say what you
checked. Verdicts are appended to `review/reviews.db`; export with
`.venv/bin/python review/app.py export` -> `review/out/review-log.jsonl`. The design decisions of the app are in `review/adr/`.

## 4. Experiments (reproducible; committed outputs in `experiments/out/`)

```bash
bash data/download-yale.sh                             # ~99 MB
.venv/bin/python data/convert-yale.py                  # once: .rdata -> Parquet
.venv/bin/python experiments/task_g_full.py            # rulebook vs practice, two arms (~4 min)
.venv/bin/python experiments/task_h_learned_comparator.py   # learned comparator (~5 min)
.venv/bin/python experiments/task_g_coverage.py        # which rules the dataset can test
.venv/bin/python experiments/tree_vs_rules.py          # learned tree vs rulebook structure
.venv/bin/python -m pytest tests/                      # encoding fidelity: handbook practice cases
```

## 5. Troubleshooting

- *The chat says nothing / very slow first turn*: the local model is loading into GPU memory
  (30-90 s the first time); `ollama ps` should show `100% GPU`.
- *Blank questions*: the model returned an empty answer - on Ollama make
  sure thinking is off (the default in `prototype/llm_ollama.py`).
- *Review app shows "PDF not present locally"*: run `bash sources/download.sh`.
- *No highlight on a handbook page*: the quoted span is not on that page as quoted - record
  that in the review; it is a finding about the rule, not the app.
