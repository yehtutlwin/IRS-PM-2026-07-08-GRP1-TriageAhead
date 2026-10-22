# Task I - persona runs through the real interview (20261019-1205)

> A test run of a teammate's six persona answer sheets exactly as the teammate posted them on 19 Oct 2026 (file: personas-newtondai-6-as-posted-20261019.yaml beside this report), not merged into prototype/personas.yaml. Same interview settings as the runs on the 25.

Interview: mode dynamic, backend ollama (gemma4:12b). Persona played by sheet (answer-sheet replay (no model)). Temperature: interview 0, persona backend default (the Claude API takes no temperature; its own default applies). 6 personas x 1 run(s). Tag: v2y-newtondai-6-sheets-as-posted-sheet-player-local-t0

Floors 4/6 · expected rules 3/6 · extraction 36/41 (88%) · danger-sign misses 0 · questions 102 · re-asks 31

Wording audit: apologies 1 · caregiver addressed as the patient 0 · questions after the report not for the nurse 0 · reports that failed to render 0

| persona | run | floor | expected floor ok | rules ok | extraction | turns | questions | to report | re-asks | sorry | misses |
| --- | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| P20-infant-fever ([ORCHID-4742](sessions-task-i-20261019-1205-v2y-newtondai-6-sheets-as-posted-sheet-player-local-t0/ORCHID-4742.transcript.txt)) | 1 | at least ESI-2 | yes | NO | 6/8 | 16 | 17 | 11 | 5 | 0 | patient.age_days: want=42 got=None; patient.age_months: want=1.5 got=None |
| P22-teen-self-harm-concern ([KOPI-7948](sessions-task-i-20261019-1205-v2y-newtondai-6-sheets-as-posted-sheet-player-local-t0/KOPI-7948.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 5/5 | 16 | 17 | - | 7 | 0 |  |
| P23-elderly-confusion ([RAFFLES-8618](sessions-task-i-20261019-1205-v2y-newtondai-6-sheets-as-posted-sheet-player-local-t0/RAFFLES-8618.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/7 | 16 | 17 | - | 5 | 1 | history.baseline_mental_status: want='known' got=None |
| P27-resolved-speech-change ([VANDA-4974](sessions-task-i-20261019-1205-v2y-newtondai-6-sheets-as-posted-sheet-player-local-t0/VANDA-4974.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 7/7 | 16 | 17 | - | 4 | 0 |  |
| P28-postpartum-bleeding ([EAGLE-3954](sessions-task-i-20261019-1205-v2y-newtondai-6-sheets-as-posted-sheet-player-local-t0/EAGLE-3954.transcript.txt)) | 1 | - | NO | NO | 6/8 | 16 | 17 | - | 6 | 0 | complaint.heavy_vaginal_bleeding: want=True got=None; complaint.postpartum_hemorrhage: want=True got=None |
| P29-pregnant-headache ([CANNA-2617](sessions-task-i-20261019-1205-v2y-newtondai-6-sheets-as-posted-sheet-player-local-t0/CANNA-2617.transcript.txt)) | 1 | - | NO | NO | 6/6 | 16 | 17 | - | 4 | 0 |  |
