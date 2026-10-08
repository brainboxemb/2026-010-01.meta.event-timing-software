#!/usr/bin/env python3
"""Generate the event-timing engineering portal from the normalized graph."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
import re
import runpy

import markdown
import shutil
import xml.etree.ElementTree as ET

# Use the same Sphinx-Needs label definitions as the authored Needs.
LINK_OPTIONS = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "docs/_sphinx-needs/conf.py")
)["needs_links"]

# Incoming relationships are navigated by the role of the linked objects.
# This is presentation vocabulary, distinct from Sphinx-Needs relation labels.
INCOMING_ROLES = {
    "specifies": ("Requirements", "Requirements defining the behaviour of this use case."),
    "refines": ("More specific requirements", "Requirements adding detail to this requirement."),
    "depends_on": ("Dependent requirements", "Requirements depending on this requirement."),
    "realizes": ("Architecture elements", "Architecture elements responsible for this requirement."),
    "elaborates": ("Detailed designs", "Designs detailing this architecture element."),
    "implements": ("Implementations", "Source implementations associated with this design."),
    "fulfills": ("Implementations", "Source implementations associated with this requirement."),
    "verifies": ("Verification cases", "Verification cases checking this requirement."),
}
DOCUMENT_GROUP_THRESHOLD = 6

SOURCE_RE = re.compile(r"^(?P<path>.+):(?P<line>[0-9]+)$")
NEED_OPEN_RE = re.compile(
    r"^(?P<fence>:::|```)\{(?P<directive>[A-Za-z0-9_-]+)\}(?:\s+.*)?$"
)
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
        source_path = match.group("path")
        line = match.group("line")
        suffix = f"?plain=1#L{line}" if source_path.endswith(".md") else f"#L{line}"
        return (
            f"https://github.com/{repository}/blob/{revision}/"
            f"{source_path}{suffix}"
        )
    return f"https://github.com/{repository}/blob/{revision}/{source}"


def _need_definition_bounds(
    lines: list[str],
    object_id: str,
    preferred_line: int,
) -> tuple[int, int] | None:
    """Return 0-based [start, end] bounds for one authored MyST Need."""

    id_forms = {f":id: {object_id}", f"id: {object_id}"}
    candidates = [
        index
        for index, text in enumerate(lines)
        if text.strip() in id_forms
    ]
    if not candidates:
        return None

    preferred_index = preferred_line - 1
    candidates.sort(key=lambda index: abs(index - preferred_index))

    for id_index in candidates:
        opener = None
        fence = None
        lower = max(-1, id_index - 40)
        for index in range(id_index - 1, lower, -1):
            text = lines[index].rstrip()
            match = NEED_OPEN_RE.match(text)
            if match:
                opener = index
                fence = match.group("fence")
                break
            if text.strip() in {":::", "```"}:
                break

        if opener is None or fence is None:
            continue

        for end in range(id_index + 1, len(lines)):
            if lines[end].strip() == fence:
                return opener, end

    return None


def source_context(
    source_root: Path,
    source: str,
    object_id: str,
) -> dict | None:
    match = SOURCE_RE.match(source)
    if not match:
        return None

    relative = Path(match.group("path"))
    root = source_root.resolve()
    path = (root / relative).resolve()
    if root != path and root not in path.parents:
        raise PortalError(f"source path escapes repository root: {relative}")
    if not path.is_file():
        raise PortalError(f"engineering source file is missing: {relative}")

    lines = path.read_text(encoding="utf-8").splitlines()
    line = int(match.group("line"))
    if line < 1 or line > len(lines):
        raise PortalError(
            f"engineering source line is outside file: {relative}:{line}"
        )

    bounds = _need_definition_bounds(lines, object_id, line)
    if bounds is not None:
        start_index, end_index = bounds
        start = start_index + 1
        end = end_index + 1
        return {
            "path": relative.as_posix(),
            "line": start,
            "start": start,
            "end": end,
            "object_id": object_id,
            "definition": True,
            "lines": [
                {"number": number, "text": lines[number - 1]}
                for number in range(start, end + 1)
            ],
        }

    # Guarded fallback for source forms that are not authored MyST Needs.
    start = max(1, line - 6)
    end = min(len(lines), line + 12)
    return {
        "path": relative.as_posix(),
        "line": line,
        "start": start,
        "end": end,
        "object_id": None,
        "definition": False,
        "lines": [
            {"number": number, "text": lines[number - 1]}
            for number in range(start, end + 1)
        ],
    }


def source_document_label(source_root: Path, source_path: str) -> str:
    """Name a source document from its authored heading/identity, not a Need ID."""

    path = (source_root / source_path).resolve()
    root = source_root.resolve()
    if root != path and root not in path.parents:
        raise PortalError(f"document path escapes repository root: {source_path}")
    if not path.is_file():
        return Path(source_path).stem

    lines = path.read_text(encoding="utf-8").splitlines()
    for line in lines[:30]:
        match = re.match(
            r"^(?:System interface|Software item):\\s*\\*\\*(.+?)\\*\\*",
            line.strip(),
            flags=re.IGNORECASE,
        )
        if match:
            return match.group(1)
    for line in lines:
        if line.startswith("# "):
            return line[2:].strip()
    return Path(source_path).stem


def build_relation_groups(item: dict, objects: dict[str, dict]) -> list[dict]:
    """Build one display representation shared by all Engineering Portal views."""

    sections = []
    for direction, target_field, incoming in (
        ("outgoing", "target", False),
        ("incoming", "source", True),
    ):
        types: dict[str, list[str]] = {}
        for edge in item[direction]:
            types.setdefault(edge["type"], []).append(edge[target_field])

        for relation_type, ids in types.items():
            if incoming:
                title, description = INCOMING_ROLES[relation_type]
                heading = f"{title} ({len(ids)})"
            else:
                title = item["type_label"].lower()
                verb = LINK_OPTIONS[relation_type]["outgoing"]
                heading = f"This {title} {verb}:"
                description = ""

            section = {
                "type": relation_type,
                "direction": direction,
                "title": heading,
                "description": description,
                "related_ids": ids,
                "document_groups": [],
            }
            if len(ids) >= DOCUMENT_GROUP_THRESHOLD:
                grouped: dict[str, dict] = {}
                for related_id in ids:
                    document = objects[related_id]["source_document"]
                    key = document["path"]
                    if key not in grouped:
                        grouped[key] = {
                            "path": key,
                            "title": document["title"],
                            "related_ids": [],
                        }
                    grouped[key]["related_ids"].append(related_id)
                section["document_groups"] = sorted(
                    grouped.values(), key=lambda group: (group["title"], group["path"])
                )
            sections.append(section)
    return sections


def make_view(graph: dict, repository: str, source_root: Path) -> dict:
    revision = graph["source_revision"]
    objects: dict[str, dict] = {}
    document_titles: dict[str, str] = {}

    for item in graph["objects"]:
        object_id = item["id"]
        if object_id in objects:
            raise PortalError(f"duplicate engineering object: {object_id}")
        context = source_context(source_root, item["source"], object_id)
        resolved_source = item["source"]
        if context and context.get("definition"):
            resolved_source = f"{context['path']}:{context['line']}"

        source_match = SOURCE_RE.match(resolved_source)
        document_path = (
            context["path"]
            if context
            else source_match.group("path") if source_match else resolved_source
        )
        if document_path not in document_titles:
            document_titles[document_path] = source_document_label(
                source_root, document_path
            )

        objects[object_id] = {
            "id": object_id,
            "type": item["type"],
            "type_label": item.get("type_name") or item["type"],
            "title": item["title"],
            "status": item.get("status") or "",
            "content": item.get("content") or "",
            "content_html": markdown.markdown(
                item.get("content") or "",
                extensions=["fenced_code", "tables"],
            ),
            "source": item["source"],
            "source_url": source_url(repository, revision, resolved_source),
            "source_document": {"path": document_path, "title": document_titles[document_path]},
            "source_context": context,
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
        if relation["type"] not in LINK_OPTIONS:
            raise PortalError(
                f"relation has no configured readable label: {relation['type']}"
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

    for item in objects.values():
        item["relation_groups"] = build_relation_groups(item, objects)

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
        "default_object": None,
        "objects": objects,
        "focus_depth_1": focus_depth_1,
        "relation_labels": {
            key: {"outgoing": value["outgoing"], "incoming": value["incoming"]}
            for key, value in LINK_OPTIONS.items()
        },
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


def render_relation_groups(obj: dict, objects: dict[str, dict]) -> list[str]:
    """Render the same role-based sections as the Explorer and Workspace."""

    result = []
    for section in obj["relation_groups"]:
        result.extend(["## " + section["title"], ""])
        if section["description"]:
            result.extend([section["description"], ""])

        groups = section["document_groups"]
        if groups:
            for group in groups:
                result.extend(
                    [
                        '<details class="eng-relation__document">',
                        f'<summary>{html.escape(group["title"])} ({len(group["related_ids"])})</summary>',
                        "<ul>",
                    ]
                )
                for related_id in group["related_ids"]:
                    related = objects[related_id]
                    result.append(
                        f'<li><a href="../{html.escape(related_id)}/">'
                        f'{html.escape(related_id)} — {html.escape(related["title"])}</a></li>'
                    )
                result.extend(["</ul>", "</details>", ""])
        else:
            for related_id in section["related_ids"]:
                related = objects[related_id]
                result.append(
                    f"- [{related_id} — {related['title']}](../{related_id}/)"
                )
            result.append("")

    return result or ["No traceability relationships are recorded for this object.", ""]


def render_object_page(obj: dict, view: dict) -> str:
    lines = [
        f"# {obj['id']} — {obj['title']}",
        "",
        f"**Type:** {obj['type_label']}  ",
        (
            "**Comparison workspace:** "
            f'<a href="../../workspace/?object={html.escape(obj["id"])}">'
            "open object comparison workspace</a>  "
        ),
        f"**Source definition:** [open authored source]({obj['source_url']})  ",
        (
            "**Engineering Explorer:** "
            f'<a href="../../explorer/?object={html.escape(obj["id"])}">'
            "open with architecture context</a>"
        ),
        "",
        (
            "This is a **derived portal page**. Engineering meaning is maintained "
            "in the authored Need, not in this generated presentation."
        ),
        "",
    ]

    if obj["content"]:
        lines.extend(["## Definition", "", obj["content"], ""])

    lines.extend(render_relation_groups(obj, view["objects"]))
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
  while inspecting one selected engineering object.
- [Traceability comparison](workspace.md) — keep one engineering object fixed
  on the left while opening related objects on the right.
- [Engineering object index](objects/index.md) — searchable generated object
  pages with readable, direction-aware relationship headings.
- [Engineering Client UI](engineering-client-ui.md) — review the Step-4 Timing
  UI wireframes and state/interaction design.
- [Architecture Book](book.md) — the existing assembled Book remains a
  first-class output and is not owned by this portal.

The portal does not author engineering meaning. Stable IDs, relations and
content come from native MyST/Sphinx-Needs and the released normalized graph
boundary.
"""


