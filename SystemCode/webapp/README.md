# webapp: the pre-arrival intake app

One process serves the whole flow on port 8090, reusing the prototype modules
unchanged (`cli` interview steps, `engine`, `report`, `llm`, the rules inspector):

| Path | Who | What |
| --- | --- | --- |
| `/` | caregiver | post-decision gate, then a new session + chat |
| `/chat/<TICKET>` | caregiver | the chat: gap-driven questions, 995-only advice: two stages, the ticket + QR (with a clickable link) as soon as the floor-setting questions are closed, the rest of the questions after; a status line while a turn is slow |
| `/r/<TICKET>` | nurse/doctor | the report, staff-only: floor + citations, practice signal (one sentence), provenance chips, AI summary (numbers checked against the facts); opening it changes nothing in the family's chat (the family's own 'we've arrived' button starts the waiting-room phase); worsening banner |
| `/qr/<TICKET>.svg` | — | QR of the report link (segno) |
| `POST /api/arrived/<TICKET>` | chat page | the family's 'we've arrived' button: starts the waiting-room phase (periodic check-ins) and records the baseline for the worsening banner |
| `POST /api/answer/<TICKET>` | chat page | `{text}` -> `{replies, done, complete, asked}`: `done` = the report is ready (QR shown), `complete` = nothing more to ask, `asked` = the fields the open question asks |
| `GET /api/state/<TICKET>` | chat page | messages, `phase` (enroute / waiting), `stage` (floor / rest), `done`, `complete`, `asked`, `status` (what the server is doing with the last answer, with the model provider's rate-limit state when any) |
| `/about-signal` | staff | what the practice signal is, its bands and its figures |
| `/rules` | team | the rulebook inspector page |

Run locally: `.venv/bin/python webapp/server.py` (LLM_BACKEND=ollama recommended); `bash webapp/run.sh`
adds a throwaway Cloudflare quick tunnel (no account; needs the cloudflared binary) and prints its address as a QR code, for scanning from a phone.
Sessions go to the gitignored `prototype/out/sessions-local/`.
Check-in cadence: `CHECKIN_SECONDS` (default 900; set 60 for demos).
