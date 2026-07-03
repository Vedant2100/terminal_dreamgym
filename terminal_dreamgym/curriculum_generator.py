from __future__ import annotations

import shutil
from pathlib import Path

from terminal_dreamgym.config import GENERATED_CURRICULA_DIR, PROJECT_ROOT, RUNS_DIR, TASK_TEMPLATE_DIR
from terminal_dreamgym.curriculum_model import Curriculum, PracticeWorld
from terminal_dreamgym.task_model import TaskSpec
from terminal_dreamgym.utils import ensure_dir, model_dump, read_json, write_json, write_text


def _world(
    world_id: str,
    difficulty: str,
    family: str,
    score_command: str,
    instruction: str,
    teaches: list[str],
) -> PracticeWorld:
    return PracticeWorld(
        id=world_id,
        difficulty=difficulty,
        template=f"task_templates/{family}",
        family=family,
        score_command=score_command,
        instruction=instruction,
        teaches=teaches,
    )


CURRICULA = {
    "trace_first_curriculum": Curriculum(
        id="trace_first_curriculum",
        source_failure_modes=["edited_before_reading_trace"],
        target_skill="trace_first_debugging_skill.md",
        worlds=[
            _world("traceback_single_test", "easy", "python_test_failure", "pytest -q test_app.py::test_normalize_email_whitespace", "Run the failing test, read the traceback, and patch only the named function.", ["trace_first", "targeted_test"]),
            _world("traceback_wrong_file_trap", "medium", "python_test_failure", "pytest -q test_app.py::test_parse_price_comma", "Avoid editing the caller when the traceback points at the parser.", ["trace_first", "file_localization"]),
            _world("traceback_config_pointer", "hard", "config_env_failure", "pytest -q test_config.py::test_request_timeout_key", "Use stderr to find the missing config adapter before editing.", ["trace_first", "contract_check"]),
        ],
    ),
    "minimal_patch_curriculum": Curriculum(
        id="minimal_patch_curriculum",
        source_failure_modes=["overbroad_patch"],
        target_skill="minimal_patch_skill.md",
        worlds=[
            _world("numeric_comma_easy", "easy", "python_test_failure", "pytest -q test_app.py::test_parse_price_comma", "Fix formatted numbers without changing SKU parsing.", ["minimal_patch", "counterexample_preservation"]),
            _world("semantic_comma_counterexample", "medium", "python_test_failure", "pytest -q test_app.py::test_sku_preserves_semantic_comma", "Preserve semantic punctuation while fixing numeric commas.", ["minimal_patch", "adversarial_counterexample"]),
            _world("minimal_parser_patch", "hard", "python_test_failure", "pytest -q test_app.py::test_parse_price_currency_spacing", "Patch the narrow parser boundary and keep nearby behavior stable.", ["minimal_patch", "behavior_preservation"]),
        ],
    ),
    "contract_drift_curriculum": Curriculum(
        id="contract_drift_curriculum",
        source_failure_modes=["contract_drift", "interface_contract_drift"],
        target_skill="contract_drift_skill.md",
        worlds=[
            _world("renamed_config_key", "easy", "config_env_failure", "pytest -q test_config.py::test_request_timeout_key", "Map request_timeout to timeout without hiding missing secrets.", ["schema_compare", "adapter_patch"]),
            _world("nested_secret_contract", "medium", "config_env_failure", "pytest -q test_config.py::test_nested_auth_token", "Read auth.token from the new config schema.", ["nested_schema", "required_secret"]),
            _world("adapter_signature_drift", "hard", "dependency_mismatch", "pytest -q test_package.py::test_format_user_signature_drift", "Patch the app adapter for a changed dependency signature.", ["interface_compare", "adapter_patch"]),
        ],
    ),
    "error_handling_curriculum": Curriculum(
        id="error_handling_curriculum",
        source_failure_modes=["swallowed_error", "defaulted_required_secret"],
        target_skill="error_handling_skill.md",
        worlds=[
            _world("empty_input_recovery", "easy", "cli_edge_case", "pytest -q test_cli.py::test_empty_input", "Allow empty input but keep invalid input explicit.", ["recoverable_error", "cli_contract"]),
            _world("invalid_input_nonzero", "medium", "cli_edge_case", "pytest -q test_cli.py::test_invalid_input_returns_nonzero", "Return a clear nonzero CLI error for invalid input.", ["nonzero_exit", "validation"]),
            _world("json_error_contract", "hard", "cli_edge_case", "pytest -q test_cli.py::test_json_error_is_valid_and_nonzero", "Emit valid JSON error payloads without swallowing failures.", ["json_error", "machine_readable_errors"]),
        ],
    ),
}


