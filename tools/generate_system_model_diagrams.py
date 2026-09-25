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
        Node("timing", "SI-01 Headless Timing Application\\n1..N TimingNodes", 500, 490, 450, 100, "core"),

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


def timing_node_software_decomposition() -> Diagram:
    nodes = [
        Node("app", "SI-01 TimingApplicationRuntime\\none JVM/process", 505, 55, 390, 90, "core"),
        Node("wp1", "TimingNode timing-node-A\\nconfigured at Location X", 120, 230, 420, 95, "service"),
        Node("wp2", "TimingNode timing-node-B\\nconfigured at Location Y", 860, 230, 420, 95, "service"),

        Node("life", "TimingNode lifecycle / status\\nOPEN • CLOSED • health", 40, 430, 300, 90, "service"),
        Node("tag", "TagProcessor\\nRFID/tag observation processing", 370, 430, 300, 90, "service"),
        Node("start", "StageStartTimeRegistry\\nlocal stage start-time reference", 700, 430, 330, 90, "service"),
        Node("journal", "TimingNodeJournal\\nregistrations + TimingNodeId-scoped sequence/persistence", 1000, 430, 340, 90, "service"),
        Node("ready", "PrepareTeamRegistry\\nteams to prepare + internal keypad history", 80, 640, 330, 100, "service"),
        Node("race", "RaceData\\nparticipant/team/tag reference data", 460, 640, 330, 100, "service"),
        Node("shared", "Shared runtime infrastructure\\nHTTP • logging • executors • configuration", 840, 640, 420, 100, "interface"),
    ]

    edges = [
        Edge("app", "wp1", "hosts 1..X"),
        Edge("app", "wp2"),
        Edge("wp1", "life"),
        Edge("wp1", "tag"),
        Edge("wp1", "start"),
        Edge("wp1", "journal"),
        Edge("wp1", "ready"),
        Edge("wp1", "race"),
        Edge("app", "shared"),
        Edge("wp1", "shared", "uses shared facilities", True),
        Edge("wp2", "shared", "uses shared facilities", True),
    ]

    return Diagram(
        "timing-node-software-decomposition",
        "SI-01 software/domain decomposition — timing node systems and responsibilities",
        1400,
        830,
        nodes,
        edges,
    )


def registration_hardware_topology() -> Diagram:
    nodes = [
        Node("asset1", "RegistrationAsset asset-01\\nphysical/inventory identity", 180, 100, 420, 100, "external"),
        Node("asset2", "RegistrationAsset asset-02\\nphysical/inventory identity", 820, 100, 420, 100, "external"),
        Node("ant11", "Antenna ANT1", 70, 340, 260, 75, "adapter"),
        Node("ant12", "Antenna ANT2", 370, 340, 260, 75, "adapter"),
        Node("ant21", "Antenna ANT1", 900, 340, 260, 75, "adapter"),
        Node("note", "Hardware topology only\\n1..N antennas do not imply 1..N TimingNodeIds", 450, 540, 500, 100, "interface"),
    ]

    edges = [
        Edge("asset1", "ant11", "1..N antennas"),
        Edge("asset1", "ant12"),
        Edge("asset2", "ant21", "1..N antennas"),
        Edge("asset1", "note", "separate from software decomposition", True),
        Edge("asset2", "note", "separate from software decomposition", True),
    ]

    return Diagram(
        "registration-hardware-topology",
        "Registration hardware/deployment topology — assets and antennas",
        1400,
        720,
        nodes,
        edges,
    )


