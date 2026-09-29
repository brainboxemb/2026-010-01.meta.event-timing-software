#!/usr/bin/env python3
"""Generate the event-timing engineering portal from the normalized graph."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import re

import markdown
import shutil
import xml.etree.ElementTree as ET

SOURCE_RE = re.compile(r"^(?P<path>.+):(?P<line>[0-9]+)$")
SVG_NS = "http://www.w3.org/2000/svg"
XLINK_NS = "http://www.w3.org/1999/xlink"
ET.register_namespace("", SVG_NS)
ET.register_namespace("xlink", XLINK_NS)


class PortalError(ValueError):
    pass


def load_graph(path: Path) -> dict:
    graph = json.loads(path.read_text(encoding="utf-8"))
    if graph.get("schema") != "brainboxemb.engineering-graph":
        raise PortalError("unexpected engineering graph schema")
    objects = graph.get("objects")
    relations = graph.get("relations")
    if not isinstance(objects, list) or not isinstance(relations, list):
        raise PortalError("engineering graph must contain object and relation lists")
    if graph.get("object_count") != len(objects):
        raise PortalError("engineering graph object_count mismatch")
    if graph.get("relation_count") != len(relations):
        raise PortalError("engineering graph relation_count mismatch")
    return graph


def source_url(repository: str, revision: str, source: str) -> str:
    match = SOURCE_RE.match(source)
    if match:
        return (
            f"https://github.com/{repository}/blob/{revision}/"
            f"{match.group('path')}#L{match.group('line')}"
        )
    return f"https://github.com/{repository}/blob/{revision}/{source}"


def make_view(graph: dict, repository: str) -> dict:
    revision = graph["source_revision"]
    objects: dict[str, dict] = {}

    for item in graph["objects"]:
        object_id = item["id"]
        if object_id in objects:
            raise PortalError(f"duplicate engineering object: {object_id}")
        objects[object_id] = {
            "id": object_id,
            "type": item["type"],
            "type_label": item.get("type_name") or item["type"],
            "title": item["title"],
            "content": item.get("content") or "",
            "content_html": markdown.markdown(
                item.get("content") or "",
                extensions=["fenced_code", "tables"],
            ),
            "source": item["source"],
            "source_url": source_url(repository, revision, item["source"]),
            "diagram_refs": item.get("diagram_refs") or [],
            "outgoing": [],
            "incoming": [],
        }

    for relation in graph["relations"]:
        source_id = relation["from"]
        target_id = relation["to"]
        if source_id not in objects or target_id not in objects:
            raise PortalError(
                f"relation target/source missing: {source_id} -> {target_id}"
            )
        objects[source_id]["outgoing"].append(
            {"type": relation["type"], "target": target_id}
        )
        objects[target_id]["incoming"].append(
            {"type": relation["type"], "source": source_id}
        )

    for item in objects.values():
        item["outgoing"].sort(key=lambda rel: (rel["type"], rel["target"]))
        item["incoming"].sort(key=lambda rel: (rel["type"], rel["source"]))

    focus_depth_1: dict[str, dict] = {}
    for object_id, item in objects.items():
        neighbors = {object_id}
        neighbors.update(rel["target"] for rel in item["outgoing"])
        neighbors.update(rel["source"] for rel in item["incoming"])
        focus_depth_1[object_id] = {"objects": sorted(neighbors)}

    return {
        "schema": "brainboxemb.engineering-portal-view",
        "schema_version": 1,
        "source_revision": revision,
        "source_graph": graph["source_graph"],
        "object_count": len(objects),
        "relation_count": len(graph["relations"]),
        "default_object": (
            "TimingNode" if "TimingNode" in objects else sorted(objects)[0]
        ),
        "objects": objects,
        "focus_depth_1": focus_depth_1,
    }


def prepare_inline_svg(
    path: Path, objects: dict[str, dict]
) -> tuple[str, set[str]]:
    root = ET.fromstring(path.read_text(encoding="utf-8"))
    classes = root.get("class", "").split()
    if "eng-architecture" not in classes:
        classes.append("eng-architecture")
    root.set("class", " ".join(item for item in classes if item))

    seen: set[str] = set()
    for element in root.iter():
        object_id = element.get("data-engineering-id")
        if not object_id:
            continue
        if object_id not in objects:
            raise PortalError(
                f"diagram engineering identity is not in graph: {object_id}"
            )
        seen.add(object_id)
        element.set("role", "button")
        element.set("tabindex", "0")
        element.set("aria-label", f"Open {object_id}")

    if not seen:
        raise PortalError("generated architecture contains no clickable engineering identities")

    return ET.tostring(root, encoding="unicode"), seen


def render_object_index(view: dict) -> str:
    lines = [
        "# Engineering object index",
        "",
        (
            f"Generated from the normalized engineering graph at "
            f"`{view['source_revision'][:12]}`. "
            "These pages are derived views, not engineering source."
        ),
        "",
        "| ID | Type | Title |",
        "| --- | --- | --- |",
    ]
    for object_id in sorted(view["objects"]):
        obj = view["objects"][object_id]
        lines.append(
            f"| [{object_id}](./{object_id}/) "
            f"| {obj['type_label']} | {obj['title']} |"
        )
    lines.append("")
    return "\n".join(lines)


def render_relation_table(
    title: str,
    relations: list[dict],
    *,
    endpoint: str,
    objects: dict[str, dict],
) -> list[str]:
    lines = [f"## {title}", ""]
    if not relations:
        return [*lines, "None in the current engineering graph.", ""]

    heading = "Target" if endpoint == "target" else "Source"
    lines.extend([f"| Relation | {heading} |", "| --- | --- |"])
    for relation in relations:
        related_id = relation[endpoint]
        related = objects[related_id]
        lines.append(
            f"| `{relation['type']}` | "
            f"[{related_id} — {related['title']}](../{related_id}/) |"
        )
    lines.append("")
    return lines


def render_object_page(obj: dict, view: dict) -> str:
    lines = [
        f"# {obj['id']} — {obj['title']}",
        "",
        f"**Type:** {obj['type_label']}  ",
        f"**Authority:** [open exact source]({obj['source_url']})  ",
        (
            "**Explorer:** "
            f'<a href="../../explorer/?object={html.escape(obj["id"])}">'
            "open with context</a>"
        ),
        "",
    ]

    if obj["content"]:
        lines.extend(["## Definition", "", obj["content"], ""])

    lines.extend(
        render_relation_table(
            "Outgoing relationships",
            obj["outgoing"],
            endpoint="target",
            objects=view["objects"],
        )
    )
    lines.extend(
        render_relation_table(
            "Incoming relationships",
            obj["incoming"],
            endpoint="source",
            objects=view["objects"],
        )
    )

    focus = view["focus_depth_1"][obj["id"]]["objects"]
    lines.extend(
        [
            "## One-hop context",
            "",
            "Incoming and outgoing graph neighbors at exact shortest-path depth 1.",
            "",
        ]
    )
    for related_id in focus:
        if related_id == obj["id"]:
            continue
        related = view["objects"][related_id]
        lines.append(
            f"- [{related_id} — {related['title']}](../{related_id}/)"
        )
    lines.append("")
    return "\n".join(lines)


def render_index(view: dict) -> str:
    return f"""# Event Timing Engineering Portal

