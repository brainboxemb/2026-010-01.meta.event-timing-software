project = "Event timing engineering graph"
version = "migration-013"
release = version

extensions = [
    "myst_parser",
    "sphinx_needs",
]

master_doc = "index"
source_suffix = {".md": "markdown"}

# Keep MyST directives readable in ordinary Markdown source review (for example GitHub).
myst_enable_extensions = ["colon_fence"]

needs_id_required = True
needs_id_regex = r"^[A-Za-z][A-Za-z0-9_-]*$"
needs_build_json = True
needs_reproducible_json = True
needs_json_remove_defaults = True

# Keep the native HTML reader content-first: engineering metadata and
# traceability remain available from each Need, but start collapsed.
needs_card_layouts = {
    "engineering_reader": {
        "extends": "clean",
        "meta": {
            "exclude": ["layout", "style"],
        },
        "collapse": "closed",
    },
}
needs_default_layout = "engineering_reader"

needs_types = [
    {"directive": "uc", "title": "Use Case", "prefix": "UC-", "color": "#BFD8D2", "style": "node"},
    {"directive": "req", "title": "Requirement", "prefix": "REQ-", "color": "#FEDCD2", "style": "node"},
    {"directive": "ifreq", "title": "Interface Requirement", "prefix": "IF-", "color": "#F6E5A8", "style": "node"},
    {"directive": "arch", "title": "Architecture Element", "prefix": "ARCH-", "color": "#D9EAF7", "style": "node"},
    {"directive": "design", "title": "Detailed Design", "prefix": "DD-", "color": "#E7DCF4", "style": "node"},
    {"directive": "impl", "title": "Implementation", "prefix": "IMPL-", "color": "#DBEBE8", "style": "node"},
    {"directive": "vc", "title": "Verification Case", "prefix": "VC-", "color": "#D8E7C5", "style": "node"},
]

# A relation runs from the Need declaring it to its target ID.
# Incoming labels describe generated backlinks, not another authored link.
needs_links = {
    "specifies": {
        "description": "Requirement specifies use-case behaviour",
        "outgoing": "specifies",
        "incoming": "specified by",
        "copy": False,
        "allow_dead_links": False,
    },
    "refines": {
        "description": "Requirement refines an upstream requirement",
        "outgoing": "refines",
        "incoming": "refined by",
        "copy": False,
        "allow_dead_links": False,
    },
    "depends_on": {
        "description": "Requirement depends on another requirement",
        "outgoing": "depends on",
        "incoming": "depended on by",
        "copy": False,
        "allow_dead_links": False,
    },
    "realizes": {
        "description": "Architecture realizes a requirement",
        "outgoing": "realizes",
        "incoming": "realized by",
        "copy": False,
        "allow_dead_links": False,
    },
    "elaborates": {
        "description": "Detailed design elaborates an architecture element",
        "outgoing": "elaborates",
        "incoming": "elaborated by",
        "copy": False,
        "allow_dead_links": False,
    },
    "implements": {
        "description": "Source implementation implements a design",
        "outgoing": "implements",
        "incoming": "implemented by",
        "copy": False,
        "allow_dead_links": False,
    },
    "fulfills": {
        "description": "Source implementation fulfills a requirement",
        "outgoing": "fulfills",
        "incoming": "fulfilled by",
        "copy": False,
        "allow_dead_links": False,
    },
    "verifies": {
        "description": "Verification case verifies a requirement",
        "outgoing": "verifies",
        "incoming": "verified by",
        "copy": False,
        "allow_dead_links": False,
    },
}

needs_schema_definitions_from_json = "schemas.json"
