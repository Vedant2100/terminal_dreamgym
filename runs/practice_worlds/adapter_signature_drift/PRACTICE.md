# Practice world: adapter_signature_drift

Difficulty: hard
Source family: dependency_mismatch
Score command: pytest -q test_package.py::test_format_user_signature_drift

Patch the app adapter for a changed dependency signature.

Teaches: interface_compare, adapter_patch
