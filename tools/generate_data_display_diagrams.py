#!/usr/bin/env python3
"""Generate data, traceability and display-behaviour architecture views."""

from pathlib import Path
import argparse

from generate_architecture_diagrams import Diagram, Edge, Node, render_drawio, render_svg


def data_display_flow() -> Diagram:
    nodes = [
        Node("backoffice", "Backoffice\\nstart times + reserve-tag data", 40, 90, 300, 85, "external"),
        Node("keypad", "CAN keypad\\nadd / remove team", 390, 90, 240, 85, "external"),
        Node("registration", "Registration candidates\\nRFID • start • manual • penalty • open", 690, 90, 360, 85, "external"),

        Node("queue", "TimingSystem serialized ingress", 390, 245, 370, 75, "queue"),
        Node("reference", "ReferenceDataService", 40, 410, 250, 75, "service"),
        Node("ready", "ReadyTeamService", 350, 410, 250, 75, "service"),
        Node("registration_service", "RegistrationService", 660, 410, 250, 75, "service"),
        Node("calculation", "TimingCalculationService\\nelapsed time + local ranking", 970, 395, 310, 100, "service"),

        Node("start_repo", "StartTimeRepository\\nin-memory", 20, 590, 250, 85, "core"),
        Node("reserve_repo", "ReserveTagRepository\\nin-memory", 300, 590, 250, 85, "core"),
        Node("ready_state", "ReadyTeamState\\nin-memory", 580, 590, 230, 85, "core"),
        Node("reg_repo", "RegistrationLedger\\nin-memory", 840, 590, 270, 85, "core"),
        Node("display_model", "DisplayModel\\nrevisioned data snapshot", 1140, 590, 300, 85, "core"),

        Node("backup", "Simple file backup / restore\\nsequence + state recovery", 280, 775, 350, 90, "adapter"),
        Node("v1", "Display V1 adapter\\nactively sends CAN display state", 850, 765, 330, 100, "adapter"),
        Node("v2", "Display V2 session\\nsynchronises data snapshot/model", 1230, 765, 330, 100, "adapter"),

        Node("display1", "Passive CAN LED display", 830, 930, 300, 75, "external"),
        Node("display2", "Smart Wi-Fi display\\nlocal presentation logic", 1240, 920, 310, 90, "external"),
    ]

    edges = [
        Edge("backoffice", "queue", "sync update"),
        Edge("keypad", "queue", "add/remove"),
        Edge("registration", "queue"),
        Edge("queue", "reference"),
        Edge("queue", "ready"),
        Edge("queue", "registration_service"),
        Edge("reference", "start_repo"),
        Edge("reference", "reserve_repo"),
        Edge("ready", "ready_state"),
        Edge("registration_service", "reg_repo"),
        Edge("start_repo", "calculation"),
        Edge("reg_repo", "calculation"),
        Edge("ready_state", "display_model"),
        Edge("calculation", "display_model"),
        Edge("start_repo", "backup", "snapshot", True),
        Edge("reserve_repo", "backup", "snapshot", True),
        Edge("ready_state", "backup", "snapshot/journal", True),
        Edge("reg_repo", "backup", "ledger + source sequences", True),
        Edge("display_model", "v1"),
        Edge("display_model", "v2"),
        Edge("v1", "display1", "active CAN commands"),
        Edge("v2", "display2", "full snapshot / updates"),
    ]

    return Diagram(
        "data-display-flow",
        "In-memory data, backup and V1/V2 display behaviour",
        1600,
        1060,
        nodes,
        edges,
    )


def registration_stream_identity() -> Diagram:
    nodes = [
        Node("source_a", "RegistrationSystem A\\nsource identity", 60, 110, 270, 80, "external"),
        Node("seq_a", "Source A sequence\\n1041 → 1042 → 1043 → 1044", 390, 100, 330, 100, "queue"),
        Node("source_b", "RegistrationSystem B\\nsource identity", 60, 300, 270, 80, "external"),
        Node("seq_b", "Source B sequence\\n551 → 552 → 553", 390, 290, 330, 100, "queue"),

        Node("record", "RegistrationRecord\\nsourceId + sequence + locationId\\ntype + timestamps + payload", 820, 180, 380, 120, "core"),
        Node("key", "Stable key\\n(RegistrationSystemId, SequenceNumber)", 820, 380, 380, 85, "service"),
        Node("location", "LocationId 1..25\\nrecord field — NOT sequence scope", 360, 500, 370, 90, "interface"),
        Node("upstream", "Backoffice / higher-level system\\nchecks order + detects per-source gaps", 820, 560, 390, 100, "external"),
        Node("gap", "Example gap\\nA: 1041, 1042, 1044 → 1043 missing", 820, 735, 390, 85, "queue"),
    ]

    edges = [
        Edge("source_a", "seq_a"),
        Edge("source_b", "seq_b"),
        Edge("seq_a", "record", "next(A)"),
        Edge("seq_b", "record", "next(B)"),
        Edge("location", "record", "associated location"),
        Edge("record", "key"),
        Edge("record", "upstream", "synchronise"),
        Edge("upstream", "gap", "consistency check"),
    ]

    return Diagram(
        "registration-stream-identity",
        "Registration traceability — monotonic sequence per registration source",
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
