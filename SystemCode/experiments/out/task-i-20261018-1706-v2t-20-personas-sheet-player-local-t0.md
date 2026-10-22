# Task I - persona runs through the real interview (20261018-1706)

Interview: mode dynamic, backend ollama (gemma4:12b). Persona played by sheet (answer-sheet replay (no model)). Temperature: interview 0, persona backend default (the Claude API takes no temperature; its own default applies). 20 personas x 1 run(s). Tag: v2t-20-personas-sheet-player-local-t0

Floors 18/20 · expected rules 16/20 · extraction 106/129 (82%) · danger-sign misses 0 · questions 318 · re-asks 62

Wording audit: apologies 8 · caregiver addressed as the patient 0 · questions after the report not for the nurse 0 · reports that failed to render 0

| persona | run | floor | expected floor ok | rules ok | extraction | turns | questions | to report | re-asks | sorry | misses |
| --- | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| P1-fall-anticoag ([SAGA-5238](sessions-task-i-20261018-1706-v2t-20-personas-sheet-player-local-t0/SAGA-5238.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 8/9 | 16 | 17 | 14 | 0 | 2 | E.loc: want=False got=None |
| P2-chest-pain ([LION-1475](sessions-task-i-20261018-1706-v2t-20-personas-sheet-player-local-t0/LION-1475.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/6 | 16 | 16 | 14 | 3 | 0 |  |
| P3-abdo-pregnant ([TIGER-5074](sessions-task-i-20261018-1706-v2t-20-personas-sheet-player-local-t0/TIGER-5074.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/6 | 16 | 17 | 12 | 4 | 1 |  |
| P4-sore-throat ([LION-1544](sessions-task-i-20261018-1706-v2t-20-personas-sheet-player-local-t0/LION-1544.transcript.txt)) | 1 | - | yes | yes | 5/5 | 14 | 14 | 13 | 1 | 0 |  |
| P6-stroke-resolved ([VANDA-6385](sessions-task-i-20261018-1706-v2t-20-personas-sheet-player-local-t0/VANDA-6385.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/6 | 14 | 14 | 13 | 2 | 0 | stroke.speech_change: want=True got=None |
| P5-fever-chemo ([BAOBAB-3687](sessions-task-i-20261018-1706-v2t-20-personas-sheet-player-local-t0/BAOBAB-3687.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/5 | 13 | 13 | 7 | 0 | 0 |  |
| P6-acute-gout ([TIGER-5659](sessions-task-i-20261018-1706-v2t-20-personas-sheet-player-local-t0/TIGER-5659.transcript.txt)) | 1 | - | yes | yes | 5/7 | 14 | 14 | 12 | 1 | 0 | complaint.trauma: want=False got=None; history.gout: want=True got=None |
| P7-heat-stroke ([CANNA-5955](sessions-task-i-20261018-1706-v2t-20-personas-sheet-player-local-t0/CANNA-5955.transcript.txt)) | 1 | at least ESI-2 | NO | NO | 1/8 | 16 | 17 | 9 | 4 | 1 | danger_signs.responsive: want=True got=False; danger_signs.altered_mental_status: want=True got=None; complaint.collapse: want=True got=None; complaint.vomiting |
| P8-decompensated-liver-disease ([LION-8614](sessions-task-i-20261018-1706-v2t-20-personas-sheet-player-local-t0/LION-8614.transcript.txt)) | 1 | at least ESI-2 | yes | NO | 5/12 | 14 | 14 | 11 | 1 | 2 | danger_signs.altered_mental_status: want=True got=None; complaint.hematemesis: want=False got=None; complaint.melena: want=False got=None; history.cirrhosis: wa |
| P9-breathing-no-pain ([DURIAN-1218](sessions-task-i-20261018-1706-v2t-20-personas-sheet-player-local-t0/DURIAN-1218.transcript.txt)) | 1 | - | yes | yes | 8/8 | 14 | 14 | 12 | 2 | 0 |  |
| P10-infant-fever ([TIGER-9634](sessions-task-i-20261018-1706-v2t-20-personas-sheet-player-local-t0/TIGER-9634.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/7 | 16 | 17 | 10 | 5 | 0 | ams.changed_from_baseline: want=False got=None |
| P11-asthma-worsening ([PANDA-1715](sessions-task-i-20261018-1706-v2t-20-personas-sheet-player-local-t0/PANDA-1715.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/6 | 16 | 16 | 12 | 4 | 1 |  |
| P12-elderly-confusion-uti ([EAGLE-5772](sessions-task-i-20261018-1706-v2t-20-personas-sheet-player-local-t0/EAGLE-5772.transcript.txt)) | 1 | at least ESI-2 | yes | NO | 5/7 | 16 | 16 | 10 | 5 | 0 | ams.changed_from_baseline: want=True got=None; history.baseline_mental_status: want='known' got=None |
| P13-cast-too-tight ([OTTER-2527](sessions-task-i-20261018-1706-v2t-20-personas-sheet-player-local-t0/OTTER-2527.transcript.txt)) | 1 | - | NO | NO | 4/5 | 16 | 17 | 16 | 4 | 0 | complaint.extremity_neurovascular_compromise: want=True got=None |
| P14-child-knee-cut ([BAOBAB-8069](sessions-task-i-20261018-1706-v2t-20-personas-sheet-player-local-t0/BAOBAB-8069.transcript.txt)) | 1 | - | yes | yes | 5/6 | 16 | 17 | - | 4 | 0 | patient.immunizations_incomplete: want=False got=None |
| P15-suicidal-thoughts ([OTTER-4703](sessions-task-i-20261018-1706-v2t-20-personas-sheet-player-local-t0/OTTER-4703.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/5 | 16 | 17 | - | 5 | 0 |  |
| P16-intentional-overdose ([PANDA-3441](sessions-task-i-20261018-1706-v2t-20-personas-sheet-player-local-t0/PANDA-3441.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/5 | 16 | 17 | 13 | 5 | 0 |  |
| P17-nosebleed-clotting ([OTTER-1990](sessions-task-i-20261018-1706-v2t-20-personas-sheet-player-local-t0/OTTER-1990.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/6 | 16 | 17 | - | 4 | 0 |  |
| P18-fall-no-floor ([HERON-1327](sessions-task-i-20261018-1706-v2t-20-personas-sheet-player-local-t0/HERON-1327.transcript.txt)) | 1 | - | yes | yes | 6/6 | 16 | 17 | - | 4 | 1 |  |
| P19-headache-no-floor ([LOTUS-8021](sessions-task-i-20261018-1706-v2t-20-personas-sheet-player-local-t0/LOTUS-8021.transcript.txt)) | 1 | - | yes | yes | 4/4 | 16 | 17 | - | 4 | 0 |  |
