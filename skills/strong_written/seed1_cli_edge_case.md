# Skill: Systematic Python Test Debugging

1. **Analyze error messages carefully** - Look for KeyError, TypeError, or AssertionErrors to identify missing keys, wrong function signatures, or incorrect return values.

2. **Check function signatures and argument counts** - Ensure functions are called with correct numbers of arguments; adapt calling code when function signatures change.

3. **Handle missing data gracefully** - Use `.get()` with defaults instead of direct key access to prevent KeyErrors in config or data loading.

4. **Validate input/output behavior step-by-step** - When fixing string processing, confirm whitespace handling, case conversion, and character replacement match expected outputs.

5. **Test edge cases explicitly** - If tests expect specific behaviors (like preserving '+' in emails), ensure your changes don't inadvertently alter those rules.

6. **Verify imports and module structure** - Confirm that external functions are imported correctly and used with matching argument structures.

7. **Ensure backward compatibility** - Don’t break existing APIs or expected return types unless the test explicitly requires a change.

8. **Re-run all tests after each fix** - Small changes can cascade into new failures; validate the full suite to catch regressions.

9. **Use default values wisely** - Provide sensible defaults in config loading but avoid hiding missing required fields that should raise errors.
