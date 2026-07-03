from __future__ import annotations

from typing import Any, List

from pydantic import BaseModel


class CommandTrace(BaseModel):
    cmd: str
    exit_code: int
    stdout: str = ""
    stderr: str = ""
    duration_seconds: float = 0.0


class EditTrace(BaseModel):
    file: str
    summary: str


class TaskRunTrace(BaseModel):
    run_id: str
    task_id: str
    family: str
    split: str
    strategy: str
    success: bool
    failure_reason: str = ""
    commands: List[CommandTrace] = []
    edits: List[EditTrace] = []
    diff: str = ""
    tests_passed: bool = False
    duration_seconds: float = 0.0
    run_dir: str = ""
    metadata: dict[str, Any] = {}
