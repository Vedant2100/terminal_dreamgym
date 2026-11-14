# Skill: Debugging and Fixing Python CLI Applications

1. **Understand the problem context**: Before modifying code, fully comprehend what the test expects and how the application should behave. Look at error messages, especially those involving return codes, stdout/stderr, and exception types.

2. **Handle exceptions properly**: When a file is missing or input is invalid, ensure that your code catches specific exceptions (e.g., `FileNotFoundError`, `ValueError`) and provides clear, user-friendly error messages instead of letting exceptions bubble up as stack traces.

3. **Validate input handling logic**: Test for edge cases like empty inputs, malformed data, or special characters. Ensure functions correctly strip, normalize, or preserve expected formats without unintended side effects (e.g., removing commas when they are semantically meaningful).

4. **Use proper JSON output formatting**: If your CLI supports JSON output mode, always use `json.dumps()` to ensure valid JSON is printed. Avoid string concatenation for JSON structures.

5. **Return correct exit codes**: Applications should return 0 on success and non-zero on failure. This allows tests to assert correct behavior based on program exit status.

6. **Preserve existing API contracts**: When fixing bugs, avoid breaking assumptions made by other parts of the codebase (e.g., function signatures, expected keys in dictionaries). Maintain backward compatibility where possible.

7. **Test edge cases incrementally**: After making changes, run individual failing tests to confirm fixes before running all tests. This helps isolate whether a change broke something else.
