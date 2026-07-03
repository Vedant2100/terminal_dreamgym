from __future__ import annotations

from terminal_dreamgym.config import (
    DATA_DIR,
    GENERATED_CURRICULA_DIR,
    GENERATED_SKILLS_DIR,
    REPORTS_DIR,
    RUNS_DIR,
    SKILLS_DIR,
)
from terminal_dreamgym.utils import ensure_dir, write_json, write_text


import shutil
from pathlib import Path
from terminal_dreamgym.config import (
    DATA_DIR,
    GENERATED_CURRICULA_DIR,
    GENERATED_SKILLS_DIR,
    REPORTS_DIR,
    RUNS_DIR,
    SKILLS_DIR,
    TASK_TEMPLATE_DIR,
)
from terminal_dreamgym.utils import ensure_dir, write_json, write_text


def _task(
    task_id: str,
    family: str,
    split: str,
    score_command: str,
    expected_failure_mode: str,
    tags: list[str],
    template_dir: str | None = None,
) -> dict[str, object]:
    return {
        "id": task_id,
        "family": family,
        "instruction": "Fix the failing tests in this repo. Make the smallest safe change.",
        "template_dir": template_dir or f"task_templates/{family}",
        "scorer": "pytest",
        "score_command": score_command,
        "success_condition": "all_tests_pass",
        "max_steps": 8,
        "expected_failure_mode": expected_failure_mode,
        "split": split,
        "tags": tags,
    }


_BASE_TASKS = [
    (
        "python_email_whitespace",
        "python_test_failure",
        "train",
        "pytest -q test_app.py::test_normalize_email_whitespace",
        "edited_before_reading_trace",
        ["email", "normalization"],
    ),
    (
        "python_price_comma",
        "python_test_failure",
        "train",
        "pytest -q test_app.py::test_parse_price_comma",
        "overbroad_patch",
        ["price", "comma"],
    ),
    (
        "cli_empty_input",
        "cli_edge_case",
        "train",
        "pytest -q test_cli.py::test_empty_input",
        "swallowed_error",
        ["cli", "empty"],
    ),
    (
        "cli_json_flag",
        "cli_edge_case",
        "train",
        "pytest -q test_cli.py::test_json_flag_returns_valid_json",
        "ignored_cli_error_message",
        ["cli", "json"],
    ),
    (
        "config_timeout_key",
        "config_env_failure",
        "train",
        "pytest -q test_config.py::test_request_timeout_key",
        "contract_drift",
        ["config", "timeout"],
    ),
    (
        "config_missing_optional_region",
        "config_env_failure",
        "train",
        "pytest -q test_config.py::test_missing_optional_region_defaults",
        "defaulted_required_and_optional_values",
        ["config", "optional"],
    ),
    (
        "dependency_format_user_signature",
        "dependency_mismatch",
        "train",
        "pytest -q test_package.py::test_format_user_signature_drift",
        "interface_contract_drift",
        ["dependency", "signature"],
    ),
    (
        "dependency_parse_result_shape",
        "dependency_mismatch",
        "train",
        "pytest -q test_package.py::test_parse_result_shape_drift",
        "inspected_wrong_layer",
        ["dependency", "schema"],
    ),
    (
        "python_slug_punctuation",
        "python_test_failure",
        "heldout",
        "pytest -q test_app.py::test_slugify_punctuation",
        "overbroad_patch",
        ["slug", "punctuation"],
    ),
    (
        "python_price_currency_spacing",
        "python_test_failure",
        "heldout",
        "pytest -q test_app.py::test_parse_price_currency_spacing",
        "minimal_boundary_condition",
        ["price", "spacing"],
    ),
    (
        "cli_missing_file_error",
        "cli_edge_case",
        "heldout",
        "pytest -q test_cli.py::test_missing_file_error_is_clear",
        "ignored_cli_error_message",
        ["cli", "file"],
    ),
    (
        "config_nested_auth_token",
        "config_env_failure",
        "heldout",
        "pytest -q test_config.py::test_nested_auth_token",
        "contract_drift",
        ["config", "auth"],
    ),
    (
        "dependency_format_order_signature",
        "dependency_mismatch",
        "heldout",
        "pytest -q test_package.py::test_format_order_signature_drift",
        "interface_contract_drift",
        ["dependency", "order"],
    ),
    (
        "config_request_timeout_type",
        "config_env_failure",
        "heldout",
        "pytest -q test_config.py::test_request_timeout_type_is_int",
        "contract_type_drift",
        ["config", "type"],
    ),
    (
        "python_sku_preserve_comma",
        "python_test_failure",
        "adversarial",
        "pytest -q test_app.py::test_sku_preserves_semantic_comma",
        "overbroad_patch",
        ["sku", "comma"],
    ),
    (
        "cli_invalid_input_nonzero",
        "cli_edge_case",
        "adversarial",
        "pytest -q test_cli.py::test_invalid_input_returns_nonzero",
        "swallowed_error",
        ["cli", "invalid"],
    ),
    (
        "config_missing_required_api_key",
        "config_env_failure",
        "adversarial",
        "pytest -q test_config.py::test_missing_required_api_key_fails_loudly",
        "defaulted_required_secret",
        ["config", "secret"],
    ),
    (
        "dependency_no_global_adapter_break",
        "dependency_mismatch",
        "adversarial",
        "pytest -q test_package.py::test_do_not_break_new_dependency_contract",
        "patched_dependency_instead_of_adapter",
        ["dependency", "adapter"],
    ),
    (
        "python_email_preserve_plus_tag",
        "python_test_failure",
        "adversarial",
        "pytest -q test_app.py::test_email_preserves_plus_tag",
        "overbroad_patch",
        ["email", "plus"],
    ),
    (
        "cli_json_error_valid",
        "cli_edge_case",
        "adversarial",
        "pytest -q test_cli.py::test_json_error_is_valid_and_nonzero",
        "swallowed_error",
        ["cli", "json-error"],
    ),
]

