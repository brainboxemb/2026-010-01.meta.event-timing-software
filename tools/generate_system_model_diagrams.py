#!/usr/bin/env python3
"""Generate system-level software-item, topology and state-model diagrams."""

from pathlib import Path
import argparse

from generate_architecture_diagrams import Diagram, Edge, Node, render_drawio, render_svg


def software_item_overview() -> Diagram:
    nodes = [
        Node("operator", "Operator", 610, 55, 220, 65, "external"),
        Node("gui", "SI-02\\nDesktop GUI", 280, 175, 260, 85, "client"),
        Node("web", "SI-03\\nWeb / iPad Operator", 900, 175, 270, 85, "client"),
        Node("if03", "IF-03 Application Control & Status\\nHTTP/JSON + WebSocket", 505, 325, 440, 90, "interface"),
        Node("timing", "SI-01 Headless Timing Application\\n1..X TimingSystemInstances", 500, 490, 450, 100, "core"),

        Node("state", "In-memory authoritative state\\nregistration • ready-team • reference data", 465, 690, 440, 95, "service"),
        Node("backup", "Simple file backup / restore", 120, 705, 270, 70, "adapter"),
        Node("outbox", "Backoffice outbox / sync", 980, 705, 270, 70, "queue"),

        Node("rfid", "IF-07 RFID subsystem\\nprivate production adapter possible", 55, 480, 330, 90, "external"),
        Node("can", "IF-08 CAN bus\\nkeypad + Display V1", 80, 850, 300, 85, "external"),
        Node("v2", "IF-09 Smart Display V2\\nmDNS + network data", 1010, 480, 330, 90, "external"),
        Node("backoffice", "IF-06 Backoffice\\nRabbitMQ intended", 1050, 850, 280, 85, "external"),
    ]

    edges = [
        Edge("operator", "gui", "desktop HMI"),
        Edge("operator", "web", "web HMI"),
        Edge("gui", "if03"),
        Edge("web", "if03"),
        Edge("if03", "timing"),
        Edge("timing", "state"),
        Edge("state", "backup", "backup/restore"),
        Edge("state", "outbox", "committed data"),
        Edge("rfid", "timing", "observations/control", True),
        Edge("can", "timing", "device I/O", True),
        Edge("v2", "timing", "connect + sync", True),
        Edge("outbox", "backoffice", "sync", True),
    ]

    return Diagram(
        "software-item-system-overview",
        "Software items and principal system interfaces",
        1420,
        1000,
        nodes,
        edges,
    )


def runtime_topology() -> Diagram:
    nodes = [
        Node("app", "SI-01 TimingApplicationRuntime\\none JVM/process", 510, 70, 390, 90, "core"),

        Node("sys1", "TimingSystemInstance system-01\\nserialized state boundary", 160, 245, 390, 90, "service"),
        Node("sys2", "TimingSystemInstance system-02\\nserialized state boundary", 860, 245, 390, 90, "service"),

        Node("rsa", "RegistrationSystem A\\nsequence A • own registration file", 60, 445, 370, 95, "queue"),
        Node("rsb", "RegistrationSystem B / name FINISH\\nsequence B • own registration file", 450, 445, 420, 95, "queue"),
        Node("rsc", "RegistrationSystem C\\nsequence C • own registration file", 930, 445, 370, 95, "queue"),

        Node("a1", "RS-A-ANT1", 20, 660, 220, 70, "external"),
        Node("f1", "RS-FINISH-ANT1", 335, 650, 260, 80, "external"),
        Node("f2", "RS-FINISH-ANT2", 625, 650, 260, 80, "external"),
        Node("c1", "RS-C-ANT1\\nstub or real adapter", 1020, 650, 260, 80, "external"),

        Node("settings", "External settings/configuration\\ninstance → registration source → antenna binding", 410, 825, 600, 95, "interface"),
        Node("backoffice", "Backoffice integration test\\nall source streams from one application", 460, 1010, 500, 90, "external"),
    ]

    edges = [
        Edge("app", "sys1"),
        Edge("app", "sys2"),
        Edge("sys1", "rsa", "1..X sources"),
        Edge("sys1", "rsb"),
        Edge("sys2", "rsc", "1..X sources"),
        Edge("rsa", "a1", "1..X antennas"),
        Edge("rsb", "f1", "1..X antennas"),
        Edge("rsb", "f2"),
        Edge("rsc", "c1", "1..X antennas"),
        Edge("settings", "app", "build topology", True),
        Edge("rsa", "backoffice", "ordered source stream", True),
        Edge("rsb", "backoffice", "ordered source stream", True),
        Edge("rsc", "backoffice", "ordered source stream", True),
    ]

    return Diagram(
        "runtime-registration-topology",
        "Configurable runtime topology — instances, registration sources and antennas",
        1400,
        1160,
        nodes,
        edges,
    )


