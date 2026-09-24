#!/usr/bin/env python3
"""Generate data, traceability and display-behaviour architecture views."""

from pathlib import Path
import argparse

from generate_architecture_diagrams import Diagram, Edge, Node, render_drawio, render_svg


def data_display_flow() -> Diagram:
    nodes = [
        Node("backoffice", "Backoffice\\nrace data + stage start times", 40, 90, 320, 85, "external"),
        Node("keypad", "CAN keypad\\nadd / remove team to prepare", 410, 90, 300, 85, "external"),
        Node("registration", "Registration candidates\\nRFID • start • manual • penalty • open", 760, 90, 400, 85, "external"),

        Node("queue", "WaypointSystem serialized ingress", 470, 245, 500, 75, "queue"),

        Node("race", "RaceData\\nparticipant/team/tag reference data", 30, 420, 300, 90, "service"),
        Node("start", "StageStartTimeRegistry\\nstage start-time reference", 360, 420, 300, 90, "service"),
        Node("prepare", "PrepareTeamRegistry\\nteams to prepare + internal history", 690, 420, 330, 90, "service"),
        Node("journal", "WaypointJournal\\nregistrations + UniqueID ordering", 1050, 420, 330, 90, "service"),

        Node("calculator", "StageTiming\\nelapsed time + local ranking", 345, 610, 310, 90, "service"),
        Node("display_model", "DisplayModel\\nrevisioned data snapshot", 715, 610, 300, 90, "core"),
        Node("backup", "Simple file backup / restore\\nwaypoint state + sequence recovery", 1080, 610, 360, 90, "adapter"),

        Node("v1", "Display V1 adapter\\nactively sends CAN display state", 640, 800, 330, 100, "adapter"),
        Node("v2", "Display V2 session\\nsynchronises data snapshot/model", 1040, 800, 330, 100, "adapter"),

        Node("display1", "Passive CAN LED display", 640, 965, 300, 75, "external"),
        Node("display2", "Smart Wi-Fi display\\nlocal presentation logic", 1050, 955, 310, 90, "external"),
    ]

    edges = [
        Edge("backoffice", "queue", "sync/update"),
        Edge("keypad", "queue", "prepare-team mutation"),
        Edge("registration", "queue", "registration command/observation"),

        Edge("queue", "race"),
        Edge("queue", "start"),
        Edge("queue", "prepare"),
        Edge("queue", "journal"),

        Edge("race", "calculator", "reference data"),
        Edge("start", "calculator", "start-time data"),
        Edge("journal", "calculator", "registration data"),

        Edge("prepare", "display_model"),
        Edge("calculator", "display_model"),

        Edge("race", "backup", "snapshot", True),
        Edge("start", "backup", "snapshot", True),
        Edge("prepare", "backup", "state + history", True),
        Edge("journal", "backup", "records + UniqueID sequence", True),

        Edge("display_model", "v1"),
        Edge("display_model", "v2"),
        Edge("v1", "display1", "active CAN commands"),
        Edge("v2", "display2", "full snapshot / updates"),
    ]

    return Diagram(
        "data-display-flow",
        "Waypoint data, backup and V1/V2 display behaviour",
        1500,
        1080,
        nodes,
        edges,
    )


def registration_stream_identity() -> Diagram:
    nodes = [
        Node("source_a", "UniqueID waypoint-01\\nWaypointSystem identity", 60, 110, 270, 80, "external"),
        Node("seq_a", "waypoint-01 sequence\\n1041 → 1042 → 1043 → 1044", 390, 100, 330, 100, "queue"),
        Node("source_b", "UniqueID waypoint-02\\nWaypointSystem identity", 60, 300, 270, 80, "external"),
        Node("seq_b", "waypoint-02 sequence\\n551 → 552 → 553", 390, 290, 330, 100, "queue"),

        Node("record", "RegistrationRecord\\nuniqueID + sequence + locationId\\ntype + timestamps + payload", 820, 180, 380, 120, "core"),
        Node("key", "Stable key\\n(UniqueID, SequenceNumber)", 820, 380, 380, 85, "service"),
        Node("location", "LocationID 1..25\\nrecord field — NOT sequence scope", 360, 500, 370, 90, "interface"),
        Node("upstream", "Backoffice / higher-level system\\nchecks order + detects per-waypoint gaps", 820, 560, 390, 100, "external"),
        Node("gap", "Example gap\\nA: 1041, 1042, 1044 → 1043 missing", 820, 735, 390, 85, "queue"),
    ]

    edges = [
        Edge("source_a", "seq_a"),
        Edge("source_b", "seq_b"),
        Edge("seq_a", "record", "next(waypoint A)"),
        Edge("seq_b", "record", "next(waypoint B)"),
        Edge("location", "record", "associated location"),
        Edge("record", "key"),
        Edge("record", "upstream", "synchronise"),
        Edge("upstream", "gap", "consistency check"),
    ]

    return Diagram(
        "registration-stream-identity",
        "Registration traceability — monotonic sequence per UniqueID",
        1320,
        880,
        nodes,
        edges,
    )


def generate(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    diagrams = [data_display_flow(), registration_stream_identity()]

    for diagram in diagrams:
        render_svg(diagram, out_dir / (diagram.name + ".svg"))
        render_drawio(diagram, out_dir / (diagram.name + ".drawio"))

    with (out_dir / "README.md").open("a", encoding="utf-8") as handle:
        handle.write("\n## Data, traceability and display views\n\n")
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
