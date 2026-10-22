# Task I - persona runs through the real interview (20261018-2127)

Interview: mode dynamic, backend ollama (gemma4:12b). Persona played by sheet (answer-sheet replay (no model)). Temperature: interview 0, persona backend default (the Claude API takes no temperature; its own default applies). 25 personas x 1 run(s). Tag: v2w-25-personas-fallback-sheet-player-local-t0

Floors 22/25 · expected rules 21/25 · extraction 133/163 (82%) · danger-sign misses 0 · questions 406 · re-asks 84

Wording audit: apologies 15 · caregiver addressed as the patient 0 · questions after the report not for the nurse 0 · reports that failed to render 0

| persona | run | floor | expected floor ok | rules ok | extraction | turns | questions | to report | re-asks | sorry | misses |
| --- | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| P1-fall-anticoag ([EAGLE-2009](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/EAGLE-2009.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 9/9 | 16 | 17 | 13 | 0 | 3 |  |
| P2-chest-pain ([RAFFLES-3994](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/RAFFLES-3994.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/6 | 16 | 17 | 15 | 4 | 0 |  |
| P3-abdo-pregnant ([TIGER-8784](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/TIGER-8784.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/6 | 16 | 17 | 9 | 3 | 0 |  |
| P4-sore-throat ([PANDA-4988](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/PANDA-4988.transcript.txt)) | 1 | - | yes | yes | 5/5 | 15 | 15 | 14 | 2 | 0 |  |
| P6-stroke-resolved ([ORCHID-1354](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/ORCHID-1354.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/6 | 14 | 14 | 13 | 2 | 0 | stroke.speech_change: want=True got=None |
| P5-fever-chemo ([EAGLE-6291](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/EAGLE-6291.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/5 | 13 | 13 | 7 | 0 | 0 |  |
| P6-acute-gout ([CANNA-4896](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/CANNA-4896.transcript.txt)) | 1 | - | yes | yes | 5/7 | 16 | 16 | 14 | 0 | 0 | complaint.trauma: want=False got=None; history.gout: want=True got=None |
| P7-heat-stroke ([CANNA-7245](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/CANNA-7245.transcript.txt)) | 1 | at least ESI-2 | NO | NO | 1/8 | 16 | 17 | 9 | 3 | 2 | danger_signs.responsive: want=True got=False; danger_signs.altered_mental_status: want=True got=None; complaint.collapse: want=True got=None; complaint.vomiting |
| P8-decompensated-liver-disease ([PANDA-7412](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/PANDA-7412.transcript.txt)) | 1 | at least ESI-2 | yes | NO | 5/12 | 14 | 14 | 11 | 1 | 1 | danger_signs.altered_mental_status: want=True got=None; complaint.hematemesis: want=False got=None; complaint.melena: want=False got=None; history.cirrhosis: wa |
| P9-breathing-no-pain ([TIGER-8148](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/TIGER-8148.transcript.txt)) | 1 | - | yes | yes | 8/8 | 14 | 14 | 12 | 2 | 0 |  |
| P10-infant-fever ([RAFFLES-3321](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/RAFFLES-3321.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/7 | 16 | 17 | 11 | 6 | 0 | ams.changed_from_baseline: want=False got=None |
| P11-asthma-worsening ([RAFFLES-3527](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/RAFFLES-3527.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/6 | 16 | 16 | 12 | 4 | 1 |  |
| P12-elderly-confusion-uti ([CANNA-4856](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/CANNA-4856.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/7 | 15 | 15 | 11 | 3 | 2 | history.baseline_mental_status: want='known' got=None |
| P13-cast-too-tight ([ORCHID-5675](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/ORCHID-5675.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/7 | 16 | 17 | - | 3 | 1 | limb.cannot_move_digits: want=True got=None; limb.cast_too_tight: want=True got=None |
| P14-child-knee-cut ([KOPI-6223](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/KOPI-6223.transcript.txt)) | 1 | - | yes | yes | 5/6 | 16 | 17 | - | 5 | 0 | patient.immunizations_incomplete: want=False got=None |
| P15-suicidal-thoughts ([LOTUS-7077](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/LOTUS-7077.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/5 | 16 | 17 | - | 3 | 1 |  |
| P16-intentional-overdose ([MERLION-7057](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/MERLION-7057.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/5 | 16 | 17 | 16 | 5 | 0 |  |
| P17-nosebleed-clotting ([KOPI-1996](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/KOPI-1996.transcript.txt)) | 1 | - | NO | NO | 5/6 | 16 | 17 | - | 5 | 0 | history.thrombocytopenia_or_clotting_disorder: want=True got=None |
| P18-fall-no-floor ([SAGA-5757](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/SAGA-5757.transcript.txt)) | 1 | - | yes | yes | 6/6 | 16 | 17 | - | 2 | 1 |  |
| P19-headache-no-floor ([OTTER-9574](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/OTTER-9574.transcript.txt)) | 1 | - | yes | yes | 4/4 | 16 | 17 | - | 4 | 0 |  |
| P20-cancer-pain ([RAFFLES-3240](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/RAFFLES-3240.transcript.txt)) | 1 | - | NO | NO | 6/7 | 16 | 17 | - | 3 | 2 | complaint.pain_cause_class: want='cancer' got=None |
| P21-child-shunt-not-right ([KOPI-2579](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/KOPI-2579.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/7 | 16 | 17 | 13 | 6 | 0 | history.baseline_mental_status: want='known' got=None |
| P22-teen-threatening-family ([EAGLE-3217](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/EAGLE-3217.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/8 | 16 | 17 | - | 6 | 0 | history.conditions: want=[] got=None; M.medications: want=[] got=[]; A.allergies: want=[] got=[] |
| P23-sawdust-in-eye ([LION-3981](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/LION-3981.transcript.txt)) | 1 | - | yes | yes | 4/5 | 16 | 17 | - | 6 | 1 | eye.injury: want=True got=None |
| P24-bug-in-ear ([SAGA-8335](sessions-task-i-20261018-2127-v2w-25-personas-fallback-sheet-player-local-t0/SAGA-8335.transcript.txt)) | 1 | - | yes | yes | 4/5 | 16 | 17 | - | 6 | 0 | history.conditions: want=[] got=None |
