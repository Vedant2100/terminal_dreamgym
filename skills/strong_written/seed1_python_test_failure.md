# Skill: Writing Robust CLI Applications

1. **Handle errors gracefully**: Always catch specific exceptions (like `FileNotFoundError`) and return appropriate exit codes. Print meaningful error messages to `stderr`, not `stdout`.

2. **Validate inputs early**: Check for empty or invalid inputs before processing. Return zero exit codes for valid operations, non-zero for failures.

3. **Use structured output for JSON mode**: When using `--json`, always print valid JSON with consistent keys and formatting. Avoid string concatenation; use `json.dumps()`.

4. **Provide defaults for optional settings**: Never assume config files contain all required fields. Use `.get(key, default)` to avoid `KeyError`.

5. **Test both success and failure paths**: Ensure CLI returns correct exit codes and output streams for valid inputs, missing files, invalid data, etc.

6. **Separate concerns in CLI logic**: Keep argument parsing, input processing, and output formatting distinct. This simplifies testing and reduces bugs.

7. **Use proper logging or error reporting**: Don't print raw exceptions to `stdout`. Use dedicated error messages that match test expectations.

8. **Avoid silent failures**: If an operation cannot proceed, explicitly exit with a non-zero code and clear messaging.
