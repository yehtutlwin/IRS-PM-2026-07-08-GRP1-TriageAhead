# Task I - persona runs through the real interview (20261015-1817)

Interview: mode dynamic, backend ollama (gemma4:12b). Persona played by ollama (gemma4:12b). 5 personas x 3 run(s). Tag: v2o-consistency-3-runs-local

Floors 12/15 · expected rules 15/15 · extraction 91/105 (87%) · danger-sign misses 0 · questions 270 · re-asks 74

Wording audit: apologies 17 · caregiver addressed as the patient 0 · questions after the report not for the nurse 0 · reports that failed to render 0

| persona | run | floor | expected floor ok | rules ok | extraction | turns | questions | to report | re-asks | sorry | misses |
| --- | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| P1-fall-anticoag ([EAGLE-2517](sessions-task-i-20261015-1817-v2o-consistency-3-runs-local/EAGLE-2517.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 9/9 | 18 | 18 | 14 | 4 | 2 |  |
| P1-fall-anticoag ([VANDA-5127](sessions-task-i-20261015-1817-v2o-consistency-3-runs-local/VANDA-5127.transcript.txt)) | 2 | at least ESI-2 | yes | yes | 9/9 | 22 | 22 | 18 | 6 | 0 |  |
| P1-fall-anticoag ([ORCHID-2680](sessions-task-i-20261015-1817-v2o-consistency-3-runs-local/ORCHID-2680.transcript.txt)) | 3 | at least ESI-2 | yes | yes | 9/9 | 21 | 21 | 17 | 5 | 2 |  |
| P3-abdo-pregnant ([ORCHID-1041](sessions-task-i-20261015-1817-v2o-consistency-3-runs-local/ORCHID-1041.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/6 | 22 | 22 | 15 | 10 | 0 | complaint.fever: want=False got=None |
| P3-abdo-pregnant ([TIGER-6332](sessions-task-i-20261015-1817-v2o-consistency-3-runs-local/TIGER-6332.transcript.txt)) | 2 | at least ESI-2 | yes | yes | 5/6 | 22 | 22 | 13 | 10 | 1 | complaint.fever: want=False got=None |
| P3-abdo-pregnant ([LOTUS-9447](sessions-task-i-20261015-1817-v2o-consistency-3-runs-local/LOTUS-9447.transcript.txt)) | 3 | at least ESI-2 | yes | yes | 5/6 | 21 | 21 | 13 | 8 | 1 | complaint.fever: want=False got=None |
| P6-stroke-resolved ([BAOBAB-1786](sessions-task-i-20261015-1817-v2o-consistency-3-runs-local/BAOBAB-1786.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/6 | 16 | 16 | 15 | 4 | 2 |  |
| P6-stroke-resolved ([EAGLE-5489](sessions-task-i-20261015-1817-v2o-consistency-3-runs-local/EAGLE-5489.transcript.txt)) | 2 | at least ESI-2 | yes | yes | 4/6 | 15 | 15 | 14 | 3 | 1 | stroke.speech_change: want=True got=None; stroke.arm_weakness: want=True got=None |
| P6-stroke-resolved ([LION-5657](sessions-task-i-20261015-1817-v2o-consistency-3-runs-local/LION-5657.transcript.txt)) | 3 | at least ESI-2 | yes | yes | 5/6 | 15 | 15 | 14 | 3 | 1 | stroke.arm_weakness: want=True got=None |
| P6-acute-gout ([LOTUS-7649](sessions-task-i-20261015-1817-v2o-consistency-3-runs-local/LOTUS-7649.transcript.txt)) | 1 | - | yes | yes | 5/7 | 17 | 17 | 15 | 4 | 1 | complaint.trauma: want=False got=None; history.gout: want=True got=None |
| P6-acute-gout ([LOTUS-8232](sessions-task-i-20261015-1817-v2o-consistency-3-runs-local/LOTUS-8232.transcript.txt)) | 2 | - | yes | yes | 5/7 | 17 | 17 | 15 | 5 | 2 | complaint.trauma: want=False got=None; history.gout: want=True got=None |
| P6-acute-gout ([RAFFLES-9366](sessions-task-i-20261015-1817-v2o-consistency-3-runs-local/RAFFLES-9366.transcript.txt)) | 3 | - | yes | yes | 5/7 | 17 | 17 | 15 | 4 | 3 | complaint.trauma: want=False got=None; history.gout: want=True got=None |
| P9-breathing-no-pain ([MERLION-5265](sessions-task-i-20261015-1817-v2o-consistency-3-runs-local/MERLION-5265.transcript.txt)) | 1 | at least ESI-2 | NO | yes | 6/7 | 18 | 18 | 16 | 5 | 0 | danger_signs.breathing_difficulty: want=True got=False |
| P9-breathing-no-pain ([SAGA-7814](sessions-task-i-20261015-1817-v2o-consistency-3-runs-local/SAGA-7814.transcript.txt)) | 2 | at least ESI-2 | NO | yes | 7/7 | 15 | 15 | 13 | 2 | 1 |  |
| P9-breathing-no-pain ([RAFFLES-3766](sessions-task-i-20261015-1817-v2o-consistency-3-runs-local/RAFFLES-3766.transcript.txt)) | 3 | at least ESI-2 | NO | yes | 6/7 | 14 | 14 | 12 | 1 | 0 | danger_signs.breathing_difficulty: want=True got=False |

Rerun consistency (same persona, identical floor across runs):

- P9-breathing-no-pain: consistent
- P6-stroke-resolved: consistent
- P1-fall-anticoag: consistent
- P3-abdo-pregnant: consistent
- P6-acute-gout: consistent
