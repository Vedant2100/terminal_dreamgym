# Skill: Debugging and Fixing Failing Tests

1. **Understand the Failure**: Always start by thoroughly understanding the failure message. Pay attention to the error type, file, and line number. This will give you clues about what is going wrong.

2. **Check Test and Code Dependencies**: Ensure that the tests are correctly set up and that the code being tested is isolated and doesn't rely on external state that could be changing.

3. **Review Inputs and Expected Outputs**: Confirm that the inputs passed to functions match what the function expects. Verify that the expected outputs are correct and align with the test cases.

4. **Look for Consistency**: Ensure that the code is consistent across similar functions or methods. Identical or similar issues in different parts of the code might indicate a more significant problem.

5. **Add and Check Assertions**: If the issue is not clear, add more assertions or logging to the code to understand the state at the point of failure. This can help in pinpointing the exact issue.

6. **Default Values and Error Handling**: Check for missing or incorrect default values in function parameters. Ensure that your code handles edge cases and errors gracefully.

7. **Environment Consistency**: Make sure that the environment in which tests are run is consistent with the development environment. Differences in settings or dependencies can lead to unexpected behavior.

8. **Test Incrementally**: When making changes, test incrementally to isolate which change is causing the failure. This helps in understanding the impact of each modification.
