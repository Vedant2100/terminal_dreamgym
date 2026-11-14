# Skill: Debugging and Fixing pytest Failures

1. **Understand the test failure deeply**: Read the full error message, including traceback and assertion details, to grasp what exactly is expected vs. what is happening.

2. **Make minimal, targeted changes**: Modify only the code necessary to satisfy the test. Avoid over-engineering or changing unrelated functionality.

3. **Test changes in isolation**: Run individual tests after each edit to confirm your fix works and doesn’t introduce new failures.

4. **Handle edge cases explicitly**: For input validation, ensure empty inputs, missing files, or invalid formats are handled gracefully with appropriate error messages or defaults.

5. **Validate output format matches expectations**: If tests check JSON output, ensure the structure and content match exactly what’s expected (e.g., correct keys, formatting, escaping).

6. **Be consistent with return codes**: Error conditions should return non-zero exit codes; successful operations should return zero.

7. **Check for implicit behavior changes**: Functions like `strip()`, `lower()`, or `replace()` may alter inputs in unexpected ways—ensure all transformations align with test expectations.

8. **Avoid hardcoded assumptions in logic flow**: Tests often verify specific error messages or return values, so avoid hardcoding strings that might differ from expected outputs.

9. **Use proper exception handling**: Catch and respond to specific exceptions rather than letting them propagate as generic errors.

10. **Verify environment and configuration settings**: When tests depend on config files or env vars, ensure defaults are used where necessary, and missing keys don’t cause crashes.
