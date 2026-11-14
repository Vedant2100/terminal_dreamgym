# Skill: Debugging and Fixing Failing Tests

1. **Understand the Error**: Carefully read the failure message to understand what the test is expecting versus what it received. Identify the type of error (e.g., `AssertionError`, `TypeError`, `AttributeError`) and the context in which it occurred.

2. **Check Test and Code Alignment**: Ensure that the test is correctly checking the expected behavior of the code. Verify that the test cases cover all possible scenarios, including edge cases and error handling.

3. **Examine the Code Logic**: Look for potential issues in the code logic that could be causing the failure. Common culprits include incorrect return values, unhandled exceptions, and misaligned error messages.

4. **Review Exception Handling**: Ensure that exceptions are properly handled and the appropriate error messages are returned. Pay attention to the message content and format, as it should match the test expectations.

5. **Assert Messages and Conditions**: Double-check the conditions in assertions. Ensure that the conditions are correctly formulated and that the expected values are accurately compared against actual values.

6. **Test Edge Cases**: Add or modify test cases to cover edge cases, such as empty inputs, invalid inputs, and unusual scenarios. This helps in identifying and fixing potential issues that might not have been considered initially.

7. **Debugging**: Use a debugger to step through the code and understand the flow of execution. This can help identify where the behavior deviates from expectations.
