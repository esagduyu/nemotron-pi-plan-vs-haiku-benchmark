"""Tests for the tiny CLI todo manager."""

import json
import os
import subprocess
import sys
import tempfile
import unittest


class TestTodoCLI(unittest.TestCase):
    """Use CLI subprocess calls so tests don't share state with real todos.json."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.bin = sys.executable
        self.script = os.path.join(os.path.dirname(__file__), "..", "todo.py")

    def tearDown(self):
        # Clean up temp dir
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _run(self, *args):
        """Run the todo script with given args in the temp dir."""
        result = subprocess.run(
            [self.bin, self.script] + list(args),
            capture_output=True,
            text=True,
            cwd=self.tmpdir,
        )
        return result

    def test_add(self):
        """Adding a todo creates it and prints the ID."""
        result = self._run("add", "Buy milk")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Added todo 1", result.stdout)
        # Verify the JSON file
        with open(os.path.join(self.tmpdir, "todos.json")) as f:
            data = json.load(f)
        todos = data["todos"]
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]["id"], 1)
        self.assertEqual(todos[0]["title"], "Buy milk")
        self.assertFalse(todos[0]["done"])

    def test_list(self):
        """Listing shows todos with correct status markers."""
        self._run("add", "Task A")
        self._run("add", "Task B")
        result = self._run("list")
        self.assertEqual(result.returncode, 0)
        self.assertIn("[1]", result.stdout)
        self.assertIn("[2]", result.stdout)
        self.assertIn("·", result.stdout)  # open marker

    def test_done(self):
        """Marking a todo done updates its status."""
        self._run("add", "Task A")
        result = self._run("done", "1")
        self.assertEqual(result.returncode, 0)
        self.assertIn("marked done", result.stdout)
        with open(os.path.join(self.tmpdir, "todos.json")) as f:
            data = json.load(f)
        todos = data["todos"]
        self.assertTrue(todos[0]["done"])

    def test_rm(self):
        """Removing a todo deletes it from the list."""
        self._run("add", "Task A")
        self._run("add", "Task B")
        result = self._run("rm", "1")
        self.assertEqual(result.returncode, 0)
        self.assertIn("deleted", result.stdout)
        with open(os.path.join(self.tmpdir, "todos.json")) as f:
            data = json.load(f)
        todos = data["todos"]
        self.assertEqual(len(todos), 1)
        self.assertEqual(todos[0]["id"], 2)

    def test_invalid_id(self):
        """Invalid ID prints error to stderr and exits non-zero."""
        result = self._run("done", "999")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Error", result.stderr)

    def test_ids_never_reused(self):
        """After removing an ID, the next new todo gets a higher ID."""
        self._run("add", "First")
        self._run("rm", "1")
        result = self._run("add", "Second")
        self.assertIn("Added todo 2", result.stdout)


if __name__ == "__main__":
    unittest.main()
