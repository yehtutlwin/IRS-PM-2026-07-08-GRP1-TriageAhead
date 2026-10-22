# Task I - persona runs through the real interview (20261018-1806)

Interview: mode dynamic, backend ollama (gemma4:12b). Persona played by sheet (answer-sheet replay (no model)). Temperature: interview 0, persona backend default (the Claude API takes no temperature; its own default applies). 20 personas x 1 run(s). Tag: v2u-20-personas-after-fixes-sheet-player-local-t0

Floors 18/20 · expected rules 17/20 · extraction 109/131 (83%) · danger-sign misses 0 · questions 320 · re-asks 61

Wording audit: apologies 13 · caregiver addressed as the patient 0 · questions after the report not for the nurse 0 · reports that failed to render 0

| persona | run | floor | expected floor ok | rules ok | extraction | turns | questions | to report | re-asks | sorry | misses |
| --- | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| P1-fall-anticoag ([RAFFLES-4845](sessions-task-i-20261018-1806-v2u-20-personas-after-fixes-sheet-player-local-t0/RAFFLES-4845.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 9/9 | 16 | 16 | 12 | 0 | 4 |  |
| P2-chest-pain ([LOTUS-3138](sessions-task-i-20261018-1806-v2u-20-personas-after-fixes-sheet-player-local-t0/LOTUS-3138.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/6 | 16 | 16 | 14 | 3 | 0 |  |
| P3-abdo-pregnant ([MERLION-9959](sessions-task-i-20261018-1806-v2u-20-personas-after-fixes-sheet-player-local-t0/MERLION-9959.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/6 | 16 | 17 | 10 | 5 | 0 |  |
| P4-sore-throat ([PANDA-8182](sessions-task-i-20261018-1806-v2u-20-personas-after-fixes-sheet-player-local-t0/PANDA-8182.transcript.txt)) | 1 | - | yes | yes | 5/5 | 15 | 15 | 14 | 2 | 0 |  |
| P6-stroke-resolved ([CANNA-6221](sessions-task-i-20261018-1806-v2u-20-personas-after-fixes-sheet-player-local-t0/CANNA-6221.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/6 | 16 | 16 | 15 | 3 | 2 |  |
| P5-fever-chemo ([DURIAN-3810](sessions-task-i-20261018-1806-v2u-20-personas-after-fixes-sheet-player-local-t0/DURIAN-3810.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/5 | 14 | 14 | 8 | 1 | 0 |  |
| P6-acute-gout ([OTTER-5212](sessions-task-i-20261018-1806-v2u-20-personas-after-fixes-sheet-player-local-t0/OTTER-5212.transcript.txt)) | 1 | - | yes | yes | 5/7 | 16 | 16 | 14 | 0 | 0 | complaint.trauma: want=False got=None; history.gout: want=True got=None |
| P7-heat-stroke ([MERLION-8942](sessions-task-i-20261018-1806-v2u-20-personas-after-fixes-sheet-player-local-t0/MERLION-8942.transcript.txt)) | 1 | at least ESI-2 | NO | NO | 1/8 | 16 | 17 | 9 | 3 | 2 | danger_signs.responsive: want=True got=False; danger_signs.altered_mental_status: want=True got=None; complaint.collapse: want=True got=None; complaint.vomiting |
| P8-decompensated-liver-disease ([EAGLE-6532](sessions-task-i-20261018-1806-v2u-20-personas-after-fixes-sheet-player-local-t0/EAGLE-6532.transcript.txt)) | 1 | at least ESI-2 | yes | NO | 5/12 | 13 | 13 | 10 | 0 | 1 | danger_signs.altered_mental_status: want=True got=None; complaint.hematemesis: want=False got=None; complaint.melena: want=False got=None; history.cirrhosis: wa |
| P9-breathing-no-pain ([LOTUS-7599](sessions-task-i-20261018-1806-v2u-20-personas-after-fixes-sheet-player-local-t0/LOTUS-7599.transcript.txt)) | 1 | - | yes | yes | 8/8 | 14 | 14 | 12 | 2 | 0 |  |
| P10-infant-fever ([DURIAN-4258](sessions-task-i-20261018-1806-v2u-20-personas-after-fixes-sheet-player-local-t0/DURIAN-4258.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/7 | 16 | 17 | 11 | 5 | 0 | ams.changed_from_baseline: want=False got=None |
| P11-asthma-worsening ([DURIAN-3903](sessions-task-i-20261018-1806-v2u-20-personas-after-fixes-sheet-player-local-t0/DURIAN-3903.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/6 | 16 | 17 | 14 | 5 | 1 |  |
| P12-elderly-confusion-uti ([MERLION-7516](sessions-task-i-20261018-1806-v2u-20-personas-after-fixes-sheet-player-local-t0/MERLION-7516.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/7 | 13 | 13 | 9 | 2 | 1 | history.baseline_mental_status: want='known' got=None |
| P13-cast-too-tight ([LOTUS-8476](sessions-task-i-20261018-1806-v2u-20-personas-after-fixes-sheet-player-local-t0/LOTUS-8476.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/7 | 16 | 17 | - | 3 | 0 | limb.cannot_move_digits: want=True got=None; limb.cast_too_tight: want=True got=None |
| P14-child-knee-cut ([HERON-9948](sessions-task-i-20261018-1806-v2u-20-personas-after-fixes-sheet-player-local-t0/HERON-9948.transcript.txt)) | 1 | - | yes | yes | 5/6 | 16 | 17 | - | 5 | 0 | patient.immunizations_incomplete: want=False got=None |
| P15-suicidal-thoughts ([OTTER-2437](sessions-task-i-20261018-1806-v2u-20-personas-after-fixes-sheet-player-local-t0/OTTER-2437.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/5 | 16 | 17 | 16 | 3 | 1 |  |
| P16-intentional-overdose ([EAGLE-4451](sessions-task-i-20261018-1806-v2u-20-personas-after-fixes-sheet-player-local-t0/EAGLE-4451.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/5 | 16 | 17 | 16 | 6 | 0 |  |
| P17-nosebleed-clotting ([VANDA-3813](sessions-task-i-20261018-1806-v2u-20-personas-after-fixes-sheet-player-local-t0/VANDA-3813.transcript.txt)) | 1 | - | NO | NO | 5/6 | 16 | 17 | - | 5 | 0 | history.thrombocytopenia_or_clotting_disorder: want=True got=None |
| P18-fall-no-floor ([EAGLE-8077](sessions-task-i-20261018-1806-v2u-20-personas-after-fixes-sheet-player-local-t0/EAGLE-8077.transcript.txt)) | 1 | - | yes | yes | 6/6 | 16 | 17 | - | 4 | 1 |  |
| P19-headache-no-floor ([HERON-3402](sessions-task-i-20261018-1806-v2u-20-personas-after-fixes-sheet-player-local-t0/HERON-3402.transcript.txt)) | 1 | - | yes | yes | 4/4 | 16 | 17 | - | 4 | 0 |  |
