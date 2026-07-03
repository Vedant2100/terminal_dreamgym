# Agent Operating Notes

This repo is a live-model hackathon MVP for Terminal DreamGym. A real LLM (Qwen via
Ollama, or Gemini) drives every task; pytest decides success. There is no scripted
mock fallback.

- Run `pytest -q` before and after behavior changes. The test suite is provider-free
  (it unit-tests the agent's parsing/safety logic) and must stay green without a model.
- The demo and `evaluate` require a running provider (Ollama for `--mode qwen`, or a
  Gemini key for `--mode gemini`). Do not reintroduce a scripted/mock outcome path —
  failures must be real.
- Never let the agent edit test files or write outside the sandbox; preserve those
  guards in `gemini_agent.py`.
- Do not introduce Streamlit. Do not add paid cloud dependencies as a hard requirement.
- Keep `python -m terminal_dreamgym.cli demo` working, and report generation working
  for both Markdown and HTML.
- Preserve the transfer-gated promotion logic; reflection-only should visibly overfit
  (raise train, regress adversarial).
- All task sandboxes must be local, temporary, and safe. No commands that delete
  outside the sandbox; network/install commands are blocked in the sandbox.
