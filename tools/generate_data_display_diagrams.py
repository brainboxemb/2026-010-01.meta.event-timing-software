#!/usr/bin/env python3
"""Generate the in-memory data and display-behaviour architecture view."""

from pathlib import Path
import argparse

from generate_architecture_diagrams import Diagram, Edge, Node, render_drawio, render_svg


def data_display_flow() -> Diagram:
    nodes = [
        Node("backoffice", "Backoffice\\nstart times + reserve-tag data", 40, 90, 300, 85, "external"),
        Node("keypad", "CAN keypad\\nadd / remove team", 390, 90, 240, 85, "external"),
        Node("registration", "Registration events\\nRFID • start • manual • penalty", 690, 90, 310, 85, "external"),

        Node("queue", "TimingSystem serialized ingress", 390, 245, 370, 75, "queue"),
        Node("reference", "ReferenceDataService", 40, 410, 250, 75, "service"),
        Node("selection", "TeamSelectionService", 350, 410, 250, 75, "service"),
        Node("registration_service", "RegistrationService", 660, 410, 250, 75, "service"),
        Node("calculation", "TimingCalculationService\\nelapsed time + local ranking", 970, 395, 310, 100, "service"),

        Node("start_repo", "StartTimeRepository\\nin-memory", 20, 590, 250, 85, "core"),
        Node("reserve_repo", "ReserveTagRepository\\nin-memory", 300, 590, 250, 85, "core"),
        Node("team_state", "TeamSelection\\nin-memory", 580, 590, 230, 85, "core"),
        Node("reg_repo", "RegistrationRepository\\nin-memory", 840, 590, 270, 85, "core"),
        Node("display_model", "DisplayModel\\nrevisioned data snapshot", 1140, 590, 300, 85, "core"),

        Node("backup", "Simple file backup / restore\\natomic snapshot strategy", 280, 775, 350, 90, "adapter"),
        Node("v1", "Display V1 adapter\\nactively renders/sends CAN commands", 850, 765, 330, 100, "adapter"),
        Node("v2", "Display V2 session\\nsynchronises data snapshot/model", 1230, 765, 330, 100, "adapter"),

        Node("display1", "Passive CAN LED display", 830, 930, 300, 75, "external"),
        Node("display2", "Smart Wi-Fi display\\nlocal presentation logic", 1240, 920, 310, 90, "external"),
    ]

    edges = [
        Edge("backoffice", "queue", "sync update"),
        Edge("keypad", "queue", "add/remove"),
        Edge("registration", "queue"),
        Edge("queue", "reference"),
        Edge("queue", "selection"),
        Edge("queue", "registration_service"),
        Edge("reference", "start_repo"),
        Edge("reference", "reserve_repo"),
        Edge("selection", "team_state"),
        Edge("registration_service", "reg_repo"),
        Edge("start_repo", "calculation"),
        Edge("reg_repo", "calculation"),
        Edge("team_state", "display_model"),
        Edge("calculation", "display_model"),
        Edge("start_repo", "backup", "snapshot", True),
        Edge("reserve_repo", "backup", "snapshot", True),
        Edge("team_state", "backup", "if required", True),
        Edge("reg_repo", "backup", "snapshot/journal", True),
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


def generate(out_dir: Path):
    out_dir.mkdir(parents=True, exist_ok=True)
    diagram = data_display_flow()
    render_svg(diagram, out_dir / (diagram.name + ".svg"))
    render_drawio(diagram, out_dir / (diagram.name + ".drawio"))

    with (out_dir / "README.md").open("a", encoding="utf-8") as handle:
        handle.write("\n## Data and display view\n\n")
        handle.write("### " + diagram.title + "\n\n")
        handle.write("![" + diagram.title + "](./" + diagram.name + ".svg)\n\n")
        handle.write("- [Editable draw.io file](./" + diagram.name + ".drawio)\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="bld/docs/architecture")
    args = parser.parse_args()
    generate(Path(args.out))


if __name__ == "__main__":
    main()
