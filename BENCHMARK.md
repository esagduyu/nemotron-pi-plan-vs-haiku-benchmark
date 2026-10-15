# Nemotron 3.5 Lightning (local, via pi) × planning strategies vs Claude Haiku 5.5

**Date:** 2026-10-15 (Nemotron runs 00:00–02:30 PDT, unattended; Qwen follow-up 07:58–08:45 PDT)
**Predecessor:** [qwen-pi-plan-vs-haiku-benchmark](https://github.com/esagduyu/qwen-pi-plan-vs-haiku-benchmark) (v1, 2026-05-01) — same spec, same `plan-first` skill, same hardware.

## Questions

1. How does **NVIDIA Nemotron 3.5 Lightning 30B-A3B** — the newest 30B-class agentic MoE that fits this box — do on v1's agentic coding task, and how does it compare to **Claude Haiku 5.5**?
2. **Does planning help, and does it matter *who* plans?** v1 found that the `plan-first` skill took local Qwen3 from 14 → 17 points. Here we separate the planner from the executor:
   - the local model plans for itself, and
   - a frontier model (**Claude Opus 5.5**) writes the plan and the local model executes it.

## Setup

| | |
|---|---|
| Hardware | beefcake — Corsair One i160, i9-9900K, RTX 2080 Ti (11 GB, Turing), 31 GB RAM, Ubuntu 24.04.4 |
| Local model | [`bartowski/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF`](https://huggingface.co/bartowski/NVIDIA-Nemotron-3.5-Lightning-30B-A3B-GGUF) **IQ4_XS** (18.9 GB; sha256 `c7be5d2c…aa270`). 30 B total / 3 B active, hybrid Mamba-attention MoE. IQ4_XS chosen to match v1's ~21 GB Qwen footprint. |
| Inference | llama.cpp **b11641** (`e467e5b5`, CUDA 13.3, `-DCMAKE_CUDA_ARCHITECTURES=75`), NVIDIA 580.178.04. ~42 tok/s generation; 9.5 GB VRAM + experts in RAM. |
| Local agent | [pi](https://github.com/earendil-works/pi) **1.2.0** (`@earendil-works/pi-coding-agent`; v1 used 0.70.6), Node 22.22 |
| Cloud agent | Claude Code **2.1.300**, headless (`claude -p`), models `claude-haiku-5-5` and `claude-opus-5-5` |
| Task | v1's [`spec/SPEC.md`](spec/SPEC.md), byte-identical (sha256 `7d000ba9…`) — a Python CLI todo app with JSON persistence, error handling, pytest tests, README |
| Skill | v1's [`skills/plan-first.md`](skills/plan-first.md), byte-identical (sha256 `26f021bf…`) |
| Reps | **3 runs per arm** (v1 had 1) |
| Grading | [`grade.py`](grade.py) — 19 automated checks, black-box CLI run from a different cwd (v1 graded by hand) |

### llama-server flags

```bash
llama-server --model NVIDIA-Nemotron-3.5-Lightning-30B-A3B-IQ4_XS.gguf \
  --host 127.0.0.1 --port 8001 --alias nemotron-3.5-lightning \
  -c 131072 -n 32768 --no-context-shift \
  --temp 0.2 --top-p 0.95 \
  --fit on -fa on -ctk q8_0 -ctv q8_0 \
  --jinja --reasoning off \
  --ctx-checkpoints 32 --checkpoint-min-step 0 \
  --metrics
```

- Context, KV-cache quantization and `--fit` are v1's Qwen flags unchanged.
- **Thinking off** (`--reasoning off` server-side + `pi --thinking off`) mirrors v1, which ran Qwen with thinking off. Sampling follows NVIDIA's recommendation for non-thinking mode (temperature 0.2).
- `--ctx-checkpoints 32 --checkpoint-min-step 0` is pi's documented setting for hybrid models; without it llama.cpp can't reuse the prompt cache between turns. With it, **97–99 % of prompt tokens were served from cache** in every local arm. v1's "full prompt re-processing every turn" tax (Qwen's SWA layers) is gone.
- The server was **restarted before every run** (empty KV cache), and `pgrep -x pi` was checked for orphans (v1's hang cause). None occurred.

### Isolation

- **pi** ran with its own config dir (`PI_CODING_AGENT_DIR` → [`config/pi-models.json`](config/pi-models.json) only), `--no-extensions --no-context-files --no-skills --no-prompt-templates`. The author's 24 installed pi extensions were not loaded.
- **Claude Code** ran with `--setting-sources project,local --strict-mcp-config --disable-slash-commands` in an empty directory: no user plugins, hooks, MCP servers or skills. (`--bare` would be cleaner but cannot use subscription auth.)
- Both sides used **Python 3.12 + pytest 7.4.4** with a `python` on PATH.

## Arms

| Arm | Planner | Executor | Protocol |
|---|---|---|---|
| **A** | — | Nemotron | Spec + "run `pytest tests/ -q` and make sure it passes" → one `pi -p` session |
| **B** | Nemotron (skill **file**) | Nemotron | v1's two-phase plan-first protocol, verbatim: phase 1 `pi -p --skill plan-first.md "Read SPEC.md. Apply the plan-first skill. Skip Phase 2 questions; make reasonable assumptions. Pause after writing TODO.md."`; phase 2 resumes the same session with `"YES, the plan looks correct. Execute every task in TODO.md in order, then run pytest tests/ -q."` |
| **B2** | Nemotron (skill **inlined**) | Nemotron | *Diagnostic, added mid-run.* Identical to B except the skill text is pasted into the phase-1 prompt instead of offered as a file. See why below. |
| **C** | **Opus 5.5** | Nemotron | Opus runs phase 1 (same prompt, skill as system prompt, tools limited to Read/Write/Glob/Grep) → `TODO.md` only. Nemotron gets `SPEC.md` + `TODO.md` in a fresh pi session: "Read SPEC.md and TODO.md. The plan … has been reviewed and approved … Execute every task in TODO.md in order, then run pytest tests/ -q." |
| **D** | — | **Haiku 5.5** | Same prompt as A, `claude -p` with Read/Write/Edit/Bash/Glob/Grep |

Every phase had a hard **25-minute timeout**.

## Results

| Arm | Setup | Score per run (/19) | Mean | Median wall | Mean turns | Timeouts | Spend |
|---|---|---|---|---|---|---|---|
| **A** | Nemotron, no planning | 15, 16, 17 | **16.0** | 5.5 min | 38 | 0 | $0 |
| **B** | Nemotron plans (skill file) → Nemotron | 16, 15, 16 | **15.7** | 12.0 min | 305 | **2** | $0 |
| **B2** | Nemotron plans (skill inlined) → Nemotron | 18, 16, 15 | **16.3** | 4.7 min | 57 | 0 | $0 |
| **C** | **Opus 5.5 plans → Nemotron** | **19**, 12, **19** | **16.7** (median 19) | 4.4 min | 48 | 0 | $0.43 total (~$0.14/plan) |
| **D** | **Haiku 5.5** | **19, 19, 19** | **19.0** | **38 s** | 8 | 0 | $0.03 total (~$0.01/run) |

Wall time for C includes Opus's planning (28–33 s). Per-run detail: [`results/RESULTS.md`](results/RESULTS.md); raw grades: [`results/grades.json`](results/grades.json).

For reference, the same grader on v1's artifacts: Qwen3 no-plan **14/19**, Qwen3 + plan-first **17/19**, Haiku 4.5 **19/19** (one run each; older llama.cpp and pi).

### What failed, and how often

| Check | A | B | B2 | C | D |
|---|---|---|---|---|---|
| `list` format exactly `[ID] [x\|·] title` | 0/3 | 0/3 | 1/3 | 2/3 | 3/3 |
| IDs never reused after removing the *highest* ID | 1/3 | 0/3 | 0/3 | 2/3 | 3/3 |
| Tests don't leave `todos.json` in the project | 2/3 | 2/3 | 3/3 | 3/3 | 3/3 |
| Everything else (15 checks) | ✅ | ✅ | ✅ (one README miss) | ✅ except C-r2 | ✅ |

The two big Nemotron misses are the same in every self-planned arm:

1. **List format.** Nemotron prints `[1] · first` / `[1] x first` — it treats the spec's `[x|·]` as *usage-syntax notation* ("one of x or ·") rather than literal brackets. That's a defensible reading of an ambiguous spec line; Haiku 4.5, Haiku 5.5 and Opus all read it literally. Counted as a miss because the spec's own example output uses the brackets.
2. **ID reuse.** Nemotron computes the next ID as `max(id) + 1`. That's monotonic *until you delete the highest ID*, then the deleted ID comes straight back. v1's hand check (delete ID 1) missed this; **v1's plan-first Qwen run has the same bug** — the grader flags it when re-run on v1's artifacts. A-r1 was worse: both todos got ID 1.

## Findings

### 1. Haiku 5.5 is perfect and ~8× faster

3/3 runs at 19/19, 7–9 turns, 38–42 s, about a cent each, 11–15 tests per run. On this task there is nothing left for a local model to beat on quality. The local case rests entirely on privacy, offline use and zero marginal cost.

### 2. Plan-first *as a skill file* doesn't work with Nemotron

In all 3 B runs Nemotron **never opened the skill file** (0 `read` calls on `plan-first.md`; pi lists skills by name and description and expects the model to load them). It ignored "Pause after writing TODO.md" and built the whole app during the planning phase.

- In **B-r1** it wrote `TODO.md`, built everything, then ran `rm -f TODO.md`. Phase 2 had nothing to do (7 s).
- In **B-r2** it fell into a **tool loop** (`rm -rf __pycache__` → `ls` → `pytest`, ×200+) and hit the 25-min timeout. Phase 2 resumed the same session, **re-entered the loop** and timed out again: 50 min, 786 turns, 74 k output tokens.

Qwen 3.6 followed the identical protocol correctly in v1. This is the "calls tools nonstop" behaviour Unsloth warns about for Nemotron 3.5.

### 3. When Nemotron does follow plan-first, its plans don't help

**B2** pasted the skill text into the prompt. Nemotron then followed the workflow properly in 3/3 runs: phase 1 wrote only `TODO.md` in 26–48 s and stopped. But scores stayed flat (mean 16.3 vs 16.0) because **its plans restate the spec instead of making decisions**.

- All 5 surviving Nemotron plans repeat "monotonically increasing, never reused", but none says *how*: there's no stored counter or `next_id`. Execution then used `max(id)+1` every time.
- All 5 copy the `[ID] [x|·] title` line verbatim, so the ambiguity passes straight through to the code.

The plan-first gains from v1 did not reproduce with this model.

### 4. A frontier planner fixes the spec-reading errors, but not execution reliability

Opus's plans make concrete design decisions: an on-disk format with an explicit `next_id` ("so IDs are never reused after `rm`"), atomic writes, a `TodoError` → stderr → exit 1 path, `monkeypatch.chdir` for test isolation, and UTF-8 stdout for `·`. With those plans Nemotron produced the **only two perfect local runs** (C-r1, C-r3: 19/19 in 15–16 turns, 3.6–4.4 min).

**C-r2 failed badly (12/19).** Nemotron took 112 turns and 25 min with 23 tool errors, and shipped a `save()` that calls `os.makedirs("")` on the default `./todos.json` path. Run from a fresh directory, every command **exits 1 silently** — a broad `except` swallows the traceback. Its own 9 tests passed because they set `TODO_FILE` to an absolute temp path, so the tests never exercised the default path. The plan was fine; the execution wasn't.

So: **who plans matters** (median 19 vs 16; C-r1 and C-r3 are two of only three Nemotron runs, out of 12, without the ID bug), but the local executor still has a long-tail failure rate, and with n = 3 one bad run decides the mean. Cost: ~$0.14 per Opus plan, and only the spec and plan go to Anthropic — the code is written and run locally.

### 5. Checkbox discipline is inconsistent

Executing Opus's plans (C), Nemotron ticked 2/24, 0/25 and 0/21 checkboxes while still implementing the plans' content. Executing its own plans (B2), it ticked 0/13, 14/14 and 15/15. Checkbox state doesn't predict quality either way (C-r1 and C-r3 scored 19/19 with almost nothing ticked). Don't use `TODO.md` checkboxes as a progress signal for this model.

### 6. Loops need a circuit breaker

Every timeout came from the same pattern: a successful `pytest`, then cleanup commands, then `pytest` again, forever. Practical mitigations for anyone using Nemotron with pi:

- Use a per-phase timeout.
- **Start a fresh session after a timeout.** Resuming carries the loop in the context.
- Consider a turn cap.

## Verdict

| If you want… | Use |
|---|---|
| The best result, fast | **Haiku 5.5.** 19/19 every time, ~40 s, ~1¢. |
| Code that never leaves the LAN, best quality | **Opus plans → Nemotron executes** (median 19/19, ~4 min, ~$0.14/plan; only the spec and plan leave the box). Budget for an occasional bad run and review the output. |
| Fully local, no cloud at all | **Nemotron without planning (A)** or **with the skill inlined (B2)** — both ~16/19, ~5 min. Don't use B: plan-first as a skill file gives nothing with Nemotron and risks long loops. |

Versus v1's Qwen 3.6 + plan-first (17/19, 3.3 min, one run), Nemotron 3.5 Lightning is **not a clear upgrade for this harness and task**. It's similar on quality, worse at following a skill workflow, and more loop-prone. The same-harness Qwen re-run below confirms it: Qwen3.6 is better on this task.

## Follow-up: Qwen3.6-35B-A3B on the same harness

Run with [`run_qwen_arms.sh`](run_qwen_arms.sh), a copy of `run_nemotron_arms.sh` with only the model and server changed:

- **Model:** v1's `unsloth/Qwen3.6-35B-A3B-GGUF` **UD-Q4_K_XL** (22.4 GB).
- **Server:** the same llama-server flags as above — thinking off, `--ctx-checkpoints 32 --checkpoint-min-step 0`, same context, KV quantization and `--fit`. Sampling is v1's Qwen settings (`--temp 0.6 --top-p 0.95 --top-k 20`). Measured ~36 tok/s generation; 92–98 % of prompt tokens served from cache.
- **Everything else identical:** spec, skill, prompts, isolated pi 1.2.0 config, 25-min phase timeout, server restart per run, 3 reps. **QC executes the same three Opus plans as C**, so C vs QC isolates the executor.

| Arm | Setup | Score per run (/19) | Mean | Median wall | Mean turns | Timeouts |
|---|---|---|---|---|---|---|
| **QA** | Qwen3.6, no planning | 19, 18, 19 | **18.7** | 3.6 min | 15 | 0 |
| **QB** | Qwen3.6 plans (skill file) → Qwen3.6 | 18, 19, 18 | **18.3** | 4.0 min | 30 | 0 |
| **QB2** | Qwen3.6 plans (skill inlined) → Qwen3.6 | 19, 18, 18 | **18.3** | 2.8 min | 19 | 0 |
| **QC** | **Opus 5.5 plans → Qwen3.6** | **19, 19, 19** | **19.0** | 4.5 min | 23 | 0 |

Side by side with Nemotron (mean /19): A 16.0 → QA 18.7 · B 15.7 → QB 18.3 · B2 16.3 → QB2 18.3 · C 16.7 → QC 19.0.

| Check | QA | QB | QB2 | QC |
|---|---|---|---|---|
| `list` format exactly `[ID] [x\|·] title` | 3/3 | 3/3 | 3/3 | 3/3 |
| IDs never reused after removing the *highest* ID | 2/3 | 1/3 | 1/3 | 3/3 |
| Everything else (17 checks) | ✅ | ✅ | ✅ | ✅ |

What this shows:

1. **The executor matters more than the planner.** With identical Opus plans, Nemotron scored 19, 12, 19 and Qwen 19, 19, 19. With no plan, Qwen (18.7) already beats every Nemotron arm, including Opus-planned Nemotron's mean.
2. **Qwen reads the spec literally** and got the bracketed list format right in all 12 runs. Its single recurring bug is `max(id)+1` ID generation (5 of 9 self-planned runs) — the same bug Nemotron has and v1's plan-first Qwen had.
3. **Qwen follows plan-first as a skill file.** In all 3 QB runs it opened `plan-first.md`, wrote only `TODO.md` in phase 1 and stopped (44–60 s), then executed in phase 2. Nemotron never did any of this.
4. **Self-planning still adds nothing.** Qwen's own plans restate the spec ("auto-incrementing ID"); none of the six makes the `next_id` decision. All three Opus plans do, and all three Opus-planned Qwen programs implement it.
5. **No loops.** 15–30 turns per run on average and no timeouts, vs 38–305 for Nemotron.
6. **The task saturates.** Haiku 5.5, Opus → Qwen and plain Qwen all score 18–19. The remaining signal is one edge case, so a harder task is needed to separate these setups further.

**Updated verdict:** for this harness and task, **Qwen3.6-35B-A3B is the better local model**; Nemotron 3.5 Lightning is not an upgrade. Code that must stay on the LAN → **Opus plans → Qwen3.6** (19/19 every run, ~4.5 min). Fully offline → **plain Qwen3.6** (~18.7/19, ~3.6 min). Fastest and cheapest overall is still Haiku 5.5.

## Caveats

- **One small task, n = 3 per arm.** Score differences of ±1 between A, B and B2 are within noise. The C-vs-self-planned gap and the Haiku gap are the robust signals.
- **Different harnesses.** Haiku ran in Claude Code; Nemotron ran in pi. This mirrors v1, but some of the gap is harness: tool design, system prompt, and Claude Code's default adaptive thinking for Haiku vs thinking **off** for Nemotron. Nemotron with reasoning on is an untested configuration and might do better.
- **The Claude arms ran on a MacBook**, not beefcake: Claude Code on beefcake was logged out and the run was unattended. Wall time for those arms is dominated by API latency; the outputs were graded on beefcake like everything else.
- **Skill delivery differs between B and C.** pi offers skills as a file to read; Opus got the skill text as an appended system prompt. B2 exists to control for this on the Nemotron side.
- **Quantization.** IQ4_XS at temperature 0.2. Q4_K_XL (25.5 GB) would need more RAM spill; untested.
- **The spec's list-format line is ambiguous** (see above). Dropping the two checks that depend on it, scored out of 17:

  | Arm | A | B | B2 | C | D |
  |---|---|---|---|---|---|
  | Mean | 16.0 | 15.7 | 15.7 | 15.3 | 17 |
  | Median | — | — | — | 17 | — |

  On that basis C's advantage survives **only in the median and in the ID check**. Its mean falls below A's because of C-r2. Read the planner effect as "fixes design errors when execution goes right", not as a uniform lift.
- **Qwen vs Nemotron isn't perfectly matched.** Qwen's quant is larger (UD-Q4_K_XL 22.4 GB vs IQ4_XS 18.9 GB), each used its own recommended sampling, and the Qwen arms ran the next morning (same box, builds and harness).
- **Runs were not sandboxed from each other.** In **B2-r2** Nemotron searched the benchmark folder while planning and read another run's finished `todo.py`, `TODO.md` and tests (B-r3). Both scored 16/19; the run is kept in the tables, and B2's mean without it is 16.5. Three Qwen runs (QB-r1, all QC) ran a `find` for `SPEC.md`/`TODO.md` across the folder but read nothing from other runs. No Claude run left its directory. A future harness should run each agent in an isolated directory or container.
- **Grader strictness.** The ID check removes the *highest* ID, which v1's manual check didn't. It is stricter than v1 and correct per the spec's "never reused even after `rm`".

## Reproducing

See [`README.md`](README.md#reproducing).
