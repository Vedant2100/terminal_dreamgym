# Skill: Fixing pytest Failures by Analyzing Error Messages

1. **Read error messages carefully** – Identify the root cause (e.g., `KeyError`, `AssertionError`, `JSONDecodeError`) before making changes.
2. **Understand test expectations** – Match your fix to what the test is asserting, not just the immediate failure.
3. **Avoid overwriting existing logic** – When default values are needed, use `.get(key, default)` instead of direct key access.
4. **Handle missing keys gracefully** – If config or input data may be incomplete, provide safe fallbacks using `dict.get()` or defaults.
5. **Ensure error messages match exactly** – Test assertions often check for specific strings; update error messages to match expected output precisely.
6. **Test in isolation** – Make minimal changes and verify each fix independently before moving on.
7. **Check both stdout and stderr** – CLI tests may require output to be printed correctly to either stream depending on flags.
8. **Don’t assume default behavior** – When a function uses defaults or environment variables, ensure fallbacks are properly handled in all code paths.
