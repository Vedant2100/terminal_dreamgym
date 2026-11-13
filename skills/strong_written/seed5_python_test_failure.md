# Skill: Debugging and Fixing pytest Failures in Python Projects

1. **Analyze error messages carefully** – Identify the root cause (e.g., KeyError, TypeError, missing imports) before making changes.
2. **Handle missing keys gracefully** – Use `.get()` with default values when accessing dictionary keys to prevent `KeyError`.
3. **Ensure proper exception handling** – Catch and re-raise exceptions with meaningful messages that match test expectations.
4. **Validate input/output behavior** – Confirm functions behave as expected under edge cases like empty or invalid inputs.
5. **Test changes incrementally** – Fix one issue at a time and rerun tests to confirm progress without introducing new bugs.
6. **Use correct JSON output formatting** – When printing JSON, ensure valid structure with proper escaping and consistent output format.
7. **Avoid syntax errors in edited files** – Double-check code syntax before finalizing edits, especially when modifying `__main__` or adding lines.
8. **Match test expectations exactly** – Ensure error messages, return codes, and output strings align precisely with what tests require.
