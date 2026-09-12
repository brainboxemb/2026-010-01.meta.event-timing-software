#!/usr/bin/env python3
"""Generate a printable milestone roadmap from the SIP Markdown.

Outputs:
- sip-roadmap.svg: one continuous three-tile panorama for GitHub/zooming
- sip-roadmap.drawio: editable panorama
- sip-roadmap-a3-tiled.pdf: three A3 landscape pages designed to join side-by-side
- sip-roadmap-a2-overview.pdf: compact one-page A2 landscape overview
- README.md: schedule table and print instructions

The SIP Markdown owns step content. A small JSON planning data file owns working
project-day estimates and cadence assumptions. Estimates are explicitly
non-authoritative planning aids.
"""

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
TIMELINE_Y_MM = 54.0


@dataclass
class Step:
    number: int
    title: str
    deliverable: str
    demonstration: str
    estimate_days: int
    workstream: str
    target_date: date


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

    cumulative_days = 0
    steps: List[Step] = []
    settings: Dict[str, dict] = plan["steps"]
    for index, match in enumerate(matches):
        number = int(match.group(1))
        if str(number) not in settings:
            raise SystemExit(f"Missing roadmap estimate for SIP Step {number}")
        cfg = settings[str(number)]
        estimate = int(cfg["estimate_project_days"])
        cumulative_days += estimate
        weeks = cumulative_days / cadence
        target = start_date + timedelta(days=round(weeks * 7))
        body_end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        body = text[match.end():body_end]
        deliverable = concise(extract_subsection(body, "Deliverable"), 185)
        demonstration = concise(extract_subsection(body, "Demonstration"), 185)
        steps.append(
            Step(
                number=number,
                title=match.group(2).strip(),
                deliverable=deliverable or "Deliverable to be refined.",
                demonstration=demonstration or "Demonstration to be refined.",
                estimate_days=estimate,
                workstream=cfg.get("workstream", "architecture"),
                target_date=target,
            )
        )
    return steps


def partition_steps(steps: List[Step], groups: int = TILE_COUNT) -> List[List[Step]]:
    """Contiguously partition steps while balancing project-day estimates."""
    count = len(steps)
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


def svg_text(parts: List[str], x: float, y: float, lines: List[str], size: float,
             anchor: str = "middle", weight: str = "normal", fill: str = "#222") -> None:
    parts.append(
        f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" '
        f'font-family="Arial,Helvetica,sans-serif" font-size="{size:.2f}" '
        f'font-weight="{weight}" fill="{fill}">'
    )
    for index, line in enumerate(lines):
        dy = 0 if index == 0 else size * 1.28
        parts.append(
            f'<tspan x="{x:.2f}" dy="{dy:.2f}">{html.escape(line)}</tspan>'
        )
    parts.append("</text>")


def tile_positions(group: List[Step], page_index: int) -> List[Tuple[Step, float, float]]:
    page_x = page_index * A3_W_MM
    usable = A3_W_MM - 2 * MARGIN_MM
    cell = usable / len(group)
    result = []
    for index, step in enumerate(group):
        center_x = page_x + MARGIN_MM + cell * (index + 0.5)
        card_width = min(110.0, cell - 5.0)
        result.append((step, center_x, card_width))
    return result


