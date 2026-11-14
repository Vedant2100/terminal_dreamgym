# Skill: Writing Robust Python Fix Scripts

1. **Understand the test failure deeply** - Read the error message carefully to identify exactly what the code is doing vs. what it should do.
2. **Make minimal, targeted changes** - Modify only the specific logic that causes the failure; avoid over-engineering or changing unrelated functionality.
3. **Handle edge cases explicitly** - Ensure functions handle empty inputs, special characters, and unexpected formats gracefully.
4. **Test your change locally before finalizing** - Run the failing test(s) after each edit to confirm progress.
5. **Preserve existing behavior for valid inputs** - Don't break working functionality when fixing broken parts.
6. **Use consistent output formats (e.g., JSON)** - When returning structured data, ensure it matches expected format exactly.
7. **Validate error handling logic** - Make sure errors are raised and caught appropriately to produce clear messages or exit codes.
8. **Be cautious with string transformations** - Pay attention to whitespace, case sensitivity, and character replacements that could silently alter intent.
