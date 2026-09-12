#!/usr/bin/env python3
"""Generate architecture diagrams as SVG and uncompressed draw.io XML.

A single Python model owns the labels, coordinates and connections so the
GitHub-readable SVG and editable draw.io files cannot drift apart.
Only the Python standard library is required.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List
import argparse
import html
import xml.etree.ElementTree as ET


@dataclass(frozen=True)
class Node:
    id: str
    label: str
    x: int
    y: int
    w: int
    h: int
    kind: str = "service"


@dataclass(frozen=True)
class Edge:
    source: str
    target: str
    label: str = ""
    dashed: bool = False


@dataclass(frozen=True)
class Diagram:
    name: str
    title: str
    width: int
    height: int
    nodes: List[Node]
    edges: List[Edge]


KIND_STYLE = {
    "client": ("#f5f5f5", "#666666"),
    "interface": ("#dae8fc", "#6c8ebf"),
    "core": ("#d5e8d4", "#82b366"),
    "service": ("#fff2cc", "#d6b656"),
    "port": ("#e1d5e7", "#9673a6"),
    "adapter": ("#f8cecc", "#b85450"),
    "external": ("#eeeeee", "#777777"),
    "queue": ("#d0e0e3", "#6c8ebf"),
    "thread": ("#f5f5f5", "#999999"),
}


def system_overview() -> Diagram:
    nodes = [
        Node("console", "Local console", 40, 90, 190, 70, "client"),
        Node("remote", "Remote terminal", 250, 90, 190, 70, "client"),
        Node("desktop", "Desktop GUI", 460, 90, 190, 70, "client"),
        Node("ipad", "iPad / browser\\nReact application", 670, 75, 220, 100, "client"),
        Node("backoffice", "Backoffice", 1240, 90, 190, 70, "external"),

        Node("console_adapter", "Console adapter", 40, 230, 190, 70, "interface"),
        Node("remote_adapter", "Remote shell adapter", 250, 230, 190, 70, "interface"),
        Node("web_adapter", "HTTP + WebSocket adapter\\nserves React bundle", 515, 215, 330, 100, "interface"),
        Node("backoffice_adapter", "Backoffice adapter\\nRabbitMQ first", 1210, 215, 250, 100, "interface"),

        Node("gateway", "Shared command / query boundary", 280, 390, 400, 80, "core"),
        Node("events", "Status + event stream", 720, 390, 300, 80, "core"),
        Node("backoffice_port", "BackofficePort", 1180, 395, 220, 70, "port"),

        Node("runtime", "Runtime / orchestration\\n1..X logical waypoint systems", 220, 550, 310, 95, "service"),
        Node("status", "Status service\\nimmutable snapshots", 565, 550, 280, 95, "service"),
        Node("registration", "Registration services\\nRFID • manual • start • penalties", 880, 550, 360, 95, "service"),

        Node("store_port", "RegistrationStore", 220, 735, 210, 65, "port"),
        Node("device_ports", "RFID + CAN ports", 470, 735, 210, 65, "port"),
        Node("platform_ports", "Clock + Settings + Platform ports", 720, 725, 310, 85, "port"),

        Node("file_store", "Text/file store", 220, 870, 210, 65, "adapter"),
        Node("device_adapters", "RFID + CAN adapters\\n(real or simulated)", 470, 860, 230, 85, "adapter"),
        Node("platform_adapters", "Windows / Linux /\\nPi Zero adapters", 750, 850, 250, 95, "adapter"),
    ]
    edges = [
        Edge("console", "console_adapter"),
        Edge("remote", "remote_adapter"),
        Edge("desktop", "web_adapter"),
        Edge("ipad", "web_adapter"),
        Edge("backoffice", "backoffice_adapter"),
        Edge("console_adapter", "gateway"),
        Edge("remote_adapter", "gateway"),
        Edge("web_adapter", "gateway"),
        Edge("events", "web_adapter", "WebSocket push", True),
        Edge("backoffice_adapter", "backoffice_port"),
        Edge("gateway", "runtime"),
        Edge("gateway", "registration"),
        Edge("runtime", "status"),
        Edge("registration", "status"),
        Edge("status", "events"),
        Edge("registration", "events"),
        Edge("registration", "backoffice_port"),
        Edge("registration", "store_port"),
        Edge("registration", "device_ports"),
        Edge("runtime", "platform_ports"),
        Edge("store_port", "file_store"),
        Edge("device_ports", "device_adapters"),
        Edge("platform_ports", "platform_adapters"),
    ]
    return Diagram(
        "system-overview",
        "Waypoint runtime — component and interface overview",
        1500,
        1010,
        nodes,
        edges,
    )


def threading_model() -> Diagram:
    nodes = [
        Node("console_io", "Console I/O", 40, 100, 180, 65, "thread"),
        Node("remote_io", "Remote shell I/O", 240, 100, 180, 65, "thread"),
        Node("http_io", "HTTP / WebSocket I/O", 440, 100, 210, 65, "thread"),
        Node("rfid_io", "RFID reader/callback", 670, 100, 210, 65, "thread"),
        Node("can_io", "CAN reader", 900, 100, 180, 65, "thread"),
        Node("mq_io", "RabbitMQ I/O", 1100, 100, 180, 65, "thread"),

        Node("normalize", "Adapter boundary\\nimmutable commands/events\\ncapture source timestamp immediately", 370, 235, 570, 100, "interface"),
        Node("queue", "Application ingress queue", 505, 400, 300, 70, "queue"),
        Node("executor", "Serialized application/domain execution\\nsingle writer for mutable waypoint state", 400, 535, 510, 100, "core"),

        Node("domain", "Application/domain handlers\\nno threads • no sleeps • injected Clock/ports", 145, 705, 450, 90, "service"),
        Node("snapshot", "Immutable status snapshots\\n+ outbound domain events", 650, 705, 330, 90, "service"),
        Node("async", "Blocking/slow I/O stays in adapters\\nstorage • network • hardware", 1035, 705, 320, 90, "adapter"),

        Node("tests", "Unit tests call the same handlers synchronously\\nfake clock • fake store • fake ports", 330, 865, 500, 80, "client"),
        Node("completion", "I/O completion/failure\\nreturns as event", 1035, 500, 270, 80, "queue"),
    ]
    edges = [
        Edge("console_io", "normalize"),
        Edge("remote_io", "normalize"),
        Edge("http_io", "normalize"),
        Edge("rfid_io", "normalize"),
        Edge("can_io", "normalize"),
        Edge("mq_io", "normalize"),
        Edge("normalize", "queue"),
        Edge("queue", "executor"),
        Edge("executor", "domain"),
        Edge("domain", "snapshot"),
        Edge("domain", "async"),
        Edge("async", "completion", dashed=True),
        Edge("completion", "queue", dashed=True),
        Edge("snapshot", "http_io", dashed=True),
        Edge("tests", "domain", dashed=True),
    ]
    return Diagram(
        "threading-model",
        "Threading and unit-testability model",
        1400,
        1010,
        nodes,
        edges,
    )


def node_center(node: Node):
    return node.x + node.w / 2, node.y + node.h / 2


def boundary_point(source: Node, target: Node):
    sx, sy = node_center(source)
    tx, ty = node_center(target)
    dx, dy = tx - sx, ty - sy
    if dx == 0 and dy == 0:
        return sx, sy
    scale_x = source.w / 2 / abs(dx) if dx else float("inf")
    scale_y = source.h / 2 / abs(dy) if dy else float("inf")
    scale = min(scale_x, scale_y)
    return sx + dx * scale, sy + dy * scale


def render_svg(diagram: Diagram, path: Path):
    nodes = {node.id: node for node in diagram.nodes}
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{diagram.width}" height="{diagram.height}" viewBox="0 0 {diagram.width} {diagram.height}">',
        "<defs>",
        '<marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">',
        '<path d="M0,0 L0,6 L9,3 z" fill="#555"/>',
        "</marker>",
        "</defs>",
        '<rect width="100%" height="100%" fill="white"/>',
        f'<text x="30" y="42" font-family="Arial, sans-serif" font-size="24" font-weight="bold">{html.escape(diagram.title)}</text>',
    ]

    for edge in diagram.edges:
        source = nodes[edge.source]
        target = nodes[edge.target]
        x1, y1 = boundary_point(source, target)
        x2, y2 = boundary_point(target, source)
        dash = ' stroke-dasharray="7 5"' if edge.dashed else ""
        parts.append(
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#555" stroke-width="2"{dash} marker-end="url(#arrow)"/>'
        )
        if edge.label:
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2 - 7
            parts.append(
                f'<rect x="{mx - 70:.1f}" y="{my - 12:.1f}" width="140" height="20" '
                'fill="white" opacity="0.9"/>'
            )
            parts.append(
                f'<text x="{mx:.1f}" y="{my + 2:.1f}" text-anchor="middle" '
                f'font-family="Arial, sans-serif" font-size="12" fill="#444">{html.escape(edge.label)}</text>'
            )

    for node in diagram.nodes:
        fill, stroke = KIND_STYLE[node.kind]
        parts.append(
            f'<rect x="{node.x}" y="{node.y}" width="{node.w}" height="{node.h}" '
            f'rx="8" ry="8" fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
        )
        lines = node.label.split("\\n")
        base_y = node.y + node.h / 2 - (len(lines) - 1) * 9
        for index, line in enumerate(lines):
            parts.append(
                f'<text x="{node.x + node.w / 2:.1f}" y="{base_y + index * 19:.1f}" '
                'text-anchor="middle" dominant-baseline="middle" '
                f'font-family="Arial, sans-serif" font-size="14">{html.escape(line)}</text>'
            )

    parts.append("</svg>")
    path.write_text("\n".join(parts) + "\n", encoding="utf-8")


def drawio_style(kind: str) -> str:
    fill, stroke = KIND_STYLE[kind]
    return (
        "rounded=1;whiteSpace=wrap;html=1;"
        f"fillColor={fill};strokeColor={stroke};"
        "fontFamily=Helvetica;fontSize=14;"
    )


def render_drawio(diagram: Diagram, path: Path):
    mxfile = ET.Element("mxfile", host="app.diagrams.net", compressed="false")
    diagram_element = ET.SubElement(
        mxfile,
        "diagram",
        id=diagram.name,
        name=diagram.title,
    )
    model = ET.SubElement(
        diagram_element,
        "mxGraphModel",
        dx="1200",
        dy="800",
        grid="1",
        gridSize="10",
        guides="1",
        tooltips="1",
        connect="1",
        arrows="1",
        fold="1",
        page="1",
        pageScale="1",
        pageWidth=str(diagram.width),
        pageHeight=str(diagram.height),
        math="0",
        shadow="0",
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", id="0")
    ET.SubElement(root, "mxCell", id="1", parent="0")

    for node in diagram.nodes:
        cell = ET.SubElement(
            root,
            "mxCell",
            id=node.id,
            value=node.label.replace("\\n", "<br>"),
            style=drawio_style(node.kind),
            vertex="1",
            parent="1",
        )
        ET.SubElement(
            cell,
            "mxGeometry",
            x=str(node.x),
            y=str(node.y),
            width=str(node.w),
            height=str(node.h),
            **{"as": "geometry"},
        )

    for index, edge in enumerate(diagram.edges, start=1):
        style = (
            "edgeStyle=orthogonalEdgeStyle;rounded=0;orthogonalLoop=1;"
            "jettySize=auto;html=1;endArrow=block;endFill=1;"
        )
        if edge.dashed:
            style += "dashed=1;"
        cell = ET.SubElement(
            root,
            "mxCell",
            id=f"e{index}",
            value=edge.label,
            style=style,
            edge="1",
            parent="1",
            source=edge.source,
            target=edge.target,
        )
        ET.SubElement(cell, "mxGeometry", relative="1", **{"as": "geometry"})

    ET.indent(mxfile, space="  ")
    path.write_text(ET.tostring(mxfile, encoding="unicode") + "\n", encoding="utf-8")


def generate(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    diagrams = [system_overview(), threading_model()]

    for diagram in diagrams:
        render_svg(diagram, out_dir / f"{diagram.name}.svg")
        render_drawio(diagram, out_dir / f"{diagram.name}.drawio")

    index = [
        "# Generated architecture diagrams",
        "",
        "Generated by `tools/generate_architecture_diagrams.py`.",
        "",
    ]
    for diagram in diagrams:
        index.extend(
            [
                f"## {diagram.title}",
                "",
                f"![{diagram.title}](./{diagram.name}.svg)",
                "",
                f"- [Editable draw.io file](./{diagram.name}.drawio)",
                "",
            ]
        )
    (out_dir / "README.md").write_text("\n".join(index), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        default="bld/docs/architecture",
        help="Output directory",
    )
    args = parser.parse_args()
    generate(Path(args.out))


if __name__ == "__main__":
    main()
