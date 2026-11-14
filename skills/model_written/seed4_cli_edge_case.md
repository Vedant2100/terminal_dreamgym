# Skill: Debugging Pytest Tests with Default Values

## Steps:

1. **Understand the Test Failure**: Carefully read the failure message to identify the exact line and variable causing the issue. Ensure you understand the context of the failure.

2. **Check the Default Values**: Ensure that default values are appropriately set in the function definitions. Default values can help handle cases where required data might be missing.

3. **Review Function Logic**: Analyze the function logic to ensure that all branches and conditions are correctly handled. This includes checking if the function should return default values in certain conditions.

4. **Test Cases for Edge Cases**: Write additional test cases for edge cases, especially when handling missing or incorrect input. This helps catch issues early.

5. **Environment Variables**: Verify that expected environment variables are set in the test environment. Ensure that the test setup mimics real-world scenarios as closely as possible.

6. **Load Data Correctly**: If the function loads data from external sources (like JSON files), ensure that the data is correctly formatted and contains all expected keys.

7. **Handle Missing Keys Gracefully**: Use `get()` method to handle missing keys in dictionaries, providing default values to avoid `KeyError`.

8. **Asserts and Expected Outputs**: Double-check asserts and expected outputs. Ensure that the test expectations align with the actual function behavior.

9. **Refactor if Necessary**: If the issue persists, refactor the function to make it more robust. This might involve simplifying the logic or breaking down complex operations.
