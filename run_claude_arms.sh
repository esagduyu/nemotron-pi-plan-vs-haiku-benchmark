#!/usr/bin/env bash
# Claude-side arms of the v2 benchmark, run headless with Claude Code on the Mac.
#   D) haiku-r$N         : Haiku 5.5 builds the project from the spec (no planning skill)
#   C) opusplan-r$N      : Opus 5.5 runs plan-first Phase 1 only -> TODO.md (Nemotron executes it later on beefcake)
# Isolation: no user settings (=> no plugins/hooks), no MCP, skills disabled, empty working dir.
set -u
B="$(cd "$(dirname "$0")" && pwd)"
CLAUDE="$HOME/.local/bin/claude"
export PATH="$B/.venv-mac/bin:$PATH"          # python 3.12 + pytest 7.4.4, matching beefcake
ISO=(--setting-sources project,local --strict-mcp-config --disable-slash-commands --no-session-persistence)
REPS="${REPS:-3}"
mkdir -p "$B/runs" "$B/logs"

TASK_PROMPT="$(cat "$B/spec/SPEC.md")

Work in the current directory. Run \`pytest tests/ -q\` and make sure it passes before you finish."
PLAN_PROMPT="Read SPEC.md. Apply the plan-first skill. Skip Phase 2 questions; make reasonable assumptions. Pause after writing TODO.md."

for n in $(seq 1 "$REPS"); do
  d="$B/runs/haiku-r$n"; rm -rf "$d"; mkdir -p "$d"; cd "$d"
  t0=$(date +%s)
  "$CLAUDE" -p --model claude-haiku-5-5 "${ISO[@]}" --max-budget-usd 3 \
    --allowedTools "Read,Write,Edit,Bash,Glob,Grep" \
    --output-format stream-json --verbose "$TASK_PROMPT" </dev/null > "$B/logs/haiku-r$n.jsonl" 2> "$B/logs/haiku-r$n.stderr"
  echo "haiku-r$n exit=$? wall=$(( $(date +%s) - t0 ))s"
done

for n in $(seq 1 "$REPS"); do
  d="$B/runs/opusplan-r$n"; rm -rf "$d"; mkdir -p "$d"; cp "$B/spec/SPEC.md" "$d/"; cd "$d"
  t0=$(date +%s)
  "$CLAUDE" -p --model claude-opus-5-5 "${ISO[@]}" --max-budget-usd 5 \
    --append-system-prompt "$(cat "$B/skills/plan-first.md")" \
    --allowedTools "Read,Write,Glob,Grep" \
    --output-format stream-json --verbose "$PLAN_PROMPT" </dev/null > "$B/logs/opusplan-r$n.jsonl" 2> "$B/logs/opusplan-r$n.stderr"
  echo "opusplan-r$n exit=$? wall=$(( $(date +%s) - t0 ))s files=$(ls | tr '\n' ' ')"
done
echo ALL_CLAUDE_ARMS_DONE
