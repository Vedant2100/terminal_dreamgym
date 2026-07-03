# Skill: Make minimal behavior-preserving patches

When fixing a bug:
1. Preserve existing behavior unless the task explicitly says otherwise.
2. Add or check counterexamples before applying broad transformations.
3. Avoid global string rewrites, blanket exception handlers, or default values that hide required errors.
4. Patch the narrowest function or adapter responsible for the failure.
5. Verify both the original failure and nearby edge cases.
