# Skill: Fixing pytest Failures by Analyzing Test Expectations

1. **Read test failure messages carefully** – Identify the exact assertion that fails, the expected vs actual values, and the line number.
2. **Understand the expected behavior** – Determine what the code should do based on the test's expectation, not just fix the error.
3. **Check for missing or incorrect function signatures** – Ensure functions are called with correct arguments as expected by tests.
4. **Handle missing or invalid data gracefully** – Use `.get()` with defaults instead of direct key access to prevent `KeyError`.
5. **Convert types properly** – Cast values (e.g., strings to integers) when tests expect specific types.
6. **Avoid applying changes blindly** – Only edit code if you understand how it connects to the test logic.
7. **Validate imports and module structure** – Confirm that all necessary modules are imported correctly.
8. **Test your fix in isolation** – Run individual failing tests after each change to verify correctness without introducing new errors.

This approach ensures minimal, targeted fixes aligned with test expectations rather than trial-and-error modifications.
