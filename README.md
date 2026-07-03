# Terminal DreamGym

Agents that dream their own practice terminals.

## What it is

Terminal DreamGym is a local wind tunnel for self-improving terminal agents. When an agent fails a terminal task, Terminal DreamGym diagnoses the missing capability, generates targeted practice environments, writes recovery skills, and promotes only skills that transfer to held-out and adversarial terminal tasks.

The "dream" is a generated practice repo: a tiny terminal world that isolates the capability the agent missed.

```text
terminal-agent failure
-> diagnosis of missing capability
-> generated practice terminal worlds
-> generated SKILL.md
-> practice + held-out/adversarial evaluation
-> promote/reject skill
-> improved future terminal behavior
```

## Why it matters

Terminal agents are brittle. They edit before reading stack traces, rerun full suites instead of targeted tests, swallow CLI errors, miss config drift, and break working behavior while fixing one visible case.

Reflection alone can overfit to the last failure. Terminal DreamGym tests whether self-improvement is real by making agents practice the capability they were missing and then measuring transfer.

## Hackathon fit

Recursive Intelligence:
Terminal DreamGym lets the agent modify its future behavior by generating and testing new terminal skills.

Continual Learning:
Failures become curricula and reusable skills.

Self-Improvement Stack:
The project provides traces, generated eval environments, practice worlds, transfer gates, and promotion logic.

## Gemini 3.5 fit

Gemini is the recursive improvement engine:

- Gemini reads terminal traces.
- Gemini diagnoses missing capabilities.
- Gemini generates practice repos/tasks.
- Gemini writes `SKILL.md` files.
- Gemini proposes improved command strategies.
- Terminal DreamGym evaluates whether those skills transfer.

Terminal DreamGym is **live-model only**: a real LLM drives every task. It reads the
failing pytest output and the active `SKILL.md` text, proposes full-file edits
(`<<<FILE … >>>END` blocks, never test files, never outside the sandbox), the edits
are applied, and **real pytest decides success**. There is no scripted fallback — if
the model produces no working patch, that is a genuine failure and is recorded as one.

## Providers

Pick a provider with `--mode` (default is `qwen`):

| Mode | Backend | Notes |
| --- | --- | --- |
| `qwen` | Local Ollama, OpenAI-compatible (`http://localhost:11434/v1`) | Free, no quota. Default. |
| `gemini` | Gemini REST (`generativelanguage.googleapis.com`) | The prize-target path. Free tier is capped at ~20 requests/day, too few for the full ~200-call loop — use a paid key for a full run. |

```bash
# Local (free), default:
ollama pull qwen2.5:7b
python -m terminal_dreamgym.cli demo            # --mode qwen

# Gemini:
cp .env.example .env   # set GEMINI_API_KEY
python -m terminal_dreamgym.cli gemini-smoke
python -m terminal_dreamgym.cli demo --mode gemini
```

Configure via `.env`: `GEMINI_API_KEY`, `GEMINI_MODEL`, `QWEN_BASE_URL`, `QWEN_MODEL`,
and `TERMINAL_DREAMGYM_MODE` (default provider). A real Qwen2.5-7B run is captured in
[`reports/live_model_run_qwen.md`](reports/live_model_run_qwen.md).

## What this is not

- Not a basic RAG app.
- Not a Streamlit app.
- Not a dashboard-first project.
- Not an image analyzer.
- Not a job screener, medical advisor, mental health advisor, nutrition coach, personality analyzer, or sports analyzer.
- Not a wrapper chatbot.

The core demo is a working terminal self-improvement harness.

## How to run

```bash
pip install -e ".[dev]"
ollama pull qwen2.5:7b                  # or set GEMINI_API_KEY and use --mode gemini
python -m terminal_dreamgym.cli demo    # runs the full live-model loop (default: qwen)
pytest -q                               # provider-free unit tests
```

> The demo and `evaluate` require a running provider (Ollama for `qwen`, or a paid
> Gemini key). `pytest` does **not** — the agent's parsing/safety logic is unit-tested
> without a model.

Individual commands (append `--mode gemini` to use Gemini):

```bash
python -m terminal_dreamgym.cli init-demo
python -m terminal_dreamgym.cli run-baseline
python -m terminal_dreamgym.cli diagnose --from-run runs/baseline.json
python -m terminal_dreamgym.cli generate-curricula --from-diagnoses runs/diagnoses.json
python -m terminal_dreamgym.cli generate-skills --from-curricula curricula/generated
python -m terminal_dreamgym.cli evaluate
python -m terminal_dreamgym.cli report
```

## Demo

The one-shot demo generates:

- `runs/baseline.json`
- `runs/diagnoses.json`
- `curricula/generated/*.json`
- `runs/practice_worlds/*`
- `skills/generated/*.md`
- `runs/evaluation.json`
- `reports/report.md`
- `reports/report.html`

Live-model results vary by model and run (the model genuinely solves each task).
The pattern that matters — and that reproduced on a real Qwen2.5-7B run — is in
**transfer and regressions**, not raw train scores:

```text
Method                Train   Heldout   Adversarial   Decision
Baseline              2/8     1/6       2/6           -
Reflection-only       4/8     2/6       1/6           REJECTED (adversarial regression)
Terminal DreamGym     6/8     3/6       4/6           PROMOTED (best transfer, 0 regressions)
```

```text
Skill                         Naive decision   DreamGym decision
reflection_overfit_skill       PROMOTE          REJECT
minimal_patch_skill            PROMOTE          PROMOTE
contract_drift_skill           PROMOTE          PROMOTE
```

Reflection raised train but **regressed** on the adversarial comma-counterexample;
the transfer gate rejected it. Full run: [`reports/live_model_run_qwen.md`](reports/live_model_run_qwen.md).

## Research question

Can failure-conditioned curriculum generation produce more transferable terminal skills than reflection alone?

Hypothesis: failure-conditioned curriculum generation produces more transferable terminal skills than naive reflection alone.

## Benchmark domains

- Python failing test repair
- CLI edge-case repair
- Config/env failure
- Dependency/API mismatch

Each run creates local sandboxes under `runs/sandboxes/`, executes pytest commands with timeouts, captures stdout/stderr/exit code, records edits, and writes trace JSON with diffs.
