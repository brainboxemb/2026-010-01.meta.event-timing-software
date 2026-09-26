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
- planning/roadmap/sip-roadmap-1.svg .. -4.svg: separate A4 pages;
- planning/steps/step-NN.svg: A4-portrait detailed step boards.

All outputs are presentations of the same planning sources.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Tuple
import argparse
import html
import json
import math
import re
import textwrap

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


A4_L_W_MM = 297.0
A4_L_H_MM = 210.0
A4_P_W_MM = 210.0
A4_P_H_MM = 297.0
ROADMAP_STEPS_PER_PAGE = 4
ROADMAP_PAGE_COUNT = 2
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
    "application": ("Application / product", "#edf6e9", "#70ad47"),
    "verification": ("Verification / test", "#f0ebf7", "#8064a2"),
    "platform": ("Deployment / target environment", "#f2f2f2", "#7f7f7f"),
    "documentation": ("Documentation / decisions", "#fff4df", "#c49a3a"),
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


def parse_sip(path: Path, plan: dict) -> List[Step]:
    text = path.read_text(encoding="utf-8")
    heading_re = re.compile(r"^## Step (\d+)\s+[—-]\s+(.+?)\s*$", re.M)
    matches = list(heading_re.finditer(text))
    if not matches:
        raise SystemExit(f"No SIP steps found in {path}")

    start = date.fromisoformat(str(plan["start_date"]))
    cadence = float(plan["cadence_project_days_per_week"])
    cumulative = 0
    settings: Dict[str, dict] = plan["steps"]
    steps: List[Step] = []

    for index, match in enumerate(matches):
        number = int(match.group(1))
        cfg = settings.get(str(number))
        if cfg is None:
            raise SystemExit(f"Missing roadmap data for SIP Step {number}")
        estimate = int(cfg["estimate_project_days"])
        cumulative += estimate
        target = start + timedelta(days=round(cumulative / cadence * 7))
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end():end]
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
                status=sip_status(body, number),
                goal=goal,
                result_bullets=result_bullets,
                demo_bullets=demo_bullets,
                done_bullets=done_bullets,
                deliverable=" ".join(result_bullets),
                demonstration=" ".join(demo_bullets),
                estimate_days=estimate,
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


def roadmap_groups(steps: List[Step]) -> List[List[Step]]:
    groups = [
        steps[index:index + ROADMAP_STEPS_PER_PAGE]
        for index in range(0, len(steps), ROADMAP_STEPS_PER_PAGE)
    ]
    if len(groups) != ROADMAP_PAGE_COUNT:
        raise SystemExit(
            f"Current roadmap must render as {ROADMAP_PAGE_COUNT} A4 pages; got {len(groups)}"
        )
    return groups


def compact_doc_label(document: dict) -> str:
    style = MATURITY[document["maturity"]]
    completeness = document.get("completeness")
    suffix = style["label"] if completeness is None else f"{style['label']}{int(completeness)}"
    return f"{document['name']} {suffix}"


def svg_text(
    parts: List[str],
    x: float,
    y: float,
    lines: Iterable[str],
    size: float,
    anchor: str = "middle",
    weight: str = "normal",
    fill: str = "#222",
) -> None:
    parts.append(
        f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" '
        f'font-family="Arial,Helvetica,sans-serif" font-size="{size:.2f}" '
        f'font-weight="{weight}" fill="{fill}">'
    )
    for index, line in enumerate(lines):
        dy = 0 if index == 0 else size * 1.20
        parts.append(
            f'<tspan x="{x:.2f}" dy="{dy:.2f}">{html.escape(str(line))}</tspan>'
        )
    parts.append("</text>")


def roadmap_positions(group: List[Step], page_x: float = 0.0) -> List[Tuple[Step, float, float]]:
    usable = A4_L_W_MM - 2 * MARGIN_MM
    cell = usable / ROADMAP_STEPS_PER_PAGE
    return [
        (step, page_x + MARGIN_MM + cell * (index + 0.5), cell - 5.0)
        for index, step in enumerate(group)
    ]


