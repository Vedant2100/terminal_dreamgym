# Writing a benchmark v2 repo

Each directory in `benchmark_v2/repos/` is one small, correct Python project, plus
a `bugs.json`. Each bug becomes one task: the repo with that bug applied. An agent
(Qwen2.5-7B) sees the failing target test's output, every test file (read-only)
and every source file, and must rewrite source files so the target test passes
without breaking any other test. See `ledger/` for a complete example.

## Repo rules

- Flat directory: 2–4 source modules (`*.py`, not starting with `test_`) and 1–3
  test files (`test_*.py`). No subdirectories, no `conftest.py`, no README.
- Standard library only. Deterministic: no wall-clock time, randomness, network or
  real files. Inject clocks as parameters; use `tmp_path` or in-memory data.
- Size: about 80–200 lines of source in total and 8–16 tests. The whole repo is
  pasted into the prompt, so stay within these limits.
- Modules should depend on each other (one imports another), so that some bugs
  surface in a different module from their cause.
- Ordinary, plausible code with docstrings and comments that state the intended
  behaviour. All tests pass on the correct code.
- Tests are short and specific: one behaviour each, plain `assert` or
  `pytest.raises`. CLI repos test `main(argv)` with `capsys`, not subprocesses.

## Bug rules

Each entry in `bugs.json`:

```json
{
  "id": "snake_case_name",
  "category": "logic | contract | error_handling | config | trap",
  "difficulty": "easy | medium | hard",
  "target_test": "test_file.py::test_name",
  "note": "what is wrong and where the correct fix goes (never shown to the agent)",
  "edits": [{"file": "module.py", "old": "exact text", "new": "buggy text"}],
  "tempting_fix": [{"file": "...", "old": "...", "new": "..."}]
}
```

- `edits` turn correct code into buggy code. Each `old` must occur exactly once in
  its file. Edits may only touch source files, never tests.
- With the bug applied, the target test fails and **every other test still
  passes** (at least 3 others). Choose bugs and tests so failures are isolated.
- The buggy code must look like a plausible mistake: no `# BUG` comments, no
  nonsense. A comment or docstring that states the intended behaviour may stay,
  as real code often contradicts its own comments.
- Categories:
  - `logic`: wrong computation inside one function.
  - `contract`: modules disagree (argument order, renamed key, return shape,
    units); the test fails in one module, and the fix belongs in a specific one.
  - `error_handling`: swallowed or wrong exception, wrong exit code or stream,
    missing validation.
  - `config`: precedence (environment over file over default), types, required
    versus optional settings.
  - `trap`: the most obvious local change that makes the target pass breaks
    another test. `tempting_fix` (applied on top of the bug) must make the target
    pass **and** make some other test fail. The validator checks this.
- Mix of difficulty per repo: roughly a third easy (one-line, obvious from the
  assertion), a third medium, a third hard (cause in a different module from the
  failure, or several interacting lines). At least one `trap` per repo, and at
  least two categories other than `logic`.
- 7–9 bugs per repo. Two bugs may share a target test if their causes differ.

## Checking

```bash
.venv/bin/python -c "
from terminal_dreamgym.benchmark_v2 import validate_repo, REPOS_DIR
print(validate_repo(REPOS_DIR / 'YOUR_REPO') or 'ok')"
```

A repo is done when this prints `ok`.
