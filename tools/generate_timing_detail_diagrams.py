#!/usr/bin/env python3
"""Generate detailed waypoint-system architecture diagrams.

This script reuses the remaining legacy SVG/draw.io renderer from
`generate_architecture_diagrams.py` and adds timing-domain specific views.

System-level device/network topology is declarative and owned by the SSAD in
`docs/_diagrams/system-device-network-topology.yaml`; it deliberately does not
live in this SI-01 detail generator.
"""

from pathlib import Path
import argparse

from generate_architecture_diagrams import Diagram, Edge, Node, render_drawio, render_svg


def waypoint_system_internals() -> Diagram:
    nodes = [
        Node("operator", "Operator commands\\nconsole • API • web UI", 40, 90, 260, 80, "client"),
        Node("rfid", "RFID observations", 340, 90, 220, 80, "external"),
        Node("can", "CAN observations\\nkeypad + discovery", 600, 90, 240, 80, "external"),
        Node("timers", "Scheduled events\\nheartbeat • scans", 880, 90, 220, 80, "external"),
        Node("backoffice", "Backoffice input\\nrace/reference data", 1140, 90, 230, 80, "external"),

        Node("messages", "Immutable WaypointSystemMessage\\nsource timestamp + waypoint id", 390, 230, 610, 90, "interface"),
        Node("queue", "Per-WaypointSystem ingress queue", 505, 370, 380, 75, "queue"),
        Node("serial", "Logical SerialExecutor\\none writer / ordered state changes", 445, 505, 500, 90, "core"),

        Node("coordinator", "WaypointSystem coordinator\\nlifecycle + command orchestration", 30, 675, 270, 90, "service"),
        Node("tag", "TagProcessor\\nRFID/tag observation processing", 320, 675, 280, 90, "service"),
        Node("journal", "WaypointJournal\\nregistration/history", 620, 675, 280, 90, "service"),
        Node("prepare", "PrepareTeamRegistry\\nteams to prepare + internal history", 920, 675, 330, 90, "service"),
        Node("status", "Waypoint status\\nimmutable snapshots", 1270, 675, 260, 90, "service"),

        Node("race_data", "RaceData\\nparticipants • teams • tag references", 180, 850, 330, 90, "service"),
        Node("start_times", "StageStartTimeRegistry\\nlocal stage start-time reference", 540, 850, 340, 90, "service"),
        Node("store", "RegistrationStore\\ndurable local records", 910, 850, 280, 90, "port"),
        Node("outbox", "Backoffice outbox\\npending committed data", 1220, 850, 280, 90, "queue"),
        Node("events", "UI / WebSocket events\\nstatus + registrations + prepare teams", 585, 1015, 410, 90, "interface"),
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
        Edge("serial", "tag"),
        Edge("serial", "journal"),
        Edge("serial", "prepare"),
        Edge("serial", "status"),
        Edge("race_data", "tag", "identity lookup", True),
        Edge("race_data", "journal", "reference lookup", True),
        Edge("start_times", "journal", "start-time lookup", True),
        Edge("tag", "journal", "accepted observation"),
        Edge("journal", "store", "append"),
        Edge("journal", "outbox", "after commit"),
        Edge("journal", "events"),
        Edge("prepare", "events"),
        Edge("status", "events"),
        Edge("coordinator", "status"),
    ]

    return Diagram(
        "waypoint-system-internals",
        "WaypointSystem internals — ordered ingress and domain responsibilities",
        1580,
        1160,
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
    diagrams = [waypoint_system_internals(), rfid_pipeline()]

    for diagram in diagrams:
        render_svg(diagram, out_dir / (diagram.name + ".svg"))
        render_drawio(diagram, out_dir / (diagram.name + ".drawio"))

    readme = out_dir / "README.md"
    with readme.open("a", encoding="utf-8") as handle:
        handle.write("\n## Waypoint-system detail views\n\n")
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
