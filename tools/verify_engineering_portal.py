#!/usr/bin/env python3
"""Verify the generated Engineering Portal structure and provenance.

The workflow supplies SOURCE_REVISION. The verifier intentionally reads the
same generated files and applies the same assertions that previously lived
inline in docs-build.yml.
"""

import json
import os
from pathlib import Path

root = Path("bld/engineering-portal")
site = root / "site"
graph = json.loads(Path("bld/engineering-graph.json").read_text(encoding="utf-8"))
provenance = json.loads(
    (root / "docs/assets/provenance.json").read_text(encoding="utf-8")
)

expected_ids = {item["id"] for item in graph["objects"]}
objects = {item["id"]: item for item in graph["objects"]}

ui_page = site / "engineering-client-ui" / "index.html"
if not ui_page.is_file():
    raise SystemExit("engineering portal missing Engineering Client UI page")
ui_html = ui_page.read_text(encoding="utf-8")
for filename in (
    "engineering-client-timing-closed.svg",
    "engineering-client-timing-open.svg",
    "engineering-client-timing-reconnecting.svg",
):
    asset = root / "docs" / "assets" / "architecture" / filename
    if not asset.is_file():
        raise SystemExit(f"engineering portal missing UI diagram asset: {filename}")
    if filename not in ui_html:
        raise SystemExit(f"Engineering Client UI page does not reference {filename}")

use_cases = {
    object_id: item
    for object_id, item in objects.items()
    if item.get("type") == "uc"
}
if len(use_cases) != 20:
    raise SystemExit(f"expected 20 current system use cases, got {len(use_cases)}")
for object_id, item in sorted(use_cases.items()):
    content = item.get("content", "")
    for token in ("**Goal:**", "**Main flow:**"):
        if token not in content:
            raise SystemExit(
                f"engineering graph missing full use-case narrative {object_id}: {token}"
            )

    page = (site / "objects" / object_id / "index.html").read_text(
        encoding="utf-8"
    )
    if "Main flow" not in page:
        raise SystemExit(
            f"portal object page missing use-case narrative {object_id}: Main flow"
        )

actual_pages = {
    path.parent.name for path in (site / "objects").glob("*/index.html")
}
if actual_pages != expected_ids:
    raise SystemExit("portal object-page set does not match engineering graph")

if provenance["source_revision"] != os.environ["SOURCE_REVISION"]:
    raise SystemExit("portal source revision mismatch")
if provenance["object_count"] != graph["object_count"]:
    raise SystemExit("portal object count does not match engineering graph")
if provenance["relation_count"] != graph["relation_count"]:
    raise SystemExit("portal relation count does not match engineering graph")
expected_tool_eng_docs = {
    "ref": "v0.9.1",
    "sha": "7d13ae32c5ac3ac3fea0192559a034b9778a517d",
}
if provenance["tool_eng_docs"] != expected_tool_eng_docs:
    raise SystemExit(
        "portal tool provenance mismatch: "
        f"actual={provenance['tool_eng_docs']!r} "
        f"expected={expected_tool_eng_docs!r}"
    )

required_diagram_ids = {
    object_id
    for object_id, item in objects.items()
    if item.get("diagram_refs")
}
if set(provenance["diagram_objects"]) != required_diagram_ids:
    raise SystemExit("portal clickable architecture identities do not match graph diagram references")

portal_view = json.loads(
    (root / "docs/assets/engineering-graph.json").read_text(encoding="utf-8")
)
if portal_view.get("default_object") is not None:
    raise SystemExit("portal view still has an implicit default object")

source_context = portal_view["objects"]["IF05-REQ-007"].get("source_context")
if not source_context:
    raise SystemExit("portal view missing IF05-REQ-007 authored source context")
if source_context.get("path") != "docs/32-05-ISD-timingdata-interchange.md":
    raise SystemExit("IF05-REQ-007 source context path mismatch")
source_lines = "\n".join(line["text"] for line in source_context["lines"])
if "Committed record immutability" not in source_lines:
    raise SystemExit("IF05-REQ-007 source context lost authored requirement heading")