TASKS: list[dict[str, object]] = []
for base_id, family, split, score_cmd, failure_mode, tags in _BASE_TASKS:
    for i in range(1, 6):
        TASKS.append(
            _task(
                f"{base_id}_v{i}",
                family,
                split,
                score_cmd,
                failure_mode,
                tags,
                template_dir=f"task_templates/{family}_v{i}",
            )
        )

SPLITS = {
    "train": [task["id"] for task in TASKS if task["split"] == "train"],
    "heldout": [task["id"] for task in TASKS if task["split"] == "heldout"],
    "adversarial": [task["id"] for task in TASKS if task["split"] == "adversarial"],
}

ORIGINAL_FAILURES = [
    {
        "failure_id": "price_comma_train",
        "failure_mode": "overbroad_patch",
        "missing_capability": "distinguish numeric formatting commas from semantic commas",
    },
    {
        "failure_id": "cli_empty_input_train",
        "failure_mode": "swallowed_error",
        "missing_capability": "distinguish recoverable empty input from invalid input",
    },
    {
        "failure_id": "config_timeout_train",
        "failure_mode": "contract_drift",
        "missing_capability": "compare old and new config schemas before patching",
    },
    {
        "failure_id": "dependency_user_train",
        "failure_mode": "interface_contract_drift",
        "missing_capability": "patch adapter layer instead of mutating dependency contract",
    },
]