def timing_system_lifecycle() -> Diagram:
    nodes = [
        Node("closed", "CLOSED\\nnot accepting normal timing operation", 170, 210, 330, 90, "core"),
        Node("open", "OPEN\\nlocal timing operation enabled", 770, 210, 330, 90, "core"),
        Node("health", "Subsystem health is orthogonal\\nHEALTHY • DEGRADED • ERROR states do not silently change OPEN/CLOSED", 355, 440, 560, 110, "service"),
        Node("example", "Example: OPEN + RFID INITIALISING/ERROR\\n=> system instance remains OPEN but status is degraded", 355, 650, 560, 95, "interface"),
    ]
    edges = [
        Edge("closed", "open", "Open command"),
        Edge("open", "closed", "Close command"),
        Edge("closed", "health", "status"),
        Edge("open", "health", "status"),
        Edge("health", "example"),
    ]
    return Diagram(
        "timing-system-lifecycle",
        "TimingSystemInstance lifecycle — operational lifecycle and health are separate",
        1280,
        820,
        nodes,
        edges,
    )


def rfid_lifecycle() -> Diagram:
    nodes = [
        Node("off", "OFF\\ndefault", 40, 180, 180, 80, "core"),
        Node("powering", "POWERING_ON", 280, 180, 200, 80, "service"),
        Node("initialising", "INITIALISING\\nboot + protocol setup", 540, 165, 240, 110, "service"),
        Node("ready", "READY", 850, 180, 180, 80, "core"),
        Node("poweroff", "POWERING_OFF", 1100, 180, 210, 80, "service"),
        Node("degraded", "DEGRADED / UNRESPONSIVE", 740, 410, 300, 85, "queue"),
        Node("error", "ERROR", 420, 410, 200, 85, "adapter"),
        Node("recover", "RECOVERING / REINITIALISE\\nreconnect -> reset -> power cycle policy TBD", 465, 625, 420, 100, "interface"),
    ]
    edges = [
        Edge("off", "powering", "power on"),
        Edge("powering", "initialising", "power available"),
        Edge("initialising", "ready", "initialised"),
        Edge("ready", "poweroff", "power off"),
        Edge("poweroff", "off", "power removed"),
        Edge("powering", "error", "failure", True),
        Edge("initialising", "error", "failure", True),
        Edge("ready", "degraded", "heartbeat/protocol loss", True),
        Edge("degraded", "recover", "reinitialise", True),
        Edge("error", "recover", "reinitialise", True),
        Edge("recover", "initialising", "recover without power cycle", True),
        Edge("recover", "off", "power cycle/reset path", True),
    ]
    return Diagram(
        "rfid-lifecycle",
        "RFID reader lifecycle and recovery direction",
        1380,
        820,
        nodes,
        edges,
    )


def connectivity_layers() -> Diagram:
    nodes = [
        Node("local", "Local LAN / router\\nindependent status", 100, 210, 300, 90, "service"),
        Node("internet", "Internet reachability\\nindependent status", 520, 210, 300, 90, "service"),
        Node("rabbit", "RabbitMQ / backoffice\\nsession status", 940, 210, 300, 90, "service"),
        Node("timing", "SI-01 local timing operation\\nRFID/CAN/in-memory state", 350, 500, 420, 100, "core"),
        Node("outbox", "Outbox + local reference data\\nallow deferred synchronisation", 880, 500, 340, 100, "queue"),
    ]
    edges = [
        Edge("local", "internet", "uplink available", True),
        Edge("internet", "rabbit", "endpoint reachable", True),
        Edge("local", "timing", "local clients/devices", True),
        Edge("timing", "outbox", "committed local data"),
        Edge("outbox", "rabbit", "sync when connected", True),
    ]
    return Diagram(
        "connectivity-layers",
        "Connectivity status is layered; local timing is not a RabbitMQ connection state",
        1340,
        700,
        nodes,
        edges,
    )


def generate(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    diagrams = [
        software_item_overview(),
        runtime_topology(),
        timing_system_lifecycle(),
        rfid_lifecycle(),
        connectivity_layers(),
    ]

    for diagram in diagrams:
        render_svg(diagram, out_dir / (diagram.name + ".svg"))
        render_drawio(diagram, out_dir / (diagram.name + ".drawio"))

    readme = out_dir / "README.md"
    with readme.open("a", encoding="utf-8") as handle:
        handle.write("\n## System software-item, topology and state-model views\n\n")
        for diagram in diagrams:
            handle.write("### " + diagram.title + "\n\n")
            handle.write("![" + diagram.title + "](./" + diagram.name + ".svg)\n\n")
            handle.write("- [Editable draw.io file](./" + diagram.name + ".drawio)\n\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", default="bld/docs/architecture")
    args = parser.parse_args()
    generate(Path(args.out))


if __name__ == "__main__":
    main()
