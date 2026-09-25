#!/usr/bin/env python3
"""Render SIP step-board PDFs from the same validated planning sources as the SVG boards."""

from pathlib import Path
import argparse
import math

from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from generate_sip_planning import (
    A4_P_H_MM,
    A4_P_W_MM,
    LANES,
    MARGIN_MM,
    MATURITY,
    STATE_STYLE,
    STEP_CARD_COLS,
    STEP_CARD_GAP,
    STEP_CARD_H,
    STEP_LANE_GAP,
    STEP_LANE_HEADER_H,
    activities_by_lane,
    concise,
    lane_height,
    load_json,
    load_step_boards,
    load_yaml,
    parse_sip,
    planning_change_lines,
    planning_changes_height,
    step_card_meta,
    step_demo_id,
    validate_data,
    wrap,
)


def font_points(size_mm: float) -> float:
    return size_mm * mm


def draw_text_top(
    c: canvas.Canvas,
    x_mm: float,
    y_mm: float,
    lines,
    size_mm: float,
    *,
    bold: bool = False,
    anchor: str = "middle",
    color: str = "#222222",
) -> None:
    c.setFillColor(HexColor(color))
    c.setFont("Helvetica-Bold" if bold else "Helvetica", font_points(size_mm))
    for index, line in enumerate(lines):
        line_y = A4_P_H_MM - (y_mm + index * size_mm * 1.20)
        if anchor == "start":
            c.drawString(x_mm * mm, line_y * mm, str(line))
        else:
            c.drawCentredString(x_mm * mm, line_y * mm, str(line))


def rounded_rect_top(
    c: canvas.Canvas,
    x_mm: float,
    y_mm: float,
    width_mm: float,
    height_mm: float,
    radius_mm: float,
    *,
    fill: str,
    stroke: str,
    line_width: float,
) -> None:
    c.setFillColor(HexColor(fill))
    c.setStrokeColor(HexColor(stroke))
    c.setLineWidth(line_width)
    c.roundRect(
        x_mm * mm,
        (A4_P_H_MM - y_mm - height_mm) * mm,
        width_mm * mm,
        height_mm * mm,
        radius_mm * mm,
        stroke=1,
        fill=1,
    )


