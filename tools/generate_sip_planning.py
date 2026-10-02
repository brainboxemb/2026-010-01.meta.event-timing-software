#!/usr/bin/env python3
"""Generate the canonical SIP planning views.

Sources:
- docs/11-SIP-software-implementation-planning.md: canonical step content
  (title, status, goal, result, demo and done).
- docs/_data/sip-roadmap.yaml: estimates, cadence, terms and document state.
- docs/_data/sip-steps/step-NN.yaml: detailed activity/status drill-down only.
- docs/_data/schemas/*.schema.json: planning data validation.

Generated output:
- planning/sip-roadmap.svg: one continuous roadmap;
- planning/sip-roadmap.pdf: the same roadmap as A4-landscape pages;
- planning/roadmap/sip-roadmap-1.svg .. -3.svg: separate A4 pages;
- planning/steps/step-NN.svg: A4-portrait detailed step boards;
- planning/steps/step-NN.pdf: printable detail boards.

All outputs are presentations of the same planning sources.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
import argparse
import json
import re
import shutil
import subprocess
import textwrap

import yaml
from jsonschema import Draft202012Validator, FormatChecker


A4_L_W_MM = 297.0
A4_L_H_MM = 210.0
A4_P_W_MM = 210.0
A4_P_H_MM = 297.0
ROADMAP_STEPS_PER_PAGE = 4
ROADMAP_PAGE_COUNT = 3
MARGIN_MM = 8.0

TIMELINE_Y = 31.0
DELIVERABLE_TOP = 59.0
DELIVERABLE_H = 37.0
DEMO_TOP = 101.0
DEMO_H = 37.0
DOC_TOP = 143.0
DOC_H = 40.0

STEP_CARD_COLS = 3
STEP_CARD_H = 22.0
STEP_CARD_GAP = 1.5
STEP_LANE_HEADER_H = 5.5
STEP_LANE_GAP = 1.5

MATURITY = {
    "outline": {"label": "O", "fill": "#f2f2f2", "stroke": "#808080"},
    "working": {"label": "W", "fill": "#ddebf7", "stroke": "#5b9bd5"},
    "review": {"label": "R", "fill": "#fff2cc", "stroke": "#bf9000"},
    "accepted": {"label": "A", "fill": "#e2f0d9", "stroke": "#70ad47"},
}

LANES = {
    "tooling": ("Tooling / engineering environment", "#eaf2f8", "#5b9bd5"),
    "documentation": ("Documentation / decisions", "#fff4df", "#c49a3a"),
    "application": ("Application / product", "#edf6e9", "#70ad47"),
    "verification": ("Verification / test", "#f0ebf7", "#8064a2"),
    "platform": ("Deployment / target environment", "#f2f2f2", "#7f7f7f"),
}

STATE_STYLE = {
    "done": ("DONE", "#e2f0d9", "#548235"),
    "next": ("NEXT", "#fff2cc", "#bf9000"),
    "active": ("ACTIVE", "#ddebf7", "#4472c4"),
    "planned": ("PLANNED", "#ffffff", "#808080"),
    "blocked": ("BLOCKED", "#f4cccc", "#a61c00"),
    "deferred": ("DEFERRED", "#eeeeee", "#999999"),
}


@dataclass(frozen=True)
class Step:
    number: int
    title: str
    status: str
    goal: str
    result_bullets: List[str]
    demo_bullets: List[str]
    done_bullets: List[str]
    deliverable: str
    demonstration: str
    estimate_days: int
    actual_days: float | None
    remaining_days: float
    target_date: date
    documents: List[dict]


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"Expected YAML mapping in {path}")
    return data


def load_json(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise SystemExit(f"Expected JSON object in {path}")
    return data


def validate_data(data: dict, schema: dict, source: Path) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(data), key=lambda item: list(item.absolute_path))
    if not errors:
        return
    lines = [f"Invalid planning data: {source}"]
    for error in errors:
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        lines.append(f"  {location}: {error.message}")
    raise SystemExit("\n".join(lines))


def strip_markdown(text: str) -> str:
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[*_>#]", "", text)
    text = re.sub(r"^\s*[-+*]\s+", "", text, flags=re.M)
    text = re.sub(r"^\s*\d+[.)]\s+", "", text, flags=re.M)
    return re.sub(r"\s+", " ", text).strip()


def concise(text: str, max_chars: int) -> str:
    clean = strip_markdown(text)
    if len(clean) <= max_chars:
        return clean
    cut = clean[:max_chars]
    pos = cut.rfind(" ")
    if pos >= int(max_chars * 0.65):
        cut = cut[:pos]
    return cut.rstrip(" .") + "..."


def wrap(text: str, width: int, max_lines: int) -> List[str]:
    lines = textwrap.wrap(
        str(text), width=max(8, width), break_long_words=False, break_on_hyphens=False
    )
    if len(lines) <= max_lines:
        return lines
    clipped = lines[:max_lines]
    clipped[-1] = clipped[-1].rstrip(" .") + "..."
    return clipped


def extract_subsection(body: str, heading: str) -> str:
    pattern = re.compile(
        rf"^### {re.escape(heading)}\s*$\n(.*?)(?=^### |^## Step |^## Java 11|^## Planning rules|\Z)",
        flags=re.M | re.S,
    )
    match = pattern.search(body)
    return match.group(1).strip() if match else ""


def subsection_bullets(body: str, heading: str) -> List[str]:
    section = extract_subsection(body, heading)
    bullets = [
        strip_markdown(match.group(1))
        for match in re.finditer(r"^\s*-\s+(.+?)\s*$", section, flags=re.M)
    ]
    if bullets:
        return [item for item in bullets if item]
    fallback = strip_markdown(section)
    return [fallback] if fallback else []


def sip_status(body: str, step_number: int) -> str:
    match = re.search(r"^Status:\s*(.+?)\s*$", body, flags=re.M)
    if not match:
        raise SystemExit(f"Missing Status for SIP Step {step_number}")
    raw = match.group(1).strip().lower()
    aliases = {
        "completed": "done",
        "complete": "done",
        "done": "done",
        "active": "active",
        "planned": "planned",
        "not started": "planned",
        "blocked": "blocked",
        "deferred": "deferred",
    }
    if raw not in aliases:
        raise SystemExit(f"Unsupported SIP Step {step_number} status: {raw}")
    return aliases[raw]


def planning_basis_text(steps: List[Step], plan: dict) -> str:
    baseline_days = sum(step.estimate_days for step in steps)
    remaining_days = sum(step.remaining_days for step in steps)
    actuals = plan["actuals"]
    spent_days = float(actuals["estimated_project_days"])
    reserve = float(plan.get("planning_reserve_fraction", 0.0))
    cadence = float(plan["cadence_project_days_per_week"])
    forecast_days = spent_days + remaining_days
    return (
        f"TOTAL: orig ~{baseline_days:g}d · forecast ~{forecast_days:g}d  |  "
        f"PROGRESS: spent ~{spent_days:g}d · rem ~{remaining_days:g}d  |  "
        f"~{cadence:g}d/week · +{reserve * 100:g}% reserve"
    )


def planning_basis_bullets(steps: List[Step], plan: dict) -> List[str]:
    baseline_days = sum(step.estimate_days for step in steps)
    remaining_days = sum(step.remaining_days for step in steps)
    actuals = plan["actuals"]
    spent_days = float(actuals["estimated_project_days"])
    spent_hours = float(actuals["estimated_hours"])
    through = date.fromisoformat(str(actuals["through_date"]))
    cadence = float(plan["cadence_project_days_per_week"])
    reserve = float(plan.get("planning_reserve_fraction", 0.0))
    forecast_days = spent_days + remaining_days
    actual_date = through.strftime("%d %b %Y").lstrip("0")
    return [
        f"TOTAL: orig ~{baseline_days:g}d · forecast ~{forecast_days:g}d",
        f"PROGRESS: spent ~{spent_days:g}d · rem ~{remaining_days:g}d",
        f"Activity snapshot: ~{spent_hours:g}h through {actual_date}",
        f"Cadence: ~{cadence:g}d/week",
        f"Reserve: +{reserve * 100:g}%",
    ]


def step_effort_lines(step: Step) -> List[str]:
    actual_days = step.actual_days if step.actual_days is not None else 0.0

    if step.status == "done":
        total_days = actual_days
        return [
            f"TOTAL: orig ~{step.estimate_days:g}d · total ~{total_days:g}d"
        ]

    forecast_days = actual_days + step.remaining_days
    lines = [
        f"TOTAL: orig ~{step.estimate_days:g}d · forecast ~{forecast_days:g}d"
    ]
    if step.status == "active":
        lines.append(
            f"PROGRESS: spent ~{actual_days:g}d · rem ~{step.remaining_days:g}d"
        )
    return lines

def phase_boundary_date(value: date) -> date:
    """Round a future calculated phase end up to the next Monday boundary."""
    return value + timedelta(days=(-value.weekday()) % 7)


def roadmap_end_text(step: Step) -> str:
    value = step.target_date.strftime("%d %b %Y")
    return value if step.status == "done" else f"end {value}"


def step_schedule_text(step: Step) -> str:
    label = "completed" if step.status == "done" else "forecast end"
    return f"{label} {step.target_date.strftime('%d %b %Y')}"


def parse_sip(path: Path, plan: dict) -> List[Step]:
    text = path.read_text(encoding="utf-8")
    heading_re = re.compile(r"^## Step (\d+)\s+[—-]\s+(.+?)\s*$", re.M)
    matches = list(heading_re.finditer(text))
    if not matches:
        raise SystemExit(f"No SIP steps found in {path}")

    reforecast_date = date.fromisoformat(str(plan["actuals"]["through_date"]))
    cadence = float(plan["cadence_project_days_per_week"])
    reserve = float(plan.get("planning_reserve_fraction", 0.0))
    cumulative_remaining = 0.0
    settings: Dict[str, dict] = plan["steps"]
    steps: List[Step] = []

    for index, match in enumerate(matches):
        number = int(match.group(1))
        cfg = settings.get(str(number))
        if cfg is None:
            raise SystemExit(f"Missing roadmap data for SIP Step {number}")
        estimate = int(cfg["estimate_project_days"])
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end():end]
        status = sip_status(body, number)

        if status == "done":
            completed = cfg.get("completed_date")
            if not completed:
                raise SystemExit(
                    f"Completed SIP Step {number} requires completed_date"
                )
            remaining = 0.0
            target = date.fromisoformat(str(completed))
        else:
            remaining = float(cfg.get("remaining_estimate_project_days", estimate))
            cumulative_remaining += remaining
            calculated_target = reforecast_date + timedelta(
                days=round(cumulative_remaining * (1.0 + reserve) / cadence * 7)
            )
            target = phase_boundary_date(calculated_target)

        goal = strip_markdown(extract_subsection(body, "Goal"))
        result_bullets = subsection_bullets(body, "Result")
        demo_bullets = subsection_bullets(body, "Demo")
        done_bullets = subsection_bullets(body, "Done")
        if not goal or not result_bullets or not demo_bullets or not done_bullets:
            raise SystemExit(
                f"SIP Step {number} must define Goal, Result, Demo and Done"
            )
        steps.append(
            Step(
                number=number,
                title=match.group(2).strip(),
                status=status,
                goal=goal,
                result_bullets=result_bullets,
                demo_bullets=demo_bullets,
                done_bullets=done_bullets,
                deliverable=" ".join(result_bullets),
                demonstration=" ".join(demo_bullets),
                estimate_days=estimate,
                actual_days=(
                    float(cfg["actual_estimated_project_days"])
                    if "actual_estimated_project_days" in cfg
                    else None
                ),
                remaining_days=remaining,
                target_date=target,
                documents=list(cfg.get("documents", [])),
            )
        )
    return steps


def load_step_boards(data_dir: Path, schema: dict) -> Dict[int, dict]:
    result: Dict[int, dict] = {}
    for path in sorted((data_dir / "sip-steps").glob("step-*.yaml")):
        data = load_yaml(path)
        validate_data(data, schema, path)
        number = int(data["step"])
        if number in result:
            raise SystemExit(f"Duplicate step-board source for Step {number}")
        ids = [item["id"] for item in data["activities"]]
        if len(ids) != len(set(ids)):
            raise SystemExit(f"Duplicate activity ID in {path}")
        known = set(ids)
        for activity in data["activities"]:
            for dependency in activity.get("depends_on", []):
                if dependency not in known:
                    raise SystemExit(
                        f"Unknown dependency {dependency} in {path} activity {activity['id']}"
                    )
                if dependency == activity["id"]:
                    raise SystemExit(f"Self dependency in {path}: {dependency}")
        result[number] = data
    return result


def compact_doc_label(document: dict) -> str:
    style = MATURITY[document["maturity"]]
    completeness = document.get("completeness")
    suffix = style["label"] if completeness is None else f"{style['label']}-{int(completeness)}"
    return f"{document['name']} {suffix}"


def activities_by_lane(board: dict) -> List[Tuple[str, List[dict]]]:
    grouped: Dict[str, List[dict]] = {}
    for activity in board["activities"]:
        grouped.setdefault(activity["lane"], []).append(activity)
    return [(lane, grouped[lane]) for lane in LANES if grouped.get(lane)]


def step_card_header_meta(activity: dict) -> List[str]:
    parts: List[str] = []
    if activity.get("estimate_project_days"):
        parts.append(f"~{activity['estimate_project_days']}d")
    if activity.get("depends_on"):
        parts.append("after " + " ".join(activity["depends_on"]))
    return parts


def step_card_note(activity: dict) -> str:
    note = activity.get("note")
    return concise(note, 30) if note else ""


def step_board_view(board: dict, step: Step) -> dict:
    state_tones = {
        "done": "success",
        "next": "warning",
        "active": "active",
        "planned": "muted",
        "blocked": "danger",
        "deferred": "muted",
    }
    maturity_tones = {
        "outline": "muted",
        "working": "active",
        "review": "warning",
        "accepted": "success",
    }
    lane_tones = {
        "tooling": "active",
        "documentation": "warning",
        "application": "success",
        "verification": "draft",
        "platform": "muted",
    }

    sections = [
        {
            "heading": "RESULT",
            "bullets": list(step.result_bullets),
        },
        {
            "heading": "END DEMO",
            "bullets": list(step.demo_bullets),
        },
    ]

    groups = []
    for lane, activities in activities_by_lane(board):
        lane_title = LANES[lane][0]
        cards = []
        for activity in activities:
            header_meta = step_card_header_meta(activity)
            note = step_card_note(activity)
            cards.append(
                {
                    "id": activity["id"],
                    "title": activity["title"],
                    "state": {
                        "label": STATE_STYLE[activity["state"]][0],
                        "tone": state_tones.get(activity["state"], "neutral"),
                    },
                    **({"header_meta": header_meta} if header_meta else {}),
                    **({"meta": [note]} if note else {}),
                }
            )
        groups.append(
            {
                "heading": lane_title,
                "tone": lane_tones.get(lane, "neutral"),
                "cards": cards,
            }
        )

    view = {
        "board": {
            "marker": str(step.number),
            "title": step.title,
            "meta": [
                step.status.upper(),
                *step_effort_lines(step),
                step_schedule_text(step),
            ],
            "summary": {
                "heading": "GOAL",
                "text": step.goal,
            },
            "section_columns": 2,
            "sections": sections,
            "groups": groups,
        }
    }

    if step.documents:
        view["board"]["badge_section"] = {
            "heading": "DOCUMENTATION",
            "badges": [
                {
                    "label": compact_doc_label(document),
                    "tone": maturity_tones.get(document["maturity"], "neutral"),
                }
                for document in step.documents
            ],
        }

    changes = board.get("planning_changes", [])
    if changes:
        view["board"]["trailing_sections"] = [
            {
                "heading": "PLANNING CHANGES",
                "bullets": [
                    f"{change['date']} — {change['change']}"
                    for change in changes
                ],
            }
        ]

    return view


def render_step_board(board: dict, step: Step, path: Path) -> None:
    render_dir = path.parent / f".{path.stem}-board"
    if render_dir.exists():
        shutil.rmtree(render_dir)
    render_dir.mkdir(parents=True)

    view_path = render_dir / "board-view.yaml"
    view_path.write_text(
        yaml.safe_dump(
            step_board_view(board, step),
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    subprocess.run(
        [
            "eng-docs",
            "board",
            "--source",
            str(view_path),
            "--out",
            str(render_dir / "rendered"),
        ],
        check=True,
    )

    shutil.copyfile(render_dir / "rendered" / "board.svg", path)
    shutil.copyfile(
        render_dir / "rendered" / "board.pdf",
        path.with_suffix(".pdf"),
    )
    shutil.rmtree(render_dir)


def write_readme(
    out_dir: Path,
    boards: Dict[int, dict],
    planning_basis: str,
    actual_method: str,
) -> None:
    lines = [
        "# Generated SIP planning",
        "",
        "All files below are generated from the same SIP/YAML planning sources.",
        "",
        f"**{planning_basis}**",
        "",
        "Actual effort is a planning indication derived from repository activity, not time registration.",
        actual_method,
        "",
        "- [Continuous roadmap](./sip-roadmap.svg) — all roadmap pages side by side.",
        f"- [Roadmap PDF](./sip-roadmap.pdf) — {ROADMAP_PAGE_COUNT} A4-landscape pages.",
        "",
        "## Roadmap pages",
        "",
    ]
    for index in range(1, ROADMAP_PAGE_COUNT + 1):
        lines.append(f"- [Roadmap page {index}](./roadmap/sip-roadmap-{index}.svg)")
    if boards:
        lines.extend(["", "## Step details", ""])
        for number in sorted(boards):
            lines.append(f"- [Step {number}](./steps/step-{number:02d}.svg)")
    lines.append("")
    (out_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sip", default="docs/11-SIP-software-implementation-planning.md")
    parser.add_argument("--data-dir", default="docs/_data")
    parser.add_argument("--out", default="bld/docs/planning")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    roadmap_source = data_dir / "sip-roadmap.yaml"
    plan = load_yaml(roadmap_source)
    validate_data(
        plan,
        load_json(data_dir / "schemas" / "sip-roadmap.schema.json"),
        roadmap_source,
    )
    steps = parse_sip(Path(args.sip), plan)
    planning_basis = planning_basis_text(steps, plan)

    boards = load_step_boards(
        data_dir,
        load_json(data_dir / "schemas" / "sip-step-board.schema.json"),
    )
    by_number = {step.number: step for step in steps}
    unknown_boards = sorted(set(boards) - set(by_number))
    if unknown_boards:
        raise SystemExit(f"Step board(s) without SIP milestone: {unknown_boards}")

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "roadmap").mkdir(parents=True, exist_ok=True)
    (out_dir / "steps").mkdir(parents=True, exist_ok=True)

    for number, board in sorted(boards.items()):
        render_step_board(
            board,
            by_number[number],
            out_dir / "steps" / f"step-{number:02d}.svg",
        )

    write_readme(
        out_dir,
        boards,
        planning_basis,
        str(plan["actuals"]["method"]),
    )


if __name__ == "__main__":
    main()