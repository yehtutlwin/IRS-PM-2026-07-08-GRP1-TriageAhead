# Task I - persona runs through the real interview (20261016-0150)

Interview: mode dynamic, backend ollama (gemma4:12b). Persona played by sheet (answer-sheet replay (no model)). Temperature: interview 0, persona backend default (the Claude API takes no temperature; its own default applies). 5 personas x 3 run(s). Tag: v2s-sheet-player-consistency-3-runs-local-t0

Floors 15/15 · expected rules 15/15 · extraction 96/108 (89%) · danger-sign misses 0 · questions 232 · re-asks 35

Wording audit: apologies 11 · caregiver addressed as the patient 0 · questions after the report not for the nurse 0 · reports that failed to render 0

| persona | run | floor | expected floor ok | rules ok | extraction | turns | questions | to report | re-asks | sorry | misses |
| --- | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| P1-fall-anticoag ([LION-5474](sessions-task-i-20261016-0150-v2s-sheet-player-consistency-3-runs-local-t0/LION-5474.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 9/9 | 15 | 15 | 12 | 0 | 2 |  |
| P1-fall-anticoag ([RAFFLES-6092](sessions-task-i-20261016-0150-v2s-sheet-player-consistency-3-runs-local-t0/RAFFLES-6092.transcript.txt)) | 2 | at least ESI-2 | yes | yes | 9/9 | 18 | 18 | 14 | 0 | 2 |  |
| P1-fall-anticoag ([TIGER-3275](sessions-task-i-20261016-0150-v2s-sheet-player-consistency-3-runs-local-t0/TIGER-3275.transcript.txt)) | 3 | at least ESI-2 | yes | yes | 9/9 | 16 | 16 | 12 | 0 | 2 |  |
| P3-abdo-pregnant ([KOPI-9154](sessions-task-i-20261016-0150-v2s-sheet-player-consistency-3-runs-local-t0/KOPI-9154.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/6 | 16 | 16 | 9 | 3 | 0 | complaint.fever: want=False got=None |
| P3-abdo-pregnant ([PANDA-5514](sessions-task-i-20261016-0150-v2s-sheet-player-consistency-3-runs-local-t0/PANDA-5514.transcript.txt)) | 2 | at least ESI-2 | yes | yes | 5/6 | 18 | 18 | 11 | 5 | 1 | complaint.fever: want=False got=None |
| P3-abdo-pregnant ([MERLION-2246](sessions-task-i-20261016-0150-v2s-sheet-player-consistency-3-runs-local-t0/MERLION-2246.transcript.txt)) | 3 | at least ESI-2 | yes | yes | 5/6 | 20 | 20 | 12 | 5 | 0 | complaint.fever: want=False got=None |
| P6-stroke-resolved ([RAFFLES-5139](sessions-task-i-20261016-0150-v2s-sheet-player-consistency-3-runs-local-t0/RAFFLES-5139.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/6 | 15 | 15 | 10 | 4 | 0 | complaint.fever: want=False got=None |
| P6-stroke-resolved ([DURIAN-5098](sessions-task-i-20261016-0150-v2s-sheet-player-consistency-3-runs-local-t0/DURIAN-5098.transcript.txt)) | 2 | at least ESI-2 | yes | yes | 5/6 | 16 | 16 | 15 | 5 | 1 | stroke.speech_change: want=True got=None |
| P6-stroke-resolved ([KOPI-5800](sessions-task-i-20261016-0150-v2s-sheet-player-consistency-3-runs-local-t0/KOPI-5800.transcript.txt)) | 3 | at least ESI-2 | yes | yes | 5/6 | 17 | 17 | 16 | 5 | 1 | stroke.speech_change: want=True got=None |
| P6-acute-gout ([HERON-4104](sessions-task-i-20261016-0150-v2s-sheet-player-consistency-3-runs-local-t0/HERON-4104.transcript.txt)) | 1 | - | yes | yes | 5/7 | 14 | 14 | 12 | 1 | 1 | complaint.trauma: want=False got=None; history.gout: want=True got=None |
| P6-acute-gout ([MERLION-1099](sessions-task-i-20261016-0150-v2s-sheet-player-consistency-3-runs-local-t0/MERLION-1099.transcript.txt)) | 2 | - | yes | yes | 5/7 | 14 | 14 | 12 | 2 | 1 | complaint.trauma: want=False got=None; history.gout: want=True got=None |
| P6-acute-gout ([KOPI-1025](sessions-task-i-20261016-0150-v2s-sheet-player-consistency-3-runs-local-t0/KOPI-1025.transcript.txt)) | 3 | - | yes | yes | 5/7 | 14 | 14 | 12 | 2 | 0 | complaint.trauma: want=False got=None; history.gout: want=True got=None |
| P9-breathing-no-pain ([CANNA-6415](sessions-task-i-20261016-0150-v2s-sheet-player-consistency-3-runs-local-t0/CANNA-6415.transcript.txt)) | 1 | - | yes | yes | 8/8 | 13 | 13 | 11 | 1 | 0 |  |
| P9-breathing-no-pain ([LION-3481](sessions-task-i-20261016-0150-v2s-sheet-player-consistency-3-runs-local-t0/LION-3481.transcript.txt)) | 2 | - | yes | yes | 8/8 | 13 | 13 | 11 | 1 | 0 |  |
| P9-breathing-no-pain ([PANDA-8109](sessions-task-i-20261016-0150-v2s-sheet-player-consistency-3-runs-local-t0/PANDA-8109.transcript.txt)) | 3 | - | yes | yes | 8/8 | 13 | 13 | 11 | 1 | 0 |  |

Rerun consistency (same persona, identical floor across runs):

- P1-fall-anticoag: consistent
- P3-abdo-pregnant: consistent
- P6-stroke-resolved: consistent
- P9-breathing-no-pain: consistent
- P6-acute-gout: consistent
