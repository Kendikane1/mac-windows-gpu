"""Small integration tests without third-party packages, GPU, or task registration."""

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT = ROOT / "examples" / "checkpoint_job.py"
RUNNER = ROOT / "scripts" / "run_job.py"


def wait_for_steps(path, minimum, process):
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        if path.exists():
            state = json.loads(path.read_text(encoding="utf-8"))
            if len(state["steps"]) >= minimum:
                return state
        if process.poll() is not None:
            raise AssertionError("Job exited before required progress")
        time.sleep(0.02)
    raise AssertionError("Timed out waiting for progress")


class CheckpointTests(unittest.TestCase):
    def test_forced_stop_and_resume_preserves_prefix(self):
        with tempfile.TemporaryDirectory() as directory:
            state_path = Path(directory) / "checkpoint.json"
            command = [sys.executable, str(CHECKPOINT), "--state", str(state_path), "--steps", "100"]
            process = subprocess.Popen(command + ["--delay", "0.1"], stdout=subprocess.DEVNULL)
            try:
                wait_for_steps(state_path, 3, process)
            finally:
                process.terminate()
                process.wait(timeout=10)
            before = json.loads(state_path.read_text())
            result = subprocess.run(command + ["--delay", "0"], capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            after = json.loads(state_path.read_text())
            self.assertEqual(after["steps"][:len(before["steps"])], before["steps"])
            self.assertEqual(after["sessions"][-1]["resume_after"], len(before["steps"]))
            self.assertEqual([x["step"] for x in after["steps"]], list(range(1, 101)))
            self.assertTrue(all(x["value"] == x["step"] ** 2 for x in after["steps"]))
            self.assertEqual(after["status"], "completed")

    def test_corrupt_checkpoint_is_rejected_without_replacement(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.json"
            payload = json.dumps({"synthetic_only": True, "total": 3, "steps": [{"step": 2, "value": 4}], "sessions": []})
            path.write_text(payload)
            result = subprocess.run([sys.executable, str(CHECKPOINT), "--state", str(path), "--steps", "3"], capture_output=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(path.read_text(), payload)

    def test_changed_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.json"
            command = [sys.executable, str(CHECKPOINT), "--state", str(path), "--delay", "0"]
            subprocess.run(command + ["--steps", "2"], check=True, capture_output=True, timeout=10)
            result = subprocess.run(command + ["--steps", "3"], capture_output=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)


class RunnerTests(unittest.TestCase):
    def test_argument_boundaries_logs_and_exit_codes(self):
        with tempfile.TemporaryDirectory(prefix="gpu guide ") as directory:
            folder = Path(directory)
            script = folder / "job with spaces.py"
            script.write_text("import json, sys\nprint(json.dumps(sys.argv[1:]))\nraise SystemExit(7)\n")
            manifest = folder / "manifest.json"
            args = ["space inside", 'quote"inside', "semi;colon", "$literal"]
            manifest.write_text(json.dumps({"script": str(script), "args": args, "cwd": directory, "log": str(folder / "job.log")}))
            result = subprocess.run([sys.executable, str(RUNNER), str(manifest)], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 7)
            log = (folder / "job.log").read_text()
            self.assertIn(json.dumps(args), log)
            self.assertIn("script_sha256", log)
            self.assertEqual(result.stdout, b"")

    def test_non_array_arguments_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "manifest.json"
            manifest.write_text(json.dumps({"args": "not-an-array"}))
            result = subprocess.run([sys.executable, str(RUNNER), str(manifest)], capture_output=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)


class PublicationTests(unittest.TestCase):
    def test_notebooks_have_no_outputs_and_code_parses(self):
        for path in (ROOT / "examples").glob("*.ipynb"):
            notebook = json.loads(path.read_text())
            for cell in notebook["cells"]:
                if cell["cell_type"] == "code":
                    self.assertEqual(cell["outputs"], [])
                    self.assertIsNone(cell["execution_count"])
                    compile("".join(cell["source"]), str(path), "exec")

    def test_python_sources_parse(self):
        for directory in ("scripts", "examples", "tests"):
            for path in (ROOT / directory).glob("*.py"):
                compile(path.read_text(encoding="utf-8"), str(path), "exec")

    def test_local_markdown_links_exist(self):
        import re
        paths = [*ROOT.glob("*.md"), *(ROOT / "docs").glob("*.md")]
        for path in paths:
            for target in re.findall(r"\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
                if "://" not in target and not target.startswith("#"):
                    self.assertTrue((path.parent / target.split("#")[0]).exists(), (path.name, target))


if __name__ == "__main__":
    unittest.main()
