| Arm | Setup | Runs | Score (each run, /19) | Mean score | Median wall | Mean turns | Timeouts | Spend |
|---|---|---|---|---|---|---|---|---|
| **A** | Nemotron, no planning | 3 | 15, 16, 17 | **16** | 5.5 min | 37.7 | 0 | $0 (local) |
| **B** | Nemotron plans (skill file) → Nemotron executes | 3 | 16, 15, 16 | **15.7** | 12.0 min | 305 | 2 | $0 (local) |
| **B2** | Nemotron plans (skill inlined in prompt) → Nemotron executes | 3 | 18, 16, 15 | **16.3** | 4.7 min | 57.3 | 0 | $0 (local) |
| **C** | Opus 5.5 plans → Nemotron executes | 3 | 19, 12, 19 | **16.7** | 4.4 min | 47.7 | 0 | $0.43 |
| **D** | Haiku 5.5, no planning | 3 | 19, 19, 19 | **19** | 38 s | 8 | 0 | $0.03 |

### Per run

| Run | Score | Wall | Turns | Output tok | Tests | Failed checks |
|---|---|---|---|---|---|---|
| nemotron-r1 | 15/19 | 5.5 min | 48 | 11,899 | 5 | tests don't pollute cwd; list format `[ID] [·] title`; done marks `[x]`; IDs never reused after rm |
| nemotron-r2 | 16/19 | 3.4 min | 32 | 7,645 | 4 | list format `[ID] [·] title`; done marks `[x]`; IDs never reused after rm |
| nemotron-r3 | 17/19 | 6.5 min | 33 | 14,594 | 10 | list format `[ID] [·] title`; done marks `[x]` |
| nemotron-plan-r1 | 16/19 | 2.1 min | 23 | 4,095 | 5 | list format `[ID] [·] title`; done marks `[x]`; IDs never reused after rm |
| nemotron-plan-r2 | 15/19 | 50.0 min | 786 | 73,936 | 5 | tests don't pollute cwd; list format `[ID] [·] title`; done marks `[x]`; IDs never reused after rm ⏱ 2 phase(s) hit the 25-min timeout |
| nemotron-plan-r3 | 16/19 | 12.0 min | 106 | 25,541 | 5 | list format `[ID] [·] title`; done marks `[x]`; IDs never reused after rm |
| nemotron-planinline-r1 | 18/19 | 8.1 min | 81 | 15,448 | 5 | IDs never reused after rm |
| nemotron-planinline-r2 | 16/19 | 3.6 min | 46 | 7,260 | 5 | list format `[ID] [·] title`; done marks `[x]`; IDs never reused after rm |
| nemotron-planinline-r3 | 15/19 | 4.7 min | 45 | 9,397 | 9 | list format `[ID] [·] title`; done marks `[x]`; IDs never reused after rm; README.md with usage examples |
| opusplan-nemotron-r1 | 19/19 | 4.4 min | 15 | 8,065 | 9 | — |
| opusplan-nemotron-r2 | 12/19 | 24.7 min | 112 | 48,104 | 9 | add prints new ID; persists to ./todos.json (cwd); list format `[ID] [·] title`; done marks `[x]`; IDs never reused after rm; clear removes done todos only; schema {id:int, title:str, done:bool} |
| opusplan-nemotron-r3 | 19/19 | 3.6 min | 16 | 6,666 | 8 | — |
| haiku-r1 | 19/19 | 42 s | 7 | 7,396 | 15 | — |
| haiku-r2 | 19/19 | 38 s | 8 | 9,316 | 11 | — |
| haiku-r3 | 19/19 | 38 s | 9 | 9,189 | 11 | — |
