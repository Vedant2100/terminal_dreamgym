# Skill: Writing Robust pytest Fixes

1. **Understand the full test failure context** before making changes—look at error messages, expected vs actual outputs, and traceback details.
2. **Make minimal, targeted edits** that directly address the root cause of the failure without introducing new logic or breaking existing functionality.
3. **Preserve the original intent** of functions by not changing their behavior unless explicitly required by tests.
4. **Test changes locally** using the exact same command or setup as in the failing test environment.
5. **Ensure output formatting matches expectations**, especially for JSON, error messages, and string representations.
6. **Avoid overwriting or modifying unrelated parts of code**—focus only on what’s broken.
7. **Verify all related tests pass** after making a change to prevent regressions.
8. **Use consistent data types and formats** (e.g., strings vs. JSON objects) in return values and printed outputs.
9. **Handle edge cases like empty inputs, special characters, or missing files properly** based on test expectations.
10. **Re-read failing tests carefully**—sometimes the fix is about raising correct exceptions or returning expected error messages, not modifying logic flow.
