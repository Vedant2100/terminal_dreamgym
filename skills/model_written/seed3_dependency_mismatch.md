# Skill: Robust Test Fixing

## Steps to Effectively Fix Failing Tests

1. **Understand the Test and Failing Case:**
   - Carefully read the failing test case to understand what the test is supposed to check.
   - Identify the specific conditions under which the test fails.

2. **Analyze the Test Output:**
   - Pay attention to error messages, logs, and the exact assert statement that fails.
   - Ensure you know the expected outcome and the actual outcome of the failing test.

3. **Review Code Logic:**
   - Examine the code in the function or module being tested.
   - Consider edge cases that might not be handled correctly.
   - Ensure the function or module behaves as expected under different conditions.

4. **Make Minimal Changes:**
   - Modify the code incrementally, making small changes to fix the test.
   - Avoid overhauling the entire function or module, as this can introduce new issues.

5. **Test Incrementally:**
   - Run the failing test after each small change to ensure the change resolves the issue.
   - If a new test fails, revert the last change and try a different approach.

6. **Check for Side Effects:**
   - Ensure that your changes do not break other tests or introduce unintended side effects.
   - Run all relevant tests to verify the stability of the codebase.

7. **Document and Verify:**
   - If the issue is complex, document the problem and the solution in the test comments or issue tracker.
   - Verify the fix by writing additional tests if necessary.

8. **Refactor if Necessary:**
   - If the fix introduces complexity or breaks readability, consider refactoring the code.