This is the event-timing engineering portal. It is a **derived reader** over
the same engineering source that produces the existing Book and traceability
evidence.

- **Source revision:** `{view['source_revision']}`
- **Engineering objects:** {view['object_count']}
- **Authored relations:** {view['relation_count']}

## Start here

- [Engineering explorer](explorer.md) — keep the real SI-01 architecture visible
  while inspecting requirements, use cases, architecture and verification.
- [Engineering object index](objects/index.md) — searchable generated object
  pages with incoming/outgoing and one-hop context.
- [Architecture Book](book.md) — the existing assembled Book remains a
  first-class output and is not owned by this portal.

The portal does not author engineering meaning. Stable IDs, relations and
content come from native MyST/Sphinx-Needs and the released normalized graph
boundary.
"""


def render_book_page(repository: str, publication_branch: str) -> str:
    url = (
        f"https://github.com/{repository}/blob/{publication_branch}/"
        "documents/architecture-book.md"
    )
    return f"""# Architecture Book

The existing assembled architecture Book remains the linear reading/review
output.

[Open the generated Architecture Book]({url})

The Material portal complements that Book with search, object pages and focused
engineering context. It does not replace Book assembly or source ownership.
"""


def render_explorer(view: dict, svg: str) -> str:
    chips = "".join(
        (
            '<button class="eng-object-chip" type="button" '
            f'data-object-id="{html.escape(object_id)}">'
            f"{html.escape(object_id)}</button>"
        )
        for object_id in sorted(view["objects"])
    )
    graph_json = json.dumps(view, separators=(",", ":")).replace("</", "<\\/")
    return f"""---
