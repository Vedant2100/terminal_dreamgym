# Skill: Debugging Failing Pytest Tests

1. **Understand the Failure**: Before making any changes, thoroughly review the failing test output. Identify the exact line of code that caused the failure and the type of error (e.g., `KeyError`, `AssertionError`, `TypeError`).

2. **Review Test Cases**: Ensure that the failing test case is valid and represents a real use case. Consider edge cases that might not be covered by existing tests but could cause failures.

3. **Isolate the Issue**: Temporarily disable other tests to isolate the failing test. Run the tests again to confirm that only the specific test is failing.

4. **Check for Consistency**: Ensure that the function or method being tested is consistent with its documentation and other parts of the codebase. Look for potential inconsistencies in function signatures and return types.

5. **Update Test and Code Concurrently**: Make small, incremental changes to the code and the test. Update the test to reflect the expected behavior after making changes. This helps in identifying if the issue was in the test or the code.

6. **Use Context and Input**: When making changes, consider the context of the input and the expected output. Ensure that all possible inputs are handled correctly, including edge cases.

7. **Add or Update Default Values**: If the test is failing due to missing or unexpected values, consider adding or updating default values in the code. Ensure that the function or method can handle these cases gracefully.

8. **Refactor and Simplify**: If the code is complex, consider refactoring it to make it simpler and easier to understand. This can help in identifying and fixing issues more efficiently.
