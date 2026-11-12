from __future__ import annotations

import difflib
import re
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

from terminal_dreamgym.config import DEFAULT_TIMEOUT_SECONDS, RUNS_DIR
from terminal_dreamgym.task_model import TaskSpec
from terminal_dreamgym.trace_model import CommandTrace, TaskRunTrace
from terminal_dreamgym.utils import ensure_dir, model_dump, write_json

BANNED_COMMANDS = {"curl", "wget", "pip", "npm", "pnpm", "yarn"}
SKIP_DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


class SandboxError(RuntimeError):
    pass


class Sandbox:
    """A local, deterministic task sandbox with command traces and diffs."""

    def __init__(self, task: TaskSpec, run_id: str, timeout: int = DEFAULT_TIMEOUT_SECONDS):
        self.task = task
        self.run_id = run_id
        self.timeout = timeout
        self.root = self._create_root()
        self.before = self.snapshot()
        self.commands: list[CommandTrace] = []

    def _create_root(self) -> Path:
        base = ensure_dir(RUNS_DIR / "sandboxes")
        root = base / f"{self.run_id}_{self.task.id}"
        suffix = 1
        while root.exists():
            root = base / f"{self.run_id}_{self.task.id}_{suffix}"
            suffix += 1
        if not self.task.template_path.exists():
            raise SandboxError(f"Missing task template: {self.task.template_path}")
        shutil.copytree(self.task.template_path, root, ignore=shutil.ignore_patterns(*SKIP_DIRS))
        return root

    def run_command(self, cmd: str, record: bool = True) -> CommandTrace:
        args = shlex.split(cmd)
        if not args:
            raise SandboxError("Empty command")
        if args[0] in BANNED_COMMANDS:
            raise SandboxError(f"Network/install command is disabled in demo sandboxes: {args[0]}")
        if args[0] == "pytest":
            args = [sys.executable, "-m", "pytest", *args[1:]]
        started = time.perf_counter()
        try:
            result = subprocess.run(
                args,
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )
            trace = CommandTrace(
                cmd=cmd,
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                duration_seconds=round(time.perf_counter() - started, 3),
            )
        except subprocess.TimeoutExpired as exc:
            trace = CommandTrace(
                cmd=cmd,
                exit_code=124,
                stdout=exc.stdout or "",
                stderr=(exc.stderr or "") + f"\nTimed out after {self.timeout}s",
                duration_seconds=round(time.perf_counter() - started, 3),
            )
        if record:
            self.commands.append(trace)
        return trace

    def suite_outcomes(self) -> dict[str, str]:
        """Per-test outcome of the whole suite, e.g. {"test_app.py::test_x": "passed"}.

        This is the harness's own check and is not shown to the agent. A collection
        error (e.g. the agent broke an import) yields an empty dict, so every test
        that used to pass counts as a regression.
        """
        result = self.run_command("pytest -q -rA -p no:cacheprovider", record=False)
        outcomes: dict[str, str] = {}
        for line in result.stdout.splitlines():
            match = re.match(r"^(PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS) (\S+::\S+)", line)
            if match:
                outcomes[match.group(2)] = match.group(1).lower()
        return outcomes

    def snapshot(self) -> dict[str, str]:
        files: dict[str, str] = {}
        for path in sorted(self.root.rglob("*")):
            if not path.is_file():
                continue
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            try:
                rel = path.relative_to(self.root).as_posix()
                files[rel] = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
        return files

    def diff(self) -> str:
        after = self.snapshot()
        chunks: list[str] = []
        for rel in sorted(set(self.before) | set(after)):
            before_lines = self.before.get(rel, "").splitlines(keepends=True)
            after_lines = after.get(rel, "").splitlines(keepends=True)
            if before_lines == after_lines:
                continue
            chunks.extend(
                difflib.unified_diff(
                    before_lines,
                    after_lines,
                    fromfile=f"a/{rel}",
                    tofile=f"b/{rel}",
                )
            )
        return "".join(chunks)

    def write_trace(self, trace: TaskRunTrace, path: Path | None = None) -> Path:
        trace_path = path or (self.root / "trace.json")
        write_json(trace_path, model_dump(trace))
        return trace_path
