#!/usr/bin/env python3
"""Objective grader for the todo-CLI benchmark (spec/SPEC.md).

Usage: python3 grade.py <run_dir> [<run_dir> ...] [--json out.json]

Each run directory is copied to a scratch location before anything executes,
so grading never mutates the artifacts. Every check maps to one line of the
spec; the score is checks passed / checks run.
"""
import ast
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PY = sys.executable
STDLIB = set(sys.stdlib_module_names)
TIMEOUT = 20


def run(args, cwd, env=None):
    p = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=TIMEOUT, env=env)
    return p.returncode, p.stdout, p.stderr


def py_sources(root: Path):
    return [p for p in root.rglob("*.py") if ".venv" not in p.parts and "__pycache__" not in p.parts]


def grade(run_dir: Path) -> dict:
    checks: dict[str, tuple[bool, str]] = {}

    def check(name, ok, note=""):
        checks[name] = (bool(ok), note)

    with tempfile.TemporaryDirectory() as td:
        src = Path(td) / "src"
        shutil.copytree(run_dir, src, ignore=shutil.ignore_patterns("todos.json*", "__pycache__", ".pytest_cache"))
        todo = src / "todo.py"
        check("entrypoint todo.py exists", todo.exists())
        if not todo.exists():
            return finish(run_dir, checks)

        # --- the agent's own tests -------------------------------------------------
        test_file = src / "tests" / "test_todo.py"
        check("tests/test_todo.py exists", test_file.exists())
        n_tests = 0
        if test_file.exists():
            try:
                tree = ast.parse(test_file.read_text(errors="replace"))
                names = [n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith("test")]
                n_tests = len(names)
            except SyntaxError:
                names = []
            check(">= 4 tests", n_tests >= 4, f"{n_tests} test functions")
            body = test_file.read_text(errors="replace").lower()
            missing = [c for c in ("add", "list", "done", "rm") if c not in body]
            check("tests cover add/list/done/rm", not missing, f"missing: {missing}" if missing else "")
            rc, out, err = run([PY, "-m", "pytest", "tests/", "-q", "-p", "no:cacheprovider"], cwd=src)
            m = re.search(r"(\d+) passed", out)
            failed = re.search(r"(\d+) (failed|error)", out)
            check("agent's pytest suite passes", rc == 0, (m.group(0) if m else "") + (f", {failed.group(0)}" if failed else ""))
            check("tests don't pollute cwd", not (src / "todos.json").exists(), "todos.json left in project dir" if (src / "todos.json").exists() else "")
            (src / "todos.json").unlink(missing_ok=True)

        # --- black-box CLI acceptance, run from a *different* cwd ------------------
        work = Path(td) / "work"
        work.mkdir()

        def cli(*a):
            return run([PY, str(todo), *a], cwd=work)

        # The spec fixes the ID *properties* (monotonic, never reused), not the values, so read the IDs
        # the program reports instead of assuming 1, 2, 3.
        def first_int(s):
            m = re.search(r"\d+", s)
            return int(m.group()) if m else None

        rc, out, err = cli("add", "first")
        id1 = first_int(out)
        check("add prints new ID", rc == 0 and id1 is not None, out.strip()[:60])
        _, out_b, _ = cli("add", "second")
        id2 = first_int(out_b)
        check("persists to ./todos.json (cwd)", (work / "todos.json").exists(),
              "" if (work / "todos.json").exists() else "not in cwd" + (" (found next to script)" if (src / "todos.json").exists() else ""))

        rc, out, err = cli("list")
        lines = [l.rstrip() for l in out.strip().splitlines()]
        check("list format `[ID] [·] title`", f"[{id1}] [·] first" in lines and f"[{id2}] [·] second" in lines, " | ".join(lines)[:80])

        rc, out, err = cli("done", str(id1))
        rc2, out2, _ = cli("list")
        check("done marks `[x]`", rc == 0 and f"[{id1}] [x] first" in out2.splitlines(), out2.strip().replace("\n", " | ")[:80])

        # remove the highest ID, then add: a max(id)+1 scheme hands the removed ID straight back
        rc, _, _ = cli("rm", str(id2))
        rc_add, out_add, _ = cli("add", "third")
        id3 = first_int(out_add)
        ok_ids = None not in (id1, id2, id3) and id1 != id2 and id3 > max(id1, id2)
        check("IDs never reused after rm", rc == 0 and ok_ids, f"ids {id1},{id2} then rm {id2} -> {id3}")

        rc, _, _ = cli("clear")
        rc2, out2, _ = cli("list")
        listed = out2.strip().splitlines()
        check("clear removes done todos only", rc == 0 and not any("first" in l for l in listed) and any("third" in l for l in listed),
              " | ".join(listed)[:80])

        data_ok, note = False, ""
        store = work / "todos.json" if (work / "todos.json").exists() else src / "todos.json"
        try:
            data = json.loads(store.read_text(errors="replace"))
            items = data if isinstance(data, list) else next((v for v in data.values() if isinstance(v, list)), [])
            data_ok = bool(items) and all(
                isinstance(t.get("id"), int) and not isinstance(t.get("id"), bool)
                and isinstance(t.get("title"), str) and isinstance(t.get("done"), bool) for t in items)
            note = f"{type(data).__name__} with {len(items)} items"
        except Exception as e:  # noqa: BLE001
            note = f"unreadable: {e.__class__.__name__}"
        check("schema {id:int, title:str, done:bool}", data_ok, note)

        for label, args in (("missing ID", ("done", "99")), ("missing ID on rm", ("rm", "99")), ("non-numeric ID", ("done", "abc"))):
            rc, out, err = cli(*args)
            ok = rc != 0 and "Traceback" not in out + err and err.strip() != ""
            check(f"{label}: stderr + nonzero exit, no traceback", ok, f"exit {rc}" + (" TRACEBACK" if "Traceback" in out + err else ""))

        # --- static checks ---------------------------------------------------------
        sources = py_sources(src)
        runtime = [p for p in sources if "tests" not in p.relative_to(src).parts]
        check("uses argparse", any("argparse" in p.read_text(errors="replace") for p in runtime))
        local_mods = {p.stem for p in sources}
        third_party = set()
        for p in runtime:
            try:
                for node in ast.walk(ast.parse(p.read_text(errors="replace"))):
                    if isinstance(node, ast.Import):
                        mods = [a.name.split(".")[0] for a in node.names]
                    elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                        mods = [node.module.split(".")[0]]
                    else:
                        continue
                    third_party |= {m for m in mods if m not in STDLIB and m not in local_mods}
            except SyntaxError:
                pass
        check("stdlib-only runtime", not third_party, ", ".join(sorted(third_party)))
        readme = src / "README.md"
        check("README.md with usage examples", readme.exists() and "todo.py" in readme.read_text(errors="replace"), "")

        loc = sum(len(p.read_text(errors="replace").splitlines()) for p in runtime)
        return finish(run_dir, checks, tests=n_tests, runtime_loc=loc, files=sorted(str(p.relative_to(src)) for p in sources))


def finish(run_dir, checks, **extra):
    passed = sum(ok for ok, _ in checks.values())
    return {"run": str(run_dir), "score": f"{passed}/{len(checks)}", "passed": passed, "total": len(checks),
            "failed": {k: n for k, (ok, n) in checks.items() if not ok},
            "checks": {k: {"ok": ok, "note": n} for k, (ok, n) in checks.items()}, **extra}


if __name__ == "__main__":
    args = sys.argv[1:]
    out_path = None
    if "--json" in args:
        i = args.index("--json")
        out_path = args[i + 1]
        del args[i:i + 2]
    results = [grade(Path(a).resolve()) for a in args]
    for r in results:
        print(f"{r['score']:>6}  {r['run']}  tests={r.get('tests')} loc={r.get('runtime_loc')}")
        for k, n in r["failed"].items():
            print(f"        ✗ {k}{' — ' + n if n else ''}")
    if out_path:
        Path(out_path).write_text(json.dumps(results, indent=2))