def render_step_pdf(board: dict, step, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path), pagesize=A4)

    draw_text_top(
        c,
        MARGIN_MM,
        10.0,
        wrap(f"SIP Step {step.number} — {step.title}", 82, 2),
        4.0,
        bold=True,
        anchor="start",
    )
    draw_text_top(
        c,
        MARGIN_MM,
        17.0,
        [
            f"{board['state'].upper()} | ~{step.estimate_days} roadmap project days | "
            f"target {step.target_date.strftime('%d %b %Y')}"
        ],
        2.9,
        bold=True,
        anchor="start",
        color="#555555",
    )
    draw_text_top(
        c,
        MARGIN_MM,
        24.0,
        wrap(board.get("summary", ""), 75, 3),
        2.7,
        anchor="start",
        color="#555555",
    )

    demo = board.get("demonstration")
    usable_w = A4_P_W_MM - 2 * MARGIN_MM
    if demo:
        demo_top = 34.0
        demo_h = 27.0
        rounded_rect_top(
            c,
            MARGIN_MM,
            demo_top,
            usable_w,
            demo_h,
            1.5,
            fill="#f6f8fa",
            stroke="#6c8ebf",
            line_width=0.45,
        )
        draw_text_top(
            c,
            MARGIN_MM + 3,
            demo_top + 5.5,
            [f"END DEMO · {step_demo_id(step.number)}"],
            2.55,
            bold=True,
            anchor="start",
            color="#4f81bd",
        )
        cursor = demo_top + 10.5
        for bullet in demo["bullets"]:
            lines = wrap(bullet, 71, 2)
            draw_text_top(
                c,
                MARGIN_MM + 4,
                cursor,
                ["• " + lines[0]] + ["  " + line for line in lines[1:]],
                2.2,
                anchor="start",
                color="#333333",
            )
            cursor += len(lines) * 2.65 + 0.9
        docs_top = demo_top + demo_h + 4.0
    else:
        docs_top = 34.0

    docs = board["documents"]
    docs_h = 25.0 if len(docs) > 4 else 19.0
    rounded_rect_top(
        c,
        MARGIN_MM,
        docs_top,
        usable_w,
        docs_h,
        1.5,
        fill="#fafafa",
        stroke="#999999",
        line_width=0.4,
    )
    draw_text_top(
        c,
        MARGIN_MM + 3,
        docs_top + 5.5,
        ["DOCUMENTATION"],
        2.55,
        bold=True,
        anchor="start",
        color="#444444",
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
        draw_text_top(
            c,
            x,
            y + 2.1,
            [label],
            2.2,
            bold=True,
            anchor="start",
            color=style["stroke"],
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
            f"Step {step.number} A4 PDF board does not fit: needs {total_h:.1f} mm, "
            f"has {available_h:.1f} mm"
        )

    for lane, activities in lanes:
        title, lane_fill, lane_stroke = LANES[lane]
        height = lane_height(len(activities))
        rounded_rect_top(
            c,
            MARGIN_MM,
            y,
            usable_w,
            height,
            1.5,
            fill="#ffffff",
            stroke=lane_stroke,
            line_width=0.45,
        )
        rounded_rect_top(
            c,
            MARGIN_MM,
            y,
            usable_w,
            STEP_LANE_HEADER_H,
            1.5,
            fill=lane_fill,
            stroke=lane_stroke,
            line_width=0.35,
        )
        draw_text_top(
            c,
            MARGIN_MM + 2.5,
            y + 4.15,
            [title],
            2.55,
            bold=True,
            anchor="start",
            color=lane_stroke,
        )

        cards_top = y + STEP_LANE_HEADER_H + 1.3
        for idx, activity in enumerate(activities):
            row, col = divmod(idx, STEP_CARD_COLS)
            card_x = MARGIN_MM + col * (card_w + STEP_CARD_GAP)
            card_y = cards_top + row * (STEP_CARD_H + STEP_CARD_GAP)
            status_label, status_fill, status_stroke = STATE_STYLE[activity["state"]]
            rounded_rect_top(
                c,
                card_x,
                card_y,
                card_w,
                STEP_CARD_H,
                1.2,
                fill="#fffdf2",
                stroke=status_stroke,
                line_width=0.45,
            )
            draw_text_top(
                c,
                card_x + 1.6,
                card_y + 4.7,
                [activity["id"]],
                2.3,
                bold=True,
                anchor="start",
                color="#555555",
            )

            badge_w = 16.0
            rounded_rect_top(
                c,
                card_x + card_w - badge_w - 1.2,
                card_y + 1.0,
                badge_w,
                5.0,
                0.8,
                fill=status_fill,
                stroke=status_stroke,
                line_width=0.25,
            )
            draw_text_top(
                c,
                card_x + card_w - badge_w / 2 - 1.2,
                card_y + 4.55,
                [status_label],
                1.9,
                bold=True,
                color=status_stroke,
            )
            draw_text_top(
                c,
                card_x + card_w / 2,
                card_y + 9.5,
                wrap(activity["title"], 22, 3),
                3.0,
                bold=True,
            )
            meta = step_card_meta(activity)
            if meta:
                draw_text_top(
                    c,
                    card_x + 1.6,
                    card_y + STEP_CARD_H - 1.8,
                    [concise(meta, 34)],
                    2.2,
                    anchor="start",
                    color="#555555",
                )

        y += height + STEP_LANE_GAP

    if changes:
        change_top = y + 1.0
        rounded_rect_top(
            c,
            MARGIN_MM,
            change_top,
            usable_w,
            changes_h,
            1.5,
            fill="#fafafa",
            stroke="#999999",
            line_width=0.4,
        )
        draw_text_top(
            c,
            MARGIN_MM + 3,
            change_top + 5.4,
            ["PLANNING CHANGES"],
            2.55,
            bold=True,
            anchor="start",
            color="#555555",
        )
        cursor = change_top + 10.0
        for change in changes:
            lines = planning_change_lines(change)
            draw_text_top(
                c,
                MARGIN_MM + 4,
                cursor,
                [change["date"]],
                2.0,
                bold=True,
                anchor="start",
                color="#6c8ebf",
            )
            draw_text_top(
                c,
                MARGIN_MM + 24,
                cursor,
                lines,
                2.15,
                anchor="start",
                color="#333333",
            )
            cursor += max(5.4, len(lines) * 2.6 + 0.9)

    c.showPage()
    c.save()


def update_generated_readme(out_dir: Path, board_numbers) -> None:
    readme = out_dir / "README.md"
    if not readme.exists():
        return
    text = readme.read_text(encoding="utf-8")
    for number in sorted(board_numbers):
        old = f"- [Step {number}](./steps/step-{number:02d}.svg)"
        new = (
            f"- Step {number}: [SVG](./steps/step-{number:02d}.svg) · "
            f"[PDF](./steps/step-{number:02d}.pdf)"
        )
        text = text.replace(old, new)
    readme.write_text(text, encoding="utf-8")


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
    by_number = {step.number: step for step in steps}
    boards = load_step_boards(
        data_dir,
        load_json(data_dir / "schemas" / "sip-step-board.schema.json"),
    )

    out_dir = Path(args.out)
    for number, board in sorted(boards.items()):
        if number not in by_number:
            raise SystemExit(f"Step board without SIP milestone: {number}")
        render_step_pdf(
            board,
            by_number[number],
            out_dir / "steps" / f"step-{number:02d}.pdf",
        )

    update_generated_readme(out_dir, boards.keys())


if __name__ == "__main__":
    main()
