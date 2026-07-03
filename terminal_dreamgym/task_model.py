from __future__ import annotations

from pathlib import Path
from typing import List

from pydantic import BaseModel

from terminal_dreamgym.config import DATA_DIR, PROJECT_ROOT
from terminal_dreamgym.utils import read_json


class TaskSpec(BaseModel):
    id: str
    family: str
    instruction: str
    template_dir: str
    scorer: str
    score_command: str
    success_condition: str
    max_steps: int
    expected_failure_mode: str
    split: str
    tags: List[str] = []
    difficulty: str = ""

    @property
    def template_path(self) -> Path:
        return PROJECT_ROOT / self.template_dir


def load_tasks(path: Path | None = None) -> list[TaskSpec]:
    task_path = path or DATA_DIR / "tasks.json"
    return [TaskSpec(**item) for item in read_json(task_path)]


def tasks_by_id(tasks: list[TaskSpec] | None = None) -> dict[str, TaskSpec]:
    loaded = tasks or load_tasks()
    return {task.id: task for task in loaded}
