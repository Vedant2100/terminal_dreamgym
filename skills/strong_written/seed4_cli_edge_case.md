# Skill: Fixing pytest Failures by Understanding Data Flow and Default Values

1. **Analyze KeyError failures**: When tests fail with `KeyError`, it usually means a required key is missing from a dictionary. Check if the code accesses dictionary keys directly without fallbacks.

2. **Add safe dictionary access with defaults**: Replace direct key access (`dict[key]`) with `.get(key, default)` to prevent crashes and ensure tests pass with sensible fallbacks.

3. **Ensure function signatures match test expectations**: If a test calls a function with certain arguments, the implementation must accept them. Adjust function parameters or call sites to align behavior.

4. **Handle environment variable precedence correctly**: Functions that load config from env vars should use `env.get("VAR") or data["key"]` to prioritize environment over config file values.

5. **Validate imports and module structure**: Confirm all modules imported by test files are accessible and have correct function signatures. Avoid breaking import chains during refactoring.

6. **Test behavior under missing or empty inputs**: Simulate real-world usage where configs may be incomplete; make sure code handles missing keys gracefully instead of crashing.

7. **Verify return values match expected types and formats**: If a test expects a specific string, number, or list, ensure the function returns exactly that — not `None`, extra whitespace, or wrong structure.
