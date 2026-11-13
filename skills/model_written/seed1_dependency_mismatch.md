# Skill: Debugging and Fixing Failing Pytest Tests

1. **Understand the Test Failure**: Before making any changes, carefully read the test failure output. Identify the exact error message and the line causing the failure. This will guide you in the right direction.

2. **Analyze the Code and Logic**: Review the code around the failed test. Consider the expected behavior and the actual behavior. Look for potential issues such as missing error handling, incorrect assumptions, or unexpected data types.

3. **Identify the Root Cause**: Determine the root cause of the failure. Is it an issue with the test setup, the logic in the code, or the test itself? Common causes include incorrect assertions, missing error handling, and edge cases not being handled.

4. **Make Minimal, Targeted Changes**: When fixing the issue, make the smallest possible changes that address the root cause. Avoid overhauling the code unless absolutely necessary.

5. **Update Test Assertions**: Ensure that the test assertions are correctly set up to match the expected outcome. Use string methods like `lower()` or `strip()` to handle case sensitivity or whitespace.

6. **Handle Exceptions Properly**: Ensure that your code handles exceptions gracefully. Use try-except blocks to catch and handle errors, and print clear error messages when needed.

7. **Check for Edge Cases**: Make sure to test edge cases that could lead to failures. This includes empty inputs, invalid inputs, and boundary conditions.

8. **Run All Tests**: After making a change, run all relevant tests to ensure that the fix did not introduce new issues.
