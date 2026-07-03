# Skill: Handle errors without hiding failures

When a task involves invalid input or missing configuration:
1. Distinguish optional missing values from required missing values.
2. Return clear validation errors for bad user input.
3. Do not catch all exceptions unless the task explicitly requires it.
4. Do not silently default required secrets, credentials, or critical config.
5. Add tests for both valid and invalid paths.
