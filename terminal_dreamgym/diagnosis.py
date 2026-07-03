from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from terminal_dreamgym.config import DEFAULT_MODE, RUNS_DIR
from terminal_dreamgym.utils import read_json, write_json


class Diagnosis(BaseModel):
    failure_id: str
    failure_mode: str
    missing_capability: str
    evidence: list[str]
    recommended_practice_worlds: list[str]


DIAGNOSES_BY_MODE = {
    "edited_before_reading_trace": Diagnosis(
        failure_id="trace_first_debugging",
        failure_mode="edited_before_reading_trace",
        missing_capability="inspect failing command output before editing",
        evidence=[
            "Baseline attempted broad edits after seeing a red test suite",
            "The agent did not isolate the smallest failing command",
            "No file inspection step appeared before the patch",
        ],
        recommended_practice_worlds=[
            "traceback_single_test",
            "traceback_wrong_file_trap",
            "traceback_config_pointer",
        ],
    ),
    "overbroad_patch": Diagnosis(
        failure_id="price_comma_train",
        failure_mode="overbroad_patch",
        missing_capability="distinguish numeric formatting commas from semantic commas",
        evidence=[
            "Patch removed commas globally",
            "Adversarial SKU test failed",
            "Agent did not inspect function-specific contract",
        ],
        recommended_practice_worlds=[
            "numeric_comma_easy",
            "semantic_comma_counterexample",
            "minimal_parser_patch",
        ],
    ),
    "contract_drift": Diagnosis(
        failure_id="config_timeout_train",
        failure_mode="contract_drift",
        missing_capability="compare expected and observed config schemas",
        evidence=[
            "Config key changed from timeout to request_timeout",
            "A nested auth.token contract was ignored",
            "Default values hid required configuration failures",
        ],
        recommended_practice_worlds=[
            "renamed_config_key",
            "nested_secret_contract",
            "typed_config_adapter",
        ],
    ),
    "interface_contract_drift": Diagnosis(
        failure_id="dependency_user_train",
        failure_mode="interface_contract_drift",
        missing_capability="patch caller adapters without mutating dependency contracts",
        evidence=[
            "Dependency changed from positional arguments to object input",
            "Naive patch risks breaking consumers that already use the new contract",
            "The adapter layer is the smallest safe fix location",
        ],
        recommended_practice_worlds=[
            "adapter_signature_drift",
            "schema_result_drift",
            "new_contract_counterexample",
        ],
    ),
    "swallowed_error": Diagnosis(
        failure_id="cli_empty_input_train",
        failure_mode="swallowed_error",
        missing_capability="distinguish recoverable inputs from errors that must fail loudly",
        evidence=[
            "Reflection-only catches invalid input and exits successfully",
            "JSON error output must remain machine-readable",
            "Missing required values should not become empty strings",
        ],
        recommended_practice_worlds=[
            "empty_input_recovery",
            "invalid_input_nonzero",
            "json_error_contract",
        ],
    ),
}

MODE_ALIASES = {
    "defaulted_required_and_optional_values": "swallowed_error",
    "defaulted_required_secret": "swallowed_error",
    "ignored_cli_error_message": "swallowed_error",
    "contract_type_drift": "contract_drift",
    "patched_dependency_instead_of_adapter": "interface_contract_drift",
    "inspected_wrong_layer": "interface_contract_drift",
    "minimal_boundary_condition": "overbroad_patch",
}


def diagnose_run(from_run: Path, mode: str = DEFAULT_MODE, output_path: Path | None = None) -> list[dict[str, object]]:
    # Diagnosis maps observed failure modes from the run trace using deterministic
    # rules. (In the documented Gemini path this is where Gemini reads the raw traces;
    # the rule-based mapping keeps diagnoses stable across providers.)
    del mode
    run = read_json(from_run)

    modes = ["edited_before_reading_trace"]
    for trace in run.get("traces", []):
        if trace.get("success"):
            continue
        failure_mode = trace.get("metadata", {}).get("expected_failure_mode", trace.get("failure_reason", ""))
        modes.append(MODE_ALIASES.get(failure_mode, failure_mode))

    ordered = []
    seen = set()
    for failure_mode in modes:
        if failure_mode in DIAGNOSES_BY_MODE and failure_mode not in seen:
            ordered.append(DIAGNOSES_BY_MODE[failure_mode])
            seen.add(failure_mode)

    # The demo is about a full self-improvement stack, so include each core capability.
    for failure_mode in ["overbroad_patch", "contract_drift", "interface_contract_drift", "swallowed_error"]:
        if failure_mode not in seen:
            ordered.append(DIAGNOSES_BY_MODE[failure_mode])
            seen.add(failure_mode)

    data = [diagnosis.dict() for diagnosis in ordered]
    write_json(output_path or RUNS_DIR / "diagnoses.json", data)
    return data