def append_roadmap_svg_page(
    parts: List[str],
    group: List[Step],
    page_index: int,
    page_x: float,
    *,
    standalone: bool,
) -> None:
    if not standalone:
        parts.append(
            f'<rect x="{page_x:.2f}" y="0" width="{A4_L_W_MM:.2f}" height="{A4_L_H_MM:.2f}" '
            'fill="none" stroke="#d0d0d0" stroke-width="0.35"/>'
        )

    title_x = page_x + MARGIN_MM
    svg_text(
        parts,
        title_x,
        10.5,
        ["Software Implementation Planning — roadmap"],
        5.2,
        anchor="start",
        weight="bold",
    )
    svg_text(
        parts,
        title_x,
        17.5,
        [f"Page {page_index + 1}/{ROADMAP_PAGE_COUNT} — Steps {group[0].number}-{group[-1].number}"],
        2.5,
        anchor="start",
        fill="#555",
    )

    parts.append(
        f'<line x1="{page_x + MARGIN_MM:.2f}" y1="{TIMELINE_Y}" '
        f'x2="{page_x + A4_L_W_MM - MARGIN_MM:.2f}" y2="{TIMELINE_Y}" '
        'stroke="#333" stroke-width="0.65"/>'
    )

    for step, center_x, width in roadmap_positions(group, page_x):
        radius = 3.4
        points = (
            f"{center_x},{TIMELINE_Y-radius} {center_x+radius},{TIMELINE_Y} "
            f"{center_x},{TIMELINE_Y+radius} {center_x-radius},{TIMELINE_Y}"
        )
        parts.append(
            f'<polygon points="{points}" fill="white" stroke="#333" stroke-width="0.55"/>'
        )
        svg_text(parts, center_x, TIMELINE_Y + 0.9, [str(step.number)], 2.7, weight="bold")
        svg_text(
            parts,
            center_x,
            24.0,
            [f"~{step.estimate_days}d", step.target_date.strftime("%d %b %Y")],
            2.3,
            weight="bold",
            fill="#555",
        )
        svg_text(
            parts,
            center_x,
            41.0,
            wrap(f"Step {step.number} — {step.title}", 29, 3),
            2.85,
            weight="bold",
        )

        x = center_x - width / 2
        parts.append(
            f'<rect x="{x:.2f}" y="{DELIVERABLE_TOP}" width="{width:.2f}" '
            f'height="{DELIVERABLE_H}" rx="1.6" fill="#f6f8fa" '
            'stroke="#6c8ebf" stroke-width="0.55"/>'
        )
        svg_text(
            parts,
            x + 2.7,
            DELIVERABLE_TOP + 6.2,
            ["DELIVERABLE"],
            2.4,
            anchor="start",
            weight="bold",
            fill="#4f81bd",
        )
        svg_text(
            parts,
            center_x,
            DELIVERABLE_TOP + 13.2,
            wrap(step.deliverable, max(22, int(width / 2.0)), 6),
            2.35,
        )

        parts.append(
            f'<rect x="{x:.2f}" y="{DEMO_TOP}" width="{width:.2f}" '
            f'height="{DEMO_H}" rx="1.6" fill="#ffffff" '
            'stroke="#6c8ebf" stroke-width="0.55"/>'
        )
        svg_text(
            parts,
            x + 2.7,
            DEMO_TOP + 6.2,
            ["DEMONSTRATION"],
            2.4,
            anchor="start",
            weight="bold",
            fill="#4f81bd",
        )
        svg_text(
            parts,
            center_x,
            DEMO_TOP + 13.2,
            wrap(step.demonstration, max(22, int(width / 2.0)), 6),
            2.3,
        )

        parts.append(
            f'<rect x="{x:.2f}" y="{DOC_TOP}" width="{width:.2f}" '
            f'height="{DOC_H}" rx="1.6" fill="#fafafa" '
            'stroke="#999" stroke-width="0.4"/>'
        )
        svg_text(
            parts,
            x + 2.7,
            DOC_TOP + 6.2,
            ["DOCUMENTS"],
            2.3,
            anchor="start",
            weight="bold",
            fill="#555",
        )

        for idx, document in enumerate(step.documents[:6]):
            row, col = divmod(idx, 2)
            chip_w = (width - 7.0) / 2
            chip_x = x + 2.3 + col * (chip_w + 2.3)
            chip_y = DOC_TOP + 10.5 + row * 8.1
            style = MATURITY[document["maturity"]]
            parts.append(
                f'<rect x="{chip_x:.2f}" y="{chip_y:.2f}" width="{chip_w:.2f}" '
                f'height="6.3" rx="1" fill="{style["fill"]}" stroke="{style["stroke"]}" '
                'stroke-width="0.3"/>'
            )
            svg_text(
                parts,
                chip_x + chip_w / 2,
                chip_y + 4.1,
                [concise(compact_doc_label(document), 20)],
                1.85,
                weight="bold",
                fill=style["stroke"],
            )


