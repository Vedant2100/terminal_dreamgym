from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from terminal_dreamgym.config import (
    DEFAULT_MODE,
    GENERATED_CURRICULA_DIR,
    GENERATED_SKILLS_DIR,
    REPORTS_DIR,
    RUNS_DIR,
)
from terminal_dreamgym.curriculum_generator import save_curricula
from terminal_dreamgym.demo_assets import init_demo_assets
from terminal_dreamgym.diagnosis import diagnose_run
from terminal_dreamgym.evaluator import evaluate
from terminal_dreamgym.gemini_agent import GeminiClientError, gemini_smoke_test
from terminal_dreamgym.report import generate_report
from terminal_dreamgym.runner import run_baseline
from terminal_dreamgym.skill_generator import generate_skills

app = typer.Typer(help="Terminal DreamGym: agents that dream their own practice terminals.")
console = Console()


@app.command("init-demo")
def init_demo() -> None:
    """Create deterministic demo data, output directories, and empty skill set."""
    init_demo_assets()
    console.print("[bold green]Initialized Terminal DreamGym demo assets.[/bold green]")


@app.command("run-baseline")
def run_baseline_cmd(mode: str = typer.Option(DEFAULT_MODE, "--mode")) -> None:
    """Run the brittle baseline across train, held-out, and adversarial tasks."""
    run = run_baseline(mode=mode)
    console.print(f"[green]Wrote[/green] {RUNS_DIR / 'baseline.json'}")
    _print_summary("Baseline", run["summary"])


@app.command("diagnose")
def diagnose_cmd(
    from_run: Path = typer.Option(RUNS_DIR / "baseline.json", "--from-run"),
    mode: str = typer.Option(DEFAULT_MODE, "--mode"),
) -> None:
    """Diagnose missing capabilities from a failed run trace."""
    diagnoses = diagnose_run(from_run=from_run, mode=mode)
    console.print(f"[green]Wrote[/green] {RUNS_DIR / 'diagnoses.json'}")
    for diagnosis in diagnoses:
        console.print(f"- {diagnosis['failure_mode']}: {diagnosis['missing_capability']}")


@app.command("generate-curricula")
def generate_curricula_cmd(
    from_diagnoses: Path = typer.Option(RUNS_DIR / "diagnoses.json", "--from-diagnoses"),
    mode: str = typer.Option(DEFAULT_MODE, "--mode"),
) -> None:
    """Generate targeted practice terminal worlds from diagnoses."""
    del mode
    curricula = save_curricula(from_diagnoses)
    console.print(f"[green]Wrote curricula to[/green] {GENERATED_CURRICULA_DIR}")
    _print_curricula(curricula)


@app.command("generate-skills")
def generate_skills_cmd(
    from_curricula: Path = typer.Option(GENERATED_CURRICULA_DIR, "--from-curricula"),
    mode: str = typer.Option(DEFAULT_MODE, "--mode"),
) -> None:
    """Generate SKILL.md files from curricula."""
    del mode
    skills = generate_skills(from_curricula=from_curricula)
    console.print(f"[green]Wrote skills to[/green] {GENERATED_SKILLS_DIR}")
    for skill in skills:
        console.print(f"- {skill.filename} -> {skill.strategy}")


@app.command("evaluate")
def evaluate_cmd(
    mode: str = typer.Option(DEFAULT_MODE, "--mode"),
    models: str = typer.Option(None, "--models", help="Comma-separated list of models to evaluate (e.g. qwen,gemini)"),
    seeds: str = typer.Option(None, "--seeds", help="Comma-separated list of integer seeds (e.g. 42,43,44)"),
) -> None:
    """Evaluate baseline and skills across multiple seeds and models."""
    parsed_models = [m.strip() for m in models.split(",")] if models else [mode]
    parsed_seeds = [int(s.strip()) for s in seeds.split(",")] if seeds else [42]
    evaluation = evaluate(mode=mode, models=parsed_models, seeds=parsed_seeds)
    console.print(f"[green]Wrote[/green] {RUNS_DIR / 'evaluation.json'}")
    _print_evaluation(evaluation)


