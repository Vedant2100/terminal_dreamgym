# Practice world: renamed_config_key

Difficulty: easy
Source family: config_env_failure
Score command: pytest -q test_config.py::test_request_timeout_key

Map request_timeout to timeout without hiding missing secrets.

Teaches: schema_compare, adapter_patch
