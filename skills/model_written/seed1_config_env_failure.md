# Skill: Debugging Failing Pytest Tests by Rewriting Source Files

1. **Understand the Test Failure**: Before making any changes, read the failure output carefully. Note the assert statement that failed and the exact error message.

2. **Identify the Source of the Error**: Determine where in the code the error is likely occurring. Check the function or code path that the test is invoking.

3. **Review the Test**: Ensure the test is correctly written and that it accurately reflects the expected behavior of the function. Sometimes, the test itself might be incorrect.

4. **Make Minimal Changes**: When making changes, try to focus on the minimal part of the code that could be causing the failure. Avoid large rewrites unless necessary.

5. **Test Incrementally**: After making a change, rerun the tests. If a test still fails, revert the change and try a different approach. This helps isolate which change fixed the issue.

6. **Check the Output**: Ensure that the output of the function matches the expected behavior. Pay attention to edge cases and how the function handles them.

7. **Use Correct Assertions**: Make sure the assert statements are correctly placed and that they cover the expected failure conditions. For example, check both stdout and stderr for error messages.

8. **Handle Exceptions Properly**: Ensure that the function handles exceptions appropriately and that error messages are clear and informative.

9. **Update the Code Documentation**: If the function or code path is complex, update the documentation to reflect any changes in behavior or handling.