object_page = (
    site / "objects" / "IF05-REQ-007" / "index.html"
).read_text(encoding="utf-8")
if "open object comparison workspace" not in object_page:
    raise SystemExit("IF05-REQ-007 object page missing comparison workspace action")

explorer = (site / "explorer/index.html").read_text(encoding="utf-8")
for object_id in required_diagram_ids:
    if f'data-engineering-id="{object_id}"' not in explorer:
        raise SystemExit(
            f"portal explorer missing architecture identity: {object_id}"
        )
if 'data-eng-detail' not in explorer or 'eng-explorer-workspace' not in explorer:
    raise SystemExit("Engineering Explorer page lost architecture + selected-object composition")
if 'eng-explorer-title' not in explorer:
    raise SystemExit("Engineering Explorer missing compact workbench heading")
if 'data-eng-workspace' in explorer:
    raise SystemExit("Engineering Explorer unexpectedly contains comparison workspace")
if '<a href="../">Home</a>' not in explorer:
    raise SystemExit("Engineering Explorer missing neutral Home navigation")

workspace_page = site / "workspace" / "index.html"
if not workspace_page.is_file():
    raise SystemExit("engineering portal missing traceability comparison page")
workspace = workspace_page.read_text(encoding="utf-8")
if 'data-eng-root-detail' not in workspace or 'data-eng-compare-detail' not in workspace:
    raise SystemExit("traceability comparison page missing two-object workspace")
if 'data-eng-object-tree' not in workspace:
    raise SystemExit("traceability comparison page missing ordered object tree")
if 'data-eng-tree-search' not in workspace or 'data-eng-tree-type' not in workspace:
    raise SystemExit("traceability comparison page missing tree filters")
if 'data-eng-tree-collapse-all' not in workspace:
    raise SystemExit("traceability comparison page missing Collapse all control")
if 'data-workspace-root-id="IF05-REQ-007"' not in workspace:
    raise SystemExit("traceability object tree missing IF05-REQ-007")
if '32-05-ISD-timingdata-interchange' not in workspace:
    raise SystemExit("traceability object tree lost source-document grouping")
for section_label in (
    "Normal operation",
    "System, backoffice and recovery",
    "Status",
    "First registration operation",
):
    if section_label not in workspace:
        raise SystemExit(
            f"traceability object tree missing authored section: {section_label}"
        )
if 'data-tree-level="1"' not in workspace:
    raise SystemExit("traceability object tree missing nested heading levels")
if workspace.count('data-eng-resizer=') != 2:
    raise SystemExit("traceability comparison page missing two pane resizers")
if 'role="separator"' not in workspace:
    raise SystemExit("traceability pane resizers missing separator semantics")
if 'md-nav__link eng-tree-group__toggle' in workspace:
    raise SystemExit("tree disclosure still depends on Material nav-link behavior")
if 'data-engineering-id=' in workspace:
    raise SystemExit("traceability comparison page unexpectedly embeds architecture diagram")
if '<a href="../">Home</a>' not in workspace:
    raise SystemExit("Traceability Comparison missing neutral Home navigation")

explorer_js = (
    site / "assets" / "javascripts" / "explorer.js"
).read_text(encoding="utf-8")
for behavior in (
    "engineering-traceability-pane-shares-v1",
    "pointerdown",
    "ArrowLeft",
    "ArrowRight",
    "localStorage",
):
    if behavior not in explorer_js:
        raise SystemExit(
            f"traceability pane resize behavior missing: {behavior}"
        )

search = (site / "search/search_index.json").read_text(encoding="utf-8")
for object_id in ("TimingNode", "SI01-REQ-020", "VC-ST1-001", "UC-001", "UC-008", "UC-014"):
    if object_id not in search:
        raise SystemExit(f"portal search index missing {object_id}")
for narrative in (
    "The operator application connects to the registration system.",
    "SI-02 connects through the system-defined application-control/status interface.",
    "Settings describe several independently addressed",
):
    if narrative not in search:
        raise SystemExit(
            f"portal search index missing use-case narrative: {narrative}"
        )

if not (site / "index.html").is_file():
    raise SystemExit("portal landing page missing")

