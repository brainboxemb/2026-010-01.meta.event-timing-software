#!/usr/bin/env python3
"""Generate screen-first A4 review SVGs for SIP planning.

The existing planning generator remains the source of the A2/A3 print views.
This companion generator deliberately optimises review SVGs for monitors:
- A4 landscape page proportions;
- compact blocks with less empty space;
- relatively larger text;
- lane headers above cards rather than wide vertical lane labels.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List, Tuple
import argparse
import html
import math

from generate_sip_planning import (
    LANES,
    MATURITY,
    STATE_STYLE,
    Step,
    compact_doc_label,
    concise,
    document_indicators,
    load_json,
    load_step_boards,
    load_yaml,
    parse_sip,
    partition_steps,
    step_card_meta,
    validate_data,
    wrap,
)


A4_L_W_MM = 297.0
A4_L_H_MM = 210.0
MARGIN_MM = 8.0
ROADMAP_TIMELINE_Y = 31.0
ROADMAP_CARD_TOP = 59.0
ROADMAP_DELIVERABLE_H = 37.0
ROADMAP_DEMO_TOP = 101.0
ROADMAP_DEMO_H = 37.0
ROADMAP_DOC_TOP = 143.0
ROADMAP_DOC_H = 40.0

STEP_TOP = 48.0
STEP_CARD_COLS = 4
STEP_CARD_H = 14.0
STEP_CARD_GAP = 1.5
STEP_LANE_HEADER_H = 5.2
STEP_LANE_GAP = 1.5


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


def roadmap_positions(group: List[Step]) -> List[Tuple[Step, float, float]]:
    usable = A4_L_W_MM - 2 * MARGIN_MM
    cell = usable / len(group)
    return [
        (
            step,
            MARGIN_MM + cell * (index + 0.5),
            max(46.0, cell - 5.0),
        )
        for index, step in enumerate(group)
    ]


def render_roadmap_page(
    group: List[Step], page_index: int, page_count: int, boards: Dict[int, dict], path: Path
) -> None:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{A4_L_W_MM}mm" height="{A4_L_H_MM}mm" '
        f'viewBox="0 0 {A4_L_W_MM} {A4_L_H_MM}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]
    svg_text(parts, MARGIN_MM, 10.5, ["Software Implementation Planning — roadmap review"], 5.1, anchor="start", weight="bold")
    svg_text(
        parts,
        MARGIN_MM,
        17.5,
        [f"A4 screen view {page_index + 1}/{page_count} — Steps {group[0].number}-{group[-1].number}; print views remain separate."],
        2.35,
        anchor="start",
        fill="#555",
    )
    parts.append(
        f'<line x1="{MARGIN_MM}" y1="{ROADMAP_TIMELINE_Y}" x2="{A4_L_W_MM-MARGIN_MM}" y2="{ROADMAP_TIMELINE_Y}" '
        'stroke="#333" stroke-width="0.65"/>'
    )

    for step, center_x, width in roadmap_positions(group):
        radius = 3.3
        points = (
            f"{center_x},{ROADMAP_TIMELINE_Y-radius} {center_x+radius},{ROADMAP_TIMELINE_Y} "
            f"{center_x},{ROADMAP_TIMELINE_Y+radius} {center_x-radius},{ROADMAP_TIMELINE_Y}"
        )
        parts.append(f'<polygon points="{points}" fill="white" stroke="#333" stroke-width="0.55"/>')
        svg_text(parts, center_x, ROADMAP_TIMELINE_Y + 0.9, [step.number], 2.5, weight="bold")
        svg_text(
            parts,
            center_x,
            24.0,
            [f"~{step.estimate_days}d", step.target_date.strftime("%d %b %Y")],
            2.15,
            weight="bold",
            fill="#555",
        )
        svg_text(parts, center_x, 41.0, wrap(f"Step {step.number} — {step.title}", 24, 3), 2.55, weight="bold")

        x = center_x - width / 2
        parts.append(
            f'<rect x="{x:.2f}" y="{ROADMAP_CARD_TOP}" width="{width:.2f}" height="{ROADMAP_DELIVERABLE_H}" rx="1.6" '
            'fill="#f6f8fa" stroke="#6c8ebf" stroke-width="0.55"/>'
        )
        svg_text(parts, x + 2.5, ROADMAP_CARD_TOP + 6.0, ["DELIVERABLE"], 2.15, anchor="start", weight="bold", fill="#4f81bd")
        svg_text(parts, center_x, ROADMAP_CARD_TOP + 13.0, wrap(step.deliverable, max(18, int(width / 2.0)), 6), 2.0)

        parts.append(
            f'<rect x="{x:.2f}" y="{ROADMAP_DEMO_TOP}" width="{width:.2f}" height="{ROADMAP_DEMO_H}" rx="1.6" '
            'fill="#ffffff" stroke="#6c8ebf" stroke-width="0.55"/>'
        )
        svg_text(parts, x + 2.5, ROADMAP_DEMO_TOP + 6.0, ["DEMONSTRATION"], 2.15, anchor="start", weight="bold", fill="#4f81bd")
        svg_text(parts, center_x, ROADMAP_DEMO_TOP + 13.0, wrap(step.demonstration, max(18, int(width / 2.0)), 6), 1.95)

        parts.append(
            f'<rect x="{x:.2f}" y="{ROADMAP_DOC_TOP}" width="{width:.2f}" height="{ROADMAP_DOC_H}" rx="1.6" '
            'fill="#fafafa" stroke="#999" stroke-width="0.4"/>'
        )
        svg_text(parts, x + 2.5, ROADMAP_DOC_TOP + 6.0, ["DOCUMENTS"], 2.05, anchor="start", weight="bold", fill="#555")
        documents = document_indicators(step, boards.get(step.number))[:6]
        for idx, document in enumerate(documents):
            row, col = divmod(idx, 2)
            chip_w = (width - 7.0) / 2
            chip_x = x + 2.3 + col * (chip_w + 2.3)
            chip_y = ROADMAP_DOC_TOP + 10.0 + row * 8.0
            style = MATURITY[document["maturity"]]
            parts.append(
                f'<rect x="{chip_x:.2f}" y="{chip_y:.2f}" width="{chip_w:.2f}" height="6.2" rx="1" '
                f'fill="{style["fill"]}" stroke="{style["stroke"]}" stroke-width="0.3"/>'
            )
            svg_text(parts, chip_x + chip_w / 2, chip_y + 4.0, [concise(compact_doc_label(document), 18)], 1.65, weight="bold", fill=style["stroke"])

    svg_text(parts, MARGIN_MM, A4_L_H_MM - 5.5, ["Screen-first A4 landscape review view — generated from the same SIP/YAML sources."], 1.9, anchor="start", fill="#666")
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def activities_by_lane(board: dict) -> List[Tuple[str, List[dict]]]:
    grouped: Dict[str, List[dict]] = {}
    for activity in board["activities"]:
        grouped.setdefault(activity["lane"], []).append(activity)
    return [(lane, grouped[lane]) for lane in LANES if grouped.get(lane)]


def lane_height(activity_count: int) -> float:
    rows = math.ceil(activity_count / STEP_CARD_COLS)
    return STEP_LANE_HEADER_H + 2.0 + rows * STEP_CARD_H + max(0, rows - 1) * STEP_CARD_GAP + 2.0


def render_step_review(board: dict, step: Step, path: Path) -> None:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{A4_L_W_MM}mm" height="{A4_L_H_MM}mm" '
        f'viewBox="0 0 {A4_L_W_MM} {A4_L_H_MM}">',
        '<rect width="100%" height="100%" fill="white"/>',
    ]
    svg_text(parts, MARGIN_MM, 10.0, [f"SIP Step {step.number} — {board['title']}"], 4.8, anchor="start", weight="bold")
    svg_text(
        parts,
        MARGIN_MM,
        16.5,
        [f"{board['state'].upper()} | ~{step.estimate_days} roadmap project days | target {step.target_date.strftime('%d %b %Y')}"],
        2.3,
        anchor="start",
        weight="bold",
        fill="#555",
    )
    svg_text(parts, MARGIN_MM, 22.5, wrap(board.get("summary", ""), 130, 2), 2.15, anchor="start", fill="#555")

    docs = board["documents"]
    docs_top = 29.0
    docs_h = 14.5 if len(docs) <= 4 else 20.5
    parts.append(
        f'<rect x="{MARGIN_MM}" y="{docs_top}" width="{A4_L_W_MM-2*MARGIN_MM}" height="{docs_h}" rx="1.5" '
        'fill="#fafafa" stroke="#999" stroke-width="0.4"/>'
    )
    svg_text(parts, MARGIN_MM + 3, docs_top + 5.0, ["DOCUMENTATION"], 2.0, anchor="start", weight="bold", fill="#444")
    doc_col_w = (A4_L_W_MM - 2 * MARGIN_MM - 9) / 2
    for idx, document in enumerate(docs):
        row, col = divmod(idx, 2)
        x = MARGIN_MM + 3 + col * (doc_col_w + 3)
        y = docs_top + 7.0 + row * 6.0
        style = MATURITY[document["maturity"]]
        label = f"{document['name']} {style['label']}{document['completeness']} — {concise(document['title'], 42)}"
        svg_text(parts, x, y + 2.0, [label], 1.7, anchor="start", weight="bold", fill=style["stroke"])

    y = docs_top + docs_h + 4.0
    usable_w = A4_L_W_MM - 2 * MARGIN_MM
    card_w = (usable_w - STEP_CARD_GAP * (STEP_CARD_COLS - 1)) / STEP_CARD_COLS

    lanes = activities_by_lane(board)
    total_lane_h = sum(lane_height(len(items)) for _, items in lanes) + STEP_LANE_GAP * max(0, len(lanes) - 1)
    available_h = A4_L_H_MM - y - 8.0
    if total_lane_h > available_h:
        raise SystemExit(
            f"Step {step.number} A4 review board does not fit: needs {total_lane_h:.1f} mm, has {available_h:.1f} mm"
        )

    for lane, activities in lanes:
        title, lane_fill, lane_stroke = LANES[lane]
        h = lane_height(len(activities))
        parts.append(
            f'<rect x="{MARGIN_MM}" y="{y:.2f}" width="{usable_w:.2f}" height="{h:.2f}" rx="1.5" '
            f'fill="#ffffff" stroke="{lane_stroke}" stroke-width="0.45"/>'
        )
        parts.append(
            f'<rect x="{MARGIN_MM}" y="{y:.2f}" width="{usable_w:.2f}" height="{STEP_LANE_HEADER_H:.2f}" rx="1.5" '
            f'fill="{lane_fill}" stroke="{lane_stroke}" stroke-width="0.35"/>'
        )
        svg_text(parts, MARGIN_MM + 2.5, y + 4.1, [title], 1.9, anchor="start", weight="bold", fill=lane_stroke)

        cards_top = y + STEP_LANE_HEADER_H + 2.0
        for idx, activity in enumerate(activities):
            row, col = divmod(idx, STEP_CARD_COLS)
            card_x = MARGIN_MM + col * (card_w + STEP_CARD_GAP)
            card_y = cards_top + row * (STEP_CARD_H + STEP_CARD_GAP)
            status_label, status_fill, status_stroke = STATE_STYLE[activity["state"]]
            parts.append(
                f'<rect x="{card_x:.2f}" y="{card_y:.2f}" width="{card_w:.2f}" height="{STEP_CARD_H:.2f}" rx="1.2" '
                f'fill="#fffdf2" stroke="{status_stroke}" stroke-width="0.45"/>'
            )
            svg_text(parts, card_x + 1.5, card_y + 3.6, [activity["id"]], 1.55, anchor="start", weight="bold", fill="#555")
            badge_w = 13.5
            parts.append(
                f'<rect x="{card_x+card_w-badge_w-1.1:.2f}" y="{card_y+0.9:.2f}" width="{badge_w:.2f}" height="3.9" rx="0.8" '
                f'fill="{status_fill}" stroke="{status_stroke}" stroke-width="0.25"/>'
            )
            svg_text(parts, card_x + card_w - badge_w / 2 - 1.1, card_y + 3.6, [status_label], 1.25, weight="bold", fill=status_stroke)
            svg_text(parts, card_x + card_w / 2, card_y + 7.8, wrap(activity["title"], 25, 2), 1.8, weight="bold")
            meta = step_card_meta(activity)
            if meta:
                svg_text(parts, card_x + 1.5, card_y + STEP_CARD_H - 1.8, [concise(meta, 48)], 1.2, anchor="start", fill="#666")
        y += h + STEP_LANE_GAP

    svg_text(parts, MARGIN_MM, A4_L_H_MM - 4.0, ["A4 landscape review view — use the A3 board when a larger print layout is preferred."], 1.7, anchor="start", fill="#666")
    parts.append("</svg>")
    path.write_text("\n".join(parts), encoding="utf-8")


def append_readme(out_dir: Path, roadmap_pages: List[Path], step_paths: List[Tuple[int, Path]]) -> None:
    readme = out_dir / "README.md"
    existing = readme.read_text(encoding="utf-8") if readme.exists() else "# Generated SIP planning\n"
    marker = "\n## A4 screen review views\n"
    if marker in existing:
        existing = existing.split(marker, 1)[0].rstrip() + "\n"
    lines = [
        "",
        "## A4 screen review views",
        "",
        "These SVGs are compact monitor-first views. They use A4-landscape proportions, less empty card space and relatively larger text. The A2/A3 outputs above remain the print-oriented views.",
        "",
        "### Roadmap pages",
        "",
    ]
    for index, path in enumerate(roadmap_pages, start=1):
        lines.append(f"- [A4 review roadmap {index}](./review/{path.name})")
    lines.extend(["", "### Step boards", ""])
    for number, path in step_paths:
        lines.append(f"- [Step {number} A4 review](./review/{path.name})")
    lines.append("")
    readme.write_text(existing.rstrip() + "\n" + "\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sip", default="docs/11-SIP-software-implementation-planning.md")
    parser.add_argument("--data-dir", default="docs/_data")
    parser.add_argument("--out", default="bld/docs/planning")
    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    roadmap_path = data_dir / "sip-roadmap.yaml"
    plan = load_yaml(roadmap_path)
    validate_data(plan, load_json(data_dir / "schemas" / "sip-roadmap.schema.json"), roadmap_path)
    steps = parse_sip(Path(args.sip), plan)
    boards = load_step_boards(data_dir, load_json(data_dir / "schemas" / "sip-step-board.schema.json"))
    step_by_number = {step.number: step for step in steps}
    groups = partition_steps(steps)

    out_dir = Path(args.out)
    review_dir = out_dir / "review"
    review_dir.mkdir(parents=True, exist_ok=True)

    roadmap_pages: List[Path] = []
    for page_index, group in enumerate(groups):
        path = review_dir / f"sip-roadmap-a4-review-{page_index+1}.svg"
        render_roadmap_page(group, page_index, len(groups), boards, path)
        roadmap_pages.append(path)

    step_paths: List[Tuple[int, Path]] = []
    for number, board in sorted(boards.items()):
        step = step_by_number[number]
        path = review_dir / f"step-{number:02d}-a4-review.svg"
        render_step_review(board, step, path)
        step_paths.append((number, path))

    append_readme(out_dir, roadmap_pages, step_paths)


if __name__ == "__main__":
    main()
