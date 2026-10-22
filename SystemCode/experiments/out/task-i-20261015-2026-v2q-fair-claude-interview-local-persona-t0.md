# Task I - persona runs through the real interview (20261015-2026)

Interview: mode dynamic, backend claude (claude-opus-5-5). Persona played by ollama (gemma4:12b). Temperature: interview backend default, persona 0 (the Claude API takes no temperature; its own default applies). 5 personas x 1 run(s). Tag: v2q-fair-claude-interview-local-persona-t0 Tokens: interview 472,438 in / 38,895 out, about $2.67; persona about $0.00 (prices of 14 Oct 2026).

Floors 4/5 · expected rules 5/5 · extraction 29/35 (83%) · danger-sign misses 0 · questions 79 · re-asks 12

Wording audit: apologies 0 · caregiver addressed as the patient 1 · questions after the report not for the nurse 0 · reports that failed to render 0

| persona | run | floor | expected floor ok | rules ok | extraction | turns | questions | to report | re-asks | sorry | misses |
| --- | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| P1-fall-anticoag ([MERLION-8874](sessions-task-i-20261015-2026-v2q-fair-claude-interview-local-persona-t0/MERLION-8874.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 9/9 | 20 | 20 | 13 | 4 | 0 |  |
| P3-abdo-pregnant ([OTTER-9597](sessions-task-i-20261015-2026-v2q-fair-claude-interview-local-persona-t0/OTTER-9597.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/6 | 19 | 19 | 10 | 4 | 0 | complaint.fever: want=False got=None |
| P6-stroke-resolved ([EAGLE-1162](sessions-task-i-20261015-2026-v2q-fair-claude-interview-local-persona-t0/EAGLE-1162.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 3/6 | 11 | 11 | 6 | 0 | 0 | stroke.speech_change: want=True got=None; stroke.arm_weakness: want=True got=None; complaint.fever: want=False got=None |
| P6-acute-gout ([TIGER-6270](sessions-task-i-20261015-2026-v2q-fair-claude-interview-local-persona-t0/TIGER-6270.transcript.txt)) | 1 | at least ESI-2 | NO | yes | 5/7 | 14 | 14 | 12 | 2 | 0 | complaint.trauma: want=False got=None; history.gout: want=True got=None |
| P9-breathing-no-pain ([DURIAN-8332](sessions-task-i-20261015-2026-v2q-fair-claude-interview-local-persona-t0/DURIAN-8332.transcript.txt)) | 1 | - | yes | yes | 7/7 | 15 | 15 | 13 | 2 | 0 |  |
