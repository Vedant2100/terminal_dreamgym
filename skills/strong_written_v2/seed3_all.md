# Skill: Debugging and Fixing pytest Failures in Python

1. **Understand the test failure message completely** – Read error types, expected vs actual values, and stack traces to pinpoint the root cause.

2. **Analyze test expectations carefully** – Determine whether the issue is with logic, input handling, or output formatting.

3. **Modify only what’s necessary** – Avoid over-engineering fixes; make small targeted changes that align with test expectations.

4. **Test your changes incrementally** – Run individual tests after each edit to confirm progress and avoid introducing new errors.

5. **Check for side effects in related functions** – When fixing one function, verify that other functions relying on it still behave correctly.

6. **Ensure correct data flow and type handling** – Pay attention to how strings are processed (strip, case, replace), and how inputs are passed between functions.

7. **Handle edge cases explicitly** – For inputs like empty strings or special characters, ensure proper error handling or normalization logic.

8. **Validate return formats (especially JSON)** – If tests expect structured output (like JSON), verify that printing and serialization match exactly what’s expected.

9. **Understand the intended behavior of helper functions** – Some functions may need to be restructured if their interfaces differ from how they are called in tests.

10. **Use clear, consistent code style** – Avoid introducing inconsistencies like incorrect parameter order or missing logic that could confuse test runners.
