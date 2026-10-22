# Task I - persona runs through the real interview (20261015-0031)

Interview: mode dynamic, backend ollama (gemma4:12b). Persona played by ollama (gemma4:12b). 10 personas x 1 run(s). Tag: v2i-interview-v2-dynamic

Floors 9/10 · expected rules 8/10 · extraction 54/71 (76%) · danger-sign misses 0 · questions 220 · re-asks 64

| persona | run | floor | expected floor ok | rules ok | extraction | turns | questions | to report | re-asks | misses |
| --- | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| P1-fall-anticoag ([TIGER-8983](sessions-task-i-20261015-0031-v2i-interview-v2-dynamic/TIGER-8983.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 9/9 | 27 | 26 | 17 | 5 |  |
| P2-chest-pain ([LOTUS-6608](sessions-task-i-20261015-0031-v2i-interview-v2-dynamic/LOTUS-6608.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/6 | 30 | 24 | 19 | 10 |  |
| P3-abdo-pregnant ([OTTER-9107](sessions-task-i-20261015-0031-v2i-interview-v2-dynamic/OTTER-9107.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/6 | 30 | 29 | 12 | 11 |  |
| P4-sore-throat ([VANDA-5393](sessions-task-i-20261015-0031-v2i-interview-v2-dynamic/VANDA-5393.transcript.txt)) | 1 | - | yes | yes | 4/5 | 20 | 20 | 19 | 6 | complaint.fever: want=False got=True |
| P6-stroke-resolved ([HERON-3932](sessions-task-i-20261015-0031-v2i-interview-v2-dynamic/HERON-3932.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 6/6 | 24 | 24 | 13 | 8 |  |
| P5-fever-chemo ([OTTER-5593](sessions-task-i-20261015-0031-v2i-interview-v2-dynamic/OTTER-5593.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 4/5 | 19 | 19 | 6 | 4 | complaint.pain_rating: want=0 got=None |
| P6-acute-gout ([KOPI-8085](sessions-task-i-20261015-0031-v2i-interview-v2-dynamic/KOPI-8085.transcript.txt)) | 1 | - | yes | yes | 5/7 | 16 | 16 | 14 | 4 | complaint.trauma: want=False got=None; history.gout: want=True got=None |
| P7-heat-stroke ([EAGLE-5453](sessions-task-i-20261015-0031-v2i-interview-v2-dynamic/EAGLE-5453.transcript.txt)) | 1 | at least ESI-2 | NO | NO | 2/8 | 30 | 23 | 14 | 4 | danger_signs.altered_mental_status: want=True got=None; complaint.collapse: want=True got=None; complaint.vomiting: want=True got=None; complaint.fever: want=Fa |
| P8-decompensated-liver-disease ([HERON-6530](sessions-task-i-20261015-0031-v2i-interview-v2-dynamic/HERON-6530.transcript.txt)) | 1 | at least ESI-2 | yes | NO | 5/12 | 22 | 22 | 13 | 7 | danger_signs.altered_mental_status: want=True got=None; complaint.hematemesis: want=False got=None; complaint.melena: want=False got=None; history.cirrhosis: wa |
| P9-breathing-no-pain ([BAOBAB-2894](sessions-task-i-20261015-0031-v2i-interview-v2-dynamic/BAOBAB-2894.transcript.txt)) | 1 | at least ESI-2 | yes | yes | 7/7 | 19 | 17 | 14 | 5 |  |
