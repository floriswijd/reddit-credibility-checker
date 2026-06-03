from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from reddit_credibility.schemas import ScoreBreakdown, ValidatedClaim


def render_report(
    username: str,
    claims: list[ValidatedClaim],
    scores: ScoreBreakdown,
    output_path: Path,
    template_dir: Path = Path("templates"),
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=select_autoescape(enabled_extensions=("html",)),
    )
    template = env.get_template("credibility_report.md.j2")
    rendered = template.render(username=username, claims=claims, scores=scores)
    output_path.write_text(rendered, encoding="utf-8")
    return output_path
