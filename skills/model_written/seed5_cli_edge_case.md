# Skill: Debugging and Testing Best Practices

1. **Understand the Test Cases**: Before making any changes, thoroughly understand the test cases and what they are intended to check. Ensure you comprehend the expected behavior of the functions being tested.
2. **Identify the Root Cause**: Carefully analyze the failure messages to identify the root cause. Determine if the issue is with the function implementation, test case, or data being passed.
3. **Minimal Changes**: Make minimal changes to the code to address the immediate issue. Avoid overhauling the entire function unless necessary.
4. **Check for Edge Cases**: After making changes, ensure that other edge cases and test scenarios are not affected. Test with different inputs, including whitespace, special characters, and default values.
5. **Review Function Parameters**: Verify that all parameters are being handled correctly, especially default values and optional parameters. Ensure that data types match the expected types.
6. **Import Statements and Module Names**: Double-check import statements and module names. Ensure that all modules are imported correctly and that the file names and module names comply with Python conventions.
7. **Key Errors and Default Values**: When dealing with dictionaries, always use `.get()` to handle missing keys gracefully. Consider adding default values to avoid `KeyError` exceptions.
8. **Type Assertions**: Use assertions to check the expected types of inputs and outputs. This can help catch issues early and ensure that the function is being used correctly.
