# Skill: Robust Test Fixing for Python Projects

1. **Understand the Test Cases**: Before making any code changes, thoroughly read through the failing test cases. Identify the expected behavior and the actual outcome.

2. **Analyze the Error Messages**: Carefully parse the error messages and traceback to understand where the failure is occurring. Look for specific assertions, exceptions, or conditions that are not being met.

3. **Check for Consistent Data Handling**: Ensure that your code consistently handles data, especially when dealing with user inputs, configuration files, and JSON serialization. Make sure that errors and edge cases are properly managed.

4. **Verify Edge Cases**: Test edge cases such as empty inputs, invalid inputs, and special characters. Ensure that your code can handle these scenarios without causing unexpected behavior.

5. **Update Assertions Appropriately**: Modify assertions to match the expected outcome. Ensure that the test cases are correctly checking the output or behavior of the functions.

6. **Review Exception Handling**: Make sure that exception handling is robust and covers all potential issues. Ensure that error messages and outputs are clear and informative.

7. **Test with Different Inputs**: Run tests with various inputs, including edge cases, to ensure that the changes you make do not introduce new bugs or alter existing functionality.

8. **Check for Default Values**: Ensure that default values are correctly set for optional parameters, especially when dealing with optional configuration options or environment variables.
