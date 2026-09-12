#!/usr/bin/env python3
"""Generate detailed timing-system architecture diagrams.

This script reuses the remaining legacy SVG/draw.io renderer from
`generate_architecture_diagrams.py` and adds timing-domain specific views.

System-level device/network topology is declarative and owned by the SSAD in
`docs/_diagrams/system-device-network-topology.yaml`; it deliberately does not
live in this SI-01 detail generator.
"""

from pathlib import Path
import argparse

from generate_architecture_diagrams import Diagram, Edge, Node, render_drawio, render_svg


def timing_system_internals() -> Diagram:
    nodes = [
        Node("operator", "Operator commands\\nconsole • API • web UI", 40, 90, 260, 80, "client"),
        Node("rfid", "RFID observations", 340, 90, 220, 80, "external"),
        Node("can", "CAN observations\\nkeypad + discovery", 600, 90, 240, 80, "external"),
        Node("timers", "Scheduled events\\nheartbeat • scans", 880, 90, 220, 80, "external"),
        Node("backoffice", "Backoffice input\\nrace/reference data", 1140, 90, 230, 80, "external"),

        Node("messages", "Immutable TimingSystemMessage\\nsource timestamp + system id", 390, 230, 610, 90, "interface"),
        Node("queue", "Per-TimingSystem ingress queue", 505, 370, 380, 75, "queue"),
        Node("serial", "Logical SerialExecutor\\none writer / ordered state changes", 445, 505, 500, 90, "core"),

        Node("coordinator", "TimingSystem coordinator\\nlifecycle + routing", 120, 675, 310, 90, "service"),
        Node("registration", "Registration service\\npassage • start • manual • penalty", 465, 675, 370, 90, "service"),
        Node("status", "Status service\\nimmutable snapshots", 870, 675, 280, 90, "service"),
        Node("race_data", "Race data + local calculations\\nparticipants/teams • reserve tags • start-related lookup", 1185, 665, 330, 110, "service"),

        Node("store", "RegistrationStore\\ndurable local records", 330, 865, 300, 85, "port"),
        Node("outbox", "Backoffice outbox\\npending committed data", 670, 865, 300, 85, "queue"),
        Node("events", "UI / WebSocket events\\nstatus + registrations", 1010, 865, 300, 85, "interface"),
    ]

    edges = [
        Edge("operator", "messages"),
        Edge("rfid", "messages"),
        Edge("can", "messages"),
        Edge("timers", "messages"),
        Edge("backoffice", "messages"),
        Edge("messages", "queue"),
        Edge("queue", "serial"),
        Edge("serial", "coordinator"),
        Edge("serial", "registration"),
        Edge("serial", "status"),
        Edge("serial", "race_data"),
        Edge("registration", "store", "append"),
        Edge("registration", "outbox", "after commit"),
        Edge("registration", "events"),
        Edge("status", "events"),
        Edge("race_data", "registration", "lookup", True),
        Edge("coordinator", "status"),
    ]

    return Diagram(
        "timing-system-internals",
        "TimingSystem internals — ordered ingress, services and persistence",
        1580,
        1020,
        nodes,
        edges,
    )


def rfid_pipeline() -> Diagram:
    nodes = [
        Node("reader", "RFID reader callback", 40, 150, 210, 70, "external"),
        Node("timestamp", "Capture observation timestamp", 290, 150, 250, 70, "interface"),
        Node("decrypt", "Decrypt + validate tag", 580, 150, 230, 70, "service"),
        Node("filter", "Accumulate / filter observations\\nfirst read is not automatically accepted", 850, 135, 340, 100, "service"),
        Node("resolve", "Resolve identity\\nnormal tag or reserve-tag mapping", 1230, 135, 300, 100, "service"),

        Node("reject", "Rejected / incomplete observation\\nstatus/diagnostic only", 610, 350, 300, 85, "queue"),
        Node("accepted", "AcceptedTag\\nwith evidence + observation time", 1040, 350, 300, 85, "queue"),
        Node("registration", "Registration candidate", 1040, 540, 300, 80, "core"),
        Node("store", "RegistrationStore", 820, 720, 250, 70, "port"),
        Node("outbox", "Backoffice outbox", 1110, 720, 250, 70, "queue"),
        Node("ui", "Status / WebSocket update", 1400, 720, 250, 70, "interface"),
    ]

    edges = [
        Edge("reader", "timestamp"),
        Edge("timestamp", "decrypt"),
        Edge("decrypt", "filter"),
        Edge("filter", "resolve", "accepted"),
        Edge("decrypt", "reject", "invalid", True),
        Edge("filter", "reject", "not enough evidence", True),
        Edge("resolve", "accepted"),
        Edge("resolve", "reject", "unknown", True),
        Edge("accepted", "registration"),
        Edge("registration", "store", "commit"),
        Edge("registration", "outbox"),
        Edge("registration", "ui"),
    ]

    return Diagram(
        "rfid-pipeline",
        "RFID pipeline — raw encrypted reads to accepted registration",
        1700,
        850,
        nodes,
        edges,
    )


def generate(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    diagrams = [timing_system_internals(), rfid_pipeline()]

    for diagram in diagrams:
        render_svg(diagram, out_dir / (diagram.name + ".svg"))
        render_drawio(diagram, out_dir / (diagram.name + ".drawio"))

    readme = out_dir / "README.md"
    with readme.open("a", encoding="utf-8") as handle:
        handle.write("\n## Timing-system detail views\n\n")
        for diagram in diagrams:
            handle.write("### " + diagram.title + "\n\n")
            handle.write("![" + diagram.title + "](./" + diagram.name + ".svg)\n\n")
            handle.write("- [Editable draw.io file](./" + diagram.name + ".drawio)\n\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="bld/docs/architecture")
    args = parser.parse_args()
    generate(Path(args.out))


if __name__ == "__main__":
    main()
