#!/usr/bin/env python3
"""Build results tables from grades + agent logs.

Run from the benchmark root:  python3 summarize.py > results/RESULTS.md
Reads: results/grades.json (from grade.py --json), logs/*.jsonl, logs/runner.log
Writes: results/summary.json, and a markdown report on stdout.
"""
import json
import re
import statistics as st
from pathlib import Path

from metrics import metrics

ROOT = Path(__file__).resolve().parent
LOGS = ROOT / "logs"

ARMS = [
    ("A", "nemotron", "Nemotron, no planning"),
    ("B", "nemotron-plan", "Nemotron plans (skill file) → Nemotron executes"),
    ("B2", "nemotron-planinline", "Nemotron plans (skill inlined in prompt) → Nemotron executes"),
    ("C", "opusplan-nemotron", "Opus 5.5 plans → Nemotron executes"),
    ("D", "haiku", "Haiku 5.5, no planning"),
    # follow-up: Qwen3.6-35B-A3B on the same harness (run_qwen_arms.sh); QC reuses arm C's Opus plans
    ("QA", "qwen", "Qwen3.6, no planning"),
    ("QB", "qwen-plan", "Qwen3.6 plans (skill file) → Qwen3.6 executes"),
    ("QB2", "qwen-planinline", "Qwen3.6 plans (skill inlined in prompt) → Qwen3.6 executes"),
    ("QC", "opusplan-qwen", "Opus 5.5 plans (same plans as C) → Qwen3.6 executes"),
]


def runner_walls():
    walls, exits = {}, {}
    p = LOGS / "runner.log"
    for line in p.read_text().splitlines() if p.exists() else []:
        m = re.match(r"(\S+?)(?::(plan|exec))? exit=(\d+) wall=([\d.]+)s", line)
        if m:
            run, ph, rc, w = m.group(1), m.group(2) or "all", int(m.group(3)), float(m.group(4))
            walls.setdefault(run, {})[ph] = w
            exits.setdefault(run, {})[ph] = rc
    return walls, exits


def add(a, b):
    out = dict(a)
    for k, v in b.items():
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            out[k] = out.get(k, 0) + v
        elif isinstance(v, bool):
            out[k] = out.get(k, False) or v
    return out


def run_record(prefix, n, grades, walls, exits):
    run = f"{prefix}-r{n}"
    g = grades.get(run)
    if g is None:
        return None
    rec = {"run": run, "score": g["passed"], "total": g["total"], "tests": g.get("tests"),
           "loc": g.get("runtime_loc"), "failed": list(g["failed"].keys())}
    if prefix == "haiku":
        m = metrics(LOGS / f"{run}.jsonl")
        rec.update(wall_s=m["duration_s"], turns=m["turns"], out_tok=m["output_tokens"], cost=m["cost_usd"], timeouts=0)
    elif prefix.startswith("opusplan-"):
        plan = metrics(LOGS / f"opusplan-r{n}.jsonl")
        ex = metrics(LOGS / f"{run}.jsonl")
        rec.update(wall_s=round(plan["duration_s"] + walls[run]["exec"], 1), plan_wall_s=plan["duration_s"],
                   turns=ex["turns"], plan_turns=plan["turns"], out_tok=ex["output_tokens"], cost=plan["cost_usd"],
                   timeouts=sum(rc == 124 for rc in exits[run].values()),
                   todo_checked=None)
        todo = ROOT / "runs" / run / "TODO.md"
        if todo.exists():
            t = todo.read_text()
            rec["todo_checked"] = f"{t.count('[x]')}/{t.count('[x]') + t.count('[ ]')}"
    elif prefix.endswith(("-plan", "-planinline")):
        p1 = metrics(LOGS / f"{run}-phase1.jsonl")
        p2 = metrics(LOGS / f"{run}-phase2.jsonl")
        both = add(p1, p2)
        rec.update(wall_s=round(sum(walls[run].values()), 1), plan_wall_s=walls[run].get("plan"),
                   turns=both["turns"], plan_turns=p1["turns"], out_tok=both["output_tokens"], cost=0.0,
                   timeouts=sum(rc == 124 for rc in exits[run].values()),
                   skill_read=p1.get("skill_file_read"),
                   todo_written=(LOGS / f"{run}-TODO.initial.md").exists(),
                   code_in_plan_phase=None)
    else:
        m = metrics(LOGS / f"{run}.jsonl")
        rec.update(wall_s=walls[run]["all"], turns=m["turns"], out_tok=m["output_tokens"], cost=0.0,
                   timeouts=int(exits[run]["all"] == 124))
    return rec


def fmt_s(s):
    return f"{s/60:.1f} min" if s >= 90 else f"{s:.0f} s"


def main():
    grades = {Path(g["run"]).name: g for g in json.loads((ROOT / "results" / "grades.json").read_text())}
    walls, exits = runner_walls()
    summary, out = [], []
    out.append("| Arm | Setup | Runs | Score (each run, /19) | Mean score | Median wall | Mean turns | Timeouts | Spend |")
    out.append("|---|---|---|---|---|---|---|---|---|")
    per_run = []
    for key, prefix, label in ARMS:
        recs = [r for n in (1, 2, 3) if (r := run_record(prefix, n, grades, walls, exits))]
        if not recs:
            continue
        per_run += [(key, r) for r in recs]
        scores = [r["score"] for r in recs]
        agg = {"arm": key, "label": label, "runs": len(recs), "scores": scores,
               "mean_score": round(st.mean(scores), 1), "median_wall_s": st.median(r["wall_s"] for r in recs),
               "mean_turns": round(st.mean(r["turns"] for r in recs), 1),
               "timeouts": sum(r["timeouts"] for r in recs), "spend_usd": round(sum(r["cost"] or 0 for r in recs), 3)}
        summary.append({**agg, "runs_detail": recs})
        spend = f"${agg['spend_usd']:.2f}" if agg["spend_usd"] else "$0 (local)"
        out.append(f"| **{key}** | {label} | {len(recs)} | {', '.join(map(str, scores))} | **{agg['mean_score']}** | "
                   f"{fmt_s(agg['median_wall_s'])} | {agg['mean_turns']} | {agg['timeouts']} | {spend} |")
    out.append("")
    out.append("### Per run")
    out.append("")
    out.append("| Run | Score | Wall | Turns | Output tok | Tests | Failed checks |")
    out.append("|---|---|---|---|---|---|---|")
    for key, r in per_run:
        extra = ""
        if r.get("timeouts"):
            extra = f" ⏱ {r['timeouts']} phase(s) hit the 25-min timeout"
        out.append(f"| {r['run']} | {r['score']}/{r['total']} | {fmt_s(r['wall_s'])} | {r['turns']} | {r['out_tok']:,} | "
                   f"{r['tests']} | {'; '.join(r['failed']) or '—'}{extra} |")
    (ROOT / "results" / "summary.json").write_text(json.dumps(summary, indent=2))
    print("\n".join(out))


if __name__ == "__main__":
    main()
