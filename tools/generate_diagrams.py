#!/usr/bin/env python3
"""Generate declarative engineering diagrams as SVG and native draw.io XML."""

from __future__ import annotations

from pathlib import Path
import argparse
import html
import json
import xml.etree.ElementTree as ET

import yaml
from jsonschema import Draft202012Validator


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def validate_source(data, schema, path: Path):
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    if errors:
        lines = [f"{path}: invalid diagram source"]
        for err in errors:
            loc = ".".join(str(x) for x in err.path) or "<root>"
            lines.append(f"  {loc}: {err.message}")
        raise SystemExit("\n".join(lines))


def validate_refs(data, theme, path: Path):
    group_ids = {g["id"] for g in data["groups"]}
    node_ids = {n["id"] for n in data["nodes"]}
    if len(group_ids) != len(data["groups"]):
        raise SystemExit(f"{path}: duplicate group id")
    if len(node_ids) != len(data["nodes"]):
        raise SystemExit(f"{path}: duplicate node id")
    overlap = group_ids & node_ids
    if overlap:
        raise SystemExit(f"{path}: ids reused by group and node: {sorted(overlap)}")
    kinds = theme.get("kinds", {})
    for item in [*data["groups"], *data["nodes"]]:
        if item["kind"] not in kinds:
            raise SystemExit(f"{path}: unknown kind {item['kind']!r} on {item['id']}")
    for node in data["nodes"]:
        if node.get("group") and node["group"] not in group_ids:
            raise SystemExit(f"{path}: node {node['id']} references missing group {node['group']}")
    for edge in data["edges"]:
        if edge["from"] not in node_ids or edge["to"] not in node_ids:
            raise SystemExit(f"{path}: edge references missing node: {edge['from']} -> {edge['to']}")


def style(theme, kind):
    return theme["kinds"][kind]


def center(item):
    r = item["layout"]
    return r["x"] + r["w"] / 2, r["y"] + r["h"] / 2


def boundary_point(source, target):
    sx, sy = center(source)
    tx, ty = center(target)
    dx, dy = tx - sx, ty - sy
    if dx == 0 and dy == 0:
        return sx, sy
    scale_x = source["layout"]["w"] / 2 / abs(dx) if dx else float("inf")
    scale_y = source["layout"]["h"] / 2 / abs(dy) if dy else float("inf")
    scale = min(scale_x, scale_y)
    return sx + dx * scale, sy + dy * scale


def svg_text(parts, text, x, y, size, family, weight="normal", anchor="middle"):
    lines = str(text).splitlines() or [""]
    line_height = size * 1.28
    start = y - (len(lines) - 1) * line_height / 2
    for i, line in enumerate(lines):
        parts.append(
            f'<text x="{x:.1f}" y="{start + i * line_height:.1f}" text-anchor="{anchor}" '
            f'dominant-baseline="middle" font-family="{html.escape(family)}" '
            f'font-size="{size}" font-weight="{weight}" fill="#202124">{html.escape(line)}</text>'
        )


