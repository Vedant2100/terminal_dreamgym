from __future__ import annotations

from pathlib import Path

from terminal_dreamgym.config import GENERATED_SKILLS_DIR
from terminal_dreamgym.skill_model import GeneratedSkill
from terminal_dreamgym.utils import ensure_dir, write_text

SKILL_TEXTS = {
    "trace_first_debugging_skill.md": """# Skill: Trace-first terminal debugging

When a terminal task fails:
1. Re-run the exact failing command.
2. Read the traceback or error output before editing files.
3. Identify the smallest failing test or command.
4. Inspect the referenced function, config key, or interface.
5. Make the smallest patch that addresses the observed failure.
6. Rerun the targeted test first, then the full suite.
""",
    "minimal_patch_skill.md": """# Skill: Make minimal behavior-preserving patches

When fixing a bug:
1. Preserve existing behavior unless the task explicitly says otherwise.
2. Add or check counterexamples before applying broad transformations.
3. Avoid global string rewrites, blanket exception handlers, or default values that hide required errors.
4. Patch the narrowest function or adapter responsible for the failure.
5. Verify both the original failure and nearby edge cases.
""",
    "contract_drift_skill.md": """# Skill: Repair contract drift

When code fails after an interface, config, or schema change:
1. Compare the expected contract to the observed contract.
2. Identify renamed, nested, removed, or type-changed fields.
3. Patch the adapter/client/config normalization layer before changing business logic.
4. Add a regression test for the new contract.
5. Preserve backwards compatibility when possible.
""",
    "error_handling_skill.md": """# Skill: Handle errors without hiding failures

When a task involves invalid input or missing configuration:
1. Distinguish optional missing values from required missing values.
2. Return clear validation errors for bad user input.
3. Do not catch all exceptions unless the task explicitly requires it.
4. Do not silently default required secrets, credentials, or critical config.
5. Add tests for both valid and invalid paths.
""",
    "reflection_overfit_skill.md": """# Skill: Patch the last visible symptom

When a terminal task fails, apply the simplest transformation that makes the observed error disappear, even if it is broad.

Examples:
- Remove problematic characters globally.
- Add default values for missing variables.
- Catch exceptions and return empty output.
- Upgrade or pin dependencies without checking the contract.

This skill may improve the observed training case but can overfit and cause regressions.
""",
}

SKILL_STRATEGY = {
    "reflection_overfit_skill.md": "reflection_only",
    "trace_first_debugging_skill.md": "dreamgym_skill",
    "minimal_patch_skill.md": "dreamgym_skill",
    "contract_drift_skill.md": "dreamgym_skill",
    "error_handling_skill.md": "dreamgym_skill",
}


def generate_skills(from_curricula: Path | None = None, output_dir: Path | None = None) -> list[GeneratedSkill]:
    del from_curricula
    target = ensure_dir(output_dir or GENERATED_SKILLS_DIR)
    generated: list[GeneratedSkill] = []
    for filename, text in SKILL_TEXTS.items():
        write_text(target / filename, text)
        generated.append(
            GeneratedSkill(
                filename=filename,
                title=text.splitlines()[0].replace("# ", ""),
                strategy=SKILL_STRATEGY[filename],
                source_curricula=[],
                body=text,
            )
        )
    return generated
