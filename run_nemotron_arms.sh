#!/usr/bin/env bash
# Local arms of the v2 benchmark, run on beefcake with pi + llama-server (Nemotron 3.5 Lightning).
#   A) nemotron-r$N           : no planning — spec in, code out
#   B) nemotron-plan-r$N      : plan-first, Nemotron plans (phase 1) then executes (phase 2, same session)
#   B2) nemotron-planinline-r$N: as B, but the skill text is pasted into the phase-1 prompt (diagnostic)
#   C) opusplan-nemotron-r$N  : Opus 5.5 wrote TODO.md (see run_claude_arms.sh); Nemotron executes it (fresh session)
# Usage: run_nemotron_arms.sh [arm...]   (default: A B C); REPS=3
# llama-server is restarted before every run so each starts from an empty KV cache.
set -u
B="$HOME/llama-bench-v2"
REPS="${REPS:-3}"
ARMS=("${@:-A B C}"); ARMS=(${ARMS[*]})
source "$HOME/.nvm/nvm.sh" >/dev/null
export PI_CODING_AGENT_DIR="$B/pi-agent"          # isolated pi config: only the local provider, no user extensions
export PATH="$B/.venv/bin:$PATH"                   # python 3.12.3 + pytest 7.4.4 (mirrors the Mac venv used for Claude arms)
PI=(pi -p --mode json --no-extensions --no-context-files --no-skills --no-prompt-templates
    --provider llama-nemotron --model nemotron-3.5-lightning --thinking off)
SKILL=(--skill "$B/skills/plan-first.md")
TIMEOUT=1500
mkdir -p "$B/runs" "$B/logs"

TASK_PROMPT="$(cat "$B/spec/SPEC.md")

Work in the current directory. Run \`pytest tests/ -q\` and make sure it passes before you finish."
PLAN_PROMPT="Read SPEC.md. Apply the plan-first skill. Skip Phase 2 questions; make reasonable assumptions. Pause after writing TODO.md."
EXEC_PROMPT="YES, the plan looks correct. Execute every task in TODO.md in order, then run pytest tests/ -q."
EXEC_FRESH_PROMPT="Read SPEC.md and TODO.md. The plan in TODO.md has been reviewed and approved: YES, the plan looks correct. Execute every task in TODO.md in order, then run pytest tests/ -q."

restart_server() {
  pgrep -x pi >/dev/null && { echo "orphan pi found, killing"; pkill -9 -x pi; }
  sudo -n systemctl restart llama-nemotron
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

for n in $(seq 1 "$REPS"); do
  for arm in "${ARMS[@]}"; do
    case "$arm" in
      A)
        d="$B/runs/nemotron-r$n"; rm -rf "$d"; mkdir -p "$d"; cd "$d"; restart_server || continue
        phase "nemotron-r$n" "$B/logs/nemotron-r$n.jsonl" --no-session "$TASK_PROMPT" ;;
      B)
        d="$B/runs/nemotron-plan-r$n"; s="$B/logs/nemotron-plan-r$n-session"
        rm -rf "$d" "$s"; mkdir -p "$d"; cp "$B/spec/SPEC.md" "$d/"; cd "$d"; restart_server || continue
        phase "nemotron-plan-r$n:plan" "$B/logs/nemotron-plan-r$n-phase1.jsonl" --session-dir "$s" "${SKILL[@]}" "$PLAN_PROMPT"
        cp TODO.md "$B/logs/nemotron-plan-r$n-TODO.initial.md" 2>/dev/null
        phase "nemotron-plan-r$n:exec" "$B/logs/nemotron-plan-r$n-phase2.jsonl" -c --session-dir "$s" "${SKILL[@]}" "$EXEC_PROMPT" ;;
      B2)
        # Diagnostic: identical to B, but the plan-first skill text is pasted into the prompt instead of
        # being offered as a skill file the model must choose to read.
        d="$B/runs/nemotron-planinline-r$n"; s="$B/logs/nemotron-planinline-r$n-session"
        rm -rf "$d" "$s"; mkdir -p "$d"; cp "$B/spec/SPEC.md" "$d/"; cd "$d"; restart_server || continue
        # (prompt must not start with "-": the skill's frontmatter "---" would be parsed as a CLI option)
        phase "nemotron-planinline-r$n:plan" "$B/logs/nemotron-planinline-r$n-phase1.jsonl" --session-dir "$s" \
          "Follow this skill exactly:

$(cat "$B/skills/plan-first.md")

---

$PLAN_PROMPT"
        cp TODO.md "$B/logs/nemotron-planinline-r$n-TODO.initial.md" 2>/dev/null
        phase "nemotron-planinline-r$n:exec" "$B/logs/nemotron-planinline-r$n-phase2.jsonl" -c --session-dir "$s" "$EXEC_PROMPT" ;;
      C)
        d="$B/runs/opusplan-nemotron-r$n"; src="$B/opus-plans/opusplan-r$n"
        [ -f "$src/TODO.md" ] || { echo "missing $src/TODO.md, skipping C r$n"; continue; }
        rm -rf "$d"; mkdir -p "$d"; cp "$B/spec/SPEC.md" "$src/TODO.md" "$d/"; cd "$d"; restart_server || continue
        phase "opusplan-nemotron-r$n:exec" "$B/logs/opusplan-nemotron-r$n.jsonl" --no-session "${SKILL[@]}" "$EXEC_FRESH_PROMPT" ;;
    esac
  done
done
echo ALL_NEMOTRON_ARMS_DONE
