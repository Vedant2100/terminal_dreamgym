# Skill: Debugging and Fixing pytest Failures in Python CLI Applications

1. **Understand the test failure message completely** - Read the error output carefully to determine if it's a missing import, incorrect return value, wrong exception handling, or formatting issue.

2. **Identify whether the issue is in source code logic or test expectations** - If the test expects specific output but your program produces something different, adjust your code to match that expected behavior exactly.

3. **Ensure proper exception handling and error messaging** - When a function raises an exception, make sure the CLI catches it and prints a clear user-facing message instead of a traceback.

4. **Validate input/output formats strictly** - Pay attention to formatting like JSON structure, string trimming, casing, special characters (e.g., `+` in emails), and whitespace handling.

5. **Check return codes and stdout/stderr consistency** - A failing test often means the CLI returns non-zero exit code or prints to stderr instead of stdout when it should not.

6. **Test edge cases explicitly** - If tests cover empty input, missing files, invalid data, etc., ensure your program handles these correctly without raising unexpected exceptions.

7. **Avoid overwriting existing functionality** - When modifying functions, keep all original behaviors intact unless the test explicitly requires a change.

8. **Use `strip()` and string methods correctly** - For email normalization or text processing, be precise about what parts of a string are modified (e.g., preserve `+` tags, not remove them).
