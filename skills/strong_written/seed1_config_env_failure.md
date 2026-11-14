# Skill: Debugging and Fixing pytest Failures in Python CLI Applications

1. **Understand the test failure context**: Read the error message and traceback carefully to identify what is expected vs. what is happening. Determine if the issue is with stdout, stderr, return codes, or JSON formatting.

2. **Check input/output handling logic**: Verify that functions correctly process inputs like empty strings, special characters, or invalid formats. Ensure exceptions are raised and handled appropriately.

3. **Validate CLI argument parsing and flow**: Confirm command-line arguments are parsed and passed correctly to core logic. Make sure file operations resolve paths properly and handle missing files gracefully.

4. **Ensure correct JSON output formatting**: When using `--json` flag, verify that error messages are structured as valid JSON with proper keys like `"error"` and not plain strings or malformed objects.

5. **Avoid overwriting or changing behavior unintentionally**: Don’t alter core logic unless necessary. Focus on fixing only the specific discrepancy between expected and actual behavior.

6. **Test edge cases explicitly**: Test empty inputs, invalid formats, missing files, and special characters to validate robustness before finalizing changes.

7. **Use consistent error messaging**: Ensure errors printed to stdout/stderr match exact test expectations, including capitalization and wording.
