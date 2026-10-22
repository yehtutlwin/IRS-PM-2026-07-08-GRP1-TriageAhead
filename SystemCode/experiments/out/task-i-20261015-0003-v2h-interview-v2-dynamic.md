# Task I - persona runs through the real interview (20261015-0003)

Interview: mode dynamic, backend ollama (gemma4:12b). Persona played by ollama (gemma4:12b). 10 personas x 1 run(s). Tag: v2h-interview-v2-dynamic

Floors 9/10 · expected rules 8/10 · extraction 52/71 (73%) · danger-sign misses 0 · questions 219 · re-asks 67

| persona | run | floor | expected floor ok | rules ok | extraction | turns | questions | to report | re-asks | misses |
| --- | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| P1-fall-anticoag | 1 | at least ESI-2 | yes | yes | 9/9 | 28 | 27 | 23 | 6 |  |
| P2-chest-pain | 1 | at least ESI-2 | yes | yes | 6/6 | 30 | 26 | 24 | 11 |  |
| P3-abdo-pregnant | 1 | at least ESI-2 | yes | yes | 5/6 | 30 | 22 | - | 10 | complaint.vaginal_bleeding: want=False got=None |
| P4-sore-throat | 1 | - | yes | yes | 4/5 | 22 | 22 | 21 | 8 | complaint.fever: want=False got=True |
| P6-stroke-resolved | 1 | at least ESI-2 | yes | yes | 5/6 | 20 | 20 | 19 | 5 | stroke.arm_weakness: want=True got=False |
| P5-fever-chemo | 1 | at least ESI-2 | yes | yes | 4/5 | 19 | 19 | 18 | 4 | complaint.pain_rating: want=0 got=None |
| P6-acute-gout | 1 | - | yes | yes | 5/7 | 17 | 17 | 15 | 5 | complaint.trauma: want=False got=None; history.gout: want=True got=None |
| P7-heat-stroke | 1 | at least ESI-2 | NO | NO | 2/8 | 22 | 20 | 19 | 6 | danger_signs.responsive: want=True got=False; danger_signs.altered_mental_status: want=True got=None; complaint.collapse: want=True got=None; complaint.fever: w |
| P8-decompensated-liver-disease | 1 | at least ESI-2 | yes | NO | 5/12 | 29 | 28 | 24 | 7 | danger_signs.altered_mental_status: want=True got=None; complaint.hematemesis: want=False got=None; complaint.melena: want=False got=None; history.cirrhosis: wa |
| P9-breathing-no-pain | 1 | at least ESI-2 | yes | yes | 7/7 | 18 | 18 | 16 | 5 |  |
