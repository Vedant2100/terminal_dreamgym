from __future__ import annotations

import html
from pathlib import Path
from typing import Any

from jinja2 import Template

from terminal_dreamgym.config import GENERATED_CURRICULA_DIR, GENERATED_SKILLS_DIR, REPORTS_DIR, RUNS_DIR
from terminal_dreamgym.evaluator import evaluate
from terminal_dreamgym.skill_generator import generate_skills
from terminal_dreamgym.utils import ensure_dir, load_markdown_snippet, read_json, write_text


def _load_evaluation() -> dict[str, Any]:
    path = RUNS_DIR / "evaluation.json"
    if not path.exists():
        return evaluate()
    return read_json(path)


def _load_curricula() -> list[dict[str, Any]]:
    return [read_json(path) for path in sorted(GENERATED_CURRICULA_DIR.glob("*.json"))]


def _load_skill_snippets() -> dict[str, str]:
    if not any(GENERATED_SKILLS_DIR.glob("*.md")):
        generate_skills()
    return {
        path.name: load_markdown_snippet(path, max_lines=10)
        for path in sorted(GENERATED_SKILLS_DIR.glob("*.md"))
    }


def _fmt_stat(stat: dict[str, float], is_pct: bool = True) -> str:
    val = stat["mean"]
    ci = stat["ci95"]
    if is_pct:
        return f"{val * 100:.1f}% ± {ci * 100:.1f}%"
    return f"{val:.2f} ± {ci:.2f}"


def _fmt_delta_stat(stat: dict[str, float]) -> str:
    val = stat["mean"]
    ci = stat["ci95"]
    sign = "+" if val >= 0 else ""
    return f"{sign}{val * 100:.1f}% ± {ci * 100:.1f}%"


def _fmt_rate(rate: float) -> str:
    return f"{rate * 100:.1f}%"


def build_markdown(evals: dict) -> str:
    models = evals["models"]
    seeds = evals["seeds"]
    aggregated = evals["aggregated"]

    lines = [
        "# Terminal DreamGym: Sweep Evaluation Report",
        "",
        "## 1. Research Overview",
        "",
        "Self-improving agent systems struggle with the proxy-reality gap: a skill can raise the score on visible training failures while regressing or failing to transfer to held-out situations. Terminal DreamGym studies how naive training-only gates compare to transfer gates under multi-seed and multi-model settings.",
        f"- **Models Swept**: {', '.join(models)}",
        f"- **Seeds Swept**: {', '.join(map(str, seeds))} ({len(seeds)} total)",
        "",
    ]

    for model, stats in aggregated.items():
        lines += [
            f"## Model: {model}",
            "",
            "### Baseline Scores",
            "",
            "The baseline agent uses only the SOP (no generated skills active). Scores represent mean ± 95% confidence intervals:",
            f"- **Train**: {_fmt_stat(stats['baseline_scores']['train'])}",
            f"- **Heldout**: {_fmt_stat(stats['baseline_scores']['heldout'])}",
            f"- **Adversarial**: {_fmt_stat(stats['baseline_scores']['adversarial'])}",
            "",
            "### Per-Skill Sweep Results",
            "",
            "Each candidate skill is evaluated individually. Delts represent mean ± 95% confidence intervals relative to the baseline of each seed:",
            "",
            "| Skill | Train Δ | Heldout Δ | Adv Δ | Adv Regressions | Practice Score | Naive Rate | Gated Rate | Disagree Rate | Wrongly Rejected |",
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
        ]

        for es in stats["evaluations"]:
            lines.append(
                f"| `{es['name']}` | "
                f"{_fmt_delta_stat(es['train_delta'])} | "
                f"{_fmt_delta_stat(es['heldout_delta'])} | "
                f"{_fmt_delta_stat(es['adversarial_delta'])} | "
                f"{_fmt_stat(es['adversarial_regressions'], False)} | "
                f"{_fmt_stat(es['practice_score'])} | "
                f"{_fmt_rate(es['naive_promote_rate'])} | "
                f"{_fmt_rate(es['gated_promote_rate'])} | "
                f"{_fmt_rate(es['disagreement_rate'])} | "
                f"{_fmt_rate(es['wrongly_rejected_rate'])} |"
            )

        lines += [
            "",
            f"**Dreamed-Curriculum trust metric**: The False-Promotion Rate of self-gating is **{_fmt_rate(stats['self_gating_false_promotion_rate'])}**. This represents the percentage of runs where a skill passed the dreamed gate (practice score ≥ 60.0%) but failed to generalize in reality (held-out delta ≤ 0.0%).",
            "",
            "### Stacking & Interference Diagnostics",
            "",
            "When multiple skills are promoted by a policy, they are stacked together. If the stacked heldout score is below the best single promoted skill, we observe skill interference. Stats represent mean ± 95% confidence intervals:",
            "",
        ]

        for policy in ["naive", "gated"]:
            p_stat = stats["interference"][policy]
            lines += [
                f"#### Policy: {policy.upper()}",
                f"- **Interference Rate**: {_fmt_rate(p_stat['interferes_rate'])} of seeds",
                f"- **Stacked Heldout Δ**: {_fmt_delta_stat(p_stat['stacked_heldout_delta'])}",
                f"- **Stacked Adversarial Δ**: {_fmt_delta_stat(p_stat['stacked_adversarial_delta'])}",
                f"- **Interference Delta (Stacked vs Best)**: {_fmt_delta_stat(p_stat['interference_delta'])}",
                "",
            ]

    return "\n".join(lines) + "\n"


