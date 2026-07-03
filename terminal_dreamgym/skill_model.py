from __future__ import annotations

from typing import List

from pydantic import BaseModel


class GeneratedSkill(BaseModel):
    filename: str
    title: str
    strategy: str
    source_curricula: List[str] = []
    body: str
