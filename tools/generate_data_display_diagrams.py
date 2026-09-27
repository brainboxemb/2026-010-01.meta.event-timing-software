#!/usr/bin/env python3
"""Generate data, traceability and display-behaviour architecture views."""

from pathlib import Path
import argparse

from generate_architecture_diagrams import Diagram, Edge, Node, render_drawio, render_svg


def data_display_flow() -> Diagram:
    nodes = [
        Node("backend", "Backend system\\nrace data + stage start times", 40, 90, 320, 85, "external"),
        Node("keypad", "CAN keypad\\nadd / remove team to prepare", 410, 90, 300, 85, "external"),
        Node("registration", "Registration candidates\\nRFID • start • manual • penalty • open", 760, 90, 400, 85, "external"),

        Node("queue", "TimingNode serialized ingress", 520, 245, 500, 75, "queue"),

        Node("race", "RaceData\\nparticipant/team/tag reference data", 30, 420, 300, 90, "service"),
        Node("start", "StageStartTimes\\nstage start-time reference", 360, 420, 300, 90, "service"),
        Node("prepare", "NextUpTeams\\nteams expected next + traceable history", 690, 420, 330, 90, "service"),
        Node("journal", "Journal\\nregistrations + TimingNodeId ordering", 1050, 420, 330, 90, "service"),

        Node("calculator", "StageTiming\\nelapsed time + local ranking", 155, 610, 310, 90, "service"),
        Node("display_model", "DisplayModel\\npassive DisplayRev1Can model", 515, 610, 300, 90, "core"),
        Node("backup", "Simple file backup / restore\\nTimingNode state + sequence recovery", 865, 610, 360, 90, "adapter"),
        Node("published", "Published timing/status/reference data\\ncurrent snapshot + updates", 1265, 610, 330, 90, "interface"),

        Node("can", "CanNetworkController\\nCAN discovery • device state • communication", 480, 800, 370, 100, "adapter"),
        Node("network", "NetworkDeviceService\\nbidirectional network-device boundary", 1240, 800, 380, 100, "adapter"),

        Node("display1", "DisplayRev1Can\\npassive CAN display", 510, 975, 310, 80, "external"),
        Node("display2", "DisplayRev2Wifi\\nsmart client • owns render + sync", 1260, 965, 350, 95, "external"),
    ]

    edges = [
        Edge("backend", "queue", "sync/update"),
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
        Edge("journal", "backup", "records + TimingNodeId sequence", True),

        Edge("display_model", "can"),
        Edge("can", "display1", "active CAN commands"),

        Edge("race", "published", "reference data"),
        Edge("start", "published", "start-time data"),
        Edge("prepare", "published", "current state"),
        Edge("calculator", "published", "timing results"),
        Edge("published", "network", "data service"),
        Edge("display2", "network", "connects / device messages"),
        Edge("network", "display2", "snapshot / updates", True),
    ]

    return Diagram(
        "data-display-flow",
        "TimingNode data — active CAN display and smart network data service",
        1650,
        1100,
        nodes,
        edges,
    )

def registration_stream_identity() -> Diagram:
    nodes = [
        Node("source_a", "TimingNodeId timing-node-01\\nTimingNode identity", 60, 110, 270, 80, "external"),
        Node("seq_a", "timing-node-01 sequence\\n1041 → 1042 → 1043 → 1044", 390, 100, 330, 100, "queue"),
        Node("source_b", "TimingNodeId timing-node-02\\nTimingNode identity", 60, 300, 270, 80, "external"),
        Node("seq_b", "timing-node-02 sequence\\n551 → 552 → 553", 390, 290, 330, 100, "queue"),

        Node("record", "RegistrationRecord\\ntimingNodeId + sequence + locationId\\ntype + timestamps + payload", 820, 180, 380, 120, "core"),
        Node("key", "Stable key\\n(TimingNodeId, SequenceNumber)", 820, 380, 380, 85, "service"),
        Node("location", "LocationID 1..25\\nrecord field — NOT sequence scope", 360, 500, 370, 90, "interface"),
        Node("upstream", "Backend / higher-level system\\nchecks order + detects per-TimingNode gaps", 820, 560, 390, 100, "external"),
        Node("gap", "Example gap\\nA: 1041, 1042, 1044 → 1043 missing", 820, 735, 390, 85, "queue"),
    ]

    edges = [
        Edge("source_a", "seq_a"),
        Edge("source_b", "seq_b"),
        Edge("seq_a", "record", "next(TimingNode A)"),
        Edge("seq_b", "record", "next(TimingNode B)"),
        Edge("location", "record", "associated location"),
        Edge("record", "key"),
        Edge("record", "upstream", "synchronise"),
        Edge("upstream", "gap", "consistency check"),
    ]

    return Diagram(
        "registration-stream-identity",
        "Registration traceability — monotonic sequence per TimingNodeId",
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