ENGINEERING_CLIENT_UI_DIAGRAMS = (
    (
        "engineering-client-timing-closed.svg",
        "CLOSED without operational location",
        "Set Location is available; Open waits for an authoritative assigned LocationId.",
    ),
    (
        "engineering-client-timing-open.svg",
        "OPEN with bounded LogBook",
        "Location is fixed; dev auto-reg is capability-gated and committed records are shown from the LogBook.",
    ),
    (
        "engineering-client-timing-reconnecting.svg",
        "RECONNECTING / stale",
        "Cached state remains visible while controls stay disabled until rebuild and dedup complete.",
    ),
)


def render_engineering_client_ui(view: dict, repository: str) -> str:
    source = source_url(
        repository,
        view["source_revision"],
        "docs/50-SDE-03-engineering-client.md",
    )
    sections = []
    for filename, title, description in ENGINEERING_CLIENT_UI_DIAGRAMS:
        sections.extend(
            [
                f"## {title}",
                "",
                description,
                "",
                f"![{title}](assets/architecture/{filename})",
                "",
            ]
        )

    return "\n".join(
        [
            "# Engineering Client — Step 4 Timing UI",
            "",
            (
                "This is a **derived portal view** of the D01 mid-fidelity UI "
                "baseline. The authoritative design text and control/state rules "
                f"remain in [SDE03 — Engineering Client]({source})."
            ),
            "",
            (
                "The wireframes are generated from declarative YAML by "
                "tool.eng-docs; the same sources also produce editable draw.io "
                "output in the normal documentation publication."
            ),
            "",
            *sections,
        ]
    )

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

