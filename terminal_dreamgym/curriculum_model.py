from __future__ import annotations

from typing import List

from pydantic import BaseModel


class PracticeWorld(BaseModel):
    id: str
    difficulty: str
    template: str
    instruction: str
    score_command: str = "pytest -q"
    teaches: List[str]
    family: str = "python_test_failure"


class Curriculum(BaseModel):
    id: str
    source_failure_modes: List[str]
    target_skill: str
    worlds: List[PracticeWorld]
