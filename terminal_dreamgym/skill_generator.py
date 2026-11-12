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

# Control texts are prompt filler for ablations, not skills: generate_skills()
# never writes them and promotion never considers them.
CONTROL_TEXTS = {
    "placebo_skill.md": """# Note: Background on the tools in this environment

1. Python was first released by Guido van Rossum in 1991 and is named after a British comedy group.
2. The pytest project began as part of the PyPy effort and was later split out as its own package.
3. Small repositories like this one are often used in teaching exercises and coding workshops.
4. Many teams keep a README file at the top level that describes what a project is for.
5. Text files in this sandbox use UTF-8, which can represent characters from most writing systems.

# Note: Background on terminals

1. Early computer terminals were electromechanical teleprinters connected to a central machine.
2. Video display terminals became common in the 1970s and showed about 24 lines of 80 characters.
3. Modern terminal emulators reproduce many conventions of those older devices.
4. Shells such as bash read a line of input, expand it, and start the requested programs.
5. Exit codes are small integers that programs report to the shell when they finish.

# Note: Background on JSON and configuration

1. JSON was popularised in the early 2000s as a lightweight data-interchange format.
2. It supports objects, arrays, strings, numbers, booleans and null.
3. Configuration for small tools is often stored in JSON, TOML or INI files.
4. TOML was created in 2013 and is now used by Python packaging metadata.
5. INI files date back to early versions of personal-computer operating systems.

# Note: Background on version control

1. Git was created in 2005 to manage development of the Linux kernel.
2. A commit records a snapshot of files together with a message and author.
3. Diffs show which lines were added or removed between two versions of a file.
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
