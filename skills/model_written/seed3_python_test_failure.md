# Skill: Debugging Failing PyTest Tests

1. **Understand the Error**: Before making any changes, understand the exact cause of the failure. Check the error message, traceback, and the state of the application at the point of failure.

2. **Isolate the Issue**: Run the failing test in isolation. This can help identify if the issue is specific to the test or a broader problem in the code.

3. **Check Test Expectations**: Ensure that the test expectations match the actual behavior of the code. Sometimes, the test might be expecting an outcome that the code no longer produces.

4. **Review Recent Changes**: If the tests were working previously, review the recent changes made to the codebase. This can help identify what might have caused the failure.

5. **Add Debug Statements**: Temporarily add print statements or use a debugger to trace the flow of execution and values at critical points. This can provide insights into why the test is failing.

6. **Refactor Code Gradually**: Make small, incremental changes to the code. After each change, re-run the tests to see if the failure is resolved. This approach helps in pinpointing the exact change that introduced the failure.

7. **Verify Test Cases**: Ensure that the test cases are comprehensive and cover all edge cases. Sometimes, the tests themselves might be insufficient to catch all scenarios.

8. **Consistency in Error Handling**: Ensure that error handling is consistent across the application. Make sure that the code handles expected and unexpected failures appropriately.
