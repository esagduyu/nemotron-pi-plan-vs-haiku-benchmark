# Nemotron 3.5 Lightning (local, via pi) × planning strategies vs Claude Haiku 5.5

v2 of [qwen-pi-plan-vs-haiku-benchmark](https://github.com/esagduyu/qwen-pi-plan-vs-haiku-benchmark): the same agentic coding task on a single RTX 2080 Ti, now with **NVIDIA Nemotron 3.5 Lightning 30B-A3B** as the local model. It asks whether planning helps, and whether it matters **who writes the plan**. A follow-up re-ran **Qwen3.6-35B-A3B** (v1's local model) through the identical harness for an apples-to-apples comparison.

| Arm | Planner | Executor |
|---|---|---|
| **A** | — | Nemotron (local) |
| **B** | Nemotron, `plan-first` skill as a file (v1's protocol) | Nemotron |
| **B2** | Nemotron, `plan-first` skill pasted into the prompt | Nemotron |
| **C** | **Claude Opus 5.5** | Nemotron |
| **D** | — | **Claude Haiku 5.5** |
| **QA / QB / QB2 / QC** | as A / B / B2 / C (QC reuses C's three Opus plans) | **Qwen3.6-35B-A3B** (local) |

Each arm got the same [spec](spec/SPEC.md) (a Python CLI todo app with JSON persistence, error handling, pytest tests and a README) and ran **3 times**. Output was scored by an automated [19-check grader](grade.py).

## TL;DR

| | **A** Nemotron | **B** +plan-first (file) | **B2** +plan-first (inline) | **C** Opus plans → Nemotron | **D** Haiku 5.5 |
|---|---|---|---|---|---|
| Score per run (/19) | 15, 16, 17 | 16, 15, 16 | 18, 16, 15 | **19**, 12, **19** | **19, 19, 19** |
| Mean | 16.0 | 15.7 | 16.3 | 16.7 (median **19**) | **19.0** |
| Median wall time | 5.5 min | 12.0 min | 4.7 min | 4.4 min | **38 s** |
| Mean turns | 38 | 305 | 57 | 48 | **8** |
| 25-min timeouts | 0 | **2** (tool loop) | 0 | 0 | 0 |
| Spend | $0 | $0 | $0 | ~$0.14 / plan | ~$0.01 / run |
| Code leaves the LAN | No | No | No | No (only spec + plan) | Yes |

**Headlines**

- **Haiku 5.5 is perfect every time and ~8× faster.** On this task there is nothing for a local model to win on quality; the local case is privacy, offline use and zero marginal cost.
- **v1's plan-first gains don't carry over to Nemotron.** As a skill file (v1's protocol), Nemotron never opened the skill, never paused after planning, and one run looped for 50 minutes. With the skill inlined it plans properly, but its plans just restate the spec, and scores stay flat.
- **A frontier planner helps the most.** Opus's plans make the design decisions Nemotron skips: a stored `next_id` so IDs are never reused, the exact output format, and test isolation. They produced the **only two perfect local runs**. The third Opus-planned run failed badly anyway (12/19, a silent crash its own tests didn't catch), so the local executor still has a long tail.
- **Nemotron's two consistent misses:** it reads the spec's `[ID] [x|·] title` as "one of x or ·" and drops the brackets, and it generates IDs as `max(id)+1`, which reuses a deleted top ID. The grader also catches that second bug in **v1's plan-first Qwen run**, which v1's manual check missed.
- **Infrastructure win:** with `--ctx-checkpoints`, 97–99 % of prompt tokens came from llama.cpp's cache. v1's "re-process the full prompt every turn" tax is gone.

**Verdict:**
- Haiku for speed and quality.
- **Opus plans → Nemotron executes** for privacy-sensitive work, reviewing the output.
- Plain Nemotron (A or B2) if nothing may leave the box.
- Avoid plan-first-as-a-file with Nemotron.

## Follow-up: Qwen3.6 on the same harness

Same spec, skill, prompts, pi config, timeouts, server flags (thinking off, ctx checkpoints) and the **same three Opus plans**. Only the model changed: v1's Unsloth `Qwen3.6-35B-A3B-UD-Q4_K_XL` with v1's sampling. Script: [`run_qwen_arms.sh`](run_qwen_arms.sh).

| | **QA** Qwen | **QB** +plan-first (file) | **QB2** +plan-first (inline) | **QC** Opus plans → Qwen |
|---|---|---|---|---|
| Score per run (/19) | 19, 18, 19 | 18, 19, 18 | 19, 18, 18 | **19, 19, 19** |
| Mean | 18.7 | 18.3 | 18.3 | **19.0** |
| Median wall time | 3.6 min | 4.0 min | 2.8 min | 4.5 min |
| Mean turns | 15 | 30 | 19 | 23 |
| 25-min timeouts | 0 | 0 | 0 | 0 |

- **Qwen3.6 beats Nemotron in every arm** — 18.3–19.0 vs 15.7–16.7 — in far fewer turns (15–30 per run vs 38–305) and with no loops.
- **Its only miss is ID reuse** (`max(id)+1`), in 5 of 9 self-planned runs. It always got the bracketed list format right, which Nemotron missed in 9 of 12 runs.
- **Qwen follows the skill-file protocol**: in all 3 QB runs it opened `plan-first.md`, wrote only `TODO.md` in phase 1 and stopped — the workflow Nemotron never followed.
- **Self-planning adds nothing on this task**; Qwen's own plans restate the spec ("auto-incrementing ID") just like Nemotron's.
- **Opus plans → Qwen is 19/19 every run**, matching Haiku 5.5 on score (at ~4.5 min instead of 38 s). The plans' explicit `next_id` decision is exactly what closes Qwen's one gap.
- Qwen + plan-first scored 17/19 on v1's artifacts (one run, older llama.cpp and pi) and averages 18.3 here.

**Updated verdict:** this task now saturates — Haiku, Opus→Qwen and plain Qwen all sit at 18–19. **Qwen3.6 is the better local model here**, and Nemotron 3.5 Lightning is not an upgrade on it. For code that must stay on the LAN, use **Opus plans → Qwen3.6 executes**; for fully offline work, plain Qwen3.6 (QA). A harder task is needed to separate the models further.

Full analysis, per-check failure table, caveats: **[`BENCHMARK.md`](BENCHMARK.md)**. Per-run numbers: [`results/RESULTS.md`](results/RESULTS.md).

## Repository layout

```
├── README.md                 # this file
├── BENCHMARK.md              # full write-up
├── spec/SPEC.md              # the task (byte-identical to v1)
├── skills/plan-first.md      # the plan-first skill (byte-identical to v1)
├── grade.py                  # 19-check grader: agent's pytest + black-box CLI from another cwd + static checks
├── metrics.py                # turns / tokens / cost / timing from pi and Claude Code logs
├── summarize.py              # builds results/ from grades + logs
├── run_nemotron_arms.sh      # local arms A, B, B2, C (execution) — pi + llama-server
├── run_qwen_arms.sh          # follow-up: the same arms with Qwen3.6 (QA, QB, QB2, QC)
├── run_claude_arms.sh        # Claude arms: D (Haiku) and C's planning step (Opus)
├── config/pi-models.json     # isolated pi provider config for the local llama-server
├── plans/
│   ├── opus/                 # Opus 5.5's three TODO.md plans (arm C)
│   ├── nemotron/             # Nemotron's own initial TODO.md plans (B, B2)
│   └── qwen/                 # Qwen3.6's own initial TODO.md plans (QB, QB2)
├── runs/<arm>-r<N>/          # every agent's output, as produced (27 runs)
├── logs/                     # full agent transcripts (*.jsonl.gz), runner.log
└── results/                  # grades.json, grades.txt, summary.json, RESULTS.md
```

## Reproducing

### 1. Model and server

```bash
huggingface-cli download bartowski/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF \
  NVIDIA-Nemotron-3.5-Lightning-30B-A3B-IQ4_XS.gguf --local-dir ~/llm-models
# sha256 c7be5d2ca9700a0e02de1a6707bbcdda3b38b7721caef7ac05bf9dda158aa270

cmake -B build -DGGML_CUDA=ON -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_ARCHITECTURES=75 \
      -DCMAKE_CUDA_COMPILER=/usr/local/cuda/bin/nvcc && cmake --build build -j   # llama.cpp b11641

sudo systemd-run --unit=llama-nemotron --uid=$USER \
  ~/llama.cpp/build/bin/llama-server \
  --model ~/llm-models/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-IQ4_XS.gguf \
  --host 127.0.0.1 --port 8001 --alias nemotron-3.5-lightning \
  -c 131072 -n 32768 --no-context-shift --temp 0.2 --top-p 0.95 \
  --fit on -fa on -ctk q8_0 -ctv q8_0 --jinja --reasoning off \
  --ctx-checkpoints 32 --checkpoint-min-step 0 --metrics
```

`run_nemotron_arms.sh` restarts the `llama-nemotron` unit before each run.

For the Qwen follow-up, download `unsloth/Qwen3.6-35B-A3B-GGUF` → `Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf`. `run_qwen_arms.sh` starts its own `llama-qwen` unit with the same flags as above, except the model, alias and v1's Qwen sampling (`--temp 0.6 --top-p 0.95 --top-k 20`).

### 2. Agents

```bash
npm i -g @earendil-works/pi-coding-agent@1.2.0       # Node >= 22.19
mkdir -p ~/llama-bench-v2/pi-agent && cp config/pi-models.json ~/llama-bench-v2/pi-agent/models.json
echo '{}' > ~/llama-bench-v2/pi-agent/settings.json
# Claude Code 2.1.300, logged in, for the Claude arms
```

Both sides expect a venv with Python 3.12 and `pytest==7.4.4`: `.venv/` on the local box, `.venv-mac/` next to `run_claude_arms.sh`.

### 3. Run

```bash
./run_claude_arms.sh                 # Haiku x3 (arm D) + Opus plans x3 (arm C, planning step)
# copy runs/opusplan-r{1,2,3}/ to ~/llama-bench-v2/opus-plans/ on the GPU box, then:
./run_nemotron_arms.sh A B B2 C      # 3 reps each; 25-min timeout per phase
./run_qwen_arms.sh                   # QA QB QB2 QC, same protocol (QC uses the same opus-plans/)
```

### 4. Grade and summarize

```bash
python3 -I grade.py runs/*-r[123] --json results/grades.json
python3 summarize.py > results/RESULTS.md
```

`grade.py` copies each run to a temp dir first, so artifacts are never modified. Run against v1's artifacts it gives Qwen3 14/19, Qwen3 + plan-first 17/19 and Haiku 4.5 19/19.

## Known caveats

- n = 3 per arm on one small task. A, B and B2 are within noise of each other.
- Haiku ran in Claude Code and Nemotron in pi (as in v1), so tools, system prompt and thinking defaults differ. Nemotron ran with thinking **off**, mirroring v1.
- The Claude arms ran from a MacBook, since Claude Code on the GPU box was logged out during the unattended run. Their outputs were graded on the GPU box.
- The spec's `[ID] [x|·] title` is ambiguous. See BENCHMARK.md for scores with those checks dropped.
- Qwen's quant (UD-Q4_K_XL, 22.4 GB) is larger than Nemotron's (IQ4_XS, 18.9 GB), and each model used its own vendor-recommended sampling. The Qwen arms ran the morning after the Nemotron arms, on the same box and builds.
- **Runs were not sandboxed from each other.** In one run (Nemotron B2-r2, 16/19) the agent searched the benchmark folder during planning and read another run's finished `todo.py`, `TODO.md` and tests (Nemotron B-r3, also 16/19). That run is kept in the tables; excluding it, B2's mean is 16.5. Three Qwen runs ran a similar `find` for `SPEC.md`/`TODO.md` but read nothing from other runs. No Claude run left its own directory.
- The B2 arm and the grader's ID check were added or tightened mid-run, after the first results came in. Both are documented in BENCHMARK.md.

## License

Benchmark artifacts (runs, logs, analysis, scripts) are released under [CC0 1.0](https://creativecommons.org/publicdomain/zero/1.0/). The `plan-first` skill is from a [public Reddit post](https://www.reddit.com/r/LocalLLaMA/comments/1stjwg5/); credit to its author.