hide:
  - navigation
  - toc
---

# Engineering explorer

<div class="eng-workspace-nav" aria-label="Engineering portal navigation">
  <a href="../">Portal</a>
  <a href="../book/">Architecture Book</a>
  <a href="../objects/">Object index</a>
</div>

The real generated SI-01 architecture stays visible while the selected
engineering object and its traceability context are inspected.

<div class="eng-workspace" data-eng-explorer>
  <section class="eng-context">
    <h2>Figure SI01-01 — architecture context</h2>
    <div class="eng-diagram">
      {svg}
    </div>
    <p>Click a diagram object or choose any graph object below.</p>
    <h2>Engineering objects</h2>
    <div class="eng-object-picker">{chips}</div>
  </section>
  <aside class="eng-detail" data-eng-detail aria-live="polite">
    Select an engineering object.
  </aside>
</div>

<script id="eng-graph-data" type="application/json">{graph_json}</script>
"""


def write_portal(
    *,
    graph_path: Path,
    architecture_path: Path,
    output_dir: Path,
    assets_dir: Path,
    repository: str,
    publication_branch: str,
    tool_ref: str,
    tool_sha: str,
) -> None:
    graph = load_graph(graph_path)
    view = make_view(graph, repository)
    svg, diagram_objects = prepare_inline_svg(
        architecture_path, view["objects"]
    )

    if output_dir.exists():
        shutil.rmtree(output_dir)
    (output_dir / "objects").mkdir(parents=True)
    (output_dir / "assets" / "javascripts").mkdir(parents=True)
    (output_dir / "assets" / "stylesheets").mkdir(parents=True)
    (output_dir / "assets" / "architecture").mkdir(parents=True)

    shutil.copy2(
        assets_dir / "javascripts" / "explorer.js",
        output_dir / "assets" / "javascripts" / "explorer.js",
    )
    shutil.copy2(
        assets_dir / "stylesheets" / "explorer.css",
        output_dir / "assets" / "stylesheets" / "explorer.css",
    )
    shutil.copy2(
        architecture_path,
        output_dir / "assets" / "architecture" / "layered-architecture.svg",
    )

    (output_dir / "index.md").write_text(render_index(view), encoding="utf-8")
    (output_dir / "book.md").write_text(
        render_book_page(repository, publication_branch), encoding="utf-8"
    )
    (output_dir / "explorer.md").write_text(
        render_explorer(view, svg), encoding="utf-8"
    )
    (output_dir / "objects" / "index.md").write_text(
        render_object_index(view), encoding="utf-8"
    )
    for object_id, obj in view["objects"].items():
        (output_dir / "objects" / f"{object_id}.md").write_text(
            render_object_page(obj, view), encoding="utf-8"
        )

    (output_dir / "assets" / "engineering-graph.json").write_text(
        json.dumps(view, indent=2) + "\n", encoding="utf-8"
    )
    provenance = {
        "schema": "brainboxemb.engineering-portal-provenance",
        "schema_version": 1,
        "source_revision": view["source_revision"],
        "source_graph": view["source_graph"],
        "object_count": view["object_count"],
        "relation_count": view["relation_count"],
        "repository": repository,
        "publication_branch": publication_branch,
        "tool_eng_docs": {"ref": tool_ref, "sha": tool_sha},
        "diagram_objects": sorted(diagram_objects),
    }
    (output_dir / "assets" / "provenance.json").write_text(
        json.dumps(provenance, indent=2) + "\n", encoding="utf-8"
    )

    print(
        "engineering portal source: "
        f"{view['object_count']} objects / {view['relation_count']} relations / "
        f"{len(diagram_objects)} clickable diagram objects"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--graph", required=True)
    parser.add_argument("--architecture", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--assets", required=True)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--publication-branch", required=True)
    parser.add_argument("--tool-ref", required=True)
    parser.add_argument("--tool-sha", required=True)
    args = parser.parse_args()

    write_portal(
        graph_path=Path(args.graph),
        architecture_path=Path(args.architecture),
        output_dir=Path(args.output),
        assets_dir=Path(args.assets),
        repository=args.repository,
        publication_branch=args.publication_branch,
        tool_ref=args.tool_ref,
        tool_sha=args.tool_sha,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
