#!/usr/bin/env python3
"""Render the manager-facing SIP roadmap.

The SIP is the content source of truth for step title, status, result and demo.
Roadmap YAML contributes only estimates, terms and document-status metadata.
This renderer overwrites only the roadmap SVG/PDF outputs produced by
`generate_sip_planning.py`; detailed per-step activity boards remain owned by
the canonical planning generator.

The roadmap intentionally fails instead of ellipsizing SIP bullets. If a bullet
no longer fits, shorten the SIP wording or revisit the layout rather than
silently clipping meaning.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, List, Tuple
import argparse
import html
import textwrap

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

import generate_sip_planning as base


PAGE_W = base.A4_L_W_MM
PAGE_H = base.A4_L_H_MM
MARGIN = base.MARGIN_MM
STEP_PAGE_COUNT = base.ROADMAP_PAGE_COUNT
STEPS_PER_PAGE = base.ROADMAP_STEPS_PER_PAGE
TIMELINE_Y = 31.0
TERMS_W = 34.0
TERMS_GAP = 2.5
TERMS_TOP = 22.0
TERMS_H = 160.0

DELIVERABLE_TOP = 56.0
DELIVERABLE_H = 42.0
DEMO_TOP = 102.0
DEMO_H = 42.0
DOC_TOP = 148.0
DOC_H = 34.0

BODY_FONT_MM = 2.85
BODY_WRAP_CHARS = 34
BODY_MAX_LINES = 2
BODY_BULLET_GAP = 2.0

STATUS_STYLE = {
    "done": ("DONE", "#e2f0d9", "#548235"),
    "active": ("ACTIVE", "#ddebf7", "#4472c4"),
    "planned": ("PLANNED", "#f2f2f2", "#7f7f7f"),
}


def demo_id(step_number: int) -> str:
    return f"SIP-STP{step_number:02d}-DEMO"


def manager_positions(
    group: List[base.Step], page_index: int, page_x: float = 0.0
) -> List[Tuple[base.Step, float, float]]:
    usable = PAGE_W - 2 * MARGIN
    left = page_x + MARGIN
    if page_index == 0:
        left += TERMS_W + TERMS_GAP
        usable -= TERMS_W + TERMS_GAP
    cell = usable / STEPS_PER_PAGE
    return [
        (step, left + cell * (index + 0.5), cell - 5.0)
        for index, step in enumerate(group)
    ]


def timeline_start(page_index: int, page_x: float) -> float:
    if page_index == 0:
        return page_x + MARGIN + TERMS_W + TERMS_GAP
    return page_x + MARGIN


def manager_state(step: base.Step) -> str:
    if step.status not in STATUS_STYLE:
        raise SystemExit(
            f"Unsupported roadmap status for Step {step.number}: {step.status}"
        )
    return step.status


def bullet_lines(text: str) -> List[str]:
    lines = textwrap.wrap(
        text,
        width=BODY_WRAP_CHARS,
        break_long_words=False,
        break_on_hyphens=False,
    )
    if not lines:
        raise SystemExit("Manager-roadmap bullet may not be empty")
    if len(lines) > BODY_MAX_LINES:
        raise SystemExit(
            "Manager-roadmap bullet does not fit without clipping: "
            f"{text!r} -> {len(lines)} lines"
        )
    return lines


def validate_sip_steps(steps: Iterable[base.Step]) -> None:
    for step in steps:
        if not 1 <= len(step.result_bullets) <= 3:
            raise SystemExit(
                f"SIP Step {step.number} Result must contain 1..3 roadmap bullets"
            )
        if not 1 <= len(step.demo_bullets) <= 3:
            raise SystemExit(
                f"SIP Step {step.number} Demo must contain 1..3 roadmap bullets"
            )
        for bullet in step.result_bullets + step.demo_bullets:
            bullet_lines(bullet)


def svg_text(
    parts: List[str],
    x: float,
    y: float,
    lines: Iterable[str],
    size: float,
    *,
    anchor: str = "start",
    weight: str = "normal",
    fill: str = "#222222",
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


def svg_bullets(
    parts: List[str], x: float, y: float, bullets: List[str], *, width: float
) -> None:
    cursor = y
    for bullet in bullets:
        lines = bullet_lines(bullet)
        parts.append(
            f'<circle cx="{x + 1.2:.2f}" cy="{cursor - 0.8:.2f}" r="0.65" fill="#4f81bd"/>'
        )
        svg_text(
            parts,
            x + 3.4,
            cursor,
            lines,
            BODY_FONT_MM,
            anchor="start",
        )
        cursor += len(lines) * BODY_FONT_MM * 1.22 + BODY_BULLET_GAP


def svg_terms(parts: List[str], page_x: float, terms: List[dict]) -> None:
    x = page_x + MARGIN
    parts.append(
        f'<rect x="{x:.2f}" y="{TERMS_TOP:.2f}" width="{TERMS_W:.2f}" height="{TERMS_H:.2f}" '
        'rx="1.6" fill="#f8f9fa" stroke="#999999" stroke-width="0.4"/>'
    )
    svg_text(
        parts,
        x + 3.0,
        TERMS_TOP + 6.2,
        ["TERMS"],
        2.5,
        weight="bold",
        fill="#555555",
    )
    cursor = TERMS_TOP + 13.0
    for item in terms:
        svg_text(
            parts,
            x + 3.0,
            cursor,
            [item["term"]],
            2.25,
            weight="bold",
            fill="#333333",
        )
        meaning = textwrap.wrap(
            item["meaning"],
            width=22,
            break_long_words=False,
            break_on_hyphens=False,
        )
        if len(meaning) > 3:
            raise SystemExit(f"Roadmap term does not fit: {item['term']}")
        svg_text(
            parts,
            x + 3.0,
            cursor + 3.4,
            meaning,
            1.95,
            fill="#555555",
        )
        cursor += 5.2 + len(meaning) * 2.45 + 2.7


def svg_status_badge(parts: List[str], center_x: float, y: float, state: str) -> None:
    label, fill, stroke = STATUS_STYLE[state]
    width = 18.0 if state != "planned" else 21.0
    x = center_x - width / 2
    parts.append(
        f'<rect x="{x:.2f}" y="{y:.2f}" width="{width:.2f}" height="5.2" '
        f'rx="1.4" fill="{fill}" stroke="{stroke}" stroke-width="0.3"/>'
    )
    svg_text(
        parts,
        center_x,
        y + 3.65,
        [label],
        2.0,
        anchor="middle",
        weight="bold",
        fill=stroke,
    )


def append_svg_page(
    parts: List[str],
    group: List[base.Step],
    terms: List[dict],
    planning_basis: str,
    page_index: int,
    page_x: float,
    *,
    standalone: bool,
) -> None:
    if not standalone:
        parts.append(
            f'<rect x="{page_x:.2f}" y="0" width="{PAGE_W:.2f}" height="{PAGE_H:.2f}" '
            'fill="none" stroke="#d0d0d0" stroke-width="0.35"/>'
        )

    svg_text(
        parts,
        page_x + MARGIN,
        10.5,
        ["Software Implementation Planning — roadmap"],
        5.2,
        weight="bold",
    )
    svg_text(
        parts,
        page_x + MARGIN,
        17.5,
        [
            f"Page {page_index + 1}/{STEP_PAGE_COUNT} — "
            f"Steps {group[0].number}-{group[-1].number} · {planning_basis}"
        ],
        2.5,
        fill="#555555",
    )
    parts.append(
        f'<line x1="{timeline_start(page_index, page_x):.2f}" y1="{TIMELINE_Y:.2f}" '
        f'x2="{page_x + PAGE_W - MARGIN:.2f}" y2="{TIMELINE_Y:.2f}" '
        'stroke="#333333" stroke-width="0.65"/>'
    )

    if page_index == 0:
        svg_terms(parts, page_x, terms)

    for step, center_x, width in manager_positions(group, page_index, page_x):
        radius = 3.4
        state = manager_state(step)
        _, state_fill, state_stroke = STATUS_STYLE[state]
        points = (
            f"{center_x},{TIMELINE_Y-radius} {center_x+radius},{TIMELINE_Y} "
            f"{center_x},{TIMELINE_Y+radius} {center_x-radius},{TIMELINE_Y}"
        )
        parts.append(
            f'<polygon points="{points}" fill="{state_fill}" stroke="{state_stroke}" '
            'stroke-width="0.65"/>'
        )
        svg_text(
            parts,
            center_x,
            TIMELINE_Y + 0.9,
            [str(step.number)],
            2.7,
            anchor="middle",
            weight="bold",
            fill=state_stroke,
        )
        svg_text(
            parts,
            center_x,
            24.0,
            [base.step_effort_text(step), step.target_date.strftime("%b %Y")],
            2.35,
            anchor="middle",
            weight="bold",
            fill="#555555",
        )
        title_lines = textwrap.wrap(
            f"Step {step.number} — {step.title}",
            width=29,
            break_long_words=False,
            break_on_hyphens=False,
        )
        if len(title_lines) > 3:
            raise SystemExit(f"Roadmap title does not fit: Step {step.number}")
        svg_text(
            parts,
            center_x,
            40.5,
            title_lines,
            2.9,
            anchor="middle",
            weight="bold",
        )
        svg_status_badge(parts, center_x, 49.0, state)

        x = center_x - width / 2
        for top, height, heading, bullets, fill in (
            (DELIVERABLE_TOP, DELIVERABLE_H, "RESULT", step.result_bullets, "#f6f8fa"),
            (DEMO_TOP, DEMO_H, f"DEMO · {demo_id(step.number)}", step.demo_bullets, "#ffffff"),
        ):
            parts.append(
                f'<rect x="{x:.2f}" y="{top:.2f}" width="{width:.2f}" height="{height:.2f}" '
                f'rx="1.6" fill="{fill}" stroke="#6c8ebf" stroke-width="0.55"/>'
            )
            svg_text(
                parts,
                x + 3.0,
                top + 6.2,
                [heading],
                2.5,
                weight="bold",
                fill="#4f81bd",
            )
            svg_bullets(parts, x + 3.0, top + 13.0, bullets, width=width - 6.0)

        parts.append(
            f'<rect x="{x:.2f}" y="{DOC_TOP:.2f}" width="{width:.2f}" height="{DOC_H:.2f}" '
            'rx="1.6" fill="#fafafa" stroke="#999999" stroke-width="0.4"/>'
        )
        svg_text(
            parts,
            x + 3.0,
            DOC_TOP + 5.8,
            ["DOCUMENT STATUS"],
            2.35,
            weight="bold",
            fill="#555555",
        )
        for idx, document in enumerate(step.documents[:6]):
            row, col = divmod(idx, 2)
            chip_w = (width - 7.0) / 2
            chip_x = x + 2.3 + col * (chip_w + 2.3)
            chip_y = DOC_TOP + 9.0 + row * 8.0
            style = base.MATURITY[document["maturity"]]
            parts.append(
                f'<rect x="{chip_x:.2f}" y="{chip_y:.2f}" width="{chip_w:.2f}" height="6.3" '
                f'rx="1" fill="{style["fill"]}" stroke="{style["stroke"]}" stroke-width="0.3"/>'
            )
            svg_text(
                parts,
                chip_x + chip_w / 2,
                chip_y + 4.15,
                [base.compact_doc_label(document)],
                2.05,
                anchor="middle",
                weight="bold",
                fill=style["stroke"],
            )



def render_svgs(
    groups: List[List[base.Step]],
    terms: List[dict],
    planning_basis: str,
    out_dir: Path,
) -> None:
    page_dir = out_dir / "roadmap"
    page_dir.mkdir(parents=True, exist_ok=True)
    panorama_w = PAGE_W * STEP_PAGE_COUNT
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{panorama_w}mm" height="{PAGE_H}mm" '
        f'viewBox="0 0 {panorama_w} {PAGE_H}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]
    for page_index, group in enumerate(groups):
        append_svg_page(
            parts,
            group,
            terms,
            planning_basis,
            page_index,
            page_index * PAGE_W,
            standalone=False,
        )
    parts.append("</svg>")
    (out_dir / "sip-roadmap.svg").write_text("\n".join(parts), encoding="utf-8")

    for page_index, group in enumerate(groups):
        page_parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{PAGE_W}mm" height="{PAGE_H}mm" '
            f'viewBox="0 0 {PAGE_W} {PAGE_H}">',
            '<rect width="100%" height="100%" fill="white"/>',
        ]
        append_svg_page(
            page_parts,
            group,
            terms,
            planning_basis,
            page_index,
            0.0,
            standalone=True,
        )
        page_parts.append("</svg>")
        (page_dir / f"sip-roadmap-{page_index + 1}.svg").write_text(
            "\n".join(page_parts), encoding="utf-8"
        )



def pdf_bullets(
    c: canvas.Canvas, x: float, y: float, bullets: List[str], page_h: float
) -> None:
    cursor = y
    c.setFillColor(HexColor("#222222"))
    c.setFont("Helvetica", 7.8)
    for bullet in bullets:
        lines = bullet_lines(bullet)
        c.setFillColor(HexColor("#4f81bd"))
        c.circle((x + 1.2) * mm, (page_h - cursor + 0.8) * mm, 0.65 * mm, fill=1, stroke=0)
        c.setFillColor(HexColor("#222222"))
        for line_index, line in enumerate(lines):
            line_y = cursor + line_index * 3.55
            c.drawString((x + 3.4) * mm, (page_h - line_y) * mm, line)
        cursor += len(lines) * 3.55 + BODY_BULLET_GAP


def pdf_status_badge(
    c: canvas.Canvas, center_x: float, y: float, state: str, page_h: float
) -> None:
    label, fill, stroke = STATUS_STYLE[state]
    width = 18.0 if state != "planned" else 21.0
    x = center_x - width / 2
    c.setStrokeColor(HexColor(stroke))
    c.setFillColor(HexColor(fill))
    c.roundRect(
        x * mm,
        (page_h - y - 5.2) * mm,
        width * mm,
        5.2 * mm,
        1.4 * mm,
        stroke=1,
        fill=1,
    )
    c.setFillColor(HexColor(stroke))
    c.setFont("Helvetica-Bold", 5.7)
    c.drawCentredString(center_x * mm, (page_h - y - 3.75) * mm, label)


def render_pdf(
    groups: List[List[base.Step]],
    terms: List[dict],
    planning_basis: str,
    path: Path,
) -> None:
    c = canvas.Canvas(str(path), pagesize=landscape(A4))
    page_h = PAGE_H
    for page_index, group in enumerate(groups):
        c.setFillColor(HexColor("#222222"))
        c.setFont("Helvetica-Bold", 14)
        c.drawString(MARGIN * mm, (page_h - 10.5) * mm, "Software Implementation Planning — roadmap")
        c.setFillColor(HexColor("#555555"))
        c.setFont("Helvetica", 7)
        c.drawString(
            MARGIN * mm,
            (page_h - 17.5) * mm,
            (
                f"Page {page_index + 1}/{STEP_PAGE_COUNT} — "
                f"Steps {group[0].number}-{group[-1].number} · {planning_basis}"
            ),
        )
        c.setStrokeColor(HexColor("#333333"))
        c.setLineWidth(0.65)
        c.line(
            timeline_start(page_index, 0.0) * mm,
            (page_h - TIMELINE_Y) * mm,
            (PAGE_W - MARGIN) * mm,
            (page_h - TIMELINE_Y) * mm,
        )

        if page_index == 0:
            x = MARGIN
            c.setStrokeColor(HexColor("#999999"))
            c.setFillColor(HexColor("#f8f9fa"))
            c.roundRect(
                x * mm,
                (page_h - TERMS_TOP - TERMS_H) * mm,
                TERMS_W * mm,
                TERMS_H * mm,
                1.6 * mm,
                stroke=1,
                fill=1,
            )
            c.setFillColor(HexColor("#555555"))
            c.setFont("Helvetica-Bold", 7.0)
            c.drawString((x + 3.0) * mm, (page_h - TERMS_TOP - 6.2) * mm, "TERMS")
            cursor = TERMS_TOP + 13.0
            for item in terms:
                c.setFillColor(HexColor("#333333"))
                c.setFont("Helvetica-Bold", 6.4)
                c.drawString((x + 3.0) * mm, (page_h - cursor) * mm, item["term"])
                meaning = textwrap.wrap(
                    item["meaning"],
                    width=22,
                    break_long_words=False,
                    break_on_hyphens=False,
                )
                if len(meaning) > 3:
                    raise SystemExit(f"Roadmap term does not fit: {item['term']}")
                c.setFillColor(HexColor("#555555"))
                c.setFont("Helvetica", 5.5)
                for line_index, line in enumerate(meaning):
                    c.drawString(
                        (x + 3.0) * mm,
                        (page_h - cursor - 3.4 - line_index * 2.45) * mm,
                        line,
                    )
                cursor += 5.2 + len(meaning) * 2.45 + 2.7

        for step, center_x, width in manager_positions(group, page_index):
            state = manager_state(step)
            _, state_fill, state_stroke = STATUS_STYLE[state]
            r = 3.4
            path_points: List[Tuple[float, float]] = [
                (center_x, TIMELINE_Y - r),
                (center_x + r, TIMELINE_Y),
                (center_x, TIMELINE_Y + r),
                (center_x - r, TIMELINE_Y),
            ]
            p = c.beginPath()
            p.moveTo(path_points[0][0] * mm, (page_h - path_points[0][1]) * mm)
            for px, py in path_points[1:]:
                p.lineTo(px * mm, (page_h - py) * mm)
            p.close()
            c.setStrokeColor(HexColor(state_stroke))
            c.setFillColor(HexColor(state_fill))
            c.drawPath(p, stroke=1, fill=1)
            c.setFillColor(HexColor(state_stroke))
            c.setFont("Helvetica-Bold", 7)
            c.drawCentredString(center_x * mm, (page_h - TIMELINE_Y - 1.0) * mm, str(step.number))

            c.setFillColor(HexColor("#555555"))
            c.setFont("Helvetica-Bold", 6.5)
            c.drawCentredString(center_x * mm, (page_h - 22.8) * mm, base.step_effort_text(step))
            c.drawCentredString(
                center_x * mm,
                (page_h - 26.0) * mm,
                step.target_date.strftime("%b %Y"),
            )
            title_lines = textwrap.wrap(
                f"Step {step.number} — {step.title}",
                width=29,
                break_long_words=False,
                break_on_hyphens=False,
            )
            c.setFillColor(HexColor("#222222"))
            c.setFont("Helvetica-Bold", 7.6)
            for line_index, line in enumerate(title_lines):
                c.drawCentredString(
                    center_x * mm,
                    (page_h - 40.5 - line_index * 3.4) * mm,
                    line,
                )
            pdf_status_badge(c, center_x, 49.0, state, page_h)

            x = center_x - width / 2
            for top, height, heading, bullets, fill in (
                (DELIVERABLE_TOP, DELIVERABLE_H, "RESULT", step.result_bullets, "#f6f8fa"),
                (DEMO_TOP, DEMO_H, f"DEMO · {demo_id(step.number)}", step.demo_bullets, "#ffffff"),
            ):
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
                c.setFont("Helvetica-Bold", 7.0)
                c.drawString((x + 3.0) * mm, (page_h - top - 6.2) * mm, heading)
                pdf_bullets(c, x + 3.0, top + 13.0, bullets, page_h)

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
            c.setFont("Helvetica-Bold", 6.5)
            c.drawString((x + 3.0) * mm, (page_h - DOC_TOP - 5.8) * mm, "DOCUMENT STATUS")
            for idx, document in enumerate(step.documents[:6]):
                row, col = divmod(idx, 2)
                chip_w = (width - 7.0) / 2
                chip_x = x + 2.3 + col * (chip_w + 2.3)
                chip_y = DOC_TOP + 9.0 + row * 8.0
                style = base.MATURITY[document["maturity"]]
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
                c.setFont("Helvetica-Bold", 5.7)
                c.drawCentredString(
                    (chip_x + chip_w / 2) * mm,
                    (page_h - chip_y - 4.25) * mm,
                    base.compact_doc_label(document),
                )
        c.showPage()


    c.save()





def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sip", default="docs/11-SIP-software-implementation-planning.md")
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
    validate_sip_steps(steps)
    groups = base.roadmap_groups(steps)
    terms = list(plan["terms"])
    planning_basis = base.planning_basis_text(steps, plan)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "roadmap").mkdir(parents=True, exist_ok=True)

    render_svgs(groups, terms, planning_basis, out_dir)
    render_pdf(groups, terms, planning_basis, out_dir / "sip-roadmap.pdf")


if __name__ == "__main__":
    main()
