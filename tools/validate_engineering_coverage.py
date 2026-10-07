#!/usr/bin/env python3
"""Validate that every stable project engineering object is in Needs and the normalized graph."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

import yaml

NEED_BLOCK_RE = re.compile(
    r"^(?P<fence>```|:::)\{(?:uc|req|ifreq|arch|design|vc)\}[^\n]*\n"
    r"(?P<body>.*?)(?=^(?P=fence)\s*$)",
    re.MULTILINE | re.DOTALL,
)
NEED_ID_RE = re.compile(r"^(?::id:|id:)\s*(?P<id>[A-Za-z][A-Za-z0-9_-]*)\s*$", re.MULTILINE)
LEGACY_UC_RE = re.compile(r"^##\s+(?P<id>UC-\d{3})\s+—\s+", re.MULTILINE)
LEGACY_REQ_RE = re.compile(
    r"^\*\*(?P<id>[A-Z][A-Z0-9]*-REQ-\d{3})\s+—\s+",
    re.MULTILINE,
)
LEGACY_VC_RE = re.compile(
    r"^(?:#{2,4}\s+|\*\*)(?P<id>VC-[A-Z0-9][A-Z0-9-]*)\s+—\s+",
    re.MULTILINE,
)
DIAGRAM_OBJECT_RE = re.compile(
    r"^\s*object_id:\s*[\"']?(?P<id>[A-Za-z][A-Za-z0-9_.-]*)[\"']?\s*$",
    re.MULTILINE,
)


def add(found: dict[str, set[str]], object_id: str, source: str) -> None:
    found.setdefault(object_id, set()).add(source)


def discover_expected(root: Path) -> tuple[dict[str, set[str]], set[str]]:
    found: dict[str, set[str]] = {}
    diagram_ids: set[str] = set()

    for path in sorted((root / "docs").rglob("*.md")):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(root).as_posix()

        for match in NEED_BLOCK_RE.finditer(text):
            id_match = NEED_ID_RE.search(match.group("body"))
            if id_match:
                add(found, id_match.group("id"), f"{rel}:need")

        for regex, label in (
            (LEGACY_UC_RE, "legacy-use-case"),
            (LEGACY_REQ_RE, "legacy-requirement"),
            (LEGACY_VC_RE, "legacy-verification-case"),
        ):
            for match in regex.finditer(text):
                add(found, match.group("id"), f"{rel}:{label}")

    semantic_notations = {"class", "component", "packaging-component"}
    for path in sorted((root / "docs" / "_diagrams").glob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(root).as_posix()

        data = yaml.safe_load(text)
        groups = data.get("groups", []) if isinstance(data, dict) else []
        nodes = data.get("nodes", []) if isinstance(data, dict) else []
        missing_identity: list[str] = []
        for element_type, elements in (("group", groups), ("node", nodes)):
            for element in elements:
                if not isinstance(element, dict):
                    continue
                notation = element.get("notation")
                object_id = element.get("object_id")
                if notation in semantic_notations and not object_id:
                    missing_identity.append(
                        f"{element_type} {element.get('id', '<unnamed>')} "
                        f"({element.get('label', '<unlabelled>')})"
                    )

        if missing_identity:
            raise ValueError(
                f"{rel} has semantic architecture element(s) without object_id: "
                + ", ".join(missing_identity)
            )

        for match in DIAGRAM_OBJECT_RE.finditer(text):
            object_id = match.group("id")
            diagram_ids.add(object_id)
            add(found, object_id, f"{rel}:object_id")

    return found, diagram_ids


def load_needs_ids(path: Path) -> set[str]:
    data = json.loads(path.read_text(encoding="utf-8"))
    current = data.get("current_version")
    if not current:
        raise ValueError("needs.json has no current_version")
    versions = data.get("versions", {})
    needs = versions.get(current, {}).get("needs")
    if not isinstance(needs, dict):
        raise ValueError("needs.json current version has no needs mapping")
    return set(needs)


def load_graph_ids(path: Path) -> tuple[set[str], dict]:
    graph = json.loads(path.read_text(encoding="utf-8"))
    objects = graph.get("objects")
    relations = graph.get("relations")
    if not isinstance(objects, list) or not isinstance(relations, list):
        raise ValueError("engineering graph has no object/relation lists")
    ids = {item["id"] for item in objects}
    if graph.get("object_count") != len(objects):
        raise ValueError("engineering graph object_count mismatch")
    if graph.get("relation_count") != len(relations):
        raise ValueError("engineering graph relation_count mismatch")
    return ids, graph


def describe(ids: set[str]) -> str:
    groups = {
        "UC": sorted(i for i in ids if re.fullmatch(r"UC-\d{3}", i)),
        "SI requirements": sorted(i for i in ids if re.fullmatch(r"SI\d{2}-REQ-\d{3}", i)),
        "IF requirements": sorted(i for i in ids if re.fullmatch(r"IF\d{2}-REQ-\d{3}", i)),
        "verification": sorted(i for i in ids if i.startswith("VC-")),
        "detailed design": sorted(i for i in ids if i.startswith("DD-")),
    }
    known = set().union(*groups.values())
    groups["architecture/other"] = sorted(ids - known)
    return ", ".join(f"{name}={len(values)}" for name, values in groups.items())


def fail_set(name: str, expected: set[str], actual: set[str], sources: dict[str, set[str]]) -> None:
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    lines = [f"{name} does not match the full-project engineering coverage contract"]
    if missing:
        lines.append("missing:")
        for object_id in missing:
            lines.append(f"  {object_id}: {', '.join(sorted(sources.get(object_id, set())))}")
    if extra:
        lines.append("unexpected:")
        lines.extend(f"  {object_id}" for object_id in extra)
    raise ValueError("\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    parser.add_argument("--needs", required=True)
    parser.add_argument("--graph", required=True)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    sources, diagram_ids = discover_expected(root)
    expected = set(sources)
    needs_ids = load_needs_ids(Path(args.needs))
    graph_ids, graph = load_graph_ids(Path(args.graph))

    if expected != needs_ids:
        fail_set("Sphinx-Needs", expected, needs_ids, sources)
    if expected != graph_ids:
        fail_set("normalized engineering graph", expected, graph_ids, sources)

    graph_by_id = {item["id"]: item for item in graph["objects"]}
    missing_diagram_refs = sorted(
        object_id
        for object_id in diagram_ids
        if not graph_by_id[object_id].get("diagram_refs")
    )
    if missing_diagram_refs:
        raise ValueError(
            "diagram object_id values missing normalized diagram_refs: "
            + ", ".join(missing_diagram_refs)
        )

    print(
        f"engineering coverage: {len(expected)} objects / "
        f"{graph['relation_count']} relations / {len(diagram_ids)} diagram identities; "
        + describe(expected)
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(f"coverage error: {exc}", file=sys.stderr)
        raise SystemExit(1)
