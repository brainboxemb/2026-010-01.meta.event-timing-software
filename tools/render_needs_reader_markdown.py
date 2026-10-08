#!/usr/bin/env python3
"""Render MyST/Sphinx-Needs directives as reader-friendly generated Markdown."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

import yaml


OPEN_RE = re.compile(r"^(?P<fence>```|:::)\{(?P<directive>[A-Za-z0-9_-]+)\}\s*(?P<title>.*)$")
COLON_OPTION_RE = re.compile(r"^:([A-Za-z0-9_-]+):\s*(.*)$")

STATUS_LABELS = {
    "D": "Draft",
    "R": "Review",
    "A": "Approved",
    "O": "Obsolete",
}

TYPE_LABELS = {
    "uc": "Use Case",
    "req": "Requirement",
    "ifreq": "Interface Requirement",
    "arch": "Architecture Element",
    "design": "Detailed Design",
    "impl": "Implementation",
    "vc": "Verification Case",
}

# Reuse the project Sphinx-Needs link labels for reader output.
import runpy

LINK_OPTIONS = runpy.run_path(
    str(Path(__file__).resolve().parents[1] / "docs/_sphinx-needs/conf.py")
)["needs_links"]
RELATION_LABELS = tuple(
    entry
    for name, definition in LINK_OPTIONS.items()
    for entry in (
        (name, definition["outgoing"].capitalize()),
        (name + "_back", definition["incoming"].capitalize()),
    )
)

class ReaderRenderError(ValueError):
    pass


def load_needs(path: Path) -> dict[str, dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    current = data.get("current_version")
    versions = data.get("versions", {})
    if not current or current not in versions:
        raise ReaderRenderError(f"{path}: invalid Sphinx-Needs current_version")
    needs = versions[current].get("needs")
    if not isinstance(needs, dict):
        raise ReaderRenderError(f"{path}: current version has no needs object")
    return needs


def parse_options(lines: list[str], start: int) -> tuple[dict, int]:
    options: dict = {}
    index = start

    if index < len(lines) and lines[index] == "---":
        end = index + 1
        while end < len(lines) and lines[end] != "---":
            end += 1
        if end >= len(lines):
            raise ReaderRenderError("unterminated YAML option block")
        raw = "\n".join(lines[index + 1 : end])
        parsed = yaml.safe_load(raw) or {}
        if not isinstance(parsed, dict):
            raise ReaderRenderError("Need YAML options must be a mapping")
        options.update(parsed)
        return options, end + 1

    while index < len(lines):
        match = COLON_OPTION_RE.match(lines[index])
        if not match:
            break
        options[match.group(1)] = match.group(2).strip()
        index += 1

    return options, index


def target_link(target: str, needs: dict[str, dict]) -> str:
    need = needs.get(target)
    if not isinstance(need, dict):
        return f"`{target}`"

    docname = need.get("docname")
    if isinstance(docname, str) and docname:
        name = Path(docname).name + ".md"
        return f"[`{target}`]({name}#{target})"

    return f"`{target}`"


def relation_items(need: dict, needs: dict[str, dict]) -> list[str]:
    items = []
    for field, label in RELATION_LABELS:
        targets = need.get(field, [])
        if not targets:
            continue
        if not isinstance(targets, list):
            raise ReaderRenderError(
                f"{need.get('id')}: relation field {field} is not a list"
            )
        links = ", ".join(target_link(target, needs) for target in targets)
        items.append(f"**{label}:** {links}")
    return items


def render_need(
    directive: str,
    title: str,
    options: dict,
    body: list[str],
    needs: dict[str, dict],
) -> list[str]:
    object_id = options.get("id")
    if not isinstance(object_id, str) or not object_id:
        raise ReaderRenderError(
            f"{directive} {title!r}: generated reader needs an explicit id"
        )

    need = needs.get(object_id)
    if not isinstance(need, dict):
        raise ReaderRenderError(f"{object_id}: not present in needs.json")

    label = TYPE_LABELS.get(directive, need.get("type_name") or directive)
    resolved_title = need.get("title") or title

    output = [
        f'<a id="{object_id}"></a>',
        "",
        f"**{object_id} — {resolved_title}**",
        "",
    ]

    metadata = [f"**Type:** {label}"]
    status = need.get("status")
    if isinstance(status, str) and status:
        if directive in {"req", "ifreq"} and status not in STATUS_LABELS:
            raise ReaderRenderError(
                f"{object_id}: unsupported requirement status {status!r}; "
                "expected D, R, A or O"
            )
        metadata.append(f"**Status:** {STATUS_LABELS.get(status, status)}")
    metadata.extend(relation_items(need, needs))

    if directive == "vc":
        # Verification cases often contain a long test specification. Keep
        # traceability visible directly below the title so the reader does not
        # have to reach the end of the procedure before seeing what it verifies.
        if metadata:
            output.extend(f"- {item}" for item in metadata)
            output.extend(["", "— — —", ""])
        output.extend(body)
    else:
        output.extend(body)
        if metadata:
            output.extend(["", "— — —", ""])
            output.extend(f"- {item}" for item in metadata)

    output.extend(["", "---", ""])
    return output


def transform_text(text: str, needs: dict[str, dict]) -> str:
    lines = text.splitlines()
    output: list[str] = []
    index = 0

    while index < len(lines):
        match = OPEN_RE.match(lines[index])
        if not match or match.group("directive") not in TYPE_LABELS:
            output.append(lines[index])
            index += 1
            continue

        fence = match.group("fence")
        directive = match.group("directive")
        title = match.group("title").strip()
        options, body_start = parse_options(lines, index + 1)

        if body_start < len(lines) and lines[body_start] == "":
            body_start += 1

        end = body_start
        while end < len(lines) and lines[end] != fence:
            end += 1
        if end >= len(lines):
            raise ReaderRenderError(
                f"unterminated MyST Need directive starting at line {index + 1}"
            )

        body = lines[body_start:end]
        output.extend(render_need(directive, title, options, body, needs))
        index = end + 1

    return "\n".join(output) + ("\n" if text.endswith("\n") else "")


def render_tree(documents: Path, needs_path: Path) -> int:
    needs = load_needs(needs_path)
    changed = 0

    for path in sorted(documents.rglob("*.md")):
        source = path.read_text(encoding="utf-8")
        rendered = transform_text(source, needs)
        if rendered != source:
            path.write_text(rendered, encoding="utf-8")
            changed += 1

    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--documents", required=True)
    parser.add_argument("--needs", required=True)
    args = parser.parse_args()

    changed = render_tree(Path(args.documents), Path(args.needs))
    print(f"reader Markdown: transformed {changed} generated document(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
