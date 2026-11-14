# Skill: Effective pytest Test Debugging and Fix Implementation

1. **Analyze error messages carefully** - Look beyond the surface assertion failure; examine input/output behavior, data types, and expected vs actual values to understand root causes.

2. **Ensure your fixes address the core logic issue** - Don't just change what's printed or caught; make sure the function's behavior matches test expectations (e.g., strip whitespace, convert types).

3. **Test edge cases during implementation** - Validate that your changes don’t break existing functionality by running all tests, not just the failing one.

4. **Understand how exceptions and return codes work** - Make sure error handling prints meaningful messages to stderr and exits with non-zero codes for CLI tools.

5. **Use defensive programming patterns** - Prefer `.get()` on dictionaries to avoid KeyError and handle type conversion explicitly (e.g., `int()`, `str()`).

6. **Verify test input/output alignment** - Confirm that test inputs exactly match expected behavior, including case sensitivity, whitespace, and special characters like `+` tags or punctuation.

7. **Keep changes minimal and targeted** - Focus on fixing only what breaks; avoid unnecessary refactoring that risks introducing new bugs.

8. **Check for missing imports or incorrect JSON handling** - Ensure all required modules are imported and data is parsed correctly from config files or CLI arguments.
