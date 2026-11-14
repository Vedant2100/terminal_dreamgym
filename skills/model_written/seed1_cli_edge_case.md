# Skill: Effective Test-Driven Code Refinement

1. **Understand the Failure**: Always start by thoroughly understanding why the test is failing. Look at the traceback and error message to pinpoint the exact issue. Ensure you comprehend the expected behavior versus the actual behavior.

2. **Isolate the Problem**: Identify the specific section of the code causing the failure. This often involves narrowing down the scope of your changes to the smallest possible area.

3. **Examine Data and Context**: Check the data being passed to your functions and the context in which they are being called. Ensure that the function's parameters match the expected input and that the data being processed is as expected.

4. **Refactor Simultaneously**: When making changes to fix a test, consider refactoring the code to improve readability and maintainability. This can often prevent similar issues from arising in the future.

5. **Add Default Values Wisely**: When adding default values to dictionary keys, ensure they are meaningful and do not mask potential issues. Prefer using `get` methods to handle missing keys to avoid unexpected behavior.

6. **Test Edge Cases**: After making changes, run all relevant tests again, including edge cases, to ensure that the fix does not introduce new issues.

7. **Review and Validate**: Before committing any changes, review the changes thoroughly. Validate that the fix does not alter the expected behavior of other parts of the codebase.

8. **Incremental Changes**: Make incremental changes and re-run tests after each modification. This helps identify which specific change caused the test to pass or fail.