<h1 class="eng-explorer-title">Engineering explorer</h1>

<div class="eng-workspace-nav eng-workspace-nav--compact" aria-label="Engineering portal navigation">
  <a href="../">Home</a>
  <a href="../workspace/">Traceability comparison</a>
  <a href="../book/">Architecture Book</a>
  <a href="../objects/">Object index</a>
</div>

<div class="eng-explorer-workspace" data-eng-explorer>
  <section class="eng-context">
    <div class="eng-diagram">
      {svg}
    </div>
    <p>Click a diagram object or choose any engineering object below.</p>
    <h2>Engineering objects</h2>
    <div class="eng-object-picker">{chips}</div>
  </section>

  <div
    class="eng-pane-resizer"
    role="separator"
    aria-orientation="vertical"
    aria-label="Resize architecture and object detail panes"
    tabindex="0"
    data-eng-explorer-resizer
  ></div>

  <aside class="eng-detail eng-explorer-detail" data-eng-detail aria-live="polite">
    Select an engineering object.
  </aside>
</div>

## About this view

The Engineering Explorer keeps the generated SI-01 architecture on the **left**
and the selected engineering object on the **right**. Selecting an architecture
element or an object below updates the right-hand detail pane without replacing
the architecture context.

For relation-by-relation comparison, use the separate
[Traceability comparison](../workspace/) workspace.

