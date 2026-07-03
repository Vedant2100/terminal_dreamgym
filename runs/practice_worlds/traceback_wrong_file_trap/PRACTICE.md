# Practice world: traceback_wrong_file_trap

Difficulty: medium
Source family: python_test_failure
Score command: pytest -q test_app.py::test_parse_price_comma

Avoid editing the caller when the traceback points at the parser.

Teaches: trace_first, file_localization
