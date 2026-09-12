#!/usr/bin/env python3
"""Generate SIP overview and A3 step boards from declarative YAML sources.

Source ownership:
- docs/11-SIP-software-implementation-planning.md owns human-readable step
  meaning, deliverable and demonstration.
- docs/_data/sip-roadmap.yaml owns estimates/cadence and overview planning.
- docs/_data/sip-steps/step-NN.yaml owns detailed activity-board data.
- docs/_data/schemas/*.schema.json validates the YAML data model.

The SVG, draw.io and PDF files are generated outputs, never planning sources.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple
import argparse
import html
import json
import math
import re
import textwrap
import xml.etree.ElementTree as ET

import yaml
from jsonschema import Draft202012Validator, FormatChecker
from reportlab.lib.pagesizes import A2, A3, landscape, portrait
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


A3_L_W_MM, A3_L_H_MM = 420.0, 297.0
A3_P_W_MM, A3_P_H_MM = 297.0, 420.0
OVERVIEW_TILE_COUNT = 3
OVERVIEW_W_MM = A3_L_W_MM * OVERVIEW_TILE_COUNT
OVERVIEW_H_MM = A3_L_H_MM
MARGIN_MM = 12.0
TIMELINE_Y_MM = 48.0

STEP_MARGIN_MM = 10.0
STEP_LANE_LABEL_W_MM = 29.0
STEP_CARD_GAP_MM = 4.0
STEP_CARD_H_MM = 27.0
STEP_CARD_COLS = 4

MATURITY = {
    "outline": {"label": "O", "long": "OUTLINE", "fill": "#f2f2f2", "stroke": "#808080"},
    "working": {"label": "W", "long": "WORKING", "fill": "#ddebf7", "stroke": "#5b9bd5"},
    "review": {"label": "R", "long": "REVIEW", "fill": "#fff2cc", "stroke": "#bf9000"},
    "accepted": {"label": "A", "long": "ACCEPTED", "fill": "#e2f0d9", "stroke": "#70ad47"},
}

WORKSTREAMS = {
    "architecture": ("Architecture / planning", "#d9e8fb", "#4f81bd"),
    "application": ("Application", "#d9ead3", "#6aa84f"),
    "platform": ("Platform / deployment", "#e2f0d9", "#70ad47"),
    "client": ("Clients / interfaces", "#fff2cc", "#c9a227"),
    "test": ("Test / simulation", "#d9d2e9", "#674ea7"),
    "extension": ("Extension / private", "#eadcf8", "#8e62b3"),
    "domain": ("Domain / data", "#fce4d6", "#c55a11"),
    "hardware": ("Hardware", "#f4cccc", "#a61c00"),
    "backoffice": ("Backoffice", "#d0e0e3", "#3d85c6"),
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

FAMILY_LABELS = {
    "requirements": "REQ/SRD",
    "idd": "IDD",
    "design": "SAD/SDD",
    "verification": "SVP",
}


@dataclass(frozen=True)
class DocGate:
    level: str
    scope: str


@dataclass(frozen=True)
class Step:
    number: int
    title: str
    deliverable: str
    demonstration: str
    estimate_days: int
    workstream: str
    target_date: date
    docs: Dict[str, DocGate]


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
    if errors:
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
        docs = {
            key: DocGate(level=value["level"], scope=value["scope"])
            for key, value in cfg["docs"].items()
        }
        steps.append(
            Step(
                number=number,
                title=match.group(2).strip(),
                deliverable=concise(extract_subsection(body, "Deliverable"), 170) or "Deliverable to be refined.",
                demonstration=concise(extract_subsection(body, "Demonstration"), 170) or "Demonstration to be refined.",
                estimate_days=estimate,
                workstream=cfg.get("workstream", "architecture"),
                target_date=target,
                docs=docs,
            )
        )
    return steps


def load_step_boards(data_dir: Path, schema: dict) -> Dict[int, dict]:
    result: Dict[int, dict] = {}
    step_dir = data_dir / "sip-steps"
    for path in sorted(step_dir.glob("step-*.yaml")):
        data = load_yaml(path)
        validate_data(data, schema, path)
        step_number = int(data["step"])
        if step_number in result:
            raise SystemExit(f"Duplicate step-board source for Step {step_number}")
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
        result[step_number] = data
    return result


def partition_steps(steps: List[Step], groups: int = OVERVIEW_TILE_COUNT) -> List[List[Step]]:
    count = len(steps)
    if count < groups:
        raise SystemExit("Roadmap has fewer steps than print tiles")
    prefix = [0]
    for step in steps:
        prefix.append(prefix[-1] + step.estimate_days)
    ideal = prefix[-1] / groups
    infinity = float("inf")
    scores = [[infinity] * (count + 1) for _ in range(groups + 1)]
    previous: List[List[Optional[int]]] = [[None] * (count + 1) for _ in range(groups + 1)]
    scores[0][0] = 0.0
    for group in range(1, groups + 1):
        for end in range(group, count + 1):
            for start in range(group - 1, end):
                if scores[group - 1][start] == infinity:
                    continue
                segment = prefix[end] - prefix[start]
                score = scores[group - 1][start] + (segment - ideal) ** 2
                if score < scores[group][end]:
                    scores[group][end] = score
                    previous[group][end] = start
    output: List[List[Step]] = []
    end = count
    for group in range(groups, 0, -1):
        start = previous[group][end]
        if start is None:
            raise SystemExit("Unable to partition roadmap")
        output.append(steps[start:end])
        end = start
    return list(reversed(output))


def overview_positions(group: List[Step], page_index: int) -> List[Tuple[Step, float, float]]:
    page_x = page_index * A3_L_W_MM
    usable = A3_L_W_MM - 2 * MARGIN_MM
    cell = usable / len(group)
    return [
        (
            step,
            page_x + MARGIN_MM + cell * (index + 0.5),
            min(108.0, cell - 5.0),
        )
        for index, step in enumerate(group)
    ]


def document_indicators(step: Step, board: Optional[dict]) -> List[dict]:
    if board:
        return board["documents"]
    return [
        {
            "name": FAMILY_LABELS[family],
            "title": step.docs[family].scope,
            "maturity": step.docs[family].level,
            "completeness": None,
        }
        for family in ("requirements", "idd", "design", "verification")
    ]


def compact_doc_label(document: dict) -> str:
    maturity = MATURITY[document["maturity"]]["label"]
    completeness = document.get("completeness")
    suffix = maturity if completeness is None else f"{maturity}{int(completeness)}"
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
        dy = 0 if index == 0 else size * 1.22
        parts.append(
            f'<tspan x="{x:.2f}" dy="{dy:.2f}">{html.escape(str(line))}</tspan>'
        )
    parts.append("</text>")


def render_overview_svg(
    steps: List[Step], groups: List[List[Step]], boards: Dict[int, dict], plan: dict, path: Path
) -> None:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{OVERVIEW_W_MM}mm" height="{OVERVIEW_H_MM}mm" '
        f'viewBox="0 0 {OVERVIEW_W_MM} {OVERVIEW_H_MM}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]
    for page in range(OVERVIEW_TILE_COUNT):
        page_x = page * A3_L_W_MM
        parts.append(
            f'<rect x="{page_x}" y="0" width="{A3_L_W_MM}" height="{A3_L_H_MM}" '
            'fill="none" stroke="#d0d0d0" stroke-width="0.35"/>'
        )
        if page:
            parts.append(
                f'<line x1="{page_x}" y1="5" x2="{page_x}" y2="292" '
                'stroke="#999" stroke-width="0.45" stroke-dasharray="3 2"/>'
            )

    svg_text(parts, 15, 13, ["Software Implementation Planning — roadmap"], 7, anchor="start", weight="bold")
    svg_text(
        parts,
        15,
        21,
        ["Milestone map; not a Gantt. Documentation stays compact here; activity detail lives on A3 step boards."],
        2.9,
        anchor="start",
        fill="#555",
    )
    parts.append(
        f'<line x1="10" y1="{TIMELINE_Y_MM}" x2="{OVERVIEW_W_MM-10}" y2="{TIMELINE_Y_MM}" '
        'stroke="#333" stroke-width="0.9"/>'
    )

    for page_index, group in enumerate(groups):
        for step, center_x, width in overview_positions(group, page_index):
            _label, work_fill, work_stroke = WORKSTREAMS.get(
                step.workstream, WORKSTREAMS["architecture"]
            )
            radius = 4.4
            points = (
                f"{center_x},{TIMELINE_Y_MM-radius} {center_x+radius},{TIMELINE_Y_MM} "
                f"{center_x},{TIMELINE_Y_MM+radius} {center_x-radius},{TIMELINE_Y_MM}"
            )
            parts.append(
                f'<polygon points="{points}" fill="white" stroke="#333" stroke-width="0.7"/>'
            )
            svg_text(parts, center_x, TIMELINE_Y_MM + 1.0, [step.number], 2.8, weight="bold")
            parts.append(
                f'<line x1="{center_x}" y1="{TIMELINE_Y_MM+4.4}" x2="{center_x}" y2="222" '
                'stroke="#888" stroke-width="0.35"/>'
            )
            svg_text(
                parts,
                center_x,
                34,
                [f"~{step.estimate_days} project days", f"target {step.target_date.strftime('%d %b %Y')}"],
                2.45,
                weight="bold",
                fill=work_stroke,
            )
            svg_text(parts, center_x, 61, wrap(f"Step {step.number} — {step.title}", 28, 3), 2.9, weight="bold")

            x = center_x - width / 2
            parts.append(
                f'<rect x="{x:.2f}" y="81" width="{width:.2f}" height="46" rx="2" '
                f'fill="{work_fill}" stroke="{work_stroke}" stroke-width="0.7"/>'
            )
            svg_text(parts, x + 3, 89, ["DELIVERABLE"], 2.3, anchor="start", weight="bold", fill=work_stroke)
            svg_text(parts, center_x, 98, wrap(step.deliverable, max(18, int(width / 2.2)), 7), 2.05)

            parts.append(
                f'<rect x="{x:.2f}" y="135" width="{width:.2f}" height="49" rx="2" '
                f'fill="#ffffff" stroke="{work_stroke}" stroke-width="0.7"/>'
            )
            svg_text(parts, x + 3, 143, ["DEMONSTRATION"], 2.3, anchor="start", weight="bold", fill=work_stroke)
            svg_text(parts, center_x, 152, wrap(step.demonstration, max(18, int(width / 2.2)), 7), 2.0)

            documents = document_indicators(step, boards.get(step.number))
            parts.append(
                f'<rect x="{x:.2f}" y="192" width="{width:.2f}" height="29" rx="2" '
                'fill="#fafafa" stroke="#999" stroke-width="0.45"/>'
            )
            svg_text(parts, x + 3, 199, ["DOCUMENTS"], 2.05, anchor="start", weight="bold", fill="#555")
            labels = [compact_doc_label(item) for item in documents[:6]]
            col_w = (width - 6) / 2
            for idx, label in enumerate(labels):
                row = idx // 2
                col = idx % 2
                chip_x = x + 2.5 + col * (col_w + 1)
                chip_y = 202.5 + row * 5.4
                document = documents[idx]
                style = MATURITY[document["maturity"]]
                parts.append(
                    f'<rect x="{chip_x:.2f}" y="{chip_y:.2f}" width="{col_w:.2f}" height="4.6" rx="1" '
                    f'fill="{style["fill"]}" stroke="{style["stroke"]}" stroke-width="0.3"/>'
                )
                svg_text(
                    parts,
                    chip_x + col_w / 2,
                    chip_y + 3.1,
                    [concise(label, 19)],
                    1.45,
                    weight="bold",
                    fill=style["stroke"],
                )

    total = sum(item.estimate_days for item in steps)
    reserve = float(plan.get("planning_reserve_fraction", 0))
    reserve_end = date.fromisoformat(str(plan["start_date"])) + timedelta(
        days=round(
            total
            * (1 + reserve)
            / float(plan["cadence_project_days_per_week"])
            * 7
        )
    )
    svg_text(
        parts,
        15,
        279,
        [
            f"Baseline {total} project days → {steps[-1].target_date.strftime('%d %b %Y')} | "
            f"+{int(reserve*100)}% reserve → about {reserve_end.strftime('%d %b %Y')}"
        ],
        2.5,
        anchor="start",
        weight="bold",
        fill="#444",
    )
    for page_index, group in enumerate(groups):
        page_x = page_index * A3_L_W_MM
        svg_text(
            parts,
            page_x + A3_L_W_MM / 2,
            290,
            [
                f"A3 tile {page_index+1}/3 — Steps {group[0].number}-{group[-1].number} "
                "— print at 100% / actual size"
            ],
            2.35,
            weight="bold",
            fill="#555",
        )
        if page_index < 2:
            svg_text(parts, page_x + A3_L_W_MM - 4, 279, ["JOIN →"], 2.0, anchor="end", weight="bold", fill="#777")
        if page_index > 0:
            svg_text(parts, page_x + 4, 279, ["← JOIN"], 2.0, anchor="start", weight="bold", fill="#777")
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def drawio_vertex(
    root: ET.Element,
    cell_id: str,
    value: str,
    x: float,
    y: float,
    width: float,
    height: float,
    style: str,
) -> None:
    cell = ET.SubElement(
        root, "mxCell", id=cell_id, value=value, style=style, vertex="1", parent="1"
    )
    ET.SubElement(
        cell,
        "mxGeometry",
        x=f"{x:.2f}",
        y=f"{y:.2f}",
        width=f"{width:.2f}",
        height=f"{height:.2f}",
        **{"as": "geometry"},
    )


def render_overview_drawio(
    groups: List[List[Step]], boards: Dict[int, dict], path: Path
) -> None:
    mxfile = ET.Element(
        "mxfile", host="app.diagrams.net", agent="sip-planning-generator", type="device"
    )
    diagram = ET.SubElement(mxfile, "diagram", id="sip-roadmap", name="SIP roadmap")
    model = ET.SubElement(
        diagram,
        "mxGraphModel",
        dx="1800",
        dy="900",
        grid="1",
        gridSize="10",
        guides="1",
        page="1",
        pageScale="1",
        pageWidth=str(OVERVIEW_W_MM),
        pageHeight=str(OVERVIEW_H_MM),
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")
    drawio_vertex(
        root,
        "title",
        "Software Implementation Planning — roadmap",
        15,
        7,
        500,
        15,
        "text;html=1;strokeColor=none;fillColor=none;fontSize=18;fontStyle=1;align=left;",
    )
    for page_index, group in enumerate(groups):
        for step, center_x, width in overview_positions(group, page_index):
            _label, fill, stroke = WORKSTREAMS.get(
                step.workstream, WORKSTREAMS["architecture"]
            )
            drawio_vertex(
                root,
                f"gate-{step.number}",
                str(step.number),
                center_x - 4.5,
                TIMELINE_Y_MM - 4.5,
                9,
                9,
                "rhombus;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#333333;fontStyle=1;",
            )
            drawio_vertex(
                root,
                f"meta-{step.number}",
                f"~{step.estimate_days} project days<br>target {step.target_date.strftime('%d %b %Y')}",
                center_x - width / 2,
                28,
                width,
                18,
                f"text;html=1;strokeColor=none;fillColor=none;fontSize=8;fontStyle=1;fontColor={stroke};align=center;",
            )
            drawio_vertex(
                root,
                f"step-title-{step.number}",
                html.escape(f"Step {step.number} — {step.title}"),
                center_x - width / 2,
                57,
                width,
                20,
                "text;html=1;strokeColor=none;fillColor=none;fontSize=8;fontStyle=1;align=center;whiteSpace=wrap;",
            )
            drawio_vertex(
                root,
                f"deliverable-{step.number}",
                f"<b>DELIVERABLE</b><br>{html.escape(step.deliverable)}",
                center_x - width / 2,
                81,
                width,
                46,
                f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};fontSize=7;align=center;verticalAlign=top;spacingTop=4;",
            )
            drawio_vertex(
                root,
                f"demo-{step.number}",
                f"<b>DEMONSTRATION</b><br>{html.escape(step.demonstration)}",
                center_x - width / 2,
                135,
                width,
                49,
                f"rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor={stroke};fontSize=7;align=center;verticalAlign=top;spacingTop=4;",
            )
            documents = document_indicators(step, boards.get(step.number))
            doc_text = "<b>DOCUMENTS</b><br>" + " &nbsp; ".join(
                html.escape(compact_doc_label(item)) for item in documents[:6]
            )
            drawio_vertex(
                root,
                f"docs-{step.number}",
                doc_text,
                center_x - width / 2,
                192,
                width,
                29,
                "rounded=1;whiteSpace=wrap;html=1;fillColor=#fafafa;strokeColor=#999999;fontSize=6;align=left;verticalAlign=top;spacing=4;",
            )
    ET.ElementTree(mxfile).write(path, encoding="utf-8", xml_declaration=True)


def pdf_lines(
    c: canvas.Canvas,
    center_x_mm: float,
    y_mm: float,
    lines: Iterable[str],
    font: str,
    size: float,
    leading_mm: float,
) -> None:
    c.setFont(font, size)
    for line in lines:
        c.drawCentredString(center_x_mm * mm, y_mm * mm, str(line))
        y_mm -= leading_mm


def render_overview_a3_pdf(
    groups: List[List[Step]], boards: Dict[int, dict], path: Path
) -> None:
    c = canvas.Canvas(str(path), pagesize=landscape(A3))
    for page_index, group in enumerate(groups):
        c.setFont("Helvetica-Bold", 18)
        c.drawString(12 * mm, (A3_L_H_MM - 14) * mm, "Software Implementation Planning — roadmap")
        c.setFont("Helvetica", 8)
        c.drawString(
            12 * mm,
            (A3_L_H_MM - 22) * mm,
            "Milestone map; documentation is compact. Detailed activities are on A3 portrait step boards.",
        )
        c.line(
            10 * mm,
            (A3_L_H_MM - TIMELINE_Y_MM) * mm,
            (A3_L_W_MM - 10) * mm,
            (A3_L_H_MM - TIMELINE_Y_MM) * mm,
        )
        for step, center_x, width in overview_positions(group, 0):
            c.setFont("Helvetica-Bold", 7)
            c.drawCentredString(
                center_x * mm,
                (A3_L_H_MM - 35) * mm,
                f"~{step.estimate_days} days | {step.target_date.strftime('%d %b %Y')}",
            )
            pdf_lines(
                c,
                center_x,
                A3_L_H_MM - 62,
                wrap(f"Step {step.number} — {step.title}", 28, 3),
                "Helvetica-Bold",
                7.8,
                3.4,
            )
            x = center_x - width / 2
            c.roundRect(x * mm, (A3_L_H_MM - 127) * mm, width * mm, 46 * mm, 2 * mm, stroke=1, fill=0)
            c.setFont("Helvetica-Bold", 6.5)
            c.drawString((x + 3) * mm, (A3_L_H_MM - 90) * mm, "DELIVERABLE")
            pdf_lines(c, center_x, A3_L_H_MM - 99, wrap(step.deliverable, max(18, int(width / 2.2)), 7), "Helvetica", 6.1, 3.1)
            c.roundRect(x * mm, (A3_L_H_MM - 184) * mm, width * mm, 49 * mm, 2 * mm, stroke=1, fill=0)
            c.setFont("Helvetica-Bold", 6.5)
            c.drawString((x + 3) * mm, (A3_L_H_MM - 144) * mm, "DEMONSTRATION")
            pdf_lines(c, center_x, A3_L_H_MM - 153, wrap(step.demonstration, max(18, int(width / 2.2)), 7), "Helvetica", 5.9, 3.0)
            documents = document_indicators(step, boards.get(step.number))
            c.roundRect(x * mm, (A3_L_H_MM - 221) * mm, width * mm, 29 * mm, 2 * mm, stroke=1, fill=0)
            c.setFont("Helvetica-Bold", 5.6)
            c.drawString((x + 3) * mm, (A3_L_H_MM - 199) * mm, "DOCUMENTS")
            doc_lines = wrap(
                " | ".join(compact_doc_label(item) for item in documents[:6]),
                max(20, int(width / 1.8)),
                3,
            )
            pdf_lines(c, center_x, A3_L_H_MM - 205, doc_lines, "Helvetica", 4.9, 2.7)
        c.setFont("Helvetica-Bold", 6.2)
        c.drawCentredString(
            A3_L_W_MM / 2 * mm,
            7 * mm,
            f"A3 tile {page_index+1}/3 — Steps {group[0].number}-{group[-1].number} — PRINT AT 100% / ACTUAL SIZE",
        )
        c.showPage()
    c.save()


def render_overview_a2_pdf(
    steps: List[Step], boards: Dict[int, dict], path: Path
) -> None:
    c = canvas.Canvas(str(path), pagesize=landscape(A2))
    page_w = landscape(A2)[0] / mm
    page_h = landscape(A2)[1] / mm
    c.setFont("Helvetica-Bold", 18)
    c.drawString(12 * mm, (page_h - 14) * mm, "Software Implementation Planning — compact overview")
    columns = 4
    rows = math.ceil(len(steps) / columns)
    cell_w = (page_w - 24) / columns
    cell_h = (page_h - 36) / rows
    for index, step in enumerate(steps):
        row, col = divmod(index, columns)
        x = 12 + col * cell_w
        top = page_h - 26 - row * cell_h
        c.roundRect(
            x * mm,
            (top - cell_h + 3) * mm,
            (cell_w - 4) * mm,
            (cell_h - 5) * mm,
            2 * mm,
            stroke=1,
            fill=0,
        )
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString((x + 3) * mm, (top - 6) * mm, f"Step {step.number} — {concise(step.title, 38)}")
        c.setFont("Helvetica", 5.8)
        c.drawString((x + 3) * mm, (top - 12) * mm, f"~{step.estimate_days} project days | target {step.target_date.strftime('%d %b %Y')}")
        documents = document_indicators(step, boards.get(step.number))
        c.drawString(
            (x + 3) * mm,
            (top - 18) * mm,
            "Docs: " + concise(" | ".join(compact_doc_label(item) for item in documents[:5]), 72),
        )
        pdf_lines(c, x + cell_w / 2 - 2, top - 27, wrap(step.deliverable, 52, 4), "Helvetica", 5.6, 3.0)
    c.save()


def lane_layout(board: dict) -> List[Tuple[str, List[dict], float]]:
    by_lane: Dict[str, List[dict]] = {key: [] for key in LANES}
    for activity in board["activities"]:
        by_lane.setdefault(activity["lane"], []).append(activity)
    result = []
    for lane in ("tooling", "application", "verification", "platform", "documentation"):
        activities = by_lane.get(lane, [])
        if not activities:
            continue
        rows = math.ceil(len(activities) / STEP_CARD_COLS)
        height = 10 + rows * (STEP_CARD_H_MM + 4)
        result.append((lane, activities, height))
    return result


def step_card_meta(activity: dict) -> str:
    parts = []
    if activity.get("estimate_project_days"):
        parts.append(f"~{activity['estimate_project_days']}d")
    if activity.get("depends_on"):
        parts.append("after " + ",".join(activity["depends_on"]))
    if activity.get("note"):
        parts.append(concise(activity["note"], 30))
    return " | ".join(parts)


def render_step_svg(board: dict, step: Step, path: Path) -> None:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{A3_P_W_MM}mm" height="{A3_P_H_MM}mm" '
        f'viewBox="0 0 {A3_P_W_MM} {A3_P_H_MM}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]
    svg_text(parts, STEP_MARGIN_MM, 15, [f"SIP Step {step.number} — {board['title']}"], 6.5, anchor="start", weight="bold")
    svg_text(
        parts,
        STEP_MARGIN_MM,
        23,
        [f"State {board['state'].upper()} | ~{step.estimate_days} roadmap project days | target {step.target_date.strftime('%d %b %Y')}"],
        2.8,
        anchor="start",
        weight="bold",
        fill="#555",
    )
    svg_text(parts, STEP_MARGIN_MM, 30, wrap(board.get("summary", ""), 105, 2), 2.5, anchor="start", fill="#555")

    docs_top = 40.0
    parts.append(
        f'<rect x="{STEP_MARGIN_MM}" y="{docs_top}" width="{A3_P_W_MM-2*STEP_MARGIN_MM}" height="46" '
        'rx="2" fill="#fafafa" stroke="#999" stroke-width="0.45"/>'
    )
    svg_text(parts, STEP_MARGIN_MM + 4, docs_top + 8, ["DOCUMENTATION — maturity / completeness for this step"], 2.7, anchor="start", weight="bold", fill="#444")
    docs = board["documents"]
    col_w = (A3_P_W_MM - 2 * STEP_MARGIN_MM - 8) / 2
    for idx, document in enumerate(docs):
        row, col = divmod(idx, 2)
        x = STEP_MARGIN_MM + 4 + col * col_w
        y = docs_top + 13 + row * 10.0
        style = MATURITY[document["maturity"]]
        parts.append(
            f'<rect x="{x:.2f}" y="{y:.2f}" width="{col_w-4:.2f}" height="8.2" rx="1.2" '
            f'fill="{style["fill"]}" stroke="{style["stroke"]}" stroke-width="0.35"/>'
        )
        svg_text(parts, x + 2, y + 3.2, [document["name"]], 2.0, anchor="start", weight="bold", fill=style["stroke"])
        svg_text(parts, x + 2, y + 6.1, [concise(document["title"], 43)], 1.65, anchor="start", fill="#333")
        svg_text(parts, x + col_w - 7, y + 4.5, [f"{style['label']} {document['completeness']}%"], 1.9, anchor="end", weight="bold", fill=style["stroke"])

    y = 92.0
    content_x = STEP_MARGIN_MM + STEP_LANE_LABEL_W_MM
    content_w = A3_P_W_MM - STEP_MARGIN_MM - content_x
    card_w = (content_w - STEP_CARD_GAP_MM * (STEP_CARD_COLS - 1)) / STEP_CARD_COLS
    for lane, activities, lane_h in lane_layout(board):
        title, lane_fill, lane_stroke = LANES[lane]
        parts.append(
            f'<rect x="{STEP_MARGIN_MM}" y="{y:.2f}" width="{A3_P_W_MM-2*STEP_MARGIN_MM}" height="{lane_h:.2f}" '
            f'rx="2" fill="#ffffff" stroke="{lane_stroke}" stroke-width="0.55"/>'
        )
        parts.append(
            f'<rect x="{STEP_MARGIN_MM}" y="{y:.2f}" width="{STEP_LANE_LABEL_W_MM-2}" height="{lane_h:.2f}" '
            f'rx="2" fill="{lane_fill}" stroke="{lane_stroke}" stroke-width="0.45"/>'
        )
        svg_text(parts, STEP_MARGIN_MM + (STEP_LANE_LABEL_W_MM - 2) / 2, y + 8, wrap(title, 18, 4), 2.25, weight="bold", fill=lane_stroke)
        for idx, activity in enumerate(activities):
            row, col = divmod(idx, STEP_CARD_COLS)
            card_x = content_x + col * (card_w + STEP_CARD_GAP_MM)
            card_y = y + 6 + row * (STEP_CARD_H_MM + 4)
            status_label, status_fill, status_stroke = STATE_STYLE[activity["state"]]
            parts.append(
                f'<rect x="{card_x:.2f}" y="{card_y:.2f}" width="{card_w:.2f}" height="{STEP_CARD_H_MM:.2f}" '
                f'rx="1.5" fill="#fffdf2" stroke="{status_stroke}" stroke-width="0.6"/>'
            )
            svg_text(parts, card_x + 2, card_y + 4.2, [activity["id"]], 1.7, anchor="start", weight="bold", fill="#555")
            badge_w = 15.5
            parts.append(
                f'<rect x="{card_x+card_w-badge_w-1.5:.2f}" y="{card_y+1.2:.2f}" width="{badge_w:.2f}" height="4.7" '
                f'rx="1" fill="{status_fill}" stroke="{status_stroke}" stroke-width="0.3"/>'
            )
            svg_text(parts, card_x + card_w - badge_w / 2 - 1.5, card_y + 4.3, [status_label], 1.4, weight="bold", fill=status_stroke)
            svg_text(parts, card_x + card_w / 2, card_y + 10, wrap(activity["title"], 23, 3), 1.95, weight="bold")
            meta = step_card_meta(activity)
            if meta:
                svg_text(parts, card_x + 2, card_y + STEP_CARD_H_MM - 2.7, [concise(meta, 43)], 1.35, anchor="start", fill="#666")
        y += lane_h + 4

    if y > A3_P_H_MM - 14:
        raise SystemExit(
            f"Step {step.number} board does not fit A3 portrait: content ends at {y:.1f} mm"
        )
    svg_text(parts, STEP_MARGIN_MM, A3_P_H_MM - 7, ["Generated from typed YAML planning data — print at 100% / actual size"], 2.0, anchor="start", fill="#666")
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def render_step_drawio(board: dict, step: Step, path: Path) -> None:
    mxfile = ET.Element(
        "mxfile", host="app.diagrams.net", agent="sip-planning-generator", type="device"
    )
    diagram = ET.SubElement(mxfile, "diagram", id=f"step-{step.number:02d}", name=f"Step {step.number:02d}")
    model = ET.SubElement(
        diagram,
        "mxGraphModel",
        dx="1200",
        dy="1600",
        grid="1",
        gridSize="5",
        guides="1",
        page="1",
        pageScale="1",
        pageWidth=str(A3_P_W_MM),
        pageHeight=str(A3_P_H_MM),
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")
    drawio_vertex(root, "title", html.escape(f"SIP Step {step.number} — {board['title']}"), 10, 7, 277, 15, "text;html=1;strokeColor=none;fillColor=none;fontSize=17;fontStyle=1;align=left;")
    drawio_vertex(root, "summary", html.escape(board.get("summary", "")), 10, 24, 277, 12, "text;html=1;strokeColor=none;fillColor=none;fontSize=7;align=left;whiteSpace=wrap;")
    docs_value = "<b>DOCUMENTATION</b><br>" + "<br>".join(
        f"<b>{html.escape(doc['name'])}</b> — {html.escape(doc['title'])} — {MATURITY[doc['maturity']]['long']} {doc['completeness']}%"
        for doc in board["documents"]
    )
    drawio_vertex(root, "documents", docs_value, 10, 40, 277, 46, "rounded=1;whiteSpace=wrap;html=1;fillColor=#fafafa;strokeColor=#999999;fontSize=6;align=left;verticalAlign=top;spacing=5;")

    y = 92.0
    content_x = STEP_MARGIN_MM + STEP_LANE_LABEL_W_MM
    content_w = A3_P_W_MM - STEP_MARGIN_MM - content_x
    card_w = (content_w - STEP_CARD_GAP_MM * (STEP_CARD_COLS - 1)) / STEP_CARD_COLS
    for lane, activities, lane_h in lane_layout(board):
        title, lane_fill, lane_stroke = LANES[lane]
        drawio_vertex(root, f"lane-{lane}", html.escape(title), 10, y, STEP_LANE_LABEL_W_MM - 2, lane_h, f"rounded=1;whiteSpace=wrap;html=1;fillColor={lane_fill};strokeColor={lane_stroke};fontSize=7;fontStyle=1;align=center;verticalAlign=top;spacingTop=5;")
        for idx, activity in enumerate(activities):
            row, col = divmod(idx, STEP_CARD_COLS)
            x = content_x + col * (card_w + STEP_CARD_GAP_MM)
            card_y = y + 6 + row * (STEP_CARD_H_MM + 4)
            status_label, _status_fill, status_stroke = STATE_STYLE[activity["state"]]
            value = f"<b>{activity['id']} · {status_label}</b><br><b>{html.escape(activity['title'])}</b>"
            meta = step_card_meta(activity)
            if meta:
                value += f"<br><font color='#666666'>{html.escape(meta)}</font>"
            drawio_vertex(root, f"activity-{activity['id']}", value, x, card_y, card_w, STEP_CARD_H_MM, f"rounded=1;whiteSpace=wrap;html=1;fillColor=#fffdf2;strokeColor={status_stroke};fontSize=6;align=center;verticalAlign=top;spacing=4;")
        y += lane_h + 4
    ET.ElementTree(mxfile).write(path, encoding="utf-8", xml_declaration=True)


def render_step_pdf(board: dict, step: Step, path: Path) -> None:
    c = canvas.Canvas(str(path), pagesize=portrait(A3))
    page_h = A3_P_H_MM
    c.setFont("Helvetica-Bold", 17)
    c.drawString(10 * mm, (page_h - 15) * mm, f"SIP Step {step.number} — {board['title']}")
    c.setFont("Helvetica-Bold", 8)
    c.drawString(10 * mm, (page_h - 23) * mm, f"State {board['state'].upper()} | ~{step.estimate_days} roadmap project days | target {step.target_date.strftime('%d %b %Y')}")
    c.setFont("Helvetica", 7)
    c.drawString(10 * mm, (page_h - 31) * mm, concise(board.get("summary", ""), 115))

    c.roundRect(10 * mm, (page_h - 86) * mm, 277 * mm, 46 * mm, 2 * mm, stroke=1, fill=0)
    c.setFont("Helvetica-Bold", 7)
    c.drawString(14 * mm, (page_h - 48) * mm, "DOCUMENTATION — maturity / completeness for this step")
    for idx, document in enumerate(board["documents"]):
        col = idx % 2
        row = idx // 2
        x = 14 + col * 136
        y = page_h - 58 - row * 10
        c.setFont("Helvetica-Bold", 6.2)
        c.drawString(x * mm, y * mm, f"{document['name']}  {MATURITY[document['maturity']]['label']} {document['completeness']}%")
        c.setFont("Helvetica", 5.5)
        c.drawString((x + 26) * mm, y * mm, concise(document["title"], 45))

    y_top = 92.0
    content_x = STEP_MARGIN_MM + STEP_LANE_LABEL_W_MM
    content_w = A3_P_W_MM - STEP_MARGIN_MM - content_x
    card_w = (content_w - STEP_CARD_GAP_MM * (STEP_CARD_COLS - 1)) / STEP_CARD_COLS
    for lane, activities, lane_h in lane_layout(board):
        title, _lane_fill, _lane_stroke = LANES[lane]
        y_pdf = page_h - y_top - lane_h
        c.roundRect(10 * mm, y_pdf * mm, 277 * mm, lane_h * mm, 2 * mm, stroke=1, fill=0)
        pdf_lines(c, 10 + (STEP_LANE_LABEL_W_MM - 2) / 2, page_h - y_top - 9, wrap(title, 18, 4), "Helvetica-Bold", 6.5, 3.3)
        for idx, activity in enumerate(activities):
            row, col = divmod(idx, STEP_CARD_COLS)
            x = content_x + col * (card_w + STEP_CARD_GAP_MM)
            card_y_top = y_top + 6 + row * (STEP_CARD_H_MM + 4)
            c.roundRect(x * mm, (page_h - card_y_top - STEP_CARD_H_MM) * mm, card_w * mm, STEP_CARD_H_MM * mm, 1.5 * mm, stroke=1, fill=0)
            c.setFont("Helvetica-Bold", 5.4)
            c.drawString((x + 2) * mm, (page_h - card_y_top - 5) * mm, f"{activity['id']} · {STATE_STYLE[activity['state']][0]}")
            pdf_lines(c, x + card_w / 2, page_h - card_y_top - 11, wrap(activity["title"], 23, 3), "Helvetica-Bold", 5.8, 3.0)
            meta = step_card_meta(activity)
            if meta:
                c.setFont("Helvetica", 4.4)
                c.drawString((x + 2) * mm, (page_h - card_y_top - STEP_CARD_H_MM + 3) * mm, concise(meta, 43))
        y_top += lane_h + 4
    if y_top > A3_P_H_MM - 14:
        raise SystemExit(f"Step {step.number} PDF content exceeds A3 portrait")
    c.setFont("Helvetica", 6)
    c.drawString(10 * mm, 7 * mm, "Generated from typed YAML planning data — PRINT AT 100% / ACTUAL SIZE")
    c.save()


def write_readme(steps: List[Step], boards: Dict[int, dict], plan: dict, out_dir: Path) -> None:
    total = sum(item.estimate_days for item in steps)
    lines = [
        "# Generated SIP planning",
        "",
        "Generated from the SIP Markdown plus validated YAML planning sources in `docs/_data/`.",
        "Generated SVG/draw.io/PDF files are outputs; edit the YAML sources instead.",
        "",
        "## Overview",
        "",
        "- [Continuous SVG roadmap](./sip-roadmap.svg)",
        "- [Editable draw.io roadmap](./sip-roadmap.drawio)",
        "- [A3 tiled print roadmap](./sip-roadmap-a3-tiled.pdf)",
        "- [A2 compact overview](./sip-roadmap-a2-overview.pdf)",
        "",
        "The overview keeps documentation compact. `O/W/R/A` means Outline/Working/Review/Accepted. A number after the letter is completeness for that step, for example `R100`.",
        "",
        "## Detailed A3 step boards",
        "",
    ]
    for number, board in sorted(boards.items()):
        lines.extend(
            [
                f"### Step {number} — {board['title']}",
                "",
                f"- [SVG](./steps/step-{number:02d}-board.svg)",
                f"- [draw.io](./steps/step-{number:02d}-board.drawio)",
                f"- [A3 portrait PDF](./steps/step-{number:02d}-board-a3-portrait.pdf)",
                "",
            ]
        )
    lines.extend(
        [
            "## Baseline",
            "",
            f"- Start: `{plan['start_date']}`",
            f"- Cadence: `{plan['cadence_project_days_per_week']}` project day/week",
            f"- Total current estimate: `{total}` project days",
            "",
        ]
    )
    (out_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sip", default="docs/11-SIP-software-implementation-planning.md")
    parser.add_argument("--data-dir", default="docs/_data")
    parser.add_argument("--out", default="bld/docs/planning")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    roadmap_path = data_dir / "sip-roadmap.yaml"
    roadmap_schema = load_json(data_dir / "schemas" / "sip-roadmap.schema.json")
    step_schema = load_json(data_dir / "schemas" / "sip-step-board.schema.json")
    plan = load_yaml(roadmap_path)
    validate_data(plan, roadmap_schema, roadmap_path)
    steps = parse_sip(Path(args.sip), plan)
    boards = load_step_boards(data_dir, step_schema)
    step_by_number = {step.number: step for step in steps}
    for number in boards:
        if number not in step_by_number:
            raise SystemExit(f"Step-board data references unknown SIP Step {number}")

    groups = partition_steps(steps)
    out_dir = Path(args.out)
    step_out = out_dir / "steps"
    out_dir.mkdir(parents=True, exist_ok=True)
    step_out.mkdir(parents=True, exist_ok=True)

    render_overview_svg(steps, groups, boards, plan, out_dir / "sip-roadmap.svg")
    render_overview_drawio(groups, boards, out_dir / "sip-roadmap.drawio")
    render_overview_a3_pdf(groups, boards, out_dir / "sip-roadmap-a3-tiled.pdf")
    render_overview_a2_pdf(steps, boards, out_dir / "sip-roadmap-a2-overview.pdf")

    for number, board in sorted(boards.items()):
        step = step_by_number[number]
        render_step_svg(board, step, step_out / f"step-{number:02d}-board.svg")
        render_step_drawio(board, step, step_out / f"step-{number:02d}-board.drawio")
        render_step_pdf(board, step, step_out / f"step-{number:02d}-board-a3-portrait.pdf")

    write_readme(steps, boards, plan, out_dir)


if __name__ == "__main__":
    main()
