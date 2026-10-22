# Task I - persona runs through the real interview (20261018-2014)

Interview: mode dynamic, backend ollama (gemma4:12b). Persona played by sheet (answer-sheet replay (no model)). Temperature: interview 0, persona backend default (the Claude API takes no temperature; its own default applies). 20 personas x 1 run(s). Tag: v2v-20-personas-after-revert-sheet-player-local-t0

Floors 17/20 · expected rules 16/20 · extraction 108/131 (82%) · danger-sign misses 0 · questions 315 · re-asks 56

Wording audit: apologies 11 · caregiver addressed as the patient 0 · questions after the report not for the nurse 0 · reports that failed to render 0

| persona | run | floor | expected floor ok | rules ok | extraction | turns | questions | to report | re-asks | sorry | misses |
| --- | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| P1-fall-anticoag ([LION-4496](sessions-task-i-20261018-2014-v2v-20-personas-after-revert-sheet-player-local-t0/LION-4496.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 9/9 | 15 | 15 | 11 | 0 | 1 |  |
| P2-chest-pain ([PANDA-1991](sessions-task-i-20261018-2014-v2v-20-personas-after-revert-sheet-player-local-t0/PANDA-1991.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/6 | 15 | 15 | 13 | 2 | 0 |  |
| P3-abdo-pregnant ([VANDA-4397](sessions-task-i-20261018-2014-v2v-20-personas-after-revert-sheet-player-local-t0/VANDA-4397.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/6 | 16 | 17 | 12 | 4 | 1 |  |
| P4-sore-throat ([CANNA-7138](sessions-task-i-20261018-2014-v2v-20-personas-after-revert-sheet-player-local-t0/CANNA-7138.transcript.txt)) | 1 | - | yes | yes | 5/5 | 13 | 13 | 12 | 2 | 0 |  |
| P6-stroke-resolved ([PANDA-1691](sessions-task-i-20261018-2014-v2v-20-personas-after-revert-sheet-player-local-t0/PANDA-1691.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/6 | 15 | 15 | 14 | 2 | 0 |  |
| P5-fever-chemo ([KOPI-3551](sessions-task-i-20261018-2014-v2v-20-personas-after-revert-sheet-player-local-t0/KOPI-3551.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/5 | 13 | 13 | 7 | 0 | 0 |  |
| P6-acute-gout ([OTTER-7524](sessions-task-i-20261018-2014-v2v-20-personas-after-revert-sheet-player-local-t0/OTTER-7524.transcript.txt)) | 1 | - | yes | yes | 5/7 | 16 | 17 | 15 | 1 | 1 | complaint.trauma: want=False got=None; history.gout: want=True got=None |
| P7-heat-stroke ([LION-8061](sessions-task-i-20261018-2014-v2v-20-personas-after-revert-sheet-player-local-t0/LION-8061.transcript.txt)) | 1 | at least ESI-2 | NO | NO | 1/8 | 16 | 17 | 9 | 3 | 1 | danger_signs.responsive: want=True got=False; danger_signs.altered_mental_status: want=True got=None; complaint.collapse: want=True got=None; complaint.vomiting |
| P8-decompensated-liver-disease ([OTTER-8923](sessions-task-i-20261018-2014-v2v-20-personas-after-revert-sheet-player-local-t0/OTTER-8923.transcript.txt)) | 1 | at least ESI-2 | yes | NO | 5/12 | 14 | 14 | 11 | 1 | 1 | danger_signs.altered_mental_status: want=True got=None; complaint.hematemesis: want=False got=None; complaint.melena: want=False got=None; history.cirrhosis: wa |
| P9-breathing-no-pain ([DURIAN-3066](sessions-task-i-20261018-2014-v2v-20-personas-after-revert-sheet-player-local-t0/DURIAN-3066.transcript.txt)) | 1 | - | yes | yes | 8/8 | 13 | 13 | 11 | 1 | 0 |  |
| P10-infant-fever ([TIGER-6328](sessions-task-i-20261018-2014-v2v-20-personas-after-revert-sheet-player-local-t0/TIGER-6328.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/7 | 16 | 17 | 11 | 5 | 0 | ams.changed_from_baseline: want=False got=None |
| P11-asthma-worsening ([PANDA-6257](sessions-task-i-20261018-2014-v2v-20-personas-after-revert-sheet-player-local-t0/PANDA-6257.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/6 | 16 | 16 | 12 | 4 | 0 |  |
| P12-elderly-confusion-uti ([BAOBAB-6346](sessions-task-i-20261018-2014-v2v-20-personas-after-revert-sheet-player-local-t0/BAOBAB-6346.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/7 | 15 | 15 | 11 | 3 | 2 | history.baseline_mental_status: want='known' got=None |
| P13-cast-too-tight ([DURIAN-4587](sessions-task-i-20261018-2014-v2v-20-personas-after-revert-sheet-player-local-t0/DURIAN-4587.transcript.txt)) | 1 | - | NO | NO | 4/7 | 16 | 17 | - | 3 | 1 | limb.numb_tingling: want=True got=None; limb.cannot_move_digits: want=True got=None; limb.cast_too_tight: want=True got=None |
| P14-child-knee-cut ([EAGLE-5923](sessions-task-i-20261018-2014-v2v-20-personas-after-revert-sheet-player-local-t0/EAGLE-5923.transcript.txt)) | 1 | - | yes | yes | 5/6 | 16 | 17 | - | 5 | 0 | patient.immunizations_incomplete: want=False got=None |
| P15-suicidal-thoughts ([BAOBAB-2140](sessions-task-i-20261018-2014-v2v-20-personas-after-revert-sheet-player-local-t0/BAOBAB-2140.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/5 | 16 | 16 | 15 | 3 | 2 |  |
| P16-intentional-overdose ([BAOBAB-1722](sessions-task-i-20261018-2014-v2v-20-personas-after-revert-sheet-player-local-t0/BAOBAB-1722.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/5 | 16 | 17 | - | 5 | 0 |  |
| P17-nosebleed-clotting ([LOTUS-6841](sessions-task-i-20261018-2014-v2v-20-personas-after-revert-sheet-player-local-t0/LOTUS-6841.transcript.txt)) | 1 | - | NO | NO | 5/6 | 16 | 17 | - | 4 | 0 | history.thrombocytopenia_or_clotting_disorder: want=True got=None |
| P18-fall-no-floor ([HERON-8544](sessions-task-i-20261018-2014-v2v-20-personas-after-revert-sheet-player-local-t0/HERON-8544.transcript.txt)) | 1 | - | yes | yes | 6/6 | 16 | 17 | - | 4 | 1 |  |
| P19-headache-no-floor ([EAGLE-6963](sessions-task-i-20261018-2014-v2v-20-personas-after-revert-sheet-player-local-t0/EAGLE-6963.transcript.txt)) | 1 | - | yes | yes | 4/4 | 16 | 17 | - | 4 | 0 |  |
