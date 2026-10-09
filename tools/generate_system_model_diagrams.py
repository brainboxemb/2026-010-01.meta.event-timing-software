#!/usr/bin/env python3
"""Generate system-level software-item, topology and state-model diagrams."""

from pathlib import Path
import argparse

from generate_architecture_diagrams import Diagram, Edge, Node, render_drawio, render_svg


def software_item_overview() -> Diagram:
    nodes = [
        Node("operator", "Operator", 610, 45, 220, 65, "external"),
        Node("browser", "Browser / tablet\nnormal operator interface", 280, 165, 280, 85, "client"),
        Node("engineering", "Engineering / test clients\nJavaFX • scripts • automated tooling", 860, 165, 320, 85, "client"),
        Node("if04", "IF-04 Web Interface\nHTTP + WebSocket", 250, 320, 330, 90, "interface"),
        Node("if03", "IF-03 API\nHTTP/JSON + WebSocket", 850, 320, 330, 90, "interface"),
        Node("timing", "SI-01 Timing Point Application\n1..N TimingNodes", 500, 490, 450, 100, "core"),

        Node("state", "In-memory authoritative state\nregistration • ready-team • reference data", 465, 690, 440, 95, "service"),
        Node("backup", "Simple file backup / restore", 120, 705, 270, 70, "adapter"),
        Node("outbox", "Upstream outbox / sync", 980, 705, 270, 70, "queue"),

        Node("rfid", "IF-07 RFID subsystem\nprivate production adapter possible", 55, 480, 330, 90, "external"),
        Node("can", "IF-08 CAN bus\nkeypad + DisplayRev1Can", 80, 850, 300, 85, "external"),
        Node("v2", "IF-09 DisplayRev2Wifi\nsmart client • mDNS + network data", 1010, 480, 330, 90, "external"),
        Node("backoffice", "IF-06 Upstream system\nRabbitMQ intended", 1050, 850, 280, 85, "external"),
    ]

    edges = [
        Edge("operator", "browser", "normal operation"),
        Edge("browser", "if04"),
        Edge("engineering", "if03"),
        Edge("if04", "timing"),
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
        "Software item and principal system interfaces",
        1420,
        1000,
        nodes,
        edges,
    )


def timing_node_software_decomposition() -> Diagram:
    nodes = [
        Node("app", "SI-01 TimingApplication\\nApplicationId • one JVM/process", 505, 45, 390, 90, "core"),
        Node("system", "TimingSystem (1..N hosted)\\nTimingSystemId • complete SystemStatus\\nsystem UpstreamMessagePort • UpstreamProtocol • TimeSource", 430, 185, 540, 120, "service"),
        Node("wp1", "TimingNode timing-node-A\\nTimingNodeId • Location X\\nUpstreamMessagePort • contains LogBook", 120, 360, 420, 105, "service"),
        Node("wp2", "TimingNode timing-node-B\\nTimingNodeId • Location Y\\nUpstreamMessagePort • contains LogBook", 860, 360, 420, 105, "service"),

        Node("life", "TimingNode lifecycle / status\\nOPEN • CLOSED • health", 40, 540, 280, 90, "service"),
        Node("tag", "TagProcessor\\nRFID/tag observation processing", 345, 540, 280, 90, "service"),
        Node("start", "StageStartTimes\\nlocal stage start-time reference", 650, 540, 300, 90, "service"),
        Node("logbook", "LogBook\\n0..N LogBookItem\\ncontained by TimingNode", 975, 540, 360, 90, "service"),
        Node("ready", "NextUpTeams\\nteams expected next", 80, 730, 300, 95, "service"),
        Node("race", "RaceData\\nparticipant/team/tag reference data", 425, 730, 300, 95, "service"),
        Node("stage", "StageTiming\\nrunning times + ranking", 770, 730, 280, 95, "service"),
        Node("timingdata", "TimingData\\ncanonical TimingDataRecord + codec", 1080, 730, 260, 95, "service"),
        Node("shared", "Shared runtime infrastructure\\nHTTP • logging • executors • configuration", 1080, 855, 260, 95, "interface"),
    ]

    edges = [
        Edge("app", "system", "hosts 1..N"),
        Edge("system", "wp1", "contains 1..N"),
        Edge("system", "wp2"),
        Edge("wp1", "life"),
        Edge("wp1", "tag"),
        Edge("wp1", "start"),
        Edge("wp1", "logbook"),
        Edge("wp1", "ready"),
        Edge("wp1", "race"),
        Edge("wp1", "stage"),
        Edge("wp1", "timingdata", "uses / produces", True),
        Edge("wp2", "timingdata", "uses / produces", True),
        Edge("app", "shared"),
        Edge("system", "shared", "uses shared facilities", True),
    ]

    return Diagram(
        "timing-node-software-decomposition",
        "SI-01 software/domain decomposition — TimingApplication, TimingSystem and TimingNode responsibilities",
        1400,
        1050,
        nodes,
        edges,
    )


