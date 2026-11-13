# Skill: Fixing Python Tests by Rewriting Source Files

1. **Understand the test failure fully** – Read the error message carefully to determine what’s expected vs. what’s returned (e.g., whitespace, case sensitivity, type conversion).

2. **Modify only what’s necessary** – Adjust the function logic to match expected behavior without breaking other functionality or introducing new bugs.

3. **Handle missing or invalid data gracefully** – Use `.get()` with defaults when accessing dictionary keys to prevent `KeyError`.

4. **Ensure correct data types** – Convert values (e.g., strings to integers) when needed, especially for numeric fields in configuration.

5. **Test your changes locally** – Run the test suite after each edit to verify fixes and catch regressions early.

6. **Preserve existing function signatures and imports** – Don’t break imports or change function interfaces unless explicitly required by tests.

7. **Be cautious with string operations** – Fix whitespace, case, and special character handling (e.g., `strip()`, `lower()`, `replace()`).

8. **Avoid overwriting existing logic unnecessarily** – When a function already exists, extend or correct it rather than rewriting entirely unless needed.
