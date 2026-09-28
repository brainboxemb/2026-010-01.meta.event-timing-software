project = "Event timing engineering graph"
version = "migration-013"
release = version

extensions = [
    "myst_parser",
    "sphinx_needs",
]

master_doc = "index"
source_suffix = {".md": "markdown"}

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
    {"directive": "vc", "title": "Verification Case", "prefix": "VC-", "color": "#D8E7C5", "style": "node"},
]

needs_links = {
    "derived_from": {
        "description": "Upstream engineering source",
        "incoming": "is source for",
        "outgoing": "derived from",
        "copy": False,
        "allow_dead_links": False,
    },
    "satisfies": {
        "description": "Design satisfaction",
        "incoming": "satisfied by",
        "outgoing": "satisfies",
        "copy": False,
        "allow_dead_links": False,
    },
    "verifies": {
        "description": "Verification coverage",
        "incoming": "verified by",
        "outgoing": "verifies",
        "copy": False,
        "allow_dead_links": False,
    },
}

needs_schema_definitions_from_json = "schemas.json"
