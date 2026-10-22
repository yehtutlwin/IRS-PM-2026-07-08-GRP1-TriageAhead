# Task I - persona runs through the real interview (20261015-2012)

Interview: mode dynamic, backend ollama (gemma4:12b). Persona played by ollama (gemma4:12b). Temperature: interview 0, persona 0 (the Claude API takes no temperature; its own default applies). 5 personas x 1 run(s). Tag: v2p-fair-local-interview-local-persona-t0

Floors 4/5 · expected rules 5/5 · extraction 30/35 (86%) · danger-sign misses 0 · questions 90 · re-asks 25

Wording audit: apologies 5 · caregiver addressed as the patient 0 · questions after the report not for the nurse 0 · reports that failed to render 0

| persona | run | floor | expected floor ok | rules ok | extraction | turns | questions | to report | re-asks | sorry | misses |
| --- | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| P1-fall-anticoag ([KOPI-8450](sessions-task-i-20261015-2012-v2p-fair-local-interview-local-persona-t0/KOPI-8450.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 9/9 | 19 | 19 | 15 | 4 | 2 |  |
| P3-abdo-pregnant ([VANDA-7481](sessions-task-i-20261015-2012-v2p-fair-local-interview-local-persona-t0/VANDA-7481.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/6 | 22 | 22 | 13 | 9 | 1 | complaint.fever: want=False got=None |
| P6-stroke-resolved ([ORCHID-7944](sessions-task-i-20261015-2012-v2p-fair-local-interview-local-persona-t0/ORCHID-7944.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 4/6 | 17 | 17 | 16 | 6 | 1 | stroke.speech_change: want=True got=None; stroke.arm_weakness: want=True got=None |
| P6-acute-gout ([RAFFLES-1596](sessions-task-i-20261015-2012-v2p-fair-local-interview-local-persona-t0/RAFFLES-1596.transcript.txt)) | 1 | - | yes | yes | 5/7 | 19 | 19 | 17 | 5 | 1 | complaint.trauma: want=False got=None; history.gout: want=True got=None |
| P9-breathing-no-pain ([LOTUS-1424](sessions-task-i-20261015-2012-v2p-fair-local-interview-local-persona-t0/LOTUS-1424.transcript.txt)) | 1 | at least ESI-2 | NO | yes | 7/7 | 13 | 13 | 11 | 1 | 0 |  |
