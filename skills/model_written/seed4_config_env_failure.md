# Skill: Debugging and Testing Python Code

1. **Understand the Test Error**: Before making changes, carefully read the error message. Identify the specific part of the code that is causing the issue and understand why the test is failing.
2. **Identify the Root Cause**: Determine whether the issue is with the test, the function being tested, or the environment. Look for edge cases, unexpected inputs, or incorrect assumptions.
3. **Isolate the Problem**: If the test is failing due to an unexpected input or behavior, create a minimal test case that reproduces the issue. This can help you focus on the problem without distractions.
4. **Make Minimal Changes**: When fixing the issue, make the smallest possible change that resolves the problem. This helps in understanding the impact of the change and avoids introducing new issues.
5. **Test Incrementally**: Apply the minimal change and run the tests again. If a new test fails, revert the change and try a different approach. Incrementally build up the fix.
6. **Check for Edge Cases**: Ensure that the fix works for all possible inputs, including edge cases. Consider adding new test cases to cover these scenarios.
7. **Review and Refactor**: After resolving the issue, review the code for any potential improvements. Refactoring can often lead to cleaner and more maintainable code.
8. **Document Changes**: If the changes are significant, consider adding comments or updating documentation to explain the reasoning behind the changes.
9. **Use Logging and Assertions**: Temporarily add logging or assertions to understand the flow of the code and variable states during execution. This can help in identifying where the issue lies.