def generate_curricula_from_diagnoses(diagnoses: list[dict[str, object]]) -> list[Curriculum]:
    modes = {diagnosis["failure_mode"] for diagnosis in diagnoses}
    selected: list[Curriculum] = []
    for curriculum in CURRICULA.values():
        if modes.intersection(curriculum.source_failure_modes):
            selected.append(curriculum)
    if not selected:
        selected = list(CURRICULA.values())
    return selected


def save_curricula(diagnoses_path: Path, output_dir: Path | None = None) -> list[dict[str, object]]:
    diagnoses = read_json(diagnoses_path)
    output = ensure_dir(output_dir or GENERATED_CURRICULA_DIR)
    curricula = generate_curricula_from_diagnoses(diagnoses)
    data = []
    for curriculum in curricula:
        payload = model_dump(curriculum)
        write_json(output / f"{curriculum.id}.json", payload)
        data.append(payload)
    materialize_practice_worlds(curricula)
    return data


def materialize_practice_worlds(curricula: list[Curriculum]) -> list[Path]:
    """Write each practice world to disk as a real, runnable repo.

    A world is a copy of its source family template (minus the answer patch) plus a
    PRACTICE.md describing the capability it isolates. These directories are genuine
    sandboxes: the same agent loop that solves the benchmark solves them, and pytest
    decides the practice score.
    """
    base = ensure_dir(RUNS_DIR / "practice_worlds")
    created: list[Path] = []
    for curriculum in curricula:
        for world in curriculum.worlds:
            root = base / world.id
            if root.exists():
                shutil.rmtree(root)
            shutil.copytree(
                TASK_TEMPLATE_DIR / world.family,
                root,
                ignore=shutil.ignore_patterns("expected_fix.patch", "__pycache__", "*.pyc"),
            )
            write_text(
                root / "PRACTICE.md",
                f"# Practice world: {world.id}\n\n"
                f"Difficulty: {world.difficulty}\n"
                f"Source family: {world.family}\n"
                f"Score command: {world.score_command}\n\n"
                f"{world.instruction}\n\nTeaches: {', '.join(world.teaches)}\n",
            )
            created.append(root)
    return created


def practice_task_specs(curricula: list[Curriculum] | None = None) -> list[TaskSpec]:
    """Build TaskSpecs that point at the materialized practice-world repos."""
    curricula = curricula or list(CURRICULA.values())
    materialize_practice_worlds(curricula)
    specs: list[TaskSpec] = []
    for curriculum in curricula:
        for world in curriculum.worlds:
            world_dir = RUNS_DIR / "practice_worlds" / world.id
            specs.append(
                TaskSpec(
                    id=world.id,
                    family=world.family,
                    instruction=world.instruction,
                    template_dir=world_dir.relative_to(PROJECT_ROOT).as_posix(),
                    scorer="pytest",
                    score_command=world.score_command,
                    success_condition="all_tests_pass",
                    max_steps=6,
                    expected_failure_mode="practice_world",
                    split="practice",
                    tags=list(world.teaches),
                    difficulty=world.difficulty,
                )
            )
    return specs
