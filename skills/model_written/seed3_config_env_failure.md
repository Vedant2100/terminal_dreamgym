# Skill: Debugging Failing Tests with pytest

1. **Understand the Test**: Before making any code changes, read the test thoroughly to understand what it is supposed to verify. Ensure you grasp the context and the expected behavior.

2. **Review the Failing Output**: Carefully examine the failing test output. Look for specific error messages or return codes that indicate what went wrong. This can provide direct clues on where the failure lies.

3. **Isolate the Issue**: Try to isolate the issue by running individual tests or parts of the tests in isolation. This can help identify whether the failure is due to a specific test case or an underlying issue in the code.

4. **Check for Edge Cases**: Ensure that your code handles edge cases correctly. This includes testing with empty inputs, invalid inputs, and boundary conditions.

5. **Test with Different Inputs**: Modify the test to use different types of inputs, such as valid and invalid, to see how the code behaves. This can help in understanding the expected outputs and identify where the code deviates from the expected behavior.

6. **Refactor Code Gradually**: Make small, incremental changes to the code and re-run the tests after each change. This approach can help in identifying which specific change caused the failure.

7. **Use Logging for Debugging**: If the test output is not clear, add logging statements in the code to print intermediate values and help trace the flow of execution. This can provide insights into what the code is doing at runtime.

8. **Review Test Assertions**: Ensure that the test assertions are correctly placed. Verify that the expected conditions are met and that the test logic is sound.
