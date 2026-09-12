#!/usr/bin/env python3
"""Generate a printable, capability-driven SIP milestone roadmap.

Outputs:
- sip-roadmap.svg: continuous three-tile panorama for GitHub/zooming
- sip-roadmap.drawio: editable panorama
- sip-roadmap-a3-tiled.pdf: three A3 landscape pages joined left-to-right
- sip-roadmap-a2-overview.pdf: compact one-page A2 overview
- README.md: schedule, print instructions and documentation-maturity table

The SIP Markdown owns step titles, deliverables and demonstrations. A small JSON
planning file owns working effort estimates, cadence assumptions and the
capability-scoped documentation maturity expected at each step gate.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import argparse
import html
import json
import re
import textwrap
import xml.etree.ElementTree as ET

from reportlab.lib.pagesizes import A2, A3, landscape
from reportlab.lib.units import mm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas


A3_W_MM, A3_H_MM = 420.0, 297.0
TILE_COUNT = 3
POSTER_W_MM = A3_W_MM * TILE_COUNT
POSTER_H_MM = A3_H_MM
MARGIN_MM = 12.0
TIMELINE_Y_MM = 49.0

DOC_TRACKS: List[Tuple[str, str]] = [
    ("requirements", "REQ / SRD"),
    ("idd", "IDD"),
    ("design", "SAD / SDD"),
    ("verification", "SVP / evidence"),
]

MATURITY_STYLE = {
    "outline": ("OUTLINE", "#f2f2f2", "#808080"),
    "working": ("WORKING", "#ddebf7", "#5b9bd5"),
    "review": ("REVIEW", "#fff2cc", "#bf9000"),
    "accepted": ("ACCEPTED", "#e2f0d9", "#70ad47"),
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
    for sep in (". ", "; ", ", ", " "):
        pos = cut.rfind(sep)
        if pos >= int(max_chars * 0.60):
            suffix = "." if sep == ". " else ""
            return cut[:pos].rstrip() + suffix + "..."
    return cut.rstrip() + "..."


def extract_subsection(body: str, heading: str) -> str:
    pattern = re.compile(
        rf"^### {re.escape(heading)}\s*$\n(.*?)(?=^### |^## Step |^## Java 11|^## Planning rules|\Z)",
        flags=re.M | re.S,
    )
    match = pattern.search(body)
    return match.group(1).strip() if match else ""


def load_plan(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate_doc_gate(track: str, cfg: dict, step_number: int) -> DocGate:
    level = str(cfg.get("level", "outline")).lower()
    if level not in MATURITY_STYLE:
        raise SystemExit(
            f"Unknown documentation maturity '{level}' for Step {step_number} / {track}"
        )
    scope = str(cfg.get("scope", "")).strip() or "scope to be refined"
    return DocGate(level=level, scope=scope)


def parse_sip(path: Path, plan: dict) -> List[Step]:
    text = path.read_text(encoding="utf-8")
    heading_re = re.compile(r"^## Step (\d+)\s+[—-]\s+(.+?)\s*$", re.M)
    matches = list(heading_re.finditer(text))
    if not matches:
        raise SystemExit(f"No SIP steps found in {path}")

    start_date = date.fromisoformat(plan["start_date"])
    cadence = float(plan["cadence_project_days_per_week"])
    if cadence <= 0:
        raise SystemExit("cadence_project_days_per_week must be > 0")

    settings: Dict[str, dict] = plan["steps"]
    cumulative_days = 0
    steps: List[Step] = []

    for index, match in enumerate(matches):
        number = int(match.group(1))
        cfg = settings.get(str(number))
        if cfg is None:
            raise SystemExit(f"Missing roadmap estimate for SIP Step {number}")

        estimate = int(cfg["estimate_project_days"])
        if estimate <= 0:
            raise SystemExit(f"Step {number} estimate_project_days must be > 0")
        cumulative_days += estimate
        target = start_date + timedelta(days=round(cumulative_days / cadence * 7))

        body_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end():body_end]
        deliverable = concise(extract_subsection(body, "Deliverable"), 170)
        demonstration = concise(extract_subsection(body, "Demonstration"), 170)

        docs_cfg = cfg.get("docs", {})
        docs = {
            track: validate_doc_gate(track, docs_cfg.get(track, {}), number)
            for track, _label in DOC_TRACKS
        }

        steps.append(
            Step(
                number=number,
                title=match.group(2).strip(),
                deliverable=deliverable or "Deliverable to be refined.",
                demonstration=demonstration or "Demonstration to be refined.",
                estimate_days=estimate,
                workstream=cfg.get("workstream", "architecture"),
                target_date=target,
                docs=docs,
            )
        )
    return steps


def partition_steps(steps: List[Step], groups: int = TILE_COUNT) -> List[List[Step]]:
    """Contiguously partition steps while balancing project-day estimates."""
    count = len(steps)
    if count < groups:
        raise SystemExit("Roadmap has fewer steps than print tiles")
    prefix = [0]
    for step in steps:
        prefix.append(prefix[-1] + step.estimate_days)
    ideal = prefix[-1] / groups

    infinity = float("inf")
    scores = [[infinity] * (count + 1) for _ in range(groups + 1)]
    previous = [[None] * (count + 1) for _ in range(groups + 1)]
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

    result: List[List[Step]] = []
    end = count
    for group in range(groups, 0, -1):
        start = previous[group][end]
        if start is None:
            raise SystemExit("Unable to partition roadmap")
        result.append(steps[start:end])
        end = start
    result.reverse()
    return result


def wrap_text(text: str, width: int, max_lines: int) -> List[str]:
    lines = textwrap.wrap(
        text,
        width=max(8, width),
        break_long_words=False,
        break_on_hyphens=False,
    )
    if len(lines) <= max_lines:
        return lines
    clipped = lines[:max_lines]
    clipped[-1] = clipped[-1].rstrip(" .") + "..."
    return clipped


def tile_positions(group: List[Step], page_index: int) -> List[Tuple[Step, float, float]]:
    page_x = page_index * A3_W_MM
    usable = A3_W_MM - 2 * MARGIN_MM
    cell = usable / len(group)
    positions = []
    for index, step in enumerate(group):
        center_x = page_x + MARGIN_MM + cell * (index + 0.5)
        card_width = min(110.0, cell - 5.0)
        positions.append((step, center_x, card_width))
    return positions


def svg_text(
    parts: List[str],
    x: float,
    y: float,
    lines: List[str],
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
            f'<tspan x="{x:.2f}" dy="{dy:.2f}">{html.escape(line)}</tspan>'
        )
    parts.append("</text>")


def draw_svg_doc_matrix(
    parts: List[str], group: List[Step], page_index: int
) -> None:
    page_x = page_index * A3_W_MM
    top = 214.0
    label_w = 27.0
    x0 = page_x + MARGIN_MM
    x1 = page_x + A3_W_MM - MARGIN_MM
    data_x0 = x0 + label_w
    data_w = x1 - data_x0
    col_w = data_w / len(group)
    row_h = 11.8

    parts.append(
        f'<rect x="{x0:.2f}" y="{top:.2f}" width="{x1-x0:.2f}" height="{row_h*5:.2f}" '
        'rx="1.5" fill="#ffffff" stroke="#999999" stroke-width="0.45"/>'
    )
    svg_text(parts, x0 + 2.0, top + 7.1, ["DOCUMENT MATURITY"], 2.5, anchor="start", weight="bold", fill="#555")
    svg_text(
        parts, data_x0 + 2.0, top + 7.1,
        ["Capability-scoped: distant functionality may remain outline"],
        2.2, anchor="start", fill="#666"
    )

    for r, (track, label) in enumerate(DOC_TRACKS, start=1):
        y = top + row_h * r
        parts.append(
            f'<line x1="{x0:.2f}" y1="{y:.2f}" x2="{x1:.2f}" y2="{y:.2f}" '
            'stroke="#c0c0c0" stroke-width="0.35"/>'
        )
        svg_text(parts, x0 + 2.0, y + 7.1, [label], 2.25, anchor="start", weight="bold", fill="#555")
        for c, step in enumerate(group):
            cell_x = data_x0 + col_w * c
            gate = step.docs[track]
            level_label, fill, stroke = MATURITY_STYLE[gate.level]
            parts.append(
                f'<rect x="{cell_x+0.5:.2f}" y="{y+0.6:.2f}" width="{col_w-1.0:.2f}" height="{row_h-1.2:.2f}" '
                f'rx="1" fill="{fill}" stroke="{stroke}" stroke-width="0.35"/>'
            )
            svg_text(parts, cell_x + col_w/2, y + 4.2, [level_label], 1.95, weight="bold", fill=stroke)
            scope = concise(gate.scope, 52)
            scope_lines = wrap_text(scope, max(13, int(col_w / 1.8)), 2)
            svg_text(parts, cell_x + col_w/2, y + 7.1, scope_lines, 1.7, fill="#333")


def render_svg(steps: List[Step], groups: List[List[Step]], plan: dict, path: Path) -> None:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{POSTER_W_MM}mm" height="{POSTER_H_MM}mm" '
        f'viewBox="0 0 {POSTER_W_MM} {POSTER_H_MM}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]
    for page in range(TILE_COUNT):
        x = page * A3_W_MM
        parts.append(
            f'<rect x="{x}" y="0" width="{A3_W_MM}" height="{A3_H_MM}" fill="none" '
            'stroke="#d0d0d0" stroke-width="0.4"/>'
        )
        if page:
            parts.append(
                f'<line x1="{x}" y1="5" x2="{x}" y2="292" stroke="#999" '
                'stroke-width="0.5" stroke-dasharray="3 2"/>'
            )

    svg_text(parts, 15, 13.5, ["Software Implementation Planning — roadmap"], 7.0, anchor="start", weight="bold")
    svg_text(
        parts, 15, 22.0,
        ["Milestone map; not a Gantt. Baseline: 1 focused project day/week. Dates are working targets, not commitments."],
        3.0, anchor="start", fill="#555"
    )
    svg_text(
        parts, 15, 27.0,
        ["Document maturity is capability-scoped: only documentation needed by the current/next increment must be concrete."],
        2.55, anchor="start", fill="#666"
    )
    parts.append(
        f'<line x1="10" y1="{TIMELINE_Y_MM}" x2="{POSTER_W_MM-10}" y2="{TIMELINE_Y_MM}" '
        'stroke="#333" stroke-width="1.0"/>'
    )

    for page_index, group in enumerate(groups):
        positions = tile_positions(group, page_index)
        for step, center_x, card_width in positions:
            _label, fill, stroke = WORKSTREAMS.get(step.workstream, WORKSTREAMS["architecture"])
            radius = 4.5
            points = (
                f"{center_x},{TIMELINE_Y_MM-radius} {center_x+radius},{TIMELINE_Y_MM} "
                f"{center_x},{TIMELINE_Y_MM+radius} {center_x-radius},{TIMELINE_Y_MM}"
            )
            parts.append(f'<polygon points="{points}" fill="white" stroke="#333" stroke-width="0.7"/>')
            svg_text(parts, center_x, TIMELINE_Y_MM + 1.1, [str(step.number)], 2.9, weight="bold")
            parts.append(
                f'<line x1="{center_x}" y1="{TIMELINE_Y_MM+4.5}" x2="{center_x}" y2="209" '
                'stroke="#777" stroke-width="0.4"/>'
            )
            svg_text(
                parts, center_x, 34.0,
                [f"~{step.estimate_days} project days", f"target {step.target_date.strftime('%d %b %Y')}"],
                2.55, weight="bold", fill=stroke
            )
            title_lines = wrap_text(f"Step {step.number} — {step.title}", 27, 3)
            svg_text(parts, center_x, 61.0, title_lines, 3.0, weight="bold")

            x = center_x - card_width / 2
            parts.append(
                f'<rect x="{x:.2f}" y="82" width="{card_width:.2f}" height="52" rx="2" '
                f'fill="{fill}" stroke="{stroke}" stroke-width="0.75"/>'
            )
            svg_text(parts, x + 3, 90.3, ["DELIVERABLE"], 2.45, anchor="start", weight="bold", fill=stroke)
            svg_text(
                parts, center_x, 100.0,
                wrap_text(step.deliverable, max(17, int(card_width / 2.2)), 8),
                2.2
            )

            parts.append(
                f'<rect x="{x:.2f}" y="143" width="{card_width:.2f}" height="58" rx="2" '
                f'fill="#ffffff" stroke="{stroke}" stroke-width="0.75"/>'
            )
            svg_text(parts, x + 3, 151.3, ["DEMONSTRATION"], 2.45, anchor="start", weight="bold", fill=stroke)
            svg_text(
                parts, center_x, 161.0,
                wrap_text(step.demonstration, max(17, int(card_width / 2.2)), 9),
                2.1
            )

        draw_svg_doc_matrix(parts, group, page_index)

    total = sum(step.estimate_days for step in steps)
    reserve = float(plan.get("planning_reserve_fraction", 0.0))
    reserve_end = date.fromisoformat(plan["start_date"]) + timedelta(
        days=round(total * (1 + reserve) / float(plan["cadence_project_days_per_week"]) * 7)
    )
    svg_text(
        parts, 15, 282.5,
        [
            f"Baseline: {total} project days → {steps[-1].target_date.strftime('%d %b %Y')} | "
            f"+{int(reserve*100)}% planning reserve → about {reserve_end.strftime('%d %b %Y')}"
        ],
        2.55, anchor="start", weight="bold", fill="#444"
    )

    for page_index, group in enumerate(groups):
        page_x = page_index * A3_W_MM
        footer = (
            f"A3 tile {page_index+1}/{TILE_COUNT} — Steps {group[0].number}-{group[-1].number} "
            "— print at 100% / actual size"
        )
        svg_text(parts, page_x + A3_W_MM/2, 291.0, [footer], 2.45, weight="bold", fill="#555")
        if page_index < TILE_COUNT - 1:
            svg_text(parts, page_x + A3_W_MM - 4, 282.5, ["JOIN →"], 2.2, anchor="end", weight="bold", fill="#777")
        if page_index > 0:
            svg_text(parts, page_x + 4, 282.5, ["← JOIN"], 2.2, anchor="start", weight="bold", fill="#777")

    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def render_drawio(groups: List[List[Step]], path: Path) -> None:
    root = ET.Element("mxfile", host="app.diagrams.net", agent="sip-roadmap-generator", version="24.7.17", type="device")
    diagram = ET.SubElement(root, "diagram", id="sip-roadmap", name="SIP roadmap")
    model = ET.SubElement(
        diagram, "mxGraphModel",
        dx="1800", dy="900", grid="1", gridSize="10", guides="1", tooltips="1",
        connect="1", arrows="1", fold="1", page="1", pageScale="1",
        pageWidth=str(POSTER_W_MM), pageHeight=str(POSTER_H_MM), math="0", shadow="0"
    )
    graph = ET.SubElement(model, "root")
    ET.SubElement(graph, "mxCell", id="0")
    ET.SubElement(graph, "mxCell", id="1", parent="0")

    def vertex(cell_id: str, value: str, x: float, y: float, w: float, h: float, style: str) -> None:
        cell = ET.SubElement(graph, "mxCell", id=cell_id, value=value, style=style, vertex="1", parent="1")
        ET.SubElement(
            cell, "mxGeometry",
            x=f"{x:.2f}", y=f"{y:.2f}", width=f"{w:.2f}", height=f"{h:.2f}", **{"as": "geometry"}
        )

    vertex(
        "title", "Software Implementation Planning — roadmap", 15, 7, 500, 16,
        "text;html=1;strokeColor=none;fillColor=none;fontSize=18;fontStyle=1;align=left;"
    )
    for page_index, group in enumerate(groups):
        positions = tile_positions(group, page_index)
        for step, center_x, card_width in positions:
            _label, fill, stroke = WORKSTREAMS.get(step.workstream, WORKSTREAMS["architecture"])
            vertex(
                f"gate-{step.number}", str(step.number), center_x-4.5, TIMELINE_Y_MM-4.5, 9, 9,
                "rhombus;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#333333;fontStyle=1;"
            )
            vertex(
                f"meta-{step.number}",
                f"~{step.estimate_days} project days<br>target {step.target_date.strftime('%d %b %Y')}",
                center_x-card_width/2, 29, card_width, 19,
                f"text;html=1;strokeColor=none;fillColor=none;fontSize=8;fontStyle=1;fontColor={stroke};align=center;"
            )
            vertex(
                f"title-{step.number}", html.escape(f"Step {step.number} — {step.title}"),
                center_x-card_width/2, 57, card_width, 22,
                "text;html=1;strokeColor=none;fillColor=none;fontSize=8;fontStyle=1;align=center;verticalAlign=top;whiteSpace=wrap;"
            )
            vertex(
                f"deliverable-{step.number}", f"<b>DELIVERABLE</b><br>{html.escape(step.deliverable)}",
                center_x-card_width/2, 82, card_width, 52,
                f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};fontSize=7;align=center;verticalAlign=top;spacingTop=4;"
            )
            vertex(
                f"demo-{step.number}", f"<b>DEMONSTRATION</b><br>{html.escape(step.demonstration)}",
                center_x-card_width/2, 143, card_width, 58,
                f"rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor={stroke};fontSize=7;align=center;verticalAlign=top;spacingTop=4;"
            )

        top = 214.0
        label_w = 27.0
        x0 = page_index*A3_W_MM + MARGIN_MM
        x1 = page_index*A3_W_MM + A3_W_MM - MARGIN_MM
        data_x0 = x0 + label_w
        col_w = (x1-data_x0)/len(group)
        row_h = 11.8
        vertex(
            f"doc-header-{page_index}",
            "<b>DOCUMENT MATURITY</b><br><font color='#666666'>Capability-scoped; future functionality may remain outline</font>",
            x0, top, x1-x0, row_h,
            "rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#999999;fontSize=6;align=left;spacingLeft=4;"
        )
        for r, (track, label) in enumerate(DOC_TRACKS, start=1):
            y = top + row_h*r
            vertex(
                f"doc-label-{page_index}-{track}", label, x0, y, label_w, row_h,
                "whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#cccccc;fontSize=6;fontStyle=1;align=left;spacingLeft=3;"
            )
            for c, step in enumerate(group):
                gate = step.docs[track]
                level_label, gate_fill, gate_stroke = MATURITY_STYLE[gate.level]
                value = f"<b>{level_label}</b><br>{html.escape(concise(gate.scope, 55))}"
                vertex(
                    f"doc-{step.number}-{track}", value,
                    data_x0+col_w*c, y, col_w, row_h,
                    f"whiteSpace=wrap;html=1;fillColor={gate_fill};strokeColor={gate_stroke};fontSize=5;align=center;verticalAlign=middle;"
                )

    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def hex_rgb(value: str) -> Tuple[float, float, float]:
    value = value.lstrip("#")
    return tuple(int(value[i:i+2], 16)/255.0 for i in (0, 2, 4))


def pdf_wrapped(
    pdf: canvas.Canvas,
    text: str,
    center_x: float,
    top_y: float,
    width: float,
    height: float,
    font: str,
    size: float,
    color: Tuple[float, float, float],
    max_lines: int,
    leading: float | None = None,
) -> None:
    leading = leading or size * 1.16
    words = text.split()
    lines: List[str] = []
    line = ""
    for word in words:
        candidate = word if not line else f"{line} {word}"
        if stringWidth(candidate, font, size) <= width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" .") + "..."
    lines = lines[:max(1, int(height // leading))]
    pdf.setFont(font, size)
    pdf.setFillColorRGB(*color)
    y = top_y
    for item in lines:
        pdf.drawCentredString(center_x, y, item)
        y -= leading


def draw_pdf_doc_matrix(pdf: canvas.Canvas, group: List[Step], page_height: float) -> None:
    def x(v: float) -> float:
        return v*mm

    def y(v: float) -> float:
        return page_height-v*mm

    top = 214.0
    label_w = 27.0
    x0 = MARGIN_MM
    x1 = A3_W_MM-MARGIN_MM
    data_x0 = x0+label_w
    col_w = (x1-data_x0)/len(group)
    row_h = 11.8

    pdf.setStrokeColorRGB(0.6, 0.6, 0.6)
    pdf.setFillColorRGB(1, 1, 1)
    pdf.roundRect(x(x0), y(top+row_h), x(x1-x0), x(row_h), x(1.5), fill=1, stroke=1)
    pdf.setFont("Helvetica-Bold", 6.5)
    pdf.setFillColorRGB(0.3, 0.3, 0.3)
    pdf.drawString(x(x0+2), y(top+7.3), "DOCUMENT MATURITY")
    pdf.setFont("Helvetica", 5.5)
    pdf.drawString(x(data_x0+2), y(top+7.3), "Capability-scoped; future functionality may remain outline")

    for r, (track, label) in enumerate(DOC_TRACKS, start=1):
        yy = top+row_h*r
        pdf.setFillColorRGB(1, 1, 1)
        pdf.setStrokeColorRGB(0.75, 0.75, 0.75)
        pdf.rect(x(x0), y(yy+row_h), x(label_w), x(row_h), fill=1, stroke=1)
        pdf.setFont("Helvetica-Bold", 5.7)
        pdf.setFillColorRGB(0.3, 0.3, 0.3)
        pdf.drawString(x(x0+2), y(yy+7.2), label)
        for c, step in enumerate(group):
            gate = step.docs[track]
            level_label, fill_hex, stroke_hex = MATURITY_STYLE[gate.level]
            fill = hex_rgb(fill_hex)
            stroke = hex_rgb(stroke_hex)
            left = data_x0+col_w*c
            pdf.setFillColorRGB(*fill)
            pdf.setStrokeColorRGB(*stroke)
            pdf.rect(x(left), y(yy+row_h), x(col_w), x(row_h), fill=1, stroke=1)
            pdf.setFillColorRGB(*stroke)
            pdf.setFont("Helvetica-Bold", 5.0)
            pdf.drawCentredString(x(left+col_w/2), y(yy+3.6), level_label)
            pdf_wrapped(
                pdf, concise(gate.scope, 56), x(left+col_w/2), y(yy+6.6),
                x(col_w-2), x(4.6), "Helvetica", 4.3, (0.18, 0.18, 0.18), 2, 4.8
            )


def draw_pdf_tile(pdf: canvas.Canvas, group: List[Step], tile_index: int) -> None:
    page_width, page_height = landscape(A3)
    pdf.setFillColorRGB(1, 1, 1)
    pdf.rect(0, 0, page_width, page_height, fill=1, stroke=0)

    def x(v: float) -> float:
        return v*mm

    def y(v: float) -> float:
        return page_height-v*mm

    pdf.setFillColorRGB(0.1, 0.1, 0.1)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(x(12), y(13.5), "Software Implementation Planning - roadmap")
    pdf.setFont("Helvetica", 8.0)
    pdf.setFillColorRGB(0.35, 0.35, 0.35)
    pdf.drawString(x(12), y(21.5), "Milestone map; not a Gantt. Baseline: 1 focused project day/week. Dates are working targets.")
    pdf.setFont("Helvetica", 6.7)
    pdf.drawString(x(12), y(27), "Document maturity is capability-scoped: only current/next capability documentation must be concrete.")

    pdf.setStrokeColorRGB(0.2, 0.2, 0.2)
    pdf.setLineWidth(1.0)
    pdf.line(x(8), y(TIMELINE_Y_MM), x(A3_W_MM-8), y(TIMELINE_Y_MM))

    usable = A3_W_MM-2*MARGIN_MM
    cell = usable/len(group)
    for index, step in enumerate(group):
        center_x_mm = MARGIN_MM+cell*(index+0.5)
        card_w_mm = min(110.0, cell-5.0)
        _label, fill_hex, stroke_hex = WORKSTREAMS.get(step.workstream, WORKSTREAMS["architecture"])
        fill = hex_rgb(fill_hex)
        stroke = hex_rgb(stroke_hex)
        cx = x(center_x_mm)
        cy = y(TIMELINE_Y_MM)
        radius = x(4.5)
        gate = pdf.beginPath()
        gate.moveTo(cx, cy+radius)
        gate.lineTo(cx+radius, cy)
        gate.lineTo(cx, cy-radius)
        gate.lineTo(cx-radius, cy)
        gate.close()
        pdf.setFillColorRGB(1, 1, 1)
        pdf.setStrokeColorRGB(0.2, 0.2, 0.2)
        pdf.drawPath(gate, fill=1, stroke=1)
        pdf.setFillColorRGB(0.1, 0.1, 0.1)
        pdf.setFont("Helvetica-Bold", 7.5)
        pdf.drawCentredString(cx, cy-2.4, str(step.number))
        pdf.setStrokeColorRGB(0.45, 0.45, 0.45)
        pdf.setLineWidth(0.45)
        pdf.line(cx, y(TIMELINE_Y_MM+4.5), cx, y(209))

        pdf.setFillColorRGB(*stroke)
        pdf.setFont("Helvetica-Bold", 6.8)
        pdf.drawCentredString(cx, y(32), f"~{step.estimate_days} project days")
        pdf.drawCentredString(cx, y(36.6), f"target {step.target_date.strftime('%d %b %Y')}")
        pdf_wrapped(
            pdf, f"Step {step.number} - {step.title}", cx, y(59.5), x(card_w_mm-4), x(18),
            "Helvetica-Bold", 6.9, (0.1, 0.1, 0.1), 3, 7.8
        )

        left = x(center_x_mm-card_w_mm/2)
        pdf.setFillColorRGB(*fill)
        pdf.setStrokeColorRGB(*stroke)
        pdf.roundRect(left, y(134), x(card_w_mm), x(52), x(2), fill=1, stroke=1)
        pdf.setFillColorRGB(*stroke)
        pdf.setFont("Helvetica-Bold", 6.2)
        pdf.drawString(left+x(3), y(90), "DELIVERABLE")
        pdf_wrapped(
            pdf, step.deliverable, cx, y(99.5), x(card_w_mm-6), x(30),
            "Helvetica", 5.7, (0.12, 0.12, 0.12), 8, 6.5
        )

        pdf.setFillColorRGB(1, 1, 1)
        pdf.setStrokeColorRGB(*stroke)
        pdf.roundRect(left, y(201), x(card_w_mm), x(58), x(2), fill=1, stroke=1)
        pdf.setFillColorRGB(*stroke)
        pdf.setFont("Helvetica-Bold", 6.2)
        pdf.drawString(left+x(3), y(151), "DEMONSTRATION")
        pdf_wrapped(
            pdf, step.demonstration, cx, y(160.5), x(card_w_mm-6), x(35),
            "Helvetica", 5.6, (0.12, 0.12, 0.12), 9, 6.3
        )

    draw_pdf_doc_matrix(pdf, group, page_height)

    pdf.setStrokeColorRGB(0.55, 0.55, 0.55)
    pdf.setLineWidth(0.5)
    for mark_y in (45, 275):
        if tile_index > 0:
            pdf.line(x(2), y(mark_y), x(8), y(mark_y))
            pdf.line(x(5), y(mark_y-3), x(5), y(mark_y+3))
        if tile_index < TILE_COUNT-1:
            pdf.line(x(A3_W_MM-8), y(mark_y), x(A3_W_MM-2), y(mark_y))
            pdf.line(x(A3_W_MM-5), y(mark_y-3), x(A3_W_MM-5), y(mark_y+3))

    footer = (
        f"A3 tile {tile_index+1}/{TILE_COUNT} - Steps {group[0].number}-{group[-1].number} "
        "- PRINT AT 100% / ACTUAL SIZE"
    )
    pdf.setFont("Helvetica-Bold", 6.5)
    pdf.setFillColorRGB(0.35, 0.35, 0.35)
    pdf.drawCentredString(page_width/2, y(289), footer)
    if tile_index > 0:
        pdf.drawString(x(4), y(280), "<- JOIN")
    if tile_index < TILE_COUNT-1:
        pdf.drawRightString(x(A3_W_MM-4), y(280), "JOIN ->")


def render_tiled_pdf(groups: List[List[Step]], path: Path) -> None:
    pdf = canvas.Canvas(str(path), pagesize=landscape(A3), pageCompression=1)
    pdf.setTitle("SIP roadmap - A3 tiled")
    for index, group in enumerate(groups):
        draw_pdf_tile(pdf, group, index)
        pdf.showPage()
    pdf.save()


def render_a2_overview(steps: List[Step], plan: dict, path: Path) -> None:
    page_width, page_height = landscape(A2)
    pdf = canvas.Canvas(str(path), pagesize=(page_width, page_height), pageCompression=1)
    pdf.setTitle("SIP roadmap - A2 overview")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(14*mm, page_height-16*mm, "Software Implementation Planning - A2 overview")
    pdf.setFont("Helvetica", 8)
    pdf.drawString(14*mm, page_height-24*mm, "Compact milestone view. Detailed deliverables, demos and document maturity are in the A3 tiled PDF.")

    left = 14*mm
    right = page_width-14*mm
    timeline_y = page_height-52*mm
    pdf.setLineWidth(1)
    pdf.line(left, timeline_y, right, timeline_y)
    usable = right-left
    cell = usable/len(steps)
    for index, step in enumerate(steps):
        cx = left+cell*(index+0.5)
        _label, fill_hex, stroke_hex = WORKSTREAMS.get(step.workstream, WORKSTREAMS["architecture"])
        fill = hex_rgb(fill_hex)
        stroke = hex_rgb(stroke_hex)
        path_gate = pdf.beginPath()
        radius = 4*mm
        path_gate.moveTo(cx, timeline_y+radius)
        path_gate.lineTo(cx+radius, timeline_y)
        path_gate.lineTo(cx, timeline_y-radius)
        path_gate.lineTo(cx-radius, timeline_y)
        path_gate.close()
        pdf.setFillColorRGB(1, 1, 1)
        pdf.setStrokeColorRGB(0.2, 0.2, 0.2)
        pdf.drawPath(path_gate, fill=1, stroke=1)
        pdf.setFont("Helvetica-Bold", 7)
        pdf.setFillColorRGB(0.1, 0.1, 0.1)
        pdf.drawCentredString(cx, timeline_y-2.5, str(step.number))

        box_w = max(24*mm, cell-2*mm)
        box_left = cx-box_w/2
        box_bottom = timeline_y-62*mm
        pdf.setFillColorRGB(*fill)
        pdf.setStrokeColorRGB(*stroke)
        pdf.roundRect(box_left, box_bottom, box_w, 32*mm, 2*mm, fill=1, stroke=1)
        pdf.setFillColorRGB(*stroke)
        pdf.setFont("Helvetica-Bold", 5.6)
        pdf.drawCentredString(cx, box_bottom+26*mm, f"STEP {step.number} | ~{step.estimate_days}d")
        pdf_wrapped(
            pdf, step.title, cx, box_bottom+21*mm, box_w-4*mm, 14*mm,
            "Helvetica-Bold", 5.1, (0.1, 0.1, 0.1), 4, 5.8
        )
        pdf.setFont("Helvetica", 4.8)
        pdf.drawCentredString(cx, box_bottom+3.5*mm, step.target_date.strftime("%d %b %Y"))

        bar_y = box_bottom-7*mm
        bar_w = (box_w-3*mm)/4
        for bar_index, (track, _track_label) in enumerate(DOC_TRACKS):
            gate = step.docs[track]
            level_label, gate_fill_hex, gate_stroke_hex = MATURITY_STYLE[gate.level]
            pdf.setFillColorRGB(*hex_rgb(gate_fill_hex))
            pdf.setStrokeColorRGB(*hex_rgb(gate_stroke_hex))
            pdf.rect(box_left+bar_index*bar_w, bar_y, bar_w-0.6*mm, 5*mm, fill=1, stroke=1)
            pdf.setFont("Helvetica-Bold", 3.7)
            pdf.setFillColorRGB(*hex_rgb(gate_stroke_hex))
            pdf.drawCentredString(box_left+bar_index*bar_w+(bar_w-0.6*mm)/2, bar_y+1.6*mm, level_label[:3])

    total = sum(step.estimate_days for step in steps)
    reserve = float(plan.get("planning_reserve_fraction", 0.0))
    cadence = float(plan["cadence_project_days_per_week"])
    reserve_end = date.fromisoformat(plan["start_date"]) + timedelta(days=round(total*(1+reserve)/cadence*7))
    pdf.setFont("Helvetica-Bold", 8)
    pdf.setFillColorRGB(0.25, 0.25, 0.25)
    pdf.drawString(14*mm, 18*mm, f"Baseline {total} project days; +{int(reserve*100)}% reserve gives a planning horizon around {reserve_end.strftime('%b %Y')}.")
    pdf.drawRightString(page_width-14*mm, 18*mm, "PRINT AT 100% / ACTUAL SIZE")
    pdf.save()


def render_readme(steps: List[Step], groups: List[List[Step]], plan: dict, path: Path) -> None:
    total = sum(step.estimate_days for step in steps)
    reserve = float(plan.get("planning_reserve_fraction", 0.0))
    cadence = float(plan["cadence_project_days_per_week"])
    start = date.fromisoformat(plan["start_date"])
    reserve_end = start + timedelta(days=round(total*(1+reserve)/cadence*7))
    principle = plan.get("documentation_maturity", {}).get("principle", "Documentation maturity is capability-scoped.")

    lines = [
        "# SIP roadmap",
        "",
        "Generated from the source SIP plus the working effort/documentation baseline in `docs/_data/sip-roadmap.json`.",
        "",
        "The roadmap is a milestone map, **not a time-scaled Gantt chart**. Dates are planning targets rather than commitments.",
        "",
        f"Planning basis: **{plan['cadence_project_days_per_week']:g} focused project day/week**, {total} baseline project days, plus {int(reserve*100)}% planning reserve.",
        f"Baseline completion: **{steps[-1].target_date.strftime('%d %b %Y')}**. Planning horizon with reserve: **about {reserve_end.strftime('%d %b %Y')}**.",
        "",
        "## Documentation maturity principle",
        "",
        principle,
        "",
        "The maturity rows therefore describe only the requirements/interfaces/design/verification material needed for the capability at that step. They do **not** require distant functionality to be fully specified early.",
        "",
        "Maturity levels:",
        "",
        "- **OUTLINE** — only high-level intent is needed;",
        "- **WORKING** — enough detail exists for the next engineering activity;",
        "- **REVIEW** — behaviour/contract is concrete enough for deliberate review;",
        "- **ACCEPTED** — accepted baseline for the applicable implemented scope.",
        "",
        "## Outputs",
        "",
        "- [Continuous SVG panorama](./sip-roadmap.svg) — best for GitHub/browser zooming.",
        "- [Editable draw.io panorama](./sip-roadmap.drawio).",
        "- [A3 tiled PDF](./sip-roadmap-a3-tiled.pdf) — three A3 landscape sheets that join left-to-right and include documentation maturity lanes.",
        "- [A2 overview PDF](./sip-roadmap-a2-overview.pdf) — compact single-page milestone overview.",
        "",
        "## A3 assembly",
        "",
        "Print all three A3 pages at **100% / Actual size**. Place them in page-number order from left to right. Join/cross marks are provided at the inner edges. The page split is recalculated from project-day estimates and only occurs **between SIP steps**, never through a step card.",
        "",
        "## Working schedule",
        "",
        "| Step | Estimate | Baseline target | REQ/SRD | IDD | SAD/SDD | SVP/evidence |",
        "| --- | ---: | --- | --- | --- | --- | --- |",
    ]
    for step in steps:
        levels = [MATURITY_STYLE[step.docs[key].level][0] for key, _ in DOC_TRACKS]
        lines.append(
            f"| {step.number} - {step.title} | {step.estimate_days} project days | "
            f"{step.target_date.strftime('%d %b %Y')} | {levels[0]} | {levels[1]} | {levels[2]} | {levels[3]} |"
        )

    lines.extend(["", "## Documentation scope at each step", ""])
    for step in steps:
        lines.append(f"### Step {step.number} — {step.title}")
        lines.append("")
        for key, label in DOC_TRACKS:
            gate = step.docs[key]
            level_label = MATURITY_STYLE[gate.level][0]
            lines.append(f"- **{label}: {level_label}** — {gate.scope}")
        lines.append("")

    lines.extend(["## Current A3 tile split", ""])
    for index, group in enumerate(groups, start=1):
        days = sum(step.estimate_days for step in group)
        lines.append(f"- Tile {index}: Steps {group[0].number}-{group[-1].number} ({days} project days).")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sip", default="docs/11-SIP-software-implementation-planning.md")
    parser.add_argument("--plan", default="docs/_data/sip-roadmap.json")
    parser.add_argument("--out", default="bld/docs/planning")
    args = parser.parse_args()

    output = Path(args.out)
    output.mkdir(parents=True, exist_ok=True)
    plan = load_plan(Path(args.plan))
    steps = parse_sip(Path(args.sip), plan)
    groups = partition_steps(steps)

    render_svg(steps, groups, plan, output/"sip-roadmap.svg")
    render_drawio(groups, output/"sip-roadmap.drawio")
    render_tiled_pdf(groups, output/"sip-roadmap-a3-tiled.pdf")
    render_a2_overview(steps, plan, output/"sip-roadmap-a2-overview.pdf")
    render_readme(steps, groups, plan, output/"README.md")

    print("Generated SIP roadmap")
    print("A3 tile split:", " | ".join(f"{g[0].number}-{g[-1].number}" for g in groups))


if __name__ == "__main__":
    main()