def render_svg(steps: List[Step], groups: List[List[Step]], plan: dict, path: Path) -> None:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{POSTER_W_MM}mm" height="{POSTER_H_MM}mm" viewBox="0 0 {POSTER_W_MM} {POSTER_H_MM}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]
    for page in range(TILE_COUNT):
        x = page * A3_W_MM
        parts.append(
            f'<rect x="{x}" y="0" width="{A3_W_MM}" height="{A3_H_MM}" '
            'fill="none" stroke="#d0d0d0" stroke-width="0.4"/>'
        )
        if page:
            parts.append(
                f'<line x1="{x}" y1="5" x2="{x}" y2="292" '
                'stroke="#999" stroke-width="0.5" stroke-dasharray="3 2"/>'
            )

    svg_text(
        parts,
        15,
        14,
        ["Software Implementation Planning - roadmap"],
        7.2,
        anchor="start",
        weight="bold",
    )
    svg_text(
        parts,
        15,
        23,
        ["Milestone map; not a Gantt. Baseline: 1 focused project day/week. Dates are working targets, not commitments."],
        3.2,
        anchor="start",
        fill="#555",
    )
    parts.append(
        f'<line x1="10" y1="{TIMELINE_Y_MM}" x2="{POSTER_W_MM-10}" '
        f'y2="{TIMELINE_Y_MM}" stroke="#333" stroke-width="1.0"/>'
    )

    for page_index, group in enumerate(groups):
        for step, center_x, card_width in tile_positions(group, page_index):
            _label, fill, stroke = WORKSTREAMS.get(
                step.workstream,
                WORKSTREAMS["architecture"],
            )
            radius = 5.0
            points = (
                f"{center_x},{TIMELINE_Y_MM-radius} "
                f"{center_x+radius},{TIMELINE_Y_MM} "
                f"{center_x},{TIMELINE_Y_MM+radius} "
                f"{center_x-radius},{TIMELINE_Y_MM}"
            )
            parts.append(
                f'<polygon points="{points}" fill="white" stroke="#333" stroke-width="0.7"/>'
            )
            svg_text(parts, center_x, TIMELINE_Y_MM + 1.2, [str(step.number)], 3.1, weight="bold")
            parts.append(
                f'<line x1="{center_x}" y1="{TIMELINE_Y_MM+5}" x2="{center_x}" '
                'y2="252" stroke="#666" stroke-width="0.45"/>'
            )

            svg_text(
                parts,
                center_x,
                34,
                [
                    f"~{step.estimate_days} project days",
                    f"target {step.target_date.strftime('%d %b %Y')}",
                ],
                2.8,
                weight="bold",
                fill=stroke,
            )
            title_lines = wrap_text(f"Step {step.number} - {step.title}", 28, 3)
            svg_text(parts, center_x, 67, title_lines, 3.25, weight="bold")

            x = center_x - card_width / 2
            parts.append(
                f'<rect x="{x:.2f}" y="94" width="{card_width:.2f}" height="63" '
                f'rx="2" fill="{fill}" stroke="{stroke}" stroke-width="0.8"/>'
            )
            svg_text(parts, x + 3, 103, ["DELIVERABLE"], 2.7, anchor="start", weight="bold", fill=stroke)
            deliverable_lines = wrap_text(
                step.deliverable,
                max(18, int(card_width / 2.25)),
                10,
            )
            svg_text(parts, center_x, 114, deliverable_lines, 2.55)

            parts.append(
                f'<rect x="{x:.2f}" y="171" width="{card_width:.2f}" height="70" '
                f'rx="2" fill="#ffffff" stroke="{stroke}" stroke-width="0.8"/>'
            )
            svg_text(parts, x + 3, 180, ["DEMONSTRATION"], 2.7, anchor="start", weight="bold", fill=stroke)
            demonstration_lines = wrap_text(
                step.demonstration,
                max(18, int(card_width / 2.25)),
                11,
            )
            svg_text(parts, center_x, 191, demonstration_lines, 2.45)

    y = 265.0
    x = 15.0
    for _key, (label, fill, stroke) in WORKSTREAMS.items():
        parts.append(
            f'<rect x="{x}" y="{y}" width="7" height="4.5" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="0.4"/>'
        )
        svg_text(parts, x + 9, y + 3.5, [label], 2.4, anchor="start")
        x += 48
        if x > POSTER_W_MM - 55:
            break

    reserve = float(plan.get("planning_reserve_fraction", 0.0))
    total = sum(step.estimate_days for step in steps)
    reserve_days = total * reserve
    baseline_end = steps[-1].target_date
    reserve_end = date.fromisoformat(plan["start_date"]) + timedelta(
        days=round(
            (total + reserve_days)
            / float(plan["cadence_project_days_per_week"])
            * 7
        )
    )
    svg_text(
        parts,
        15,
        284,
        [
            f"Baseline: {total} project days -> {baseline_end.strftime('%d %b %Y')} | "
            f"+{int(reserve*100)}% planning reserve -> about {reserve_end.strftime('%d %b %Y')}"
        ],
        2.8,
        anchor="start",
        weight="bold",
    )

    for page_index, group in enumerate(groups):
        page_x = page_index * A3_W_MM
        footer = (
            f"A3 tile {page_index+1}/{TILE_COUNT} - Steps "
            f"{group[0].number}-{group[-1].number} - print at 100% / actual size"
        )
        svg_text(parts, page_x + A3_W_MM / 2, 291, [footer], 2.6, weight="bold", fill="#555")
        if page_index < TILE_COUNT - 1:
            svg_text(parts, page_x + A3_W_MM - 5, 282, ["JOIN ->"], 2.4, anchor="end", weight="bold", fill="#777")
        if page_index > 0:
            svg_text(parts, page_x + 5, 282, ["<- JOIN"], 2.4, anchor="start", weight="bold", fill="#777")

    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def render_drawio(groups: List[List[Step]], path: Path) -> None:
    root = ET.Element(
        "mxfile",
        host="app.diagrams.net",
        agent="sip-roadmap-generator",
        version="24.7.17",
        type="device",
    )
    diagram = ET.SubElement(root, "diagram", id="sip-roadmap", name="SIP roadmap")
    model = ET.SubElement(
        diagram,
        "mxGraphModel",
        dx="1800",
        dy="900",
        grid="1",
        gridSize="10",
        guides="1",
        tooltips="1",
        connect="1",
        arrows="1",
        fold="1",
        page="1",
        pageScale="1",
        pageWidth=str(POSTER_W_MM),
        pageHeight=str(POSTER_H_MM),
        math="0",
        shadow="0",
    )
    graph_root = ET.SubElement(model, "root")
    ET.SubElement(graph_root, "mxCell", id="0")
    ET.SubElement(graph_root, "mxCell", id="1", parent="0")

    def vertex(cell_id: str, value: str, x: float, y: float, width: float, height: float, style: str) -> None:
        cell = ET.SubElement(
            graph_root,
            "mxCell",
            id=cell_id,
            value=value,
            style=style,
            vertex="1",
            parent="1",
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

    vertex(
        "title",
        "Software Implementation Planning - roadmap",
        15,
        7,
        420,
        18,
        "text;html=1;strokeColor=none;fillColor=none;fontSize=18;fontStyle=1;align=left;",
    )
    for page_index, group in enumerate(groups):
        if page_index:
            x = page_index * A3_W_MM
            vertex(
                f"join-{page_index}",
                "",
                x - 0.2,
                4,
                0.4,
                286,
                "shape=line;strokeColor=#999999;dashed=1;",
            )
        for step, center_x, card_width in tile_positions(group, page_index):
            _label, fill, stroke = WORKSTREAMS.get(
                step.workstream,
                WORKSTREAMS["architecture"],
            )
            vertex(
                f"gate-{step.number}",
                str(step.number),
                center_x - 5,
                TIMELINE_Y_MM - 5,
                10,
                10,
                "rhombus;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor=#333333;fontStyle=1;",
            )
            meta = (
                f"~{step.estimate_days} project days<br>"
                f"target {step.target_date.strftime('%d %b %Y')}"
            )
            vertex(
                f"meta-{step.number}",
                meta,
                center_x - card_width / 2,
                28,
                card_width,
                22,
                f"text;html=1;strokeColor=none;fillColor=none;fontSize=8;fontStyle=1;"
                f"fontColor={stroke};align=center;",
            )
            vertex(
                f"title-{step.number}",
                html.escape(f"Step {step.number} - {step.title}"),
                center_x - card_width / 2,
                62,
                card_width,
                28,
                "text;html=1;strokeColor=none;fillColor=none;fontSize=9;fontStyle=1;"
                "align=center;verticalAlign=top;whiteSpace=wrap;",
            )
            vertex(
                f"deliverable-{step.number}",
                f"<b>DELIVERABLE</b><br>{html.escape(step.deliverable)}",
                center_x - card_width / 2,
                94,
                card_width,
                63,
                f"rounded=1;whiteSpace=wrap;html=1;fillColor={fill};strokeColor={stroke};"
                "fontSize=7;align=center;verticalAlign=top;spacingTop=5;",
            )
            vertex(
                f"demo-{step.number}",
                f"<b>DEMONSTRATION</b><br>{html.escape(step.demonstration)}",
                center_x - card_width / 2,
                171,
                card_width,
                70,
                f"rounded=1;whiteSpace=wrap;html=1;fillColor=#ffffff;strokeColor={stroke};"
                "fontSize=7;align=center;verticalAlign=top;spacingTop=5;",
            )

    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def hex_rgb(value: str) -> Tuple[float, float, float]:
    value = value.lstrip("#")
    return tuple(int(value[index:index+2], 16) / 255.0 for index in (0, 2, 4))


def pdf_wrapped(pdf: canvas.Canvas, text: str, center_x: float, top_y: float,
                width: float, height: float, font: str, size: float, color,
                max_lines: int, leading: float = None) -> None:
    leading = leading or size * 1.18
    words = text.split()
    lines: List[str] = []
    line = ""
    for word in words:
        candidate = word if not line else line + " " + word
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
    max_by_height = max(1, int(height // leading))
    lines = lines[:max_by_height]
    pdf.setFont(font, size)
    pdf.setFillColorRGB(*color)
    y = top_y
    for line in lines:
        pdf.drawCentredString(center_x, y, line)
        y -= leading


def draw_pdf_tile(pdf: canvas.Canvas, group: List[Step], tile_index: int) -> None:
    page_width, page_height = landscape(A3)
    pdf.setFillColorRGB(1, 1, 1)
    pdf.rect(0, 0, page_width, page_height, fill=1, stroke=0)

    def x(value: float) -> float:
        return value * mm

    def y(value: float) -> float:
        return page_height - value * mm

    pdf.setFillColorRGB(0.1, 0.1, 0.1)
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(x(12), y(14), "Software Implementation Planning - roadmap")
    pdf.setFont("Helvetica", 8.5)
    pdf.setFillColorRGB(0.35, 0.35, 0.35)
    pdf.drawString(
        x(12),
        y(22),
        "Milestone map; not a Gantt. Baseline: 1 focused project day/week. Dates are working targets.",
    )

    pdf.setStrokeColorRGB(0.2, 0.2, 0.2)
    pdf.setLineWidth(1.0)
    pdf.line(x(8), y(TIMELINE_Y_MM), x(A3_W_MM - 8), y(TIMELINE_Y_MM))

    usable = A3_W_MM - 2 * MARGIN_MM
    cell = usable / len(group)
    for index, step in enumerate(group):
        center_x_mm = MARGIN_MM + cell * (index + 0.5)
        card_width_mm = min(110.0, cell - 5.0)
        _label, fill_hex, stroke_hex = WORKSTREAMS.get(
            step.workstream,
            WORKSTREAMS["architecture"],
        )
        fill = hex_rgb(fill_hex)
        stroke = hex_rgb(stroke_hex)

        center_x = x(center_x_mm)
        center_y = y(TIMELINE_Y_MM)
        radius = x(5)
        path = pdf.beginPath()
        path.moveTo(center_x, center_y + radius)
        path.lineTo(center_x + radius, center_y)
        path.lineTo(center_x, center_y - radius)
        path.lineTo(center_x - radius, center_y)
        path.close()
        pdf.setFillColorRGB(1, 1, 1)
        pdf.setStrokeColorRGB(0.2, 0.2, 0.2)
        pdf.drawPath(path, fill=1, stroke=1)
        pdf.setFillColorRGB(0.1, 0.1, 0.1)
        pdf.setFont("Helvetica-Bold", 8)
        pdf.drawCentredString(center_x, center_y - 2.5, str(step.number))
        pdf.setStrokeColorRGB(0.4, 0.4, 0.4)
        pdf.setLineWidth(0.5)
        pdf.line(center_x, y(TIMELINE_Y_MM + 5), center_x, y(248))

        pdf.setFillColorRGB(*stroke)
        pdf.setFont("Helvetica-Bold", 7.2)
        pdf.drawCentredString(center_x, y(32), f"~{step.estimate_days} project days")
        pdf.drawCentredString(center_x, y(37), f"target {step.target_date.strftime('%d %b %Y')}")

        pdf_wrapped(
            pdf,
            f"Step {step.number} - {step.title}",
            center_x,
            y(65),
            x(card_width_mm - 4),
            x(24),
            "Helvetica-Bold",
            7.5,
            (0.1, 0.1, 0.1),
            3,
            8.5,
        )

        left = x(center_x_mm - card_width_mm / 2)
        pdf.setFillColorRGB(*fill)
        pdf.setStrokeColorRGB(*stroke)
        pdf.roundRect(left, y(157), x(card_width_mm), x(63), x(2), fill=1, stroke=1)
        pdf.setFillColorRGB(*stroke)
        pdf.setFont("Helvetica-Bold", 6.8)
        pdf.drawString(left + x(3), y(103), "DELIVERABLE")
        pdf_wrapped(
            pdf,
            step.deliverable,
            center_x,
            y(113),
            x(card_width_mm - 6),
            x(40),
            "Helvetica",
            6.4,
            (0.12, 0.12, 0.12),
            9,
            7.3,
        )

        pdf.setFillColorRGB(1, 1, 1)
        pdf.setStrokeColorRGB(*stroke)
        pdf.roundRect(left, y(241), x(card_width_mm), x(70), x(2), fill=1, stroke=1)
        pdf.setFillColorRGB(*stroke)
        pdf.setFont("Helvetica-Bold", 6.8)
        pdf.drawString(left + x(3), y(180), "DEMONSTRATION")
        pdf_wrapped(
            pdf,
            step.demonstration,
            center_x,
            y(190),
            x(card_width_mm - 6),
            x(45),
            "Helvetica",
            6.2,
            (0.12, 0.12, 0.12),
            10,
            7.0,
        )

    pdf.setStrokeColorRGB(0.55, 0.55, 0.55)
    pdf.setLineWidth(0.5)
    for mark_y in (50, 255):
        if tile_index > 0:
            pdf.line(x(2), y(mark_y), x(8), y(mark_y))
            pdf.line(x(5), y(mark_y - 3), x(5), y(mark_y + 3))
        if tile_index < TILE_COUNT - 1:
            pdf.line(x(A3_W_MM - 8), y(mark_y), x(A3_W_MM - 2), y(mark_y))
            pdf.line(
                x(A3_W_MM - 5),
                y(mark_y - 3),
                x(A3_W_MM - 5),
                y(mark_y + 3),
            )

    footer = (
        f"A3 tile {tile_index+1}/{TILE_COUNT} - Steps {group[0].number}-{group[-1].number} "
        "- PRINT AT 100% / ACTUAL SIZE"
    )
    pdf.setFont("Helvetica-Bold", 7)
    pdf.setFillColorRGB(0.35, 0.35, 0.35)
    pdf.drawCentredString(page_width / 2, y(288), footer)
    if tile_index > 0:
        pdf.drawString(x(4), y(279), "<- JOIN")
    if tile_index < TILE_COUNT - 1:
        pdf.drawRightString(x(A3_W_MM - 4), y(279), "JOIN ->")


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
    pdf.drawString(14 * mm, page_height - 16 * mm, "Software Implementation Planning - A2 overview")
    pdf.setFont("Helvetica", 8)
    pdf.drawString(
        14 * mm,
        page_height - 24 * mm,
        "Compact milestone view. For detailed deliverables/demonstrations use the three-tile A3 PDF.",
    )

    left = 14 * mm
    right = page_width - 14 * mm
    timeline_y = page_height - 52 * mm
    pdf.setLineWidth(1)
    pdf.line(left, timeline_y, right, timeline_y)
    usable = right - left
    cell = usable / len(steps)
    for index, step in enumerate(steps):
        center_x = left + cell * (index + 0.5)
        _label, fill_hex, stroke_hex = WORKSTREAMS.get(
            step.workstream,
            WORKSTREAMS["architecture"],
        )
        fill = hex_rgb(fill_hex)
        stroke = hex_rgb(stroke_hex)
        pdf.setFillColorRGB(1, 1, 1)
        pdf.setStrokeColorRGB(0.2, 0.2, 0.2)
        path = pdf.beginPath()
        radius = 4 * mm
        path.moveTo(center_x, timeline_y + radius)
        path.lineTo(center_x + radius, timeline_y)
        path.lineTo(center_x, timeline_y - radius)
        path.lineTo(center_x - radius, timeline_y)
        path.close()
        pdf.drawPath(path, fill=1, stroke=1)
        pdf.setFont("Helvetica-Bold", 7)
        pdf.setFillColorRGB(0.1, 0.1, 0.1)
        pdf.drawCentredString(center_x, timeline_y - 2.5, str(step.number))
        pdf.setStrokeColorRGB(*stroke)
        pdf.setLineWidth(0.5)
        pdf.line(center_x, timeline_y - 4 * mm, center_x, timeline_y - 26 * mm)
        box_width = max(24 * mm, cell - 2 * mm)
        box_left = center_x - box_width / 2
        box_bottom = timeline_y - 61 * mm
        pdf.setFillColorRGB(*fill)
        pdf.setStrokeColorRGB(*stroke)
        pdf.roundRect(box_left, box_bottom, box_width, 31 * mm, 2 * mm, fill=1, stroke=1)
        pdf.setFillColorRGB(*stroke)
        pdf.setFont("Helvetica-Bold", 5.8)
        pdf.drawCentredString(center_x, box_bottom + 25 * mm, f"STEP {step.number} | ~{step.estimate_days}d")
        pdf_wrapped(
            pdf,
            step.title,
            center_x,
            box_bottom + 20 * mm,
            box_width - 4 * mm,
            15 * mm,
            "Helvetica-Bold",
            5.4,
            (0.1, 0.1, 0.1),
            4,
            6.0,
        )
        pdf.setFont("Helvetica", 5.0)
        pdf.drawCentredString(center_x, box_bottom + 3.5 * mm, step.target_date.strftime("%d %b %Y"))

    total = sum(step.estimate_days for step in steps)
    reserve = float(plan.get("planning_reserve_fraction", 0.0))
    cadence = float(plan["cadence_project_days_per_week"])
    reserve_end = date.fromisoformat(plan["start_date"]) + timedelta(
        days=round(total * (1 + reserve) / cadence * 7)
    )
    pdf.setFont("Helvetica-Bold", 8)
    pdf.setFillColorRGB(0.25, 0.25, 0.25)
    pdf.drawString(
        14 * mm,
        18 * mm,
        f"Baseline {total} project days; +{int(reserve*100)}% reserve gives a planning horizon around {reserve_end.strftime('%b %Y')}.",
    )
    pdf.drawRightString(page_width - 14 * mm, 18 * mm, "PRINT AT 100% / ACTUAL SIZE")
    pdf.save()


def render_readme(steps: List[Step], groups: List[List[Step]], plan: dict, path: Path) -> None:
    total = sum(step.estimate_days for step in steps)
    reserve = float(plan.get("planning_reserve_fraction", 0.0))
    cadence = float(plan["cadence_project_days_per_week"])
    start = date.fromisoformat(plan["start_date"])
    reserve_end = start + timedelta(days=round(total * (1 + reserve) / cadence * 7))
    lines = [
        "# SIP roadmap",
        "",
        "Generated from the source SIP plus the working effort baseline in `docs/_data/sip-roadmap.json`.",
        "",
        "The roadmap is a milestone map, **not a time-scaled Gantt chart**. Dates are planning targets rather than commitments.",
        "",
        f"Planning basis: **{plan['cadence_project_days_per_week']:g} focused project day/week**, {total} baseline project days, plus {int(reserve*100)}% planning reserve.",
        f"Baseline completion: **{steps[-1].target_date.strftime('%d %b %Y')}**. Planning horizon with reserve: **about {reserve_end.strftime('%d %b %Y')}**.",
        "",
        "## Outputs",
        "",
        "- [Continuous SVG panorama](./sip-roadmap.svg) - best for GitHub/browser zooming.",
        "- [Editable draw.io panorama](./sip-roadmap.drawio).",
        "- [A3 tiled PDF](./sip-roadmap-a3-tiled.pdf) - three A3 landscape sheets that join left-to-right.",
        "- [A2 overview PDF](./sip-roadmap-a2-overview.pdf) - compact single-page milestone overview.",
        "",
        "## A3 assembly",
        "",
        "Print all three A3 pages at **100% / Actual size**. Place them in page-number order from left to right. Join/cross marks are provided at the inner edges. The page split is recalculated from project-day estimates and only occurs **between SIP steps**, never through a step card.",
        "",
        "## Working schedule",
        "",
        "| Step | Estimate | Baseline target |",
        "| --- | ---: | --- |",
    ]
    for step in steps:
        lines.append(
            f"| {step.number} - {step.title} | {step.estimate_days} project days | "
            f"{step.target_date.strftime('%d %b %Y')} |"
        )
    lines.extend(["", "## Current A3 tile split", ""])
    for index, group in enumerate(groups, start=1):
        days = sum(step.estimate_days for step in group)
        lines.append(
            f"- Tile {index}: Steps {group[0].number}-{group[-1].number} ({days} project days)."
        )
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

    render_svg(steps, groups, plan, output / "sip-roadmap.svg")
    render_drawio(groups, output / "sip-roadmap.drawio")
    render_tiled_pdf(groups, output / "sip-roadmap-a3-tiled.pdf")
    render_a2_overview(steps, plan, output / "sip-roadmap-a2-overview.pdf")
    render_readme(steps, groups, plan, output / "README.md")

    print("Generated SIP roadmap")
    print(
        "A3 tile split:",
        " | ".join(f"{group[0].number}-{group[-1].number}" for group in groups),
    )


if __name__ == "__main__":
    main()
