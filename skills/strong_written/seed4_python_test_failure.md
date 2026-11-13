# Skill: Writing Robust CLI Applications

1. **Handle errors gracefully**: Always catch exceptions and ensure error messages are informative and consistent. Don't let raw Python tracebacks leak to users.

2. **Validate input types early**: Convert string inputs to appropriate types (e.g., int, bool) at the start of processing. Use defaults or fail fast with clear messages.

3. **Maintain interface consistency**: When changing function signatures, ensure all callers are updated. Check that imported functions match expected parameters.

4. **Test error conditions explicitly**: Write tests for failure cases, like invalid input, missing files, or type mismatches, and verify both return codes and message content.

5. **Use structured output formats**: When supporting JSON output, ensure valid JSON is produced. Avoid manual string formatting; use `json.dumps()` instead.

6. **Check for missing keys in config**: Never assume configuration keys exist. Use `.get()` with defaults or validate required fields early.

7. **Ensure clear and predictable CLI behavior**: Commands should behave consistently with documented expectations, especially around exit codes, stdout/stderr usage, and argument parsing.

8. **Avoid overwriting or shadowing**: Be cautious when renaming or reordering variables, especially in error handling blocks — make sure logic is preserved across changes.
