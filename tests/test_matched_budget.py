"""Provider-free tests for the fairness fixes: equal attempt budget for every
strategy and regression-aware (strict) success. They run real pytest inside real
task sandboxes, with a scripted stub instead of a model."""
from __future__ import annotations

import shutil

import pytest

from terminal_dreamgym.gemini_agent import LLMTerminalAgent, PROMPT_TEXTS, STRATEGY_SKILLS
from terminal_dreamgym.task_model import load_tasks, tasks_by_id

GOOD_APP = '''def normalize_email(email: str) -> str:
    return email.strip().lower()


def parse_price(value: str) -> float:
    return float(value.replace("$", ""))


def parse_sku(value: str) -> str:
    return value.replace(",", "")


def slugify(text: str) -> str:
    return text.lower().replace(" ", "-")
'''

# Fixes the email test but breaks parse_price, whose currency-spacing test passed before.
REGRESSING_APP = GOOD_APP.replace(
    'return float(value.replace("$", ""))', 'return float(value.replace("$", "").replace(" ", "x"))'
)


class ScriptedClient:
    name = "stub"
    model = "stub-model"
    available = True

    def __init__(self, replies):
        self.replies = list(replies)
        self.calls = 0
        self.last_usage = {}

    def generate_text(self, prompt: str, seed=None) -> str:
        self.calls += 1
        self.last_usage = {"prompt_tokens": len(prompt) // 4, "completion_tokens": 10}
        return self.replies.pop(0) if self.replies else "no file blocks here"


@pytest.fixture
def email_task():
    return tasks_by_id(load_tasks())["python_email_whitespace_v1"]


def _run(strategy, client, task):
    agent = LLMTerminalAgent(strategy=strategy, provider="qwen", client=client)
    trace = agent.run_task(task, seed=1)
    shutil.rmtree(trace.run_dir, ignore_errors=True)
    return agent, trace


@pytest.mark.parametrize("strategy", ["baseline", "no_skill", "handwritten_skills", "placebo", "symptom_patch"])
def test_every_strategy_gets_the_same_attempt_budget(strategy, email_task):
    client = ScriptedClient([])  # never produces an edit
    agent, trace = _run(strategy, client, email_task)
    assert client.calls == agent.max_steps
    assert trace.metadata["model_calls"] == agent.max_steps
    assert not trace.success


def test_correct_fix_is_strict_success(email_task):
    client = ScriptedClient([f"<<<FILE app.py\n{GOOD_APP}>>>END"])
    _, trace = _run("no_skill", client, email_task)
    assert trace.success and trace.metadata["score_passed"]
    assert trace.metadata["regressions"] == []
    assert trace.metadata["first_attempt_success"]
    assert client.calls == 1  # stops once the target passes


def test_fix_that_breaks_a_passing_test_is_not_success(email_task):
    client = ScriptedClient([f"<<<FILE app.py\n{REGRESSING_APP}>>>END"])
    _, trace = _run("handwritten_skills", client, email_task)
    assert trace.metadata["score_passed"]
    assert trace.metadata["regressions"] == ["test_app.py::test_parse_price_currency_spacing"]
    assert not trace.success
    assert not trace.metadata["first_attempt_success"]


def test_broken_import_counts_previously_passing_tests_as_regressions(email_task):
    client = ScriptedClient(["<<<FILE app.py\nthis is not python\n>>>END"])
    _, trace = _run("no_skill", client, email_task)
    assert "test_app.py::test_parse_price_currency_spacing" in trace.metadata["regressions"]


def test_strategies_differ_only_in_skill_text():
    for skills in STRATEGY_SKILLS.values():
        for name in skills:
            assert name in PROMPT_TEXTS
    handwritten = sum(len(PROMPT_TEXTS[n]) for n in STRATEGY_SKILLS["handwritten_skills"])
    placebo = len(PROMPT_TEXTS["placebo_skill.md"])
    assert abs(placebo - handwritten) / handwritten < 0.10


def test_read_timeout_is_recorded_as_infra_error(email_task, monkeypatch):
    # On Python 3.13 a read timeout escapes urllib as a bare TimeoutError.
    import urllib.request

    from terminal_dreamgym.gemini_agent import OpenAICompatClient

    def timeout(*args, **kwargs):
        raise TimeoutError("The read operation timed out")

    monkeypatch.setattr(urllib.request, "urlopen", timeout)
    client = OpenAICompatClient(base_url="http://127.0.0.1:9", timeout=1)
    agent = LLMTerminalAgent(strategy="no_skill", provider="qwen", client=client)
    trace = agent.run_task(email_task, seed=1)
    shutil.rmtree(trace.run_dir, ignore_errors=True)
    assert trace.metadata["infra_error"] and not trace.success


def test_each_attempt_uses_a_distinct_seed(email_task):
    seen = []

    class Recorder(ScriptedClient):
        def generate_text(self, prompt, seed=None):
            seen.append(seed)
            return "no blocks"

    _run("no_skill", Recorder([]), email_task)
    assert len(seen) == 3 and len(set(seen)) == 3


def test_agent_cannot_write_pytest_config(email_task):
    reply = "<<<FILE conftest.py\nimport pytest\n>>>END\n<<<FILE pytest.ini\n[pytest]\n>>>END"
    _, trace = _run("no_skill", ScriptedClient([reply]), email_task)
    assert trace.edits == []
