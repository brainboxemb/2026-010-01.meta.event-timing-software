#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path

ENG_RE = re.compile(r'<!-- eng (\{.*\}) -->')
ENG_REL_RE = re.compile(r'<!-- eng-rel (\{.*\}) -->')
ANCHOR_RE = re.compile(r'<a id="([^"]+)"></a>')
OBJECT_ID_RE = re.compile(r'^\s*object_id:\s*([^#\s]+)\s*$', re.M)


def relation_rows(owner, meta, source):
    rows = []
    for kind, targets in meta.get("relations", {}).items():
        if not isinstance(targets, list) or not all(isinstance(x, str) and x for x in targets):
            raise SystemExit(f"{source}: relation {kind} must be a list of ids")
        rows += [
            {"from": owner, "type": kind, "to": target, "source": source}
            for target in targets
        ]
    return rows


def add_authoring(obj, source, raw):
    obj.setdefault("authoring", []).append({"source": source, "input": raw})


def markdown_review(graph):
    objects = {item["id"]: item for item in graph["objects"]}
    outgoing = {key: [] for key in objects}
    incoming = {key: [] for key in objects}
    for rel in graph["relations"]:
        outgoing[rel["from"]].append(rel)
        incoming[rel["to"]].append(rel)

    lines = [
        "# Traceability review",
        "",
        f"Source revision: {graph.get('source_revision') or 'unknown'}",
        "",
        "This view makes the Step-3 canary explicit for human review:",
        "",
        "- **Authored input** is the exact hidden Markdown/YAML identity or relation input.",
        "- **Authored outgoing** is the normalized meaning owned by that source object.",
        "- **Generated incoming** is derived from other objects and is not authored again here.",
        "",
        "## Overview",
        "",
        "| Object | Type | Authored outgoing | Generated incoming |",
        "| --- | --- | ---: | ---: |",
    ]
    for oid in sorted(objects):
        anchor = oid.lower().replace("_", "-")
        lines.append(
            f"| [{oid}](#{anchor}) | {objects[oid]['type']} | "
            f"{len(outgoing[oid])} | {len(incoming[oid])} |"
        )

    for oid in sorted(objects):
        obj = objects[oid]
        lines += [
            "",
            f"## {oid}",
            "",
            f"Type: {obj['type']}  ",
            f"Primary source: {obj['source']}",
            "",
            "### Authored input",
            "",
        ]
        for authored in obj.get("authoring", []):
            lines += [
                f"Source: {authored['source']}",
                "",
                "~~~text",
                authored["input"],
                "~~~",
                "",
            ]
        if not obj.get("authoring"):
            lines += ["_No explicit authoring input retained._", ""]

        lines += ["### Authored outgoing", ""]
        if outgoing[oid]:
            for rel in sorted(outgoing[oid], key=lambda r: (r["type"], r["to"])):
                lines.append(f"- {rel['type']} -> **{rel['to']}**")
        else:
            lines.append("_None._")

        lines += ["", "### Generated incoming", ""]
        if incoming[oid]:
            for rel in sorted(incoming[oid], key=lambda r: (r["type"], r["from"])):
                lines.append(f"- {rel['type']} <- **{rel['from']}**")
        else:
            lines.append("_None._")

    return "\n".join(lines) + "\n"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--docs", default="docs")
    p.add_argument("--diagrams", default="docs/_diagrams")
    p.add_argument("--output")
    p.add_argument("--review-output")
    p.add_argument("--source-revision")
    a = p.parse_args()

    objects = {}
    relations = []
    extensions = []

    for path in sorted(Path(a.docs).glob("*.md")):
        lines = path.read_text(encoding="utf-8").splitlines()
        current = None
        for n, line in enumerate(lines, 1):
            stripped = line.strip()

            m = ANCHOR_RE.fullmatch(stripped)
            if m:
                current = m.group(1)

            m = ENG_RE.fullmatch(stripped)
            if m:
                if not current:
                    raise SystemExit(f"{path}:{n}: eng metadata requires a preceding stable anchor")
                try:
                    meta = json.loads(m.group(1))
                except json.JSONDecodeError as e:
                    raise SystemExit(f"{path}:{n}: invalid eng JSON: {e}")
                if current in objects:
                    raise SystemExit(f"{path}:{n}: duplicate engineering id {current}")
                source = f"{path}:{n}"
                objects[current] = {
                    "id": current,
                    "type": meta["type"],
                    "source": source,
                    "authoring": [],
                }
                add_authoring(objects[current], source, stripped)
                relations += relation_rows(current, meta, source)
                continue

            m = ENG_REL_RE.fullmatch(stripped)
            if m:
                try:
                    meta = json.loads(m.group(1))
                except json.JSONDecodeError as e:
                    raise SystemExit(f"{path}:{n}: invalid eng-rel JSON: {e}")
                owner = meta.get("id")
                if not isinstance(owner, str) or not owner:
                    raise SystemExit(f"{path}:{n}: eng-rel requires a non-empty id")
                extensions.append((owner, meta, f"{path}:{n}", stripped))

    for path in sorted(Path(a.diagrams).glob("*.yaml")):
        text = path.read_text(encoding="utf-8")
        for m in OBJECT_ID_RE.finditer(text):
            oid = m.group(1).strip('"\'')
            line = text[:m.start()].count("\n") + 1
            source = f"{path}:{line}"
            if oid in objects:
                raise SystemExit(f"{source}: duplicate engineering id {oid}")
            objects[oid] = {
                "id": oid,
                "type": "architecture-element",
                "source": source,
                "authoring": [],
            }
            add_authoring(objects[oid], source, f"object_id: {oid}")

    for owner, meta, source, raw in extensions:
        if owner not in objects:
            raise SystemExit(f"{source}: eng-rel owner does not exist: {owner}")
        add_authoring(objects[owner], source, raw)
        relations += relation_rows(owner, meta, source)

    for rel in relations:
        if rel["to"] not in objects:
            raise SystemExit(f'{rel["source"]}: unknown {rel["type"]} target {rel["to"]}')

    graph = {
        "schema": "brainboxemb.engineering-graph-canary",
        "schema_version": 1,
        "source_revision": a.source_revision,
        "object_count": len(objects),
        "relation_count": len(relations),
        "objects": [objects[k] for k in sorted(objects)],
        "relations": relations,
    }

    if a.output:
        out = Path(a.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")

    if a.review_output:
        review = Path(a.review_output)
        review.parent.mkdir(parents=True, exist_ok=True)
        review.write_text(markdown_review(graph), encoding="utf-8")

    print(f"engineering graph: {len(objects)} objects, {len(relations)} relations")


if __name__ == "__main__":
    main()
