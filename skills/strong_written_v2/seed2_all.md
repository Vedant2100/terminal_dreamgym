# Skill: Debugging and Fixing Python Test Failures

1. **Understand the error message completely** before making changes—identify if it's a syntax, type, logic, or runtime issue.
2. **Read the test case expectations carefully** to ensure your fix aligns with intended behavior, not just the current output.
3. **Make minimal, targeted changes** that directly address the root cause of the failure.
4. **Test locally after each edit** using the same command as the failing test to catch regressions early.
5. **Avoid assumptions about code structure or imports**—always verify how functions are defined and called.
6. **Handle edge cases explicitly**, especially for input validation, file operations, and parsing logic.
7. **Ensure error messages are user-friendly and match test expectations**, especially for failure scenarios.
8. **Check that all dependencies and imports are correctly referenced** in both source and test files.
9. **Run the full test suite after fixing** to ensure no regressions were introduced.
10. **Use version control diffs wisely**—only modify what’s necessary, and review the diff before finalizing.
