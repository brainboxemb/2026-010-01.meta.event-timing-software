#!/usr/bin/env python3
"""Adapt project-owned SIP planning semantics to the generic RoadmapView."""

from __future__ import annotations

from pathlib import Path
import argparse
import shutil
import subprocess

import yaml

import generate_sip_planning as base


STATE_TONES = {
    "done": "success",
    "active": "active",
    "planned": "muted",
    "blocked": "danger",
    "deferred": "muted",
}

MATURITY_TONES = {
    "outline": "muted",
    "working": "active",
    "review": "warning",
    "accepted": "success",
}


def compact_roadmap_bullets(values: list[str], max_items: int = 3) -> list[str]:
    """Keep the broad roadmap compact; detailed wording remains in SIP/step boards."""
    if len(values) <= max_items:
        selected = values
    elif max_items == 3:
        selected = [values[0], values[len(values) // 2], values[-1]]
    else:
        selected = values[:max_items]
    return [base.concise(value, 105) for value in selected]


def roadmap_view(steps: list[base.Step], plan: dict) -> dict:
    items: list[dict] = []

    for step in steps:
        label = base.STATE_STYLE[step.status][0]
        item = {
            "id": str(step.number),
            "marker": str(step.number),
            "title": step.title,
            "state": {
                "label": label,
                "tone": STATE_TONES.get(step.status, "neutral"),
            },
            "meta": [
                base.roadmap_end_text(step),
                base.step_effort_text(step),
            ],
            "sections": [
                {
                    "heading": "RESULT",
                    "bullets": compact_roadmap_bullets(step.result_bullets),
                },
                {
                    "heading": "DEMO",
                    "bullets": compact_roadmap_bullets(step.demo_bullets),
                },
            ],
        }
        if step.documents:
            item["badge_heading"] = "DOCUMENT STATUS"
            item["badges"] = [
                {
                    "label": base.compact_doc_label(document),
                    "tone": MATURITY_TONES.get(
                        document["maturity"], "neutral"
                    ),
                }
                for document in step.documents
            ]
        items.append(item)

    return {
        "roadmap": {
            "title": "Software Implementation Planning — roadmap",
            "subtitle": base.planning_basis_text(steps, plan),
            "items": items,
        }
    }


def write_readme(
    out_dir: Path,
    plan: dict,
    page_count: int,
) -> None:
    lines = [
        "# Generated SIP planning",
        "",
        "All files below are generated from the same SIP/YAML planning sources.",
        "",
        "- [Continuous roadmap](./sip-roadmap.svg)",
        f"- [Roadmap PDF](./sip-roadmap.pdf) — {page_count} A4-landscape page(s).",
        "- [RoadmapView input](./roadmap-view.yaml) — project-owned compact presentation data.",
        "",
        "Actual effort is a planning indication derived from repository activity, not time registration.",
        str(plan["actuals"]["method"]),
        "",
        "## Roadmap pages",
        "",
    ]
    for index in range(1, page_count + 1):
        lines.append(
            f"- [Roadmap page {index}](./roadmap/sip-roadmap-{index}.svg)"
        )

    step_pages = sorted((out_dir / "steps").glob("step-*.svg"))
    if step_pages:
        lines.extend(["", "## Step details", ""])
        for path in step_pages:
            number = int(path.stem.split("-")[-1])
            lines.append(
                f"- Step {number}: [SVG](./steps/{path.name}) · "
                f"[PDF](./steps/step-{number:02d}.pdf)"
            )

    lines.append("")
    (out_dir / "README.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sip",
        default="docs/11-SIP-software-implementation-planning.md",
    )
    parser.add_argument("--data-dir", default="docs/_data")
    parser.add_argument("--out", default="bld/docs/planning")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    plan_path = data_dir / "sip-roadmap.yaml"
    plan = base.load_yaml(plan_path)
    base.validate_data(
        plan,
        base.load_json(data_dir / "schemas" / "sip-roadmap.schema.json"),
        plan_path,
    )
    steps = base.parse_sip(Path(args.sip), plan)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    view_path = out_dir / "roadmap-view.yaml"
    view_path.write_text(
        yaml.safe_dump(
            roadmap_view(steps, plan),
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    render_dir = out_dir / "_roadmap-render"
    if render_dir.exists():
        shutil.rmtree(render_dir)

    subprocess.run(
        [
            "eng-docs",
            "roadmap",
            "--source",
            str(view_path),
            "--out",
            str(render_dir),
        ],
        check=True,
    )

    shutil.copyfile(render_dir / "roadmap.svg", out_dir / "sip-roadmap.svg")
    shutil.copyfile(render_dir / "roadmap.pdf", out_dir / "sip-roadmap.pdf")

    page_out = out_dir / "roadmap"
    if page_out.exists():
        shutil.rmtree(page_out)
    page_out.mkdir(parents=True)

    generated_pages = sorted(
        (render_dir / "roadmap").glob("roadmap-page-*.svg")
    )
    if not generated_pages:
        raise SystemExit("eng-docs roadmap produced no page SVGs")

    for index, source in enumerate(generated_pages, start=1):
        shutil.copyfile(
            source,
            page_out / f"sip-roadmap-{index}.svg",
        )

    shutil.rmtree(render_dir)
    write_readme(out_dir, plan, len(generated_pages))


if __name__ == "__main__":
    main()