def timing_node_routing_mapping() -> Diagram:
    nodes = [
        Node("app", "TimingApplication\\nApplicationId", 520, 35, 360, 80, "core"),
        Node("system", "TimingSystem context\\nTimingSystemId • complete SystemStatus\\nUpstreamMessagePort • TimeSource", 500, 145, 400, 105, "service"),
        Node("protocol", "UpstreamProtocol\\nTimingData • sync • ping/pong", 500, 285, 400, 90, "service"),

        Node("ant1", "Devices / Antenna ANT1\\nAntennaId", 60, 195, 280, 80, "adapter"),
        Node("ant2", "Devices / Antenna ANT2\\nAntennaId", 60, 430, 280, 80, "adapter"),

        Node("router", "UpstreamMessageRouter\\nsystem / TimingNode target resolution", 500, 430, 400, 100, "interface"),

        Node("node_a", "TimingNode timing-node-A\\nTimingNodeId\\nUpstreamMessagePort", 975, 205, 350, 105, "service"),
        Node("node_b", "TimingNode timing-node-B\\nTimingNodeId\\nUpstreamMessagePort", 975, 430, 350, 105, "service"),
        Node("loc_a", "Location X\\nLocationID", 1040, 590, 220, 75, "external"),

        Node("gateway", "Messaging / UpstreamGateway\\ntransport/session boundary", 500, 610, 400, 90, "interface"),
        Node("conn1", "Connector 01\\nRabbitMQ", 85, 785, 280, 80, "adapter"),
        Node("conn2", "Connector 02\\nother transport", 1035, 785, 280, 80, "adapter"),
    ]

    edges = [
        Edge("app", "system", "hosts 1..N"),
        Edge("system", "protocol", "owns"),
        Edge("system", "node_a", "contains 1..N"),
        Edge("system", "node_b"),
        Edge("ant1", "node_a"),
        Edge("ant1", "node_b"),
        Edge("ant2", "node_b"),
        Edge("node_a", "loc_a"),
        Edge("conn1", "gateway", "transport"),
        Edge("conn2", "gateway", "transport"),
        Edge("gateway", "protocol", "encoded UpstreamProtocol"),
        Edge("protocol", "router", "semantic messages"),
        Edge("protocol", "system", "system messages via UpstreamMessagePort", True),
        Edge("router", "node_a", "TimingNodeId"),
        Edge("router", "node_b", "TimingNodeId"),
    ]

    return Diagram(
        "timing-node-routing-mapping",
        "TimingSystem/TimingNode I/O mapping — internal system context with TimingNode-oriented upstream addressing",
        1400,
        950,
        nodes,
        edges,
    )

def rabbitmq_source_topology() -> Diagram:
    nodes = [
        Node("broker1", "RabbitMQ broker A", 95, 60, 300, 75, "external"),
        Node("broker2", "RabbitMQ broker B", 1005, 60, 300, 75, "external"),

        Node("conn1", "RabbitMqConnector connector-01\\nowns connection/channels internally", 55, 220, 380, 100, "adapter"),
        Node("conn2", "RabbitMqConnector connector-02\\nowns connection/channels internally", 965, 220, 380, 100, "adapter"),

        Node("gateway", "UpstreamGateway\\nexternal upstream-system boundary\\nuses 1..N connectors", 500, 390, 400, 110, "interface"),
        Node("router", "UpstreamMessageRouter\\napplication / TimingNode target routing", 500, 555, 400, 100, "interface"),

        Node("node1", "TimingNode timing-node-01\\nTimingNodeId\\nUpstreamMessagePort", 95, 735, 350, 105, "service"),
        Node("node2", "TimingNode timing-node-02\\nTimingNodeId\\nUpstreamMessagePort", 955, 735, 350, 105, "service"),
        Node("outbox", "local durable/pending outbox\\nTimingNodeId retained", 525, 745, 350, 90, "service"),

        Node("note", "Gateway owns connectors / upstream-system boundary\\nRouter owns target resolution\\nTimingNode port is bidirectional", 430, 900, 540, 100, "interface"),
    ]

    edges = [
        Edge("broker1", "conn1", "transport"),
        Edge("broker2", "conn2", "transport"),
        Edge("conn1", "gateway", "messages"),
        Edge("conn2", "gateway", "messages"),
        Edge("gateway", "router", "transport-neutral messages"),
        Edge("router", "node1", "TimingNodeId"),
        Edge("router", "node2", "TimingNodeId"),
        Edge("node1", "outbox", "committed outbound"),
        Edge("node2", "outbox", "committed outbound"),
        Edge("outbox", "router", "publish pending"),
        Edge("router", "note", "responsibility split", True),
    ]

    return Diagram(
        "rabbitmq-source-topology",
        "RabbitMQ connectors behind UpstreamGateway and UpstreamMessageRouter",
        1400,
        1040,
        nodes,
        edges,
    )

def timing_node_lifecycle() -> Diagram:
    nodes = [
        Node("closed", "CLOSED\\nnot accepting normal TimingNode operation", 170, 210, 330, 90, "core"),
        Node("open", "OPEN\\nTimingNode operation enabled", 770, 210, 330, 90, "core"),
        Node("health", "Subsystem health is orthogonal\\nHEALTHY • DEGRADED • ERROR do not silently change OPEN/CLOSED", 355, 440, 560, 110, "service"),
        Node("example", "Example: OPEN + RFID INITIALISING/ERROR\\n=> TimingNode remains OPEN while health is degraded", 355, 650, 560, 95, "interface"),
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
        Node("rabbit", "RabbitMQ / upstream\\nsession status", 940, 210, 300, 90, "service"),
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
