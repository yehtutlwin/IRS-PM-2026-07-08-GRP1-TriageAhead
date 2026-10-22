# Task I - persona runs through the real interview (20261016-0117)

Interview: mode dynamic, backend ollama (gemma4:12b). Persona played by sheet (answer-sheet replay (no model)). Temperature: interview 0, persona backend default (the Claude API takes no temperature; its own default applies). 10 personas x 1 run(s). Tag: v2r-sheet-player-local-interview-t0

Floors 9/10 · expected rules 8/10 · extraction 55/72 (76%) · danger-sign misses 0 · questions 157 · re-asks 20

Wording audit: apologies 10 · caregiver addressed as the patient 0 · questions after the report not for the nurse 0 · reports that failed to render 0

| persona | run | floor | expected floor ok | rules ok | extraction | turns | questions | to report | re-asks | sorry | misses |
| --- | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| P1-fall-anticoag ([TIGER-7092](sessions-task-i-20261016-0117-v2r-sheet-player-local-interview-t0/TIGER-7092.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 9/9 | 16 | 16 | 12 | 0 | 3 |  |
| P2-chest-pain ([PANDA-2043](sessions-task-i-20261016-0117-v2r-sheet-player-local-interview-t0/PANDA-2043.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/6 | 14 | 14 | 12 | 2 | 1 |  |
| P3-abdo-pregnant ([SAGA-2718](sessions-task-i-20261016-0117-v2r-sheet-player-local-interview-t0/SAGA-2718.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/6 | 20 | 20 | 12 | 5 | 0 | complaint.fever: want=False got=None |
| P4-sore-throat ([KOPI-7784](sessions-task-i-20261016-0117-v2r-sheet-player-local-interview-t0/KOPI-7784.transcript.txt)) | 1 | - | yes | yes | 5/5 | 17 | 17 | 16 | 3 | 0 |  |
| P6-stroke-resolved ([DURIAN-7302](sessions-task-i-20261016-0117-v2r-sheet-player-local-interview-t0/DURIAN-7302.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/6 | 15 | 15 | 14 | 2 | 0 |  |
| P5-fever-chemo ([ORCHID-5048](sessions-task-i-20261016-0117-v2r-sheet-player-local-interview-t0/ORCHID-5048.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/5 | 13 | 13 | 7 | 0 | 1 |  |
| P6-acute-gout ([LION-2011](sessions-task-i-20261016-0117-v2r-sheet-player-local-interview-t0/LION-2011.transcript.txt)) | 1 | - | yes | yes | 5/7 | 14 | 14 | 12 | 1 | 1 | complaint.trauma: want=False got=None; history.gout: want=True got=None |
| P7-heat-stroke ([HERON-9049](sessions-task-i-20261016-0117-v2r-sheet-player-local-interview-t0/HERON-9049.transcript.txt)) | 1 | at least ESI-2 | NO | NO | 1/8 | 19 | 19 | 9 | 4 | 2 | danger_signs.responsive: want=True got=False; danger_signs.altered_mental_status: want=True got=None; complaint.collapse: want=True got=None; complaint.vomiting |
| P8-decompensated-liver-disease ([ORCHID-4298](sessions-task-i-20261016-0117-v2r-sheet-player-local-interview-t0/ORCHID-4298.transcript.txt)) | 1 | at least ESI-2 | yes | NO | 5/12 | 14 | 14 | 11 | 1 | 2 | danger_signs.altered_mental_status: want=True got=None; complaint.hematemesis: want=False got=None; complaint.melena: want=False got=None; history.cirrhosis: wa |
| P9-breathing-no-pain ([HERON-2230](sessions-task-i-20261016-0117-v2r-sheet-player-local-interview-t0/HERON-2230.transcript.txt)) | 1 | - | yes | yes | 8/8 | 15 | 15 | 13 | 2 | 0 |  |
