# Skill: Debugging and Fixing Python CLI and Configuration Tests

1. **Understand the test failure context**: Before editing code, carefully read the error message and test assertion to determine what behavior is expected vs. what’s happening.

2. **Handle edge cases explicitly**: When a function should return an error for invalid input, ensure it raises an appropriate exception or returns a non-zero exit code — not just prints to stdout.

3. **Validate input processing logic**: For CLI tools, make sure that invalid or empty inputs are handled gracefully and result in proper error messages printed to stderr, not stdout.

4. **Use `get()` method for dict access**: When reading from JSON config files, use `.get(key, default)` instead of direct key access (`dict[key]`) to avoid `KeyError` exceptions.

5. **Ensure correct data type conversions**: If configuration values are expected as integers (e.g., timeout), parse them explicitly using `int()` after fetching from config.

6. **Test both stdout and stderr**: Some tests validate error messages in stderr, so ensure errors are printed there, not just to stdout or silently swallowed.

7. **Avoid syntax errors in edits**: Never introduce invalid Python syntax like stray `>>>` lines or malformed strings when modifying source files.

8. **Match expected output format exactly**: If tests expect JSON-formatted output, use `json.dumps()` with correct structure; if plain text is required, match string formatting precisely.

9. **Test your changes in isolation**: Run individual tests after each edit to verify that you’re not breaking other functionality.