def timing_node_routing_mapping() -> Diagram:
    nodes = [
        Node("asset", "RegistrationAsset asset-01\\nphysical hardware", 65, 80, 310, 85, "external"),
        Node("antenna", "Antenna ANT1\\nAntennaId", 85, 230, 270, 80, "adapter"),
        Node("reg_router", "RegistrationRouter\\nconfigured fan-out", 455, 180, 330, 95, "interface"),

        Node("node_a", "TimingNode timing-node-A\\nTimingNodeId", 930, 80, 350, 90, "service"),
        Node("node_b", "TimingNode timing-node-B\\nTimingNodeId", 930, 260, 350, 90, "service"),
        Node("loc_a", "Location X\\nLocationID", 1060, 420, 220, 75, "external"),

        Node("bo_router", "BackofficeRouter\\nconnector bindings / names", 505, 540, 350, 95, "interface"),
        Node("conn1", "BackofficeConnector 01\\nRabbitMQ / credentials A", 70, 500, 330, 90, "adapter"),
        Node("conn2", "BackofficeConnector 02\\nRabbitMQ / credentials B", 70, 660, 330, 90, "adapter"),
        Node("note", "Router = mapping / fan-out\\nManager = resource + lifecycle ownership", 900, 620, 390, 100, "interface"),
    ]

    edges = [
        Edge("asset", "antenna", "owns 1..N antennas"),
        Edge("antenna", "reg_router", "observation origin"),
        Edge("reg_router", "node_a", "route 1..N"),
        Edge("reg_router", "node_b"),
        Edge("node_a", "loc_a", "configured at"),

        Edge("conn1", "bo_router", "1..N bindings"),
        Edge("conn2", "bo_router", "1..N bindings"),
        Edge("bo_router", "node_a", "inbound / outbound"),
        Edge("bo_router", "node_b", "inbound / outbound"),
        Edge("bo_router", "note", "separate responsibilities", True),
    ]

    return Diagram(
        "timing-node-routing-mapping",
        "Configuration routing — hardware, TimingNodes and backoffice connectors",
        1400,
        820,
        nodes,
        edges,
    )

def rabbitmq_source_topology() -> Diagram:
    nodes = [
        Node("broker1", "RabbitMQ broker A", 95, 70, 300, 75, "external"),
        Node("broker2", "RabbitMQ broker B", 1005, 70, 300, 75, "external"),

        Node("conn1", "RabbitMqConnector connector-01\\nConnectionManager owns connection/channels", 55, 250, 380, 100, "adapter"),
        Node("conn2", "RabbitMqConnector connector-02\\nConnectionManager owns connection/channels", 965, 250, 380, 100, "adapter"),

        Node("router", "BackofficeRouter\\nTimingNode bindings + external names", 500, 410, 400, 100, "interface"),

        Node("node1", "TimingNode timing-node-01\\nTimingNodeId-scoped application path", 95, 620, 340, 90, "service"),
        Node("node2", "TimingNode timing-node-02\\nTimingNodeId-scoped application path", 965, 620, 340, 90, "service"),
        Node("outbox", "local durable/pending outbox\\nTimingNodeId retained", 525, 620, 350, 90, "service"),

        Node("note", "0..N connectors per application\\n1..N TimingNode bindings per connector\\none TimingNode may use multiple connectors", 455, 790, 490, 105, "interface"),
    ]

    edges = [
        Edge("broker1", "conn1", "transport"),
        Edge("broker2", "conn2", "transport"),
        Edge("conn1", "router", "inbound / outbound"),
        Edge("conn2", "router", "inbound / outbound"),
        Edge("router", "node1", "route / bind"),
        Edge("router", "node2", "route / bind"),
        Edge("node1", "outbox", "committed outbound"),
        Edge("node2", "outbox", "committed outbound"),
        Edge("outbox", "router", "publish pending"),
        Edge("router", "note", "configured multiplicity", True),
    ]

    return Diagram(
        "rabbitmq-source-topology",
        "RabbitMQ — connector managers with explicit TimingNode routing",
        1400,
        960,
        nodes,
        edges,
    )

def timing_node_lifecycle() -> Diagram:
    nodes = [
        Node("closed", "CLOSED\\nnot accepting normal timing node timing operation", 170, 210, 330, 90, "core"),
        Node("open", "OPEN\\ntiming node timing operation enabled", 770, 210, 330, 90, "core"),
        Node("health", "Subsystem health is orthogonal\\nHEALTHY • DEGRADED • ERROR do not silently change OPEN/CLOSED", 355, 440, 560, 110, "service"),
        Node("example", "Example: OPEN + RFID INITIALISING/ERROR\\n=> timing node remains OPEN while status is degraded", 355, 650, 560, 95, "interface"),
    ]
    edges = [
        Edge("closed", "open", "Open command"),
        Edge("open", "closed", "Close command"),
        Edge("closed", "health", "status"),
        Edge("open", "health", "status"),
        Edge("health", "example"),
    ]
    return Diagram(
        "timing-node-lifecycle",
        "TimingNode lifecycle — operational lifecycle and health are separate",
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
        timing_node_software_decomposition(),
        registration_hardware_topology(),
        timing_node_routing_mapping(),
        rabbitmq_source_topology(),
        timing_node_lifecycle(),
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
