from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Any


TREE_MARKER = "<!-- ENGINEERING_OBJECT_TREE -->"


def _repository_root(config: Any) -> Path:
    config_path = getattr(config, "config_file_path", None)
    if config_path:
        return Path(config_path).resolve().parent.parent.parent
    return Path.cwd().resolve()


def _load_current_needs(config: Any) -> dict[str, dict[str, Any]]:
    path = _repository_root(config) / "bld" / "sphinx-needs" / "needs" / "needs.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    current = data.get("current_version")
    if not current:
        versions = data.get("versions") or {}
        if len(versions) != 1:
            raise RuntimeError("cannot determine current Sphinx-Needs version")
        current = next(iter(versions))
    return data["versions"][current]["needs"]


def _document_label(docname: str) -> str:
    return Path(docname).name


def _section_path(need: dict[str, Any]) -> list[str]:
    sections = list(reversed(need.get("sections") or []))
    # Sphinx-Needs includes the document H1 as the outermost section. The
    # document node already represents that level in the tree.
    if sections:
        sections = sections[1:]
    return [str(section) for section in sections if str(section).strip()]


def _common_prefix(paths: list[list[str]]) -> list[str]:
    non_empty = [path for path in paths if path]
    if not non_empty:
        return []
    prefix = list(non_empty[0])
    for path in non_empty[1:]:
        limit = min(len(prefix), len(path))
        index = 0
        while index < limit and prefix[index] == path[index]:
            index += 1
        prefix = prefix[:index]
        if not prefix:
            break
    return prefix


def _tree_node() -> dict[str, Any]:
    return {"children": {}, "entries": []}


def _render_need(need: dict[str, Any]) -> str:
    object_id = html.escape(need["id"])
    title = html.escape(need.get("title") or need["id"])
    type_name = html.escape(need.get("type_name") or need.get("type") or "")
    search = html.escape(f"{need['id']} {need.get('title') or ''}".lower())
    return (
        '<li class="md-nav__item eng-tree-leaf" role="none">'
        '<button class="md-nav__link eng-tree-item" type="button" role="treeitem" '
        f'data-workspace-root-id="{object_id}" '
        f'data-object-type="{type_name}" '
        f'data-object-search="{search}">'
        '<span class="eng-tree-item__label">'
        f'<strong class="eng-tree-item__id">{object_id}</strong>'
        f'<span class="eng-tree-item__title">{title}</span>'
        "</span></button></li>"
    )


def _render_group(label: str, node: dict[str, Any], *, level: int) -> str:
    children: list[str] = []
    for kind, value in node["entries"]:
        if kind == "group":
            child_label = value
            children.append(
                _render_group(
                    child_label,
                    node["children"][child_label],
                    level=level + 1,
                )
            )
        else:
            children.append(_render_need(value))

    return (
        '<li class="md-nav__item eng-tree-group" role="none" '
        f'data-eng-tree-group data-tree-level="{level}">'
        '<button class="md-nav__link eng-tree-group__toggle" type="button" '
        'role="treeitem" aria-expanded="false" data-eng-tree-toggle>'
        f'<span class="eng-tree-group__label">{html.escape(label)}</span>'
        '<span class="eng-tree-group__chevron" aria-hidden="true">›</span>'
        "</button>"
        '<ul class="md-nav__list eng-tree-group__items" role="group">'
        + "".join(children)
        + "</ul></li>"
    )


def _render_tree(needs: dict[str, dict[str, Any]]) -> str:
    by_document: dict[str, list[dict[str, Any]]] = {}
    ordered = sorted(
        needs.values(),
        key=lambda need: (
            need.get("docname") or "",
            int(need.get("lineno") or 0),
            need.get("id") or "",
        ),
    )
    for need in ordered:
        docname = need.get("docname")
        if not docname or not need.get("id"):
            continue
        by_document.setdefault(docname, []).append(need)

    documents: list[str] = []
    for docname, document_needs in by_document.items():
        section_paths = [_section_path(need) for need in document_needs]
        prefix = _common_prefix(section_paths)
        root = _tree_node()

        for need, full_path in zip(document_needs, section_paths):
            path = full_path[len(prefix) :]
            node = root
            for section in path:
                if section not in node["children"]:
                    node["children"][section] = _tree_node()
                    node["entries"].append(("group", section))
                node = node["children"][section]
            node["entries"].append(("need", need))

        documents.append(_render_group(_document_label(docname), root, level=0))

    return (
        '<nav class="md-nav eng-object-tree" aria-label="Engineering objects">'
        '<ul class="md-nav__list eng-tree-root" role="tree" data-eng-object-tree>'
        + "".join(documents)
        + "</ul></nav>"
    )


def on_page_markdown(markdown: str, page: Any, config: Any, files: Any) -> str:
    if getattr(page.file, "src_uri", "") != "workspace.md":
        return markdown
    if TREE_MARKER not in markdown:
        raise RuntimeError("Traceability workspace is missing tree marker")
    return markdown.replace(TREE_MARKER, _render_tree(_load_current_needs(config)))
