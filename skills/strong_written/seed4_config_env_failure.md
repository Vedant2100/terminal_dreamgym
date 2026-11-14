# Skill: Systematic Test-Driven Debugging

1. **Understand the test failure deeply** - Read the error message completely, including traceback and expected vs actual values. Identify if it's a logic error, argument mismatch, or output format issue.

2. **Make minimal, targeted changes** - Edit only what's necessary to fix the specific test failure. Avoid over-engineering or refactoring unrelated code sections.

3. **Verify side effects** - After fixing one test, run all tests to ensure no regressions were introduced. A fix that passes one test may break another.

4. **Respect function signatures and expected inputs/outputs** - When functions are called with wrong arguments or return unexpected types, adjust the calling code or implementation accordingly.

5. **Handle edge cases explicitly** - Tests often check for empty input, missing files, or invalid data. Ensure your fix properly handles these scenarios without raising exceptions.

6. **Test output format carefully** - For CLI tools, ensure error messages and JSON outputs match exactly what tests expect in both content and formatting (quotes, casing, structure).

7. **Avoid premature optimization** - Focus first on making the test pass with correct behavior before improving code style or performance.