def build_html(evals: dict) -> str:
    models = evals["models"]
    seeds = evals["seeds"]
    aggregated = evals["aggregated"]

    def td(x: str, cls: str = "") -> str:
        c = f' class="{cls}"' if cls else ""
        return f"<td{c}>{html.escape(x)}</td>"

    sections = []
    for model, stats in aggregated.items():
        rows_html = []
        for es in stats["evaluations"]:
            rows_html.append(
                "<tr>"
                + td(es["name"], "font-mono")
                + td(_fmt_delta_stat(es["train_delta"]))
                + td(_fmt_delta_stat(es["heldout_delta"]))
                + td(_fmt_delta_stat(es["adversarial_delta"]))
                + td(_fmt_stat(es["adversarial_regressions"], False))
                + td(_fmt_stat(es["practice_score"]))
                + td(_fmt_rate(es["naive_promote_rate"]))
                + td(_fmt_rate(es["gated_promote_rate"]))
                + td(_fmt_rate(es["disagreement_rate"]))
                + td(_fmt_rate(es["wrongly_rejected_rate"]))
                + "</tr>"
            )

        baseline_html = f"""
        <div class="card">
            <h3>Baseline Scores</h3>
            <table class="nested-table">
                <thead><tr><th>Split</th><th>Mean ± 95% CI</th></tr></thead>
                <tbody>
                    <tr><td>Train</td><td>{_fmt_stat(stats['baseline_scores']['train'])}</td></tr>
                    <tr><td>Heldout</td><td>{_fmt_stat(stats['baseline_scores']['heldout'])}</td></tr>
                    <tr><td>Adversarial</td><td>{_fmt_stat(stats['baseline_scores']['adversarial'])}</td></tr>
                </tbody>
            </table>
        </div>
        """

        interference_html = ""
        for policy in ["naive", "gated"]:
            p_stat = stats["interference"][policy]
            interference_html += f"""
            <div class="policy-card">
                <h4>Policy: {policy.upper()}</h4>
                <ul>
                    <li><strong>Interference Rate:</strong> {_fmt_rate(p_stat['interferes_rate'])} of seeds</li>
                    <li><strong>Stacked Heldout Δ:</strong> {_fmt_delta_stat(p_stat['stacked_heldout_delta'])}</li>
                    <li><strong>Stacked Adversarial Δ:</strong> {_fmt_delta_stat(p_stat['stacked_adversarial_delta'])}</li>
                    <li><strong>Interference Delta (Stacked vs Best):</strong> {_fmt_delta_stat(p_stat['interference_delta'])}</li>
                </ul>
            </div>
            """

        sections.append(
            f"""
            <section class="model-section">
                <h2>Model: {model}</h2>
                <div class="row">
                    {baseline_html}
                    <div class="card trust-card">
                        <h3>Dreamed-Curriculum Trust Metric</h3>
                        <div class="metric-value">{_fmt_rate(stats['self_gating_false_promotion_rate'])}</div>
                        <p class="metric-label">Self-Gating False-Promotion Rate</p>
                        <p class="metric-desc">Percentage of runs where a skill passed the dreamed gate (practice score ≥ 60.0%) but failed to generalize in reality (held-out delta ≤ 0.0%).</p>
                    </div>
                </div>
                <h3>Per-Skill Evaluation</h3>
                <div class="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>Skill</th>
                                <th>Train Δ</th>
                                <th>Heldout Δ</th>
                                <th>Adv Δ</th>
                                <th>Adv Regressions</th>
                                <th>Practice Score</th>
                                <th>Naive Rate</th>
                                <th>Gated Rate</th>
                                <th>Disagree Rate</th>
                                <th>Wrongly Rejected</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join(rows_html)}
                        </tbody>
                    </table>
                </div>
                <h3>Stacking & Interference Diagnostics</h3>
                <div class="row">
                    {interference_html}
                </div>
            </section>
            """
        )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Terminal DreamGym: Sweep Evaluation Report</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@500;700&display=swap" rel="stylesheet">