@app.command("gemini-smoke")
def gemini_smoke() -> None:
    """Verify GEMINI_API_KEY/GEMINI_MODEL without running the full benchmark."""
    try:
        response = gemini_smoke_test()
    except GeminiClientError as exc:
        console.print(f"[bold red]Gemini smoke test failed:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc
    console.print("[bold green]Gemini smoke test passed.[/bold green]")
    console.print(response)


@app.command("report")
def report_cmd() -> None:
    """Generate Markdown and HTML reports."""
    md_path, html_path = generate_report()
    console.print(f"[green]Wrote[/green] {md_path}")
    console.print(f"[green]Wrote[/green] {html_path}")


@app.command("demo")
def demo(mode: str = typer.Option(DEFAULT_MODE, "--mode")) -> None:
    """Run the full Terminal DreamGym loop end-to-end."""
    init_demo_assets()
    console.print(Panel.fit("Terminal DreamGym\nAgents that dream their own practice terminals", title="Demo"))

    run_baseline(mode=mode)
    diagnoses = diagnose_run(RUNS_DIR / "baseline.json", mode=mode)
    curricula = save_curricula(RUNS_DIR / "diagnoses.json")
    skills = generate_skills(from_curricula=GENERATED_CURRICULA_DIR)
    evaluation = evaluate(mode=mode)
    md_path, html_path = generate_report(REPORTS_DIR)

    _print_evaluation(evaluation)
    console.print()
    _print_curricula(curricula)
    console.print()
    console.print("[bold]Generated skills[/bold]")
    for skill in skills:
        console.print(f"- {skill.filename} -> {skill.strategy}")
    console.print()
    _print_sample_diff(evaluation)
    console.print()
    console.print(f"[green]Report:[/green] {md_path}")
    console.print(f"[green]HTML:[/green] {html_path}")
    console.print(f"[dim]Diagnoses generated:[/dim] {len(diagnoses)}")


def _print_summary(title: str, summary: dict[str, object]) -> None:
    table = Table(title=title)
    table.add_column("Split")
    table.add_column("Success", justify="right")
    for split in ["train", "heldout", "adversarial"]:
        item = summary[split]
        table.add_row(split, f"{item['successes']}/{item['total']}")
    console.print(table)


def _print_evaluation(evaluation: dict[str, object]) -> None:
    aggregated = evaluation["aggregated"]
    for model, stats in aggregated.items():
        console.print(Panel(f"Model: [bold cyan]{model}[/bold cyan] (aggregated over {len(evaluation['seeds'])} seeds)"))

        table = Table(title="Baseline Scores")
        table.add_column("Split")
        table.add_column("Mean ± 95% CI")
        for split in ["train", "heldout", "adversarial"]:
            s = stats["baseline_scores"][split]
            table.add_row(split, f"{s['mean'] * 100:.1f}% ± {s['ci95'] * 100:.1f}%")
        console.print(table)

        skills_table = Table(title="Per-Skill Evaluation vs Baseline")
        skills_table.add_column("Skill")
        skills_table.add_column("Train Δ")
        skills_table.add_column("Heldout Δ")
        skills_table.add_column("Adv Δ")
        skills_table.add_column("Adv Regressions")
        skills_table.add_column("Practice Score")
        skills_table.add_column("Naive Rate")
        skills_table.add_column("Gated Rate")
        skills_table.add_column("Disagreed")

        for skill_stat in stats["evaluations"]:
            name = skill_stat["name"]
            tr = skill_stat["train_delta"]
            he = skill_stat["heldout_delta"]
            ad = skill_stat["adversarial_delta"]
            ar = skill_stat["adversarial_regressions"]
            pr = skill_stat["practice_score"]

            skills_table.add_row(
                name,
                f"{tr['mean']*100:+.1f}% ± {tr['ci95']*100:.1f}%",
                f"{he['mean']*100:+.1f}% ± {he['ci95']*100:.1f}%",
                f"{ad['mean']*100:+.1f}% ± {ad['ci95']*100:.1f}%",
                f"{ar['mean']:.1f} ± {ar['ci95']:.1f}",
                f"{pr['mean']*100:.1f}% ± {pr['ci95']*100:.1f}%",
                f"{skill_stat['naive_promote_rate']*100:.1f}%",
                f"{skill_stat['gated_promote_rate']*100:.1f}%",
                f"{skill_stat['disagreement_rate']*100:.1f}%",
            )
        console.print(skills_table)
        console.print(f"[bold red]Self-Gating False-Promotion Rate:[/bold red] {stats['self_gating_false_promotion_rate']*100:.1f}%")


def _print_curricula(curricula: list[dict[str, object]]) -> None:
    table = Table(title="Generated practice worlds")
    table.add_column("Curriculum")
    table.add_column("Target skill")
    table.add_column("Worlds")
    for curriculum in curricula:
        worlds = ", ".join(world["id"] for world in curriculum["worlds"])
        table.add_row(curriculum["id"], curriculum["target_skill"], worlds)
    console.print(table)


def _print_sample_diff(evaluation: dict[str, object]) -> None:
    console.print("[dim]Sample repaired diff: see active trace logs in runs/sandboxes/[/dim]")


if __name__ == "__main__":
    app()
