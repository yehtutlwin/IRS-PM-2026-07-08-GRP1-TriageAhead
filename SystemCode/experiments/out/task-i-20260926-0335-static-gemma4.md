# Task I - persona runs through the real interview (20260926-0335)

Interview: mode static, backend ollama (gemma4:12b). Persona played by ollama (gemma4:12b). 9 personas x 1 run(s). Tag: static-gemma4

Floors 7/9 · expected rules 7/9 · extraction 45/64 (70%) · danger-sign misses 0 · questions 99 · re-asks 37

| persona | run | floor | expected floor ok | rules ok | extraction | turns | questions | re-asks | misses |
| --- | ---: | --- | --- | --- | ---: | ---: | ---: | ---: | --- |
| P1-fall-anticoag | 1 | at least ESI-2 | yes | yes | 9/9 | 16 | 13 | 3 |  |
| P2-chest-pain | 1 | at least ESI-2 | yes | yes | 6/6 | 10 | 10 | 3 |  |
| P3-abdo-pregnant | 1 | at least ESI-2 | yes | yes | 5/6 | 9 | 9 | 3 | complaint.vaginal_bleeding: want=False got=None |
| P4-sore-throat | 1 | - | yes | yes | 4/5 | 11 | 11 | 5 | infection.fever: want=False got=True |
| P6-stroke-resolved | 1 | at least ESI-2 | yes | yes | 6/6 | 12 | 12 | 5 |  |
| P5-fever-chemo | 1 | at least ESI-2 | yes | yes | 4/5 | 10 | 10 | 4 | complaint.pain_rating: want=0 got=None |
| P6-acute-gout | 1 | - | yes | yes | 5/7 | 16 | 11 | 4 | complaint.trauma: want=False got=None; history.gout: want=True got=None |
| P7-heat-stroke | 1 | at least ESI-2 | NO | NO | 1/8 | 16 | 11 | 4 | red_flags.responsive: want=True got=False; red_flags.altered_mental_status: want=True got=None; complaint.collapse: want=True got=None; complaint.vomiting: want |
| P8-decompensated-liver-disease | 1 | - | NO | NO | 5/12 | 16 | 12 | 6 | red_flags.altered_mental_status: want=True got=None; complaint.hematemesis: want=False got=None; complaint.melena: want=False got=None; history.cirrhosis: want= |
