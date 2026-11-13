# Skill: Writing Robust CLI Applications

1. **Handle exceptions explicitly** - Catch specific exceptions like `FileNotFoundError` and print clear error messages to stderr instead of letting them propagate as tracebacks.

2. **Validate inputs early** - Check for invalid or empty inputs at the start of functions and raise descriptive `ValueError` exceptions with meaningful messages that match test expectations.

3. **Match expected output format exactly** - Ensure error messages, JSON formatting, and return codes match exactly what tests expect; avoid generic print statements.

4. **Use default values gracefully** - When reading config files or environment variables, use `.get()` with defaults instead of direct key access to prevent `KeyError`.

5. **Separate logic from CLI interface** - Keep business logic (e.g., processing text, rendering output) separate from argument parsing and I/O handling for easier testing.

6. **Test edge cases thoroughly** - Consider empty inputs, missing files, malformed data, and invalid formats during development to prevent runtime errors in tests.

7. **Avoid silent failures** - If a function is expected to return an error code or raise an exception, make sure it does so explicitly rather than returning unexpected values.

8. **Use consistent output formatting** - Prefer `json.dumps()` for structured output over string concatenation to ensure correct JSON syntax and avoid typos.

9. **Validate function signatures** - Ensure that all imported functions are called with the correct number and type of arguments; adjust call sites if necessary when APIs change.
