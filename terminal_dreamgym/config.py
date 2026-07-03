from __future__ import annotations

import os
from pathlib import Path

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover - keeps import safe before install
    load_dotenv = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if load_dotenv is not None:
    load_dotenv(PROJECT_ROOT / ".env")

DATA_DIR = PROJECT_ROOT / "data"
TASK_TEMPLATE_DIR = PROJECT_ROOT / "task_templates"
CURRICULA_DIR = PROJECT_ROOT / "curricula"
GENERATED_CURRICULA_DIR = CURRICULA_DIR / "generated"
SKILLS_DIR = PROJECT_ROOT / "skills"
GENERATED_SKILLS_DIR = SKILLS_DIR / "generated"
RUNS_DIR = PROJECT_ROOT / "runs"
REPORTS_DIR = PROJECT_ROOT / "reports"

DEFAULT_TIMEOUT_SECONDS = 10
# Live-model only: pick the provider. 'qwen' (local Ollama, free) or 'gemini' (REST).
DEFAULT_MODE = os.getenv("TERMINAL_DREAMGYM_MODE", "qwen")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# OpenAI-compatible provider (used for `--mode qwen` / local Ollama, vLLM, LM Studio, etc.).
# Ollama exposes an OpenAI-compatible endpoint at http://localhost:11434/v1.
QWEN_BASE_URL = os.getenv("QWEN_BASE_URL", "http://localhost:11434/v1")
QWEN_MODEL = os.getenv("QWEN_MODEL", "qwen2.5:7b")
QWEN_API_KEY = os.getenv("QWEN_API_KEY", "ollama")

# How many edit/rerun iterations an LLM agent gets per task before giving up.
LLM_MAX_STEPS = int(os.getenv("TERMINAL_DREAMGYM_MAX_STEPS", "3"))