<script id="eng-graph-data" type="application/json">{graph_json}</script>
"""


def render_workspace(view: dict) -> str:
    type_counts: dict[str, int] = {}
    for obj in view["objects"].values():
        label = obj["type_label"]
        type_counts[label] = type_counts.get(label, 0) + 1
    type_options = "".join(
        (
            f'<option value="{html.escape(label)}">'
            f"{html.escape(label)} ({count})</option>"
        )
        for label, count in sorted(type_counts.items())
    )
    graph_json = json.dumps(view, separators=(",", ":")).replace("</", "<\\/")
    return f"""---
hide:
  - navigation
  - toc
---

<h1 class="eng-trace-title">Traceability comparison</h1>

<div class="eng-workspace-nav eng-workspace-nav--compact" aria-label="Engineering portal navigation">
  <a href="../">Home</a>
  <a href="../explorer/">Engineering Explorer</a>
  <a href="../book/">Architecture Book</a>
  <a href="../objects/">Object index</a>
</div>

<div data-eng-workspace>
  <div class="eng-trace-layout">
    <aside class="eng-object-browser" aria-label="Engineering object browser">
      <div class="eng-object-browser__filters">
        <input
          type="search"
          aria-label="Filter engineering objects"
          placeholder="filter ID / title"
          autocomplete="off"
          data-eng-tree-search
        >
        <div class="eng-object-browser__filter-row">
          <select aria-label="Filter by object type" data-eng-tree-type>
            <option value="">all types ({view["object_count"]})</option>
            {type_options}
          </select>
          <button
            class="eng-tree-collapse-all"
            type="button"
            data-eng-tree-collapse-all
            title="Collapse all tree groups"
          >Collapse all</button>
        </div>
        <span class="eng-object-browser__count" data-eng-tree-count>
          {view["object_count"]} objects
        </span>
      </div>
      <!-- ENGINEERING_OBJECT_TREE -->
    </aside>

    <div
      class="eng-pane-resizer"
      role="separator"
      aria-orientation="vertical"
      aria-label="Resize engineering object browser"
      tabindex="0"
      data-eng-resizer="tree-root"
    ></div>

    <section class="eng-detail" data-eng-root-detail aria-live="polite">
      Select an engineering object.
    </section>

    <div
      class="eng-pane-resizer"
      role="separator"
      aria-orientation="vertical"
      aria-label="Resize selected and compared object panes"
      tabindex="0"
      data-eng-resizer="root-compare"
    ></div>

    <aside class="eng-detail" data-eng-compare-detail aria-live="polite">
      Select a related object to compare.
    </aside>
  </div>
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
    source_root: Path,
    tool_ref: str,
    tool_sha: str,
) -> None:
    graph = load_graph(graph_path)
    view = make_view(graph, repository, source_root)
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
    for filename, _, _ in ENGINEERING_CLIENT_UI_DIAGRAMS:
        source = architecture_path.parent / filename
        if not source.is_file():
            raise PortalError(
                f"missing generated Engineering Client UI diagram: {source}"
            )
        shutil.copy2(
            source,
            output_dir / "assets" / "architecture" / filename,
        )

    (output_dir / "index.md").write_text(render_index(view), encoding="utf-8")
    (output_dir / "engineering-client-ui.md").write_text(
        render_engineering_client_ui(view, repository),
        encoding="utf-8",
    )
    (output_dir / "book.md").write_text(
        render_book_page(repository, publication_branch), encoding="utf-8"
    )
    (output_dir / "explorer.md").write_text(
        render_explorer(view, svg), encoding="utf-8"
    )
    (output_dir / "workspace.md").write_text(
        render_workspace(view), encoding="utf-8"
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
    parser.add_argument("--source-root", required=True)
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
        source_root=Path(args.source_root),
        tool_ref=args.tool_ref,
        tool_sha=args.tool_sha,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
