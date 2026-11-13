# Skill: Debugging and Fixing pytest Test Failures in Python CLI Applications

1. **Understand the test failure context**: Read the error message carefully to identify whether the issue is with output formatting, error handling, function signatures, or missing logic.

2. **Validate input/output behavior**: Ensure that command-line tools print correct outputs (stdout/stderr) and return proper exit codes for both success and error cases.

3. **Handle exceptions gracefully**: When errors occur, ensure they are caught and printed in a user-friendly way — avoid showing raw tracebacks unless necessary.

4. **Match expected function signatures**: If using imported functions, make sure argument counts and types match between caller and callee.

5. **Test edge cases explicitly**: Consider how your code handles invalid inputs, missing files, empty strings, and malformed data.

6. **Use JSON output correctly**: When producing JSON, ensure valid formatting with `json.dumps()` and proper structure (e.g., keys like `"error"` or `"result"`).

7. **Check return codes in CLI tests**: Confirm that non-zero exit codes are returned on invalid input or errors.

8. **Avoid hardcoding test expectations**: Use generic checks for error messages or outputs, not hardcoded strings unless necessary.

9. **Ensure consistency between CLI and library functions**: If a CLI script calls a module function, ensure both interfaces align.

10. **Refactor incrementally and verify after each change**: Small, atomic changes help isolate which modification caused an issue.
