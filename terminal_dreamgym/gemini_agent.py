from __future__ import annotations

import json
import re
import time
import uuid
import urllib.error
import urllib.request
from pathlib import Path

from terminal_dreamgym.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    LLM_MAX_OUTPUT_TOKENS,
    LLM_MAX_STEPS,
    LLM_TEMPERATURE,
    QWEN_API_KEY,
    QWEN_BASE_URL,
    QWEN_MODEL,
)
from terminal_dreamgym.sandbox import Sandbox
from terminal_dreamgym.skill_generator import CONTROL_TEXTS, SKILL_TEXTS
from terminal_dreamgym.task_model import TaskSpec
from terminal_dreamgym.trace_model import EditTrace, TaskRunTrace
from terminal_dreamgym.utils import make_run_id, write_text

PROMPT_TEXTS = {**SKILL_TEXTS, **CONTROL_TEXTS}

EDIT_BLOCKLIST = {"expected_fix.patch", "trace.json"}
MAX_OUTPUT_CHARS = 4000


class GeminiClientError(RuntimeError):
    pass


class GeminiClient:
    """Small REST client for Gemini text generation with no extra dependency."""

    name = "gemini"

    def __init__(self, api_key: str | None = None, model: str | None = None, timeout: int = 60):
        self.api_key = api_key if api_key is not None else GEMINI_API_KEY
        self.model = model or GEMINI_MODEL
        self.timeout = timeout

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def generate_text(self, prompt: str, seed: int | None = None) -> str:
        if not self.available:
            raise GeminiClientError("GEMINI_API_KEY is not set")
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.model}:generateContent?key={self.api_key}"
        )
        self.last_usage = {}
        generation_config = {"temperature": LLM_TEMPERATURE, "maxOutputTokens": LLM_MAX_OUTPUT_TOKENS}
        if seed is not None:
            generation_config["seed"] = seed
        body = json.dumps(
            {
                "contents": [{"role": "user", "parts": [{"text": prompt}]}],
                "generationConfig": generation_config,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise GeminiClientError(f"Gemini HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise GeminiClientError(f"Gemini network error: {exc.reason}") from exc
        try:
            parts = payload["candidates"][0]["content"]["parts"]
            meta = payload.get("usageMetadata") or {}
            self.last_usage = {
                "prompt_tokens": meta.get("promptTokenCount"),
                "completion_tokens": meta.get("candidatesTokenCount"),
            }
            return "\n".join(part.get("text", "") for part in parts).strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise GeminiClientError(f"Unexpected Gemini response: {payload}") from exc


class OpenAICompatClient:
    """OpenAI-compatible chat client for Qwen / Ollama / vLLM / LM Studio.

    Ollama serves this protocol at http://localhost:11434/v1, so `--mode qwen`
    can drive the exact same terminal-agent loop locally and for free.
    """

    name = "qwen"

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: int = 120,
    ):
        self.base_url = (base_url or QWEN_BASE_URL).rstrip("/")
        self.api_key = api_key if api_key is not None else QWEN_API_KEY
        self.model = model or QWEN_MODEL
        self.timeout = timeout

    @property
    def available(self) -> bool:
        return bool(self.base_url)

    def generate_text(self, prompt: str, seed: int | None = None) -> str:
        url = f"{self.base_url}/chat/completions"
        self.last_usage = {}
        req_body = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": LLM_TEMPERATURE,
            "max_tokens": LLM_MAX_OUTPUT_TOKENS,
            "stream": False,
        }
        if seed is not None:
            req_body["seed"] = seed
        body = json.dumps(req_body).encode("utf-8")
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = urllib.request.Request(url, data=body, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise GeminiClientError(f"{self.model} HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise GeminiClientError(f"{self.model} network error ({self.base_url}): {exc.reason}") from exc
        usage = payload.get("usage") or {}
        self.last_usage = {
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
            "finish_reason": (payload.get("choices") or [{}])[0].get("finish_reason"),
        }
        try:
            return payload["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise GeminiClientError(f"Unexpected response: {payload}") from exc


def make_client(provider: str):
    provider = provider.lower()
    if provider in {"gemini", "google"}:
        return GeminiClient()
    if provider in {"qwen", "ollama", "openai", "openai-compat", "local"}:
        return OpenAICompatClient()
    raise GeminiClientError(f"Unknown LLM provider: {provider}")


HANDWRITTEN_SKILLS = [
    "trace_first_debugging_skill.md",
    "minimal_patch_skill.md",
    "contract_drift_skill.md",
    "error_handling_skill.md",
]

# Strategy -> the text placed in the prompt's ACTIVE SKILLS block. All skill texts
# are fixed, handwritten strings (see skill_generator.py); no model writes them.
# The strategies differ ONLY in this block: same model, attempts, sampling and tests.
STRATEGY_SKILLS = {
    "baseline": [],
    "no_skill": [],
    "handwritten_skills": HANDWRITTEN_SKILLS,
    # Length-matched text with no debugging advice: controls for "any extra text".
    "placebo": ["placebo_skill.md"],
    # Deliberately bad advice ("patch the visible symptom"). The old name
    # "reflection_only" is kept for compatibility; it is not model reflection.
    "symptom_patch": ["reflection_overfit_skill.md"],
    "reflection_only": ["reflection_overfit_skill.md"],
    "dreamgym_skill": [
        "trace_first_debugging_skill.md",
        "minimal_patch_skill.md",
        "contract_drift_skill.md",
        "error_handling_skill.md",
    ],
    "dreamgym": [
        "trace_first_debugging_skill.md",
        "minimal_patch_skill.md",
        "contract_drift_skill.md",
        "error_handling_skill.md",
    ],
}


def _truncate(text: str, limit: int = MAX_OUTPUT_CHARS) -> str:
    text = text or ""
    return text if len(text) <= limit else text[:limit] + "\n...[truncated]..."


def _parse_file_blocks(text: str) -> dict[str, str]:
    """Parse `<<<FILE path` ... `>>>END` blocks into {path: contents}.

    Robust to a leading ```-fence and to a missing trailing newline before >>>END.
    """
    files: dict[str, str] = {}
    pattern = re.compile(r"<<<FILE[ \t]+(?P<path>\S+)[ \t]*\n(?P<body>.*?)\n?>>>END", re.DOTALL)
    for match in pattern.finditer(text):
        body = match.group("body")
        # Strip an accidental code fence the model may have wrapped the body in.
        body = re.sub(r"^```[a-zA-Z0-9]*\n", "", body)
        body = re.sub(r"\n```\s*$", "", body)
        files[match.group("path").strip()] = body
    return files


def _extract_json(text: str) -> dict:
    """Pull the first JSON object out of a model reply (handles ``` fences)."""
    fenced = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    candidate = fenced.group(1) if fenced else None
    if candidate is None:
        start = text.find("{")
        end = text.rfind("}")
        candidate = text[start : end + 1] if start != -1 and end > start else text
    return json.loads(candidate)


class LLMTerminalAgent:
    """A real terminal agent: an LLM reads the failing test and edits files until green.

    Loop per task:
      1. Copy the task template into a sandbox and run the failing score command.
      2. Send the instruction, active SKILL.md text, source files, and the failing
         test output to the model.
      3. The model returns full-file replacements (in <<<FILE ... >>>END blocks); we
         apply them to source files (never the test files), then re-run the command.
      4. Repeat up to `max_steps`. For the dreamgym strategy, run the full suite too.

    The model genuinely decides the patch; pytest genuinely decides success. This is a
    live-model-only system: there is no scripted fallback. If the configured provider
    is unreachable, the run raises rather than substituting fake results.
    """

    def __init__(self, strategy: str = "dreamgym_skill", provider: str = "gemini", client=None, active_skills: list[str] | None = None):
        self.strategy = strategy
        self.provider = provider
        self.client = client or make_client(provider)
        self.max_steps = max(1, LLM_MAX_STEPS)
        self.active_skills = active_skills

    @property
    def available(self) -> bool:
        return getattr(self.client, "available", False)

    def run_task(self, task: TaskSpec, seed: int | None = None) -> TaskRunTrace:
        if not self.available:
            raise GeminiClientError(
                f"Provider '{self.provider}' is not configured/reachable. "
                "Set GEMINI_API_KEY (mode gemini) or run Ollama (mode qwen)."
            )

        tag = f"{self.client.name}_{self.strategy}" + (f"_s{seed}" if seed is not None else "")
        run_id = f"{make_run_id(tag)}_{uuid.uuid4().hex[:6]}"
        sandbox = Sandbox(task, run_id)
        started = time.perf_counter()

        # Harness-only check (not shown to the agent): which tests pass before any edit.
        suite_before = sandbox.suite_outcomes()
        first = sandbox.run_command(task.score_command)
        edits: list[EditTrace] = []
        notes: list[str] = []
        attempts: list[dict] = []
        last_output = self._command_text(first)
        score_passed = first.exit_code == 0
        infra_error = False

        # Same budget for every strategy. A reply with no usable edit still uses up
        # an attempt; the loop only stops early when the scoring command passes.
        for attempt_index in range(self.max_steps):
            if score_passed:
                break
            prompt = self._build_prompt(task, sandbox, last_output)
            try:
                reply = self.client.generate_text(prompt, seed=seed)
            except GeminiClientError as exc:
                notes.append(f"model call failed: {exc}")
                infra_error = True
                break
            usage = dict(getattr(self.client, "last_usage", {}) or {})
            applied, summary = self._apply_reply(sandbox, reply)
            if summary:
                notes.append(summary)
            edits.extend(applied)
            if applied:
                result = sandbox.run_command(task.score_command)
                last_output = self._command_text(result)
                score_passed = result.exit_code == 0
            regressions = self._regressions(suite_before, sandbox.suite_outcomes())
            attempts.append(
                {
                    "attempt": attempt_index + 1,
                    "parsed_edit": bool(applied),
                    "score_passed": score_passed,
                    "regressions": regressions,
                    "prompt_chars": len(prompt),
                    **usage,
                }
            )

        suite_after = sandbox.suite_outcomes()
        regressions = self._regressions(suite_before, suite_after)
        # Strict success: the target test passes AND no test that passed before broke.
        success = score_passed and not regressions
        first_attempt = attempts[0] if attempts else None

        current_skills = self.active_skills if self.active_skills is not None else STRATEGY_SKILLS.get(self.strategy, [])
        trace = TaskRunTrace(
            run_id=run_id,
            task_id=task.id,
            family=task.family,
            split=task.split,
            strategy=self.strategy,
            success=success,
            failure_reason="" if success else self._failure_reason(task, score_passed, regressions),
            commands=sandbox.commands,
            edits=edits,
            diff=sandbox.diff(),
            tests_passed=score_passed,
            duration_seconds=round(time.perf_counter() - started, 3),
            run_dir=str(sandbox.root),
            metadata={
                "expected_failure_mode": task.expected_failure_mode,
                "provider": self.client.name,
                "model": self.client.model,
                "active_skills": current_skills,
                "notes": notes,
                "seed": seed,
                "temperature": LLM_TEMPERATURE,
                "max_output_tokens": LLM_MAX_OUTPUT_TOKENS,
                "max_steps": self.max_steps,
                "solved_before_any_edit": first.exit_code == 0,
                "score_passed": score_passed,
                "regressions": regressions,
                "suite_before": suite_before,
                "suite_after": suite_after,
                "attempts": attempts,
                "model_calls": len(attempts),
                "infra_error": infra_error,
                "first_attempt_score_passed": bool(first_attempt and first_attempt["score_passed"]),
                "first_attempt_success": bool(
                    first_attempt and first_attempt["score_passed"] and not first_attempt["regressions"]
                ),
            },
        )
        sandbox.write_trace(trace)
        return trace

    @staticmethod
    def _regressions(before: dict[str, str], after: dict[str, str]) -> list[str]:
        """Tests that passed before the agent's edits and no longer pass."""
        return sorted(test for test, outcome in before.items() if outcome == "passed" and after.get(test) != "passed")

    # -- prompt + reply handling -------------------------------------------------

    def _editable_files(self, sandbox: Sandbox) -> dict[str, str]:
        files: dict[str, str] = {}
        for path in sorted(sandbox.root.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(sandbox.root).as_posix()
            name = path.name
            if name in EDIT_BLOCKLIST or name.startswith("test_") or "__pycache__" in rel:
                continue
            if path.suffix not in {".py", ".json", ".toml", ".cfg", ".ini"}:
                continue
            try:
                files[rel] = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
        return files

    def _test_files(self, sandbox: Sandbox) -> dict[str, str]:
        files: dict[str, str] = {}
        for path in sorted(sandbox.root.rglob("test_*.py")):
            rel = path.relative_to(sandbox.root).as_posix()
            files[rel] = path.read_text(encoding="utf-8")
        return files

    def _build_prompt(self, task: TaskSpec, sandbox: Sandbox, failing_output: str) -> str:
        active_skills = self.active_skills if self.active_skills is not None else STRATEGY_SKILLS.get(self.strategy, [])
        skills = "\n\n".join(PROMPT_TEXTS[name] for name in active_skills)
        skills_block = skills or "(no extra skills provided)"
        editable = self._editable_files(sandbox)
        tests = self._test_files(sandbox)

        def render(files: dict[str, str]) -> str:
            return "\n".join(f"### {rel}\n```\n{content}\n```" for rel, content in files.items())

        return (
            "You are a terminal coding agent fixing a small Python repository.\n\n"
            f"TASK: {task.instruction}\n"
            f"Scoring command (must exit 0): {task.score_command}\n\n"
            f"ACTIVE SKILLS (follow these):\n{skills_block}\n\n"
            f"FAILING TEST OUTPUT:\n{_truncate(failing_output)}\n\n"
            f"TEST FILES (read-only; you may NOT edit these):\n{render(tests)}\n\n"
            f"EDITABLE SOURCE FILES:\n{render(editable)}\n\n"
            "For each source file you change, output a block in EXACTLY this format:\n"
            "<<<FILE app.py\n"
            "<entire new file contents>\n"
            ">>>END\n"
            "You may output several such blocks. After the blocks, optionally add one "
            "line `SUMMARY: ...`.\n"
            "CRITICAL: each block must contain the COMPLETE file — keep every existing "
            "import, function, and class the tests still import; change only what is needed "
            "to pass. Do not delete unrelated code. Never edit test files. Output only the "
            "FILE blocks (and optional SUMMARY line), nothing else."
        )

    def _apply_reply(self, sandbox: Sandbox, reply: str) -> tuple[list[EditTrace], str]:
        files = _parse_file_blocks(reply)
        if not files:
            # Tolerate a model that ignored the format and emitted a JSON object.
            try:
                data = _extract_json(reply)
                files = {k: v for k, v in (data.get("files") or {}).items() if isinstance(v, str)}
            except (json.JSONDecodeError, ValueError):
                files = {}
        summary_match = re.search(r"^SUMMARY:\s*(.+)$", reply, re.MULTILINE)
        summary = summary_match.group(1).strip() if summary_match else ""
        if not files:
            return [], "could not parse model reply into file edits"
        applied: list[EditTrace] = []
        root = sandbox.root.resolve()
        for rel, content in files.items():
            name = Path(rel).name
            if name in EDIT_BLOCKLIST or name.startswith("test_"):
                continue
            target = (sandbox.root / rel).resolve()
            if root not in target.parents and target != root:
                continue  # refuse writes outside the sandbox
            write_text(target, content)
            applied.append(EditTrace(file=rel, summary=summary or f"model edited {rel}"))
        return applied, summary

    def _command_text(self, command) -> str:
        return f"$ {command.cmd}\n[exit {command.exit_code}]\n{command.stdout}\n{command.stderr}"

    def _failure_reason(self, task: TaskSpec, score_passed: bool, regressions: list[str]) -> str:
        if score_passed and regressions:
            return f"target test passed but broke previously passing tests: {', '.join(regressions)}"
        return f"{self.client.name} did not satisfy {task.score_command} within {self.max_steps} attempts"


class GeminiTerminalAgent(LLMTerminalAgent):
    """Gemini-backed terminal agent (kept for the documented Gemini integration path)."""

    def __init__(self, strategy: str = "dreamgym_skill", api_key: str | None = None, model: str | None = None):
        super().__init__(strategy=strategy, provider="gemini", client=GeminiClient(api_key=api_key, model=model))


def build_agent(strategy: str, mode: str):
    """Return the live agent for a given CLI mode ('gemini', 'qwen', ...)."""
    return LLMTerminalAgent(strategy=strategy, provider=mode)


def gemini_smoke_test(api_key: str | None = None, model: str | None = None) -> str:
    client = GeminiClient(api_key=api_key, model=model, timeout=30)
    return client.generate_text(
        "Reply in one short sentence: Terminal DreamGym uses Gemini to diagnose terminal failures and generate practice worlds."
    )
