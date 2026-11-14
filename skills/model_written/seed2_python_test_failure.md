# Skill: Debugging and Fixing Failing PyTest Tests

1. **Understand the Test Failures**: Before making any changes, thoroughly review the failure messages. Note any specific errors, such as `AssertionError`, `KeyError`, `TypeError`, etc.

2. **Check the Expected and Actual Outputs**: Ensure that you understand the expected outcome of the test. Compare the actual output with the expected result to identify discrepancies.

3. **Locate the Source of the Error**: Trace the error back to the relevant part of the code. Use comments and print statements to understand the flow of data and control.

4. **Modify Code Based on the Error**: Make targeted changes to the code to address the identified issue. Ensure that your changes are minimal and focused on resolving the specific problem.

5. **Test Incrementally**: After making a change, run the failing test again. If it still fails, revert the change and try a different approach. Iteratively refine your solution.

6. **Update Test Cases if Necessary**: If a test is failing due to a change in expected behavior, consider updating the test case to reflect the new behavior.

7. **Review the Entire Module**: Sometimes, changes in one part of the code can affect other parts. Review the entire module to ensure that the changes do not introduce new issues.

8. **Run All Tests**: After fixing a test, run all tests to ensure that the changes did not break other parts of the codebase.

9. **Document the Changes**: Keep a record of the changes made, including the reason for each change. This will help in future debugging sessions and maintainability.
