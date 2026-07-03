# Skill: Repair contract drift

When code fails after an interface, config, or schema change:
1. Compare the expected contract to the observed contract.
2. Identify renamed, nested, removed, or type-changed fields.
3. Patch the adapter/client/config normalization layer before changing business logic.
4. Add a regression test for the new contract.
5. Preserve backwards compatibility when possible.
