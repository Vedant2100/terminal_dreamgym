# Skill: Trace-first terminal debugging

When a terminal task fails:
1. Re-run the exact failing command.
2. Read the traceback or error output before editing files.
3. Identify the smallest failing test or command.
4. Inspect the referenced function, config key, or interface.
5. Make the smallest patch that addresses the observed failure.
6. Rerun the targeted test first, then the full suite.
