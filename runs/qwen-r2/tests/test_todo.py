"""Tests for the tiny CLI todo manager."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

# Resolve paths so we can run this file from anywhere.
_ROOT = Path(__file__).resolve().parent.parent
_TODO = _ROOT / "todo.py"


def _run(args: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Run todo.py with *args* and return the CompletedProcess."""
    return subprocess.run(
        [sys.executable, str(_TODO)] + args,
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
    )


@pytest.fixture()
def work_dir(tmp_path: Path) -> Path:
    """A fresh temporary directory for each test."""
    return tmp_path


# ── add ──────────────────────────────────────────────────────────────


class TestAdd:
    def test_add_creates_todo(self, work_dir: Path) -> None:
        result = _run(["add", "Buy milk"], cwd=work_dir)
        assert result.returncode == 0
        assert "#1" in result.stdout

        todos = json.loads((work_dir / "todos.json").read_text())
        assert len(todos) == 1
        assert todos[0]["title"] == "Buy milk"
        assert todos[0]["done"] is False

    def test_add_assigns_increasing_ids(self, work_dir: Path) -> None:
        _run(["add", "First"], cwd=work_dir)
        result = _run(["add", "Second"], cwd=work_dir)
        assert "#2" in result.stdout


# ── list ─────────────────────────────────────────────────────────────


class TestList:
    def test_list_empty(self, work_dir: Path) -> None:
        result = _run(["list"], cwd=work_dir)
        assert result.returncode == 0
        assert "(no todos)" in result.stdout

    def test_list_shows_status(self, work_dir: Path) -> None:
        _run(["add", "Task A"], cwd=work_dir)
        result = _run(["list"], cwd=work_dir)
        assert "[1] [·] Task A" in result.stdout


# ── done ─────────────────────────────────────────────────────────────


class TestDone:
    def test_done_marks_done(self, work_dir: Path) -> None:
        _run(["add", "Task A"], cwd=work_dir)
        result = _run(["done", "1"], cwd=work_dir)
        assert result.returncode == 0
        assert "done" in result.stdout.lower()

        todos = json.loads((work_dir / "todos.json").read_text())
        assert todos[0]["done"] is True

    def test_done_invalid_id(self, work_dir: Path) -> None:
        result = _run(["done", "99"], cwd=work_dir)
        assert result.returncode != 0
        assert "not found" in result.stderr.lower()


# ── rm ───────────────────────────────────────────────────────────────


class TestRm:
    def test_rm_removes_todo(self, work_dir: Path) -> None:
        _run(["add", "Task A"], cwd=work_dir)
        result = _run(["rm", "1"], cwd=work_dir)
        assert result.returncode == 0
        assert "removed" in result.stdout.lower()

        todos = json.loads((work_dir / "todos.json").read_text())
        assert len(todos) == 0

    def test_rm_invalid_id(self, work_dir: Path) -> None:
        result = _run(["rm", "99"], cwd=work_dir)
        assert result.returncode != 0
        assert "not found" in result.stderr.lower()

    def test_rm_does_not_reuse_id(self, work_dir: Path) -> None:
        _run(["add", "First"], cwd=work_dir)
        _run(["add", "Second"], cwd=work_dir)
        _run(["rm", "1"], cwd=work_dir)
        result = _run(["add", "Third"], cwd=work_dir)
        # ID should be 3, not 1
        assert "#3" in result.stdout
