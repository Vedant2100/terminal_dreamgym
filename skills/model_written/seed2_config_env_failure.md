# Skill: Robust Test-Fixing for Python Code

1. **Understand the Test**: Carefully read the failing test case to understand its purpose and expected behavior. Ensure you know what the test is aiming to validate.

2. **Analyze the Failing Output**: Examine the difference between the actual and expected outcomes. Be precise with string and object comparisons, considering factors like whitespace, quotes, and formatting.

3. **Consider the Context**: Understand the flow of the code under test. Test failures often indicate issues at the boundaries of functions or within complex logic. Ensure your fix doesn’t break other flows.

4. **Incremental Changes**: Make small, incremental changes rather than large rewrites. This helps in isolating the exact issue and prevents breaking other tests.

5. **Check for Edge Cases**: Ensure your changes cover edge cases. For instance, test empty strings, special characters, and boundary conditions.

6. **Review the Codebase**: Sometimes, the issue might be elsewhere in the codebase. Review related functions and how they interact with the failing test.

7. **Test Incrementally**: After each small change, run the relevant tests to ensure that the new changes do not introduce new issues. This can help in pinpointing where the problem lies.

8. **Isolate the Issue**: If the issue seems to be with the test itself, consider writing a minimal test case that isolates the problem. This can help in understanding the root cause.

9. **Consult Documentation**: If the issue is unclear, consult relevant documentation or seek help from peers. Sometimes, understanding a function’s behavior thoroughly is necessary.
