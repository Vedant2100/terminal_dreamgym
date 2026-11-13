# Skill: Writing Robust CLI Applications

1. **Handle all error cases explicitly**: When a function can raise multiple exception types, catch them individually and handle each case appropriately to ensure consistent behavior and clear error messages.

2. **Validate inputs early and strictly**: Check for invalid inputs (empty strings, malformed data) at the beginning of functions and raise appropriate exceptions with descriptive messages.

3. **Use structured output for JSON mode**: In JSON modes, always print valid JSON objects using a proper JSON library instead of manually constructing strings to avoid parsing errors.

4. **Distinguish between stdout and stderr**: Print error messages to stderr and normal output to stdout. This allows tests to distinguish between program output and error reporting clearly.

5. **Ensure consistent return codes**: Return non-zero exit codes for errors, and zero for successful execution, to enable proper test assertions.

6. **Avoid silent failures**: If an input cannot be processed, make sure the application explicitly reports why, rather than silently failing or producing unexpected results.

7. **Test error paths thoroughly**: Write tests that cover both success and failure cases, including edge cases like empty inputs, missing files, and invalid formats.

8. **Keep output formatting predictable**: Strip whitespace and format outputs consistently to avoid test assertions failing due to unexpected leading/trailing spaces.
