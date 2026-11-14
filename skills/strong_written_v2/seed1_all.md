# Skill: Debugging and Fixing pytest Test Failures in Python CLI Applications

1. **Understand the test failure message completely** – Read the full error output including expected vs actual values, and tracebacks to identify root causes.
2. **Handle exceptions properly** – When code raises exceptions, ensure they are caught and handled with appropriate user-facing messages or exit codes.
3. **Validate input handling logic** – Check for proper stripping of whitespace, validation of inputs, and correct behavior for edge cases like empty strings or invalid formats.
4. **Ensure stdout/stderr consistency** – Make sure error messages are printed to stderr, not stdout, and that return codes match expected behavior (0 for success, non-zero for failure).
5. **Test edge cases explicitly** – Always consider how your changes affect boundary conditions such as empty input, missing files, or malformed data.
6. **Avoid breaking existing functionality** – When modifying one part of the code, ensure other functions or features still work as intended (e.g., imports, function signatures).
7. **Verify CLI argument parsing and flow control** – Confirm that command-line arguments are correctly parsed and that execution follows the intended logic path.
8. **Use consistent formatting for JSON output** – If outputting JSON, use `json.dumps()` to ensure valid, properly formatted output.
