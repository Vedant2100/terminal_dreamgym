"""Provider-free unit tests for the live LLM terminal agent.

These exercise the deterministic, safety-critical parts of the agent — reply
parsing and the rules that protect test files and the sandbox boundary — without
calling any model, so the suite stays green in CI with no provider running.
"""
import json
from pathlib import Path

from terminal_dreamgym.gemini_agent import (
    LLMTerminalAgent,
    _extract_json,
    _parse_file_blocks,
)


class _StubClient:
    """Stands in for a reachable provider without making network calls."""

    name = "stub"
    model = "stub-model"
    available = True

    def generate_text(self, prompt: str) -> str:  # pragma: no cover - not invoked here
        raise AssertionError("network should not be called in unit tests")


def _agent() -> LLMTerminalAgent:
    return LLMTerminalAgent(strategy="dreamgym_skill", provider="qwen", client=_StubClient())


def test_parse_file_blocks_extracts_full_file():
    reply = "<<<FILE app.py\nprint('hi')\nx = 1\n>>>END\nSUMMARY: done"
    files = _parse_file_blocks(reply)
    assert files == {"app.py": "print('hi')\nx = 1"}


def test_parse_file_blocks_strips_inner_code_fence():
    reply = "<<<FILE app.py\n```python\nx = 1\n```\n>>>END"
    assert _parse_file_blocks(reply)["app.py"] == "x = 1"


def test_json_fallback_when_no_blocks():
    reply = 'noise {"files": {"app.py": "y = 2"}, "summary": "s"} trailing'
    assert _extract_json(reply)["files"]["app.py"] == "y = 2"


def test_apply_reply_refuses_test_file_edits(tmp_path: Path):
    agent = _agent()
    sandbox = _FakeSandbox(tmp_path)
    reply = "<<<FILE test_app.py\nassert True\n>>>END"
    applied, _ = agent._apply_reply(sandbox, reply)
    assert applied == []
    assert not (tmp_path / "test_app.py").exists()


def test_apply_reply_refuses_writes_outside_sandbox(tmp_path: Path):
    agent = _agent()
    sandbox = _FakeSandbox(tmp_path)
    reply = "<<<FILE ../escape.py\nimport os\n>>>END"
    applied, _ = agent._apply_reply(sandbox, reply)
    assert applied == []
    assert not (tmp_path.parent / "escape.py").exists()


def test_apply_reply_writes_source_file(tmp_path: Path):
    agent = _agent()
    sandbox = _FakeSandbox(tmp_path)
    reply = "<<<FILE app.py\nvalue = 42\n>>>END\nSUMMARY: set value"
    applied, summary = agent._apply_reply(sandbox, reply)
    assert [e.file for e in applied] == ["app.py"]
    assert summary == "set value"
    assert (tmp_path / "app.py").read_text() == "value = 42"


class _FakeSandbox:
    """Minimal sandbox stub exposing only `.root`, which is all _apply_reply needs."""

    def __init__(self, root: Path):
        self.root = root