<style>
  body {{
    font-family: 'Inter', system-ui, sans-serif;
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem 1.5rem 4rem;
    color: #1e293b;
    background: #f8fafc;
  }}
  header {{
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
    color: white;
    padding: 2.5rem 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
  }}
  h1 {{
    font-family: 'Outfit', sans-serif;
    font-size: 2.5rem;
    margin: 0 0 0.5rem;
    font-weight: 700;
  }}
  .subtitle {{
    color: #94a3b8;
    font-size: 1.1rem;
    margin: 0;
  }}
  .meta-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    margin-top: 1.5rem;
    border-top: 1px solid #334155;
    padding-top: 1rem;
  }}
  .meta-item strong {{
    color: #f1f5f9;
  }}
  .meta-item span {{
    color: #cbd5e1;
  }}
  .model-section {{
    background: white;
    padding: 2rem;
    border-radius: 12px;
    margin-bottom: 2.5rem;
    box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1);
    border: 1px solid #e2e8f0;
  }}
  h2 {{
    font-family: 'Outfit', sans-serif;
    font-size: 1.8rem;
    margin-top: 0;
    margin-bottom: 1.5rem;
    color: #0f172a;
    border-bottom: 2px solid #f1f5f9;
    padding-bottom: 0.5rem;
  }}
  h3 {{
    font-family: 'Outfit', sans-serif;
    font-size: 1.3rem;
    color: #1e293b;
    margin-top: 2rem;
    margin-bottom: 1rem;
  }}
  h4 {{
    font-family: 'Outfit', sans-serif;
    font-size: 1.1rem;
    color: #0f172a;
    margin: 0 0 1rem;
  }}
  .row {{
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
    margin-bottom: 1.5rem;
  }}
  .card {{
    flex: 1;
    min-width: 280px;
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    padding: 1.5rem;
    border-radius: 8px;
  }}
  .trust-card {{
    background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%);
    border-color: #fed7aa;
  }}
  .metric-value {{
    font-family: 'Outfit', sans-serif;
    font-size: 3rem;
    font-weight: 700;
    color: #ea580c;
    line-height: 1;
    margin-bottom: 0.25rem;
  }}
  .metric-label {{
    font-weight: 600;
    color: #9a3412;
    margin: 0 0 0.5rem;
  }}
  .metric-desc {{
    font-size: 0.875rem;
    color: #7c2d12;
    margin: 0;
    line-height: 1.4;
  }}
  .policy-card {{
    flex: 1;
    min-width: 280px;
    background: #f1f5f9;
    border: 1px solid #cbd5e1;
    padding: 1.5rem;
    border-radius: 8px;
  }}
  .policy-card ul {{
    margin: 0;
    padding-left: 1.25rem;
  }}
  .policy-card li {{
    margin-bottom: 0.5rem;
    line-height: 1.4;
  }}
  .table-container {{
    overflow-x: auto;
    margin: 1rem 0;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
  }}
  table {{
    border-collapse: collapse;
    width: 100%;
    background: white;
  }}
  th, td {{
    padding: 0.75rem 1rem;
    text-align: left;
    border-bottom: 1px solid #e2e8f0;
    font-size: 0.9rem;
  }}
  th {{
    background: #f1f5f9;
    color: #475569;
    font-weight: 600;
  }}
  tr:hover {{
    background: #f8fafc;
  }}
  .nested-table {{
    width: 100%;
    background: transparent;
  }}
  .nested-table th, .nested-table td {{
    padding: 0.5rem 0.75rem;
  }}
  .nested-table th {{
    background: #e2e8f0;
  }}
  .font-mono {{
    font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 0.85rem;
  }}
</style>
</head>
<body>
<header>
  <h1>Terminal DreamGym Sweep Report</h1>
  <p class="subtitle">Characterizing recursive self-improvement and environment proxy-reality gaps</p>
  <div class="meta-grid">
    <div class="meta-item"><strong>Models:</strong> <span>{', '.join(models)}</span></div>
    <div class="meta-item"><strong>Seeds:</strong> <span>{', '.join(map(str, seeds))}</span></div>
    <div class="meta-item"><strong>Tasks per Run:</strong> <span>100 (5x Scaled)</span></div>
  </div>
</header>

{''.join(sections)}

</body>
</html>
"""


def generate_report(output_dir: Path | None = None) -> tuple[Path, Path]:
    target = ensure_dir(output_dir or REPORTS_DIR)
    evaluation_data = _load_evaluation()

    md_content = build_markdown(evaluation_data)
    html_content = build_html(evaluation_data)

    md_path = target / "report.md"
    html_path = target / "report.html"

    write_text(md_path, md_content)
    write_text(html_path, html_content)

    return md_path, html_path