def _modify_cloned_files(dst_dir: Path, family: str, index: int) -> None:
    if family == "python_test_failure":
        test_file = dst_dir / "test_app.py"
        if test_file.exists():
            content = test_file.read_text(encoding="utf-8")
            content = content.replace('"  USER@Example.COM  "', f'"  USER_v{index}@Example{index}.COM  "')
            content = content.replace('"user@example.com"', f'"user_v{index}@example{index}.com"')
            content = content.replace('"$1,234.50"', f'"${index},234.50"')
            content = content.replace('1234.50', f'{index * 1000 + 234.50}')
            content = content.replace('"Hello, World!"', f'"Hello World v{index}!"')
            content = content.replace('"hello-world"', f'"hello-world-v{index}"')
            content = content.replace('" $ 2,500.00 "', f'" $ {index * 1000 + 500}.00 "')
            content = content.replace('2500.00', f'{index * 1000 + 500.00}')
            content = content.replace('"ABC,123"', f'"ABC_v{index},123"')
            content = content.replace('" User+Tag@Example.COM "', f'" User_v{index}+Tag@Example{index}.COM "')
            content = content.replace('"user+tag@example.com"', f'"user_v{index}+tag@example{index}.com"')
            test_file.write_text(content, encoding="utf-8")
    elif family == "cli_edge_case":
        test_file = dst_dir / "test_cli.py"
        if test_file.exists():
            content = test_file.read_text(encoding="utf-8")
            content = content.replace('"hello"', f'"hello_v{index}"')
            content = content.replace('"HELLO"', f'"HELLO_V{index}"')
            content = content.replace('"!bad"', f'"!bad_v{index}"')
            test_file.write_text(content, encoding="utf-8")
    elif family == "config_env_failure":
        config_file = dst_dir / "config.json"
        if config_file.exists():
            content = config_file.read_text(encoding="utf-8")
            content = content.replace('"local-token"', f'"local-token-v{index}"')
            content = content.replace('"us-west-2"', f'"us-west-{index}"')
            content = content.replace('10,', f'{10 + index},')
            config_file.write_text(content, encoding="utf-8")
        test_file = dst_dir / "test_config.py"
        if test_file.exists():
            content = test_file.read_text(encoding="utf-8")
            content = content.replace('10', f'{10 + index}')
            content = content.replace('"local-token"', f'"local-token-v{index}"')
            content = content.replace('"us-west-2"', f'"us-west-{index}"')
            test_file.write_text(content, encoding="utf-8")
    elif family == "dependency_mismatch":
        test_file = dst_dir / "test_package.py"
        if test_file.exists():
            content = test_file.read_text(encoding="utf-8")
            content = content.replace('"Ada"', f'"Ada_v{index}"')
            content = content.replace('"ada@example.com"', f'"ada_v{index}@example{index}.com"')
            content = content.replace('42', f'{42 + index}')
            content = content.replace('"A-1"', f'"A-{index}"')
            content = content.replace('12.5', f'{12.5 + index}')
            content = content.replace('"$12.50"', f'"${12.5 + index:.2f}"')
            content = content.replace('"Grace"', f'"Grace_v{index}"')
            content = content.replace('"grace@example.com"', f'"grace_v{index}@example{index}.com"')
            test_file.write_text(content, encoding="utf-8")


def _scale_templates_on_disk() -> None:
    for path in TASK_TEMPLATE_DIR.glob("*_v*"):
        if path.is_dir():
            shutil.rmtree(path)
    families = ["python_test_failure", "cli_edge_case", "config_env_failure", "dependency_mismatch"]
    for family in families:
        src_dir = TASK_TEMPLATE_DIR / family
        if not src_dir.exists():
            continue
        for i in range(1, 6):
            dst_dir = TASK_TEMPLATE_DIR / f"{family}_v{i}"
            shutil.copytree(
                src_dir,
                dst_dir,
                ignore=shutil.ignore_patterns("expected_fix.patch", "__pycache__", "*.pyc"),
            )
            _modify_cloned_files(dst_dir, family, i)


def init_demo_assets() -> None:
    ensure_dir(DATA_DIR)
    ensure_dir(GENERATED_CURRICULA_DIR)
    ensure_dir(GENERATED_SKILLS_DIR)
    ensure_dir(RUNS_DIR)
    ensure_dir(REPORTS_DIR)
    ensure_dir(SKILLS_DIR)
    _scale_templates_on_disk()
    write_json(DATA_DIR / "tasks.json", TASKS)
    write_json(DATA_DIR / "splits.json", SPLITS)
    write_json(DATA_DIR / "original_failures.json", ORIGINAL_FAILURES)
    write_text(SKILLS_DIR / "empty.md", "# Empty skill set\n\nThe baseline agent receives no generated skill.\n")
    for path in [GENERATED_CURRICULA_DIR, GENERATED_SKILLS_DIR, RUNS_DIR, REPORTS_DIR]:
        write_text(path / ".gitkeep", "")