def render_roadmap_svgs(groups: List[List[Step]], out_dir: Path) -> None:
    page_dir = out_dir / "roadmap"
    page_dir.mkdir(parents=True, exist_ok=True)

    panorama_w = A4_L_W_MM * ROADMAP_PAGE_COUNT
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{panorama_w}mm" '
        f'height="{A4_L_H_MM}mm" viewBox="0 0 {panorama_w} {A4_L_H_MM}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]
    for page_index, group in enumerate(groups):
        append_roadmap_svg_page(
            parts, group, page_index, page_index * A4_L_W_MM, standalone=False
        )
    parts.append("</svg>")
    (out_dir / "sip-roadmap.svg").write_text("\n".join(parts), encoding="utf-8")

    for page_index, group in enumerate(groups):
        page_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{A4_L_W_MM}mm" '
            f'height="{A4_L_H_MM}mm" viewBox="0 0 {A4_L_W_MM} {A4_L_H_MM}">',
            '<rect width="100%" height="100%" fill="white"/>',
        ]
        append_roadmap_svg_page(
            page_parts, group, page_index, 0.0, standalone=True
        )
        page_parts.append("</svg>")
        (page_dir / f"sip-roadmap-{page_index + 1}.svg").write_text(
            "\n".join(page_parts), encoding="utf-8"
        )


def pdf_text(
    c: canvas.Canvas,
    x: float,
    y: float,
    lines: Iterable[str],
    size: float,
    *,
    bold: bool = False,
    center: bool = True,
) -> None:
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    for index, line in enumerate(lines):
        y_pos = y - index * size * 1.25 / 2.83465
        if center:
            c.drawCentredString(x * mm, y_pos * mm, str(line))
        else:
            c.drawString(x * mm, y_pos * mm, str(line))


