# Skill: Debugging Failing Tests in Python Repositories

1. **Understand the Test Failure**: Carefully read the failing test output to understand the exact assertion or error. Identify the line causing the failure and the expected vs actual values.

2. **Review the Code and Test**: Check the relevant code and test. Ensure that the test accurately reflects the intended behavior of the function or method. Verify that the function is being called with the correct parameters.

3. **Isolate the Issue**: If the test is failing, try to isolate the issue by adding print statements or using a debugger to trace the flow of execution and the state of variables at the point of failure.

4. **Check for Consistency**: Ensure that the function or method is consistent with its documentation and other similar functions. Look for edge cases that might not be handled correctly.

5. **Default Values and Error Handling**: Consider adding default values or error handling in functions where necessary. For example, handle missing keys in dictionaries or ensure type consistency.

6. **Use Mocks and Stubs**: If the function interacts with external systems or dependencies, use mocks or stubs to isolate the function and focus on its behavior in isolation.

7. **Test Data and Edge Cases**: Test with a variety of input data, including edge cases, to ensure the function behaves as expected under all conditions.

8. **Refactor if Necessary**: If the function or test is complex, refactor it to make it more maintainable and easier to test. Simplify the function if possible.
