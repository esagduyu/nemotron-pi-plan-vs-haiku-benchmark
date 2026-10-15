"""Tests for the tiny CLI todo manager."""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest


def run_todo(args, cwd):
    """Run todo.py with given args in the given directory."""
    src = os.path.join(os.path.dirname(__file__), "..", "todo.py")
    shutil.copy2(src, os.path.join(cwd, "todo.py"))
    result = subprocess.run(
        [sys.executable, "todo.py"] + args,
        cwd=cwd,
        capture_output=True,
        text=True,
    )
    return result


class TestTodoAdd(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def test_add_creates_todo_with_incrementing_id(self):
        r1 = run_todo(["add", "Buy milk"], self.tmpdir)
        self.assertEqual(r1.returncode, 0)
        self.assertIn("Added todo 1:", r1.stdout)

        r2 = run_todo(["add", "Walk the dog"], self.tmpdir)
        self.assertEqual(r2.returncode, 0)
        self.assertIn("Added todo 2:", r2.stdout)

        # Verify JSON file
        with open(os.path.join(self.tmpdir, "todos.json")) as f:
            data = json.load(f)
        todos = data["_todos"]
        self.assertEqual(len(todos), 2)
        self.assertEqual(todos[0]["id"], 1)
        self.assertEqual(todos[0]["title"], "Buy milk")
        self.assertFalse(todos[0]["done"])


class TestTodoList(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def test_list_shows_all_todos(self):
        run_todo(["add", "Task one"], self.tmpdir)
        run_todo(["add", "Task two"], self.tmpdir)
        r = run_todo(["list"], self.tmpdir)
        self.assertEqual(r.returncode, 0)
        self.assertIn("[1] [·] Task one", r.stdout)
        self.assertIn("[2] [·] Task two", r.stdout)

    def test_list_shows_done_status(self):
        run_todo(["add", "Task one"], self.tmpdir)
        run_todo(["done", "1"], self.tmpdir)
        r = run_todo(["list"], self.tmpdir)
        self.assertEqual(r.returncode, 0)
        self.assertIn("[1] [x] Task one", r.stdout)


class TestTodoDone(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def test_done_marks_todo_as_done(self):
        run_todo(["add", "A task"], self.tmpdir)
        r = run_todo(["done", "1"], self.tmpdir)
        self.assertEqual(r.returncode, 0)
        self.assertIn("Todo 1 marked done.", r.stdout)

        with open(os.path.join(self.tmpdir, "todos.json")) as f:
            data = json.load(f)
        todos = data["_todos"]
        self.assertTrue(todos[0]["done"])

    def test_done_invalid_id_exits_nonzero(self):
        run_todo(["add", "A task"], self.tmpdir)
        r = run_todo(["done", "999"], self.tmpdir)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("not found", r.stderr)


class TestTodoRm(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()

    def test_rm_deletes_todo(self):
        run_todo(["add", "Task one"], self.tmpdir)
        run_todo(["add", "Task two"], self.tmpdir)
        r = run_todo(["rm", "1"], self.tmpdir)
        self.assertEqual(r.returncode, 0)
        self.assertIn("Deleted todo 1.", r.stdout)

        with open(os.path.join(self.tmpdir, "todos.json")) as f:
            data = json.load(f)
        todos = data["_todos"]
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]["id"], 2)

    def test_rm_id_not_reused(self):
        run_todo(["add", "Task one"], self.tmpdir)
        run_todo(["rm", "1"], self.tmpdir)
        run_todo(["add", "New task"], self.tmpdir)
        with open(os.path.join(self.tmpdir, "todos.json")) as f:
            data = json.load(f)
        todos = data["_todos"]
        # ID should be 2, not 1
        self.assertEqual(todos[0]["id"], 2)


if __name__ == "__main__":
    unittest.main()