def render_svg(data, theme, out: Path):
    d = data["diagram"]
    family = theme["font"]["family"]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{d["width"]}" height="{d["height"]}" viewBox="0 0 {d["width"]} {d["height"]}">',
        "<defs>",
        '<marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">',
        f'<path d="M0,0 L0,6 L9,3 z" fill="{theme["canvas"]["edge"]}"/>',
        "</marker>",
        "</defs>",
        f'<rect width="100%" height="100%" fill="{theme["canvas"]["background"]}"/>',
    ]
    svg_text(parts, d["title"], 30, 38, theme["font"]["title_size"], family, "bold", "start")
    if d.get("note"):
        svg_text(parts, d["note"], 30, 68, theme["font"]["note_size"], family, "normal", "start")

    for group in data["groups"]:
        r = group["layout"]
        s = style(theme, group["kind"])
        parts.append(
            f'<rect x="{r["x"]}" y="{r["y"]}" width="{r["w"]}" height="{r["h"]}" '
            f'rx="10" ry="10" fill="{s["fill"]}" stroke="{s["stroke"]}" stroke-width="2"/>'
        )
        svg_text(parts, group["label"], r["x"] + 16, r["y"] + 22, theme["font"]["group_title_size"], family, "bold", "start")

    nodes = {n["id"]: n for n in data["nodes"]}
    for edge in data["edges"]:
        source = nodes[edge["from"]]
        target = nodes[edge["to"]]
        x1, y1 = boundary_point(source, target)
        x2, y2 = boundary_point(target, source)
        points = [(x1, y1)] + [(p["x"], p["y"]) for p in edge.get("route", [])] + [(x2, y2)]
        dash = ' stroke-dasharray="7 5"' if edge.get("dashed") else ""
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        parts.append(
            f'<polyline points="{pts}" fill="none" stroke="{theme["canvas"]["edge"]}" stroke-width="2"{dash} marker-end="url(#arrow)"/>'
        )
        if edge.get("label"):
            mx, my = points[len(points) // 2]
            label = edge["label"]
            width = max(80, min(190, 8 * len(label)))
            parts.append(
                f'<rect x="{mx - width / 2:.1f}" y="{my - 13:.1f}" width="{width}" height="22" '
                f'fill="{theme["canvas"]["edge_label_background"]}" opacity="0.94"/>'
            )
            svg_text(parts, label, mx, my - 1, 12, family)

    for node in data["nodes"]:
        r = node["layout"]
        s = style(theme, node["kind"])
        parts.append(
            f'<rect x="{r["x"]}" y="{r["y"]}" width="{r["w"]}" height="{r["h"]}" '
            f'rx="8" ry="8" fill="{s["fill"]}" stroke="{s["stroke"]}" stroke-width="2"/>'
        )
        svg_text(parts, node["label"], r["x"] + r["w"] / 2, r["y"] + r["h"] / 2, theme["font"]["node_size"], family)

    parts.append("</svg>")
    out.write_text("\n".join(parts) + "\n", encoding="utf-8")


def drawio_node_style(theme, kind, group=False):
    s = style(theme, kind)
    result = (
        "rounded=1;whiteSpace=wrap;html=1;"
        f"fillColor={s['fill']};strokeColor={s['stroke']};fontFamily=Helvetica;"
    )
    if group:
        result += "verticalAlign=top;align=left;spacingTop=8;spacingLeft=10;fontStyle=1;fontSize=17;"
    else:
        result += "fontSize=14;"
    return result


def render_drawio(data, theme, out: Path):
    d = data["diagram"]
    mxfile = ET.Element("mxfile", host="app.diagrams.net", compressed="false")
    diagram = ET.SubElement(mxfile, "diagram", id=d["id"], name=d["title"])
    model = ET.SubElement(
        diagram, "mxGraphModel", dx="1200", dy="800", grid="1", gridSize="10",
        guides="1", tooltips="1", connect="1", arrows="1", fold="1", page="1",
        pageScale="1", pageWidth=str(d["width"]), pageHeight=str(d["height"]), math="0", shadow="0"
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    for group in data["groups"]:
        r = group["layout"]
        cell = ET.SubElement(
            root, "mxCell", id=f"group-{group['id']}", value=group["label"],
            style=drawio_node_style(theme, group["kind"], True), vertex="1", parent="1"
        )
        ET.SubElement(cell, "mxGeometry", x=str(r["x"]), y=str(r["y"]), width=str(r["w"]), height=str(r["h"]), **{"as": "geometry"})

    for node in data["nodes"]:
        r = node["layout"]
        cell = ET.SubElement(
            root, "mxCell", id=node["id"], value=node["label"].replace("\n", "<br>"),
            style=drawio_node_style(theme, node["kind"]), vertex="1", parent="1"
        )
        ET.SubElement(cell, "mxGeometry", x=str(r["x"]), y=str(r["y"]), width=str(r["w"]), height=str(r["h"]), **{"as": "geometry"})

    for i, edge in enumerate(data["edges"], 1):
        edge_style = "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;jettySize=auto;html=1;endArrow=block;endFill=1;"
        if edge.get("dashed"):
            edge_style += "dashed=1;"
        cell = ET.SubElement(
            root, "mxCell", id=f"edge-{i}", value=edge.get("label", ""), style=edge_style,
            edge="1", parent="1", source=edge["from"], target=edge["to"]
        )
        geom = ET.SubElement(cell, "mxGeometry", relative="1", **{"as": "geometry"})
        if edge.get("route"):
            points = ET.SubElement(geom, "Array", **{"as": "points"})
            for point in edge["route"]:
                ET.SubElement(points, "mxPoint", x=str(point["x"]), y=str(point["y"]))

    ET.indent(mxfile, space="  ")
    out.write_text(ET.tostring(mxfile, encoding="unicode") + "\n", encoding="utf-8")


def generate(source_dir: Path, schema_path: Path, theme_path: Path, out_dir: Path):
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    theme = load_yaml(theme_path)
    out_dir.mkdir(parents=True, exist_ok=True)
    generated = []

    for path in sorted(source_dir.glob("*.yaml")):
        data = load_yaml(path)
        validate_source(data, schema, path)
        validate_refs(data, theme, path)
        diagram_id = data["diagram"]["id"]
        render_svg(data, theme, out_dir / f"{diagram_id}.svg")
        render_drawio(data, theme, out_dir / f"{diagram_id}.drawio")
        generated.append(data["diagram"])

    index = [
        "# Generated declarative architecture diagrams", "",
        "Sources: `docs/_diagrams/*.yaml`; schema and theme are validated during generation.", "",
    ]
    for d in generated:
        index.extend([
            f"## {d['title']}", "",
            f"![{d['title']}](./{d['id']}.svg)", "",
            f"- [Editable draw.io file](./{d['id']}.drawio)", "",
        ])
    (out_dir / "README.md").write_text("\n".join(index), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="docs/_diagrams")
    parser.add_argument("--schema", default="docs/_data/schemas/diagram.schema.json")
    parser.add_argument("--theme", default="docs/_diagram-theme/default.yaml")
    parser.add_argument("--out", default="bld/docs/architecture")
    args = parser.parse_args()
    generate(Path(args.source), Path(args.schema), Path(args.theme), Path(args.out))


if __name__ == "__main__":
    main()
