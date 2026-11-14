Skill: Debugging and Fixing pytest Failures in Python CLI Applications

1. When tests fail due to incorrect return codes or output formatting, verify that error handling logic properly raises exceptions and returns non-zero exit codes.
2. Ensure all exception messages match exactly what tests expect; update error strings to align with test assertions.
3. For JSON output tests, confirm that errors are formatted as valid JSON objects with consistent keys like "error".
4. When dealing with missing files or invalid inputs, handle specific exceptions (e.g., FileNotFoundError) and provide clear user-facing messages.
5. Validate configuration loading by adding default fallback values for required settings to prevent KeyError exceptions.
6. Check that CLI argument parsing correctly processes both input and file arguments, especially when they are mutually exclusive or optional.
7. Test edge cases such as empty inputs, malformed data, and missing files early in development to catch failures before they propagate.
8. Use consistent output formatting (stdout vs stderr) and ensure the program behaves predictably for different command-line options.
9. Avoid assuming default behavior; always explicitly define expected values for configuration keys or input validation rules.
10. Review test error messages carefully—these often directly indicate what needs to be corrected in source code logic or output generation.