def render_roadmap_pdf(groups: List[List[Step]], path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=landscape(A4))
    page_w = A4_L_W_MM
    page_h = A4_L_H_MM

    for page_index, group in enumerate(groups):
        c.setFillColor(HexColor("#222222"))
        c.setStrokeColor(HexColor("#333333"))
        c.setFont("Helvetica-Bold", 14)
        c.drawString(MARGIN_MM * mm, (page_h - 10.5) * mm, "Software Implementation Planning — roadmap")
        c.setFillColor(HexColor("#555555"))
        c.setFont("Helvetica", 7)
        c.drawString(
            MARGIN_MM * mm,
            (page_h - 17.5) * mm,
            f"Page {page_index + 1}/{ROADMAP_PAGE_COUNT} — Steps {group[0].number}-{group[-1].number}",
        )
        c.setStrokeColor(HexColor("#333333"))
        c.setLineWidth(0.65)
        c.line(
            MARGIN_MM * mm,
            (page_h - TIMELINE_Y) * mm,
            (page_w - MARGIN_MM) * mm,
            (page_h - TIMELINE_Y) * mm,
        )

        for step, center_x, width in roadmap_positions(group):
            r = 3.4
            c.setStrokeColor(HexColor("#333333"))
            c.line(center_x * mm, (page_h - (TIMELINE_Y-r)) * mm,
                   (center_x+r) * mm, (page_h-TIMELINE_Y) * mm)
            c.line((center_x+r) * mm, (page_h-TIMELINE_Y) * mm,
                   center_x * mm, (page_h-(TIMELINE_Y+r)) * mm)
            c.line(center_x * mm, (page_h-(TIMELINE_Y+r)) * mm,
                   (center_x-r) * mm, (page_h-TIMELINE_Y) * mm)
            c.line((center_x-r) * mm, (page_h-TIMELINE_Y) * mm,
                   center_x * mm, (page_h-(TIMELINE_Y-r)) * mm)
            c.setFillColor(HexColor("#222222"))
            c.setFont("Helvetica-Bold", 7)
            c.drawCentredString(
                center_x * mm,
                (page_h - TIMELINE_Y - 1.0) * mm,
                str(step.number),
            )
            c.setFillColor(HexColor("#555555"))
            pdf_text(
                c,
                center_x,
                page_h - 24.0,
                [f"~{step.estimate_days}d", step.target_date.strftime("%d %b %Y")],
                6.2,
                bold=True,
            )
            c.setFillColor(HexColor("#222222"))
            pdf_text(
                c,
                center_x,
                page_h - 41.0,
                wrap(f"Step {step.number} — {step.title}", 29, 3),
                7.2,
                bold=True,
            )

            x = center_x - width / 2
            for top, height, heading, text, fill in [
                (DELIVERABLE_TOP, DELIVERABLE_H, "DELIVERABLE", step.deliverable, "#f6f8fa"),
                (DEMO_TOP, DEMO_H, "DEMONSTRATION", step.demonstration, "#ffffff"),
            ]:
                c.setStrokeColor(HexColor("#6c8ebf"))
                c.setFillColor(HexColor(fill))
                c.roundRect(
                    x * mm,
                    (page_h - top - height) * mm,
                    width * mm,
                    height * mm,
                    1.6 * mm,
                    stroke=1,
                    fill=1,
                )
                c.setFillColor(HexColor("#4f81bd"))
                c.setFont("Helvetica-Bold", 6.2)
                c.drawString((x + 2.7) * mm, (page_h - top - 6.2) * mm, heading)
                c.setFillColor(HexColor("#222222"))
                pdf_text(
                    c,
                    center_x,
                    page_h - top - 13.2,
                    wrap(text, max(22, int(width / 2.0)), 6),
                    5.9,
                )

            c.setStrokeColor(HexColor("#999999"))
            c.setFillColor(HexColor("#fafafa"))
            c.roundRect(
                x * mm,
                (page_h - DOC_TOP - DOC_H) * mm,
                width * mm,
                DOC_H * mm,
                1.6 * mm,
                stroke=1,
                fill=1,
            )
            c.setFillColor(HexColor("#555555"))
            c.setFont("Helvetica-Bold", 6.0)
            c.drawString((x + 2.7) * mm, (page_h - DOC_TOP - 6.2) * mm, "DOCUMENTS")
            for idx, document in enumerate(step.documents[:6]):
                row, col = divmod(idx, 2)
                chip_w = (width - 7.0) / 2
                chip_x = x + 2.3 + col * (chip_w + 2.3)
                chip_y = DOC_TOP + 10.5 + row * 8.1
                style = MATURITY[document["maturity"]]
                c.setStrokeColor(HexColor(style["stroke"]))
                c.setFillColor(HexColor(style["fill"]))
                c.roundRect(
                    chip_x * mm,
                    (page_h - chip_y - 6.3) * mm,
                    chip_w * mm,
                    6.3 * mm,
                    1.0 * mm,
                    stroke=1,
                    fill=1,
                )
                c.setFillColor(HexColor(style["stroke"]))
                c.setFont("Helvetica-Bold", 4.7)
                c.drawCentredString(
                    (chip_x + chip_w / 2) * mm,
                    (page_h - chip_y - 4.3) * mm,
                    concise(compact_doc_label(document), 20),
                )

        c.showPage()
    c.save()


def step_demo_id(step_number: int) -> str:
    return f"SIP-STP{step_number:02d}-DEMO"


def planning_change_lines(change: dict) -> List[str]:
    lines = textwrap.wrap(
        change["change"],
        width=70,
        break_long_words=False,
        break_on_hyphens=False,
    )
    if not lines or len(lines) > 3:
        raise SystemExit(
            f"Planning change does not fit a step card: {change['change']!r}"
        )
    return lines


def planning_changes_height(changes: List[dict]) -> float:
    if not changes:
        return 0.0
    body = 0.0
    for change in changes:
        body += max(5.4, len(planning_change_lines(change)) * 2.6 + 0.9)
    return 8.5 + body + 2.0


def activities_by_lane(board: dict) -> List[Tuple[str, List[dict]]]:
    grouped: Dict[str, List[dict]] = {}
    for activity in board["activities"]:
        grouped.setdefault(activity["lane"], []).append(activity)
    return [(lane, grouped[lane]) for lane in LANES if grouped.get(lane)]


def lane_height(activity_count: int) -> float:
    rows = math.ceil(activity_count / STEP_CARD_COLS)
    return (
        STEP_LANE_HEADER_H
        + 1.3
        + rows * STEP_CARD_H
        + max(0, rows - 1) * STEP_CARD_GAP
        + 1.3
    )


def step_card_meta(activity: dict) -> str:
    parts: List[str] = []
    if activity.get("estimate_project_days"):
        parts.append(f"~{activity['estimate_project_days']}d")
    if activity.get("depends_on"):
        parts.append("after " + ",".join(activity["depends_on"]))
    if activity.get("note"):
        parts.append(concise(activity["note"], 30))
    return " | ".join(parts)


