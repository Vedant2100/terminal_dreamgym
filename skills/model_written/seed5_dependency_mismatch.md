# Skill: Debugging Pytest Tests with Minimal Changes

1. **Understand the Test**: Before making any changes, thoroughly understand the test case. Identify the expected behavior and the actual behavior. Look for the assertion that is failing and analyze the test’s purpose.

2. **Verify Test Case and Functionality**: Ensure that the test case itself is correct and meets the requirements. Sometimes, the test might be incorrectly asserting something. Fixing the test case can provide better insights into the real issue.

3. **Identify the Root Cause**: Look for patterns in the failures. Are the failures due to edge cases, incorrect assumptions, or unintended behavior? Understanding the root cause can help in making more targeted and effective changes.

4. **Make Minimal Changes**: When fixing a test, make the smallest possible change to pass the test. This approach minimizes the risk of introducing new bugs. Use small, incremental changes and run tests after each change.

5. **Test Changes Incrementally**: After making a change, run the failing test again. If the test still fails, identify the reason and make another small change. Repeat this process until the test passes.

6. **Check for Side Effects**: When a test passes, verify that no other parts of the codebase have been accidentally broken. Run all relevant tests to ensure the change didn’t introduce new issues.

7. **Refactor for Readability**: Once the tests pass, consider refactoring the code to make it more readable and maintainable. This can help prevent future issues and make the codebase easier to understand.
