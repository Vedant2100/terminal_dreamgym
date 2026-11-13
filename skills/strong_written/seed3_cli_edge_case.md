# Skill: Effective Test-Driven Refactoring

1. **Understand the test intent fully** - Before editing, analyze what the test expects vs. what the current code does. Look at error messages and trace the execution path.

2. **Make minimal, targeted changes** - Fix only what's broken. Avoid rewriting entire functions unless necessary. Small changes reduce regression risk.

3. **Respect function signatures and argument counts** - When a function is called with N args but defined for M, ensure compatibility or adjust the call site accordingly.

4. **Handle data structure access safely** - Use `.get()` with defaults instead of direct key access to prevent KeyError exceptions from missing keys.

5. **Validate input/output behavior matches test expectations exactly** - Pay attention to whitespace, casing, punctuation, and return types — even small differences break tests.

6. **Test changes incrementally** - Run tests after each edit to confirm progress and detect new failures early.

7. **Don't assume function behavior from name alone** - A function named `parse_result` may not behave like a parser; inspect its actual logic and test cases before modifying.