def render_step_svg(board: dict, step: Step, path: Path) -> None:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{A4_P_W_MM}mm" '
        f'height="{A4_P_H_MM}mm" viewBox="0 0 {A4_P_W_MM} {A4_P_H_MM}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]
    svg_text(
        parts,
        MARGIN_MM,
        10.0,
        wrap(f"SIP Step {step.number} — {step.title}", 82, 2),
        4.0,
        anchor="start",
        weight="bold",
    )
    svg_text(
        parts,
        MARGIN_MM,
        17.0,
        [
            f"{step.status.upper()} | ~{step.estimate_days} roadmap project days | "
            f"target {step.target_date.strftime('%d %b %Y')}"
        ],
        2.9,
        anchor="start",
        weight="bold",
        fill="#555",
    )
    svg_text(
        parts,
        MARGIN_MM,
        24.0,
        wrap(step.goal, 75, 3),
        2.7,
        anchor="start",
        fill="#555",
    )

    demo = step.demo_bullets
    usable_w = A4_P_W_MM - 2 * MARGIN_MM
    if demo:
        demo_top = 34.0
        demo_h = 27.0
        parts.append(
            f'<rect x="{MARGIN_MM}" y="{demo_top}" width="{usable_w}" height="{demo_h}" '
            'rx="1.5" fill="#f6f8fa" stroke="#6c8ebf" stroke-width="0.45"/>'
        )
        svg_text(
            parts,
            MARGIN_MM + 3,
            demo_top + 5.5,
            [f"END DEMO · {step_demo_id(step.number)}"],
            2.55,
            anchor="start",
            weight="bold",
            fill="#4f81bd",
        )
        cursor = demo_top + 10.5
        for bullet in demo:
            lines = wrap(bullet, 71, 2)
            svg_text(
                parts,
                MARGIN_MM + 4,
                cursor,
                ["• " + lines[0]] + ["  " + line for line in lines[1:]],
                2.2,
                anchor="start",
                fill="#333",
            )
            cursor += len(lines) * 2.65 + 0.9
        docs_top = demo_top + demo_h + 4.0
    else:
        docs_top = 34.0

    docs = step.documents
    docs_h = 25.0 if len(docs) > 4 else 19.0
    parts.append(
        f'<rect x="{MARGIN_MM}" y="{docs_top}" width="{usable_w}" height="{docs_h}" '
        'rx="1.5" fill="#fafafa" stroke="#999" stroke-width="0.4"/>'
    )
    svg_text(
        parts,
        MARGIN_MM + 3,
        docs_top + 5.5,
        ["DOCUMENTATION"],
        2.55,
        anchor="start",
        weight="bold",
        fill="#444",
    )
    doc_col_w = (usable_w - 9) / 2
    for idx, document in enumerate(docs):
        row, col = divmod(idx, 2)
        x = MARGIN_MM + 3 + col * (doc_col_w + 3)
        y = docs_top + 8.0 + row * 6.4
        style = MATURITY[document["maturity"]]
        label = (
            f"{document['name']} {style['label']}{document['completeness']} — "
            f"{concise(document['title'], 27)}"
        )
        svg_text(
            parts,
            x,
            y + 2.1,
            [label],
            2.2,
            anchor="start",
            weight="bold",
            fill=style["stroke"],
        )

    y = docs_top + docs_h + 4.0
    card_w = (usable_w - STEP_CARD_GAP * (STEP_CARD_COLS - 1)) / STEP_CARD_COLS
    lanes = activities_by_lane(board)
    changes = board.get("planning_changes", [])
    changes_h = planning_changes_height(changes)
    total_h = sum(lane_height(len(items)) for _, items in lanes)
    total_h += STEP_LANE_GAP * max(0, len(lanes) - 1)
    reserved_changes_h = changes_h + (2.5 if changes else 0.0)
    available_h = A4_P_H_MM - y - 4.0 - reserved_changes_h
    if total_h > available_h:
        raise SystemExit(
            f"Step {step.number} A4 board does not fit: needs {total_h:.1f} mm, "
            f"has {available_h:.1f} mm"
        )

    for lane, activities in lanes:
        title, lane_fill, lane_stroke = LANES[lane]
        height = lane_height(len(activities))
        parts.append(
            f'<rect x="{MARGIN_MM}" y="{y:.2f}" width="{usable_w:.2f}" height="{height:.2f}" '
            f'rx="1.5" fill="#ffffff" stroke="{lane_stroke}" stroke-width="0.45"/>'
        )
        parts.append(
            f'<rect x="{MARGIN_MM}" y="{y:.2f}" width="{usable_w:.2f}" '
            f'height="{STEP_LANE_HEADER_H:.2f}" rx="1.5" fill="{lane_fill}" '
            f'stroke="{lane_stroke}" stroke-width="0.35"/>'
        )
        svg_text(
            parts,
            MARGIN_MM + 2.5,
            y + 4.15,
            [title],
            2.55,
            anchor="start",
            weight="bold",
            fill=lane_stroke,
        )

        cards_top = y + STEP_LANE_HEADER_H + 1.3
        for idx, activity in enumerate(activities):
            row, col = divmod(idx, STEP_CARD_COLS)
            card_x = MARGIN_MM + col * (card_w + STEP_CARD_GAP)
            card_y = cards_top + row * (STEP_CARD_H + STEP_CARD_GAP)
            status_label, status_fill, status_stroke = STATE_STYLE[activity["state"]]
            parts.append(
                f'<rect x="{card_x:.2f}" y="{card_y:.2f}" width="{card_w:.2f}" '
                f'height="{STEP_CARD_H:.2f}" rx="1.2" fill="#fffdf2" '
                f'stroke="{status_stroke}" stroke-width="0.45"/>'
            )
            svg_text(
                parts,
                card_x + 1.6,
                card_y + 4.7,
                [activity["id"]],
                2.3,
                anchor="start",
                weight="bold",
                fill="#555",
            )
            badge_w = 16.0
            parts.append(
                f'<rect x="{card_x+card_w-badge_w-1.2:.2f}" y="{card_y+1.0:.2f}" '
                f'width="{badge_w:.2f}" height="5.0" rx="0.8" fill="{status_fill}" '
                f'stroke="{status_stroke}" stroke-width="0.25"/>'
            )
            svg_text(
                parts,
                card_x + card_w - badge_w / 2 - 1.2,
                card_y + 4.55,
                [status_label],
                1.9,
                weight="bold",
                fill=status_stroke,
            )
            svg_text(
                parts,
                card_x + card_w / 2,
                card_y + 9.5,
                wrap(activity["title"], 22, 3),
                3.0,
                weight="bold",
            )
            meta = step_card_meta(activity)
            if meta:
                svg_text(
                    parts,
                    card_x + 1.6,
                    card_y + STEP_CARD_H - 1.8,
                    [concise(meta, 34)],
                    2.2,
                    anchor="start",
                    fill="#555",
                )
        y += height + STEP_LANE_GAP

    if changes:
        change_top = y + 1.0
        parts.append(
            f'<rect x="{MARGIN_MM}" y="{change_top:.2f}" width="{usable_w:.2f}" '
            f'height="{changes_h:.2f}" rx="1.5" fill="#fafafa" '
            'stroke="#999999" stroke-width="0.4"/>'
        )
        svg_text(
            parts,
            MARGIN_MM + 3,
            change_top + 5.4,
            ["PLANNING CHANGES"],
            2.55,
            anchor="start",
            weight="bold",
            fill="#555555",
        )
        cursor = change_top + 10.0
        for change in changes:
            lines = planning_change_lines(change)
            svg_text(
                parts,
                MARGIN_MM + 4,
                cursor,
                [change["date"]],
                2.0,
                anchor="start",
                weight="bold",
                fill="#6c8ebf",
            )
            svg_text(
                parts,
                MARGIN_MM + 24,
                cursor,
                lines,
                2.15,
                anchor="start",
                fill="#333333",
            )
            cursor += max(5.4, len(lines) * 2.6 + 0.9)

    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def write_readme(out_dir: Path, boards: Dict[int, dict]) -> None:
    lines = [
        "# Generated SIP planning",
        "",
        "All files below are generated from the same SIP/YAML planning sources.",
        "",
        "- [Continuous roadmap](./sip-roadmap.svg) — all roadmap pages side by side.",
        "- [Roadmap PDF](./sip-roadmap.pdf) — four A4-landscape pages.",
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
    groups = roadmap_groups(steps)

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

    render_roadmap_svgs(groups, out_dir)
    render_roadmap_pdf(groups, out_dir / "sip-roadmap.pdf")

    for number, board in sorted(boards.items()):
        render_step_svg(
            board,
            by_number[number],
            out_dir / "steps" / f"step-{number:02d}.svg",
        )

    write_readme(out_dir, boards)


if __name__ == "__main__":
    main()