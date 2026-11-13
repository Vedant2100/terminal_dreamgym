# Skill: General Approach to Fixing Failing Tests

1. **Understand the Test Failure**: Carefully read the test failure output to identify the exact assertion or condition that is failing. Note the error message and traceback.

2. **Analyze the Code**: Review the code in the relevant file(s) to understand why the test is failing. Look for potential issues such as incorrect logic, missing values, or edge cases.

3. **Check for Consistency**: Ensure that the test and the code being tested are consistent. For example, if the test expects a specific error, make sure the code raises that error.

4. **Test Edge Cases**: Implement or modify tests to cover edge cases that might not have been considered initially. This can help uncover unexpected behaviors.

5. **Refactor and Simplify**: If the code is complex or hard to understand, consider refactoring it to improve clarity. This can make it easier to identify and fix issues.

6. **Use Assertions Wisely**: Ensure that your assertions are clear and meaningful. Avoid overly complex assertions that can be difficult to understand or maintain.

7. **Add Default Values**: When dealing with optional values, consider adding default values to avoid `KeyError` or `AttributeError` exceptions.

8. **Check for Side Effects**: Ensure that your code does not have unintended side effects, such as modifying global state or relying on external environment changes.

9. **Consistent Error Handling**: Make sure error handling is consistent across your codebase. Use `try-except` blocks where necessary to handle errors gracefully.
