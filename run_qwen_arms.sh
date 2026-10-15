#!/usr/bin/env bash
# Qwen3.6-35B-A3B on the v2 harness (follow-up to the Nemotron arms): same spec, skill, prompts, pi config,
# timeouts and Opus plans as run_nemotron_arms.sh — only the model/server changes.
#   QA)  qwen-r$N              : no planning
#   QB)  qwen-plan-r$N         : plan-first, skill as a file (v1's protocol)
#   QB2) qwen-planinline-r$N   : plan-first, skill text pasted into the phase-1 prompt
#   QC)  opusplan-qwen-r$N     : executes the same Opus 5.5 TODO.md files used by arm C
# Usage: run_qwen_arms.sh [arm...]   (default: A B B2 C); REPS=3
# Server: transient unit llama-qwen (see start_qwen_server below); restarted before every run.
set -u
B="$HOME/llama-bench-v2"
REPS="${REPS:-3}"
ARMS=("${@:-A B B2 C}"); ARMS=(${ARMS[*]})
source "$HOME/.nvm/nvm.sh" >/dev/null
export PI_CODING_AGENT_DIR="$B/pi-agent"          # isolated pi config: only the local provider, no user extensions
export PATH="$B/.venv/bin:$PATH"                   # python 3.12.3 + pytest 7.4.4 (mirrors the Mac venv used for Claude arms)
PI=(pi -p --mode json --no-extensions --no-context-files --no-skills --no-prompt-templates
    --provider llama-qwen --model qwen3.6-35b-a3b --thinking off)
SKILL=(--skill "$B/skills/plan-first.md")
TIMEOUT=1500
mkdir -p "$B/runs" "$B/logs"

TASK_PROMPT="$(cat "$B/spec/SPEC.md")

Work in the current directory. Run \`pytest tests/ -q\` and make sure it passes before you finish."
PLAN_PROMPT="Read SPEC.md. Apply the plan-first skill. Skip Phase 2 questions; make reasonable assumptions. Pause after writing TODO.md."
EXEC_PROMPT="YES, the plan looks correct. Execute every task in TODO.md in order, then run pytest tests/ -q."
EXEC_FRESH_PROMPT="Read SPEC.md and TODO.md. The plan in TODO.md has been reviewed and approved: YES, the plan looks correct. Execute every task in TODO.md in order, then run pytest tests/ -q."

start_qwen_server() {  # v1's Qwen sampling + v2's server flags (thinking off, ctx checkpoints, metrics)
  systemctl is-active -q llama-qwen && return 0
  sudo -n systemctl stop llama-nemotron llama-server 2>/dev/null; sudo -n systemctl reset-failed llama-qwen 2>/dev/null
  sudo -n systemd-run --unit=llama-qwen --uid=ege --gid=ege --property=Restart=no \
    "$HOME/llama.cpp/build/bin/llama-server" \
    --model "$HOME/llm-models/Qwen3.6-35B-A3B-UD-Q4_K_XL.gguf" \
    --host 127.0.0.1 --port 8001 --alias qwen3.6-35b-a3b \
    -c 131072 -n 32768 --no-context-shift \
    --temp 0.6 --top-p 0.95 --top-k 20 --repeat-penalty 1.00 --presence-penalty 0.00 \
    --fit on -fa on -ctk q8_0 -ctv q8_0 \
    --jinja --reasoning off \
    --ctx-checkpoints 32 --checkpoint-min-step 0 \
    --metrics
}

restart_server() {
  pgrep -x pi >/dev/null && { echo "orphan pi found, killing"; pkill -9 -x pi; }
  sudo -n systemctl restart llama-qwen
  for i in $(seq 1 60); do curl -sf http://127.0.0.1:8001/health >/dev/null && return 0; sleep 2; done
  echo "server failed to come up"; return 1
}

phase() {  # phase <label> <logfile> <pi args...>
  local label="$1" log="$2"; shift 2
  local t0=$(date +%s.%N)
  timeout --foreground "$TIMEOUT" "${PI[@]}" "$@" </dev/null > "$log" 2> "${log%.jsonl}.stderr"
  local rc=$?
  printf '%s exit=%s wall=%.1fs\n' "$label" "$rc" "$(echo "$(date +%s.%N) - $t0" | bc)"
}

start_qwen_server
for n in $(seq 1 "$REPS"); do
  for arm in "${ARMS[@]}"; do
    case "$arm" in
      A)
        d="$B/runs/qwen-r$n"; rm -rf "$d"; mkdir -p "$d"; cd "$d"; restart_server || continue
        phase "qwen-r$n" "$B/logs/qwen-r$n.jsonl" --no-session "$TASK_PROMPT" ;;
      B)
        d="$B/runs/qwen-plan-r$n"; s="$B/logs/qwen-plan-r$n-session"
        rm -rf "$d" "$s"; mkdir -p "$d"; cp "$B/spec/SPEC.md" "$d/"; cd "$d"; restart_server || continue
        phase "qwen-plan-r$n:plan" "$B/logs/qwen-plan-r$n-phase1.jsonl" --session-dir "$s" "${SKILL[@]}" "$PLAN_PROMPT"
        cp TODO.md "$B/logs/qwen-plan-r$n-TODO.initial.md" 2>/dev/null
        phase "qwen-plan-r$n:exec" "$B/logs/qwen-plan-r$n-phase2.jsonl" -c --session-dir "$s" "${SKILL[@]}" "$EXEC_PROMPT" ;;
      B2)
        # Diagnostic: identical to B, but the plan-first skill text is pasted into the prompt instead of
        # being offered as a skill file the model must choose to read.
        d="$B/runs/qwen-planinline-r$n"; s="$B/logs/qwen-planinline-r$n-session"
        rm -rf "$d" "$s"; mkdir -p "$d"; cp "$B/spec/SPEC.md" "$d/"; cd "$d"; restart_server || continue
        # (prompt must not start with "-": the skill's frontmatter "---" would be parsed as a CLI option)
        phase "qwen-planinline-r$n:plan" "$B/logs/qwen-planinline-r$n-phase1.jsonl" --session-dir "$s" \
          "Follow this skill exactly:

$(cat "$B/skills/plan-first.md")

---

$PLAN_PROMPT"
        cp TODO.md "$B/logs/qwen-planinline-r$n-TODO.initial.md" 2>/dev/null
        phase "qwen-planinline-r$n:exec" "$B/logs/qwen-planinline-r$n-phase2.jsonl" -c --session-dir "$s" "$EXEC_PROMPT" ;;
      C)
        d="$B/runs/opusplan-qwen-r$n"; src="$B/opus-plans/opusplan-r$n"
        [ -f "$src/TODO.md" ] || { echo "missing $src/TODO.md, skipping C r$n"; continue; }
        rm -rf "$d"; mkdir -p "$d"; cp "$B/spec/SPEC.md" "$src/TODO.md" "$d/"; cd "$d"; restart_server || continue
        phase "opusplan-qwen-r$n:exec" "$B/logs/opusplan-qwen-r$n.jsonl" --no-session "${SKILL[@]}" "$EXEC_FRESH_PROMPT" ;;
    esac
  done
done
echo ALL_QWEN_ARMS_DONE
