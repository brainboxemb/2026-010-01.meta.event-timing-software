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
# The portal must use Sphinx-Needs relationship labels, including backlinks.
portal_view = json.loads(
    (root / "docs" / "assets" / "engineering-graph.json").read_text(encoding="utf-8")
)
labels = portal_view["relation_labels"]
if labels["realizes"] != {"outgoing": "realizes", "incoming": "realized by"}:
    raise SystemExit("portal realizes labels drifted from Sphinx-Needs")
if labels["elaborates"] != {"outgoing": "elaborates", "incoming": "elaborated by"}:
    raise SystemExit("portal elaborates labels drifted from Sphinx-Needs")
for obsolete in ("derived_from", "satisfies", "detailed_by"):
    if obsolete in labels:
        raise SystemExit("obsolete relation label survived: " + obsolete)

timing_node_page = (site / "objects" / "TimingNode" / "index.html").read_text(
    encoding="utf-8"
)
for heading in (
    "This architecture element realizes:",
    "Detailed designs (2)",
):
    if heading not in timing_node_page:
        raise SystemExit("object details missing semantic heading: " + heading)
if "One-hop context" in timing_node_page:
    raise SystemExit("object details duplicate neighbors in a one-hop list")

design_page = (site / "objects" / "DD-TimingNodeExecution" / "index.html").read_text(
    encoding="utf-8"
)
if "This detailed design elaborates:" not in design_page:
    raise SystemExit("design details missing outgoing elaborates heading")

# UC-001 is specifically the normal browser/IF-04 path.
uc = portal_view["objects"]["UC-001"]
specification_sections = [
    section for section in uc["relation_groups"]
    if section["type"] == "specifies" and section["direction"] == "incoming"
]
if len(specification_sections) != 1:
    raise SystemExit("UC-001 missing a unique incoming requirement section")
requirements = specification_sections[0]
if requirements["title"] != "Requirements (5)":
    raise SystemExit("UC-001 wrong incoming role/count: " + requirements["title"])
expected = [
    "IF04-REQ-001",
    "IF04-REQ-002",
    "IF04-REQ-006",
    "IF04-REQ-008",
    "IF04-REQ-009",
]
if sorted(requirements["related_ids"]) != sorted(expected):
    raise SystemExit(
        f"UC-001 must link only to its IF-04 browser requirements: {requirements['related_ids']}"
    )
if requirements["document_groups"]:
    raise SystemExit("single-source UC-001 requirements should remain a flat list")

for forbidden in (
    "IF03-REQ-003", "IF03-REQ-004", "IF03-REQ-006", "IF03-REQ-011",
    "SI01-REQ-020", "SI01-REQ-021", "SI01-REQ-040",
    "SI02-REQ-002", "SI02-REQ-003", "SI02-REQ-004", "SI02-REQ-005",
):
    if forbidden in requirements["related_ids"]:
        raise SystemExit("UC-001 still contains non-Web direct trace: " + forbidden)

uc_page = (site / "objects" / "UC-001" / "index.html").read_text(
    encoding="utf-8"
)
if "This use case is specified by:" in uc_page:
    raise SystemExit("old reverse-grammar label found in UC-001 object page")
if "Requirements (5)" not in uc_page:
    raise SystemExit("UC-001 object page missing role-based heading")
if 'class="eng-relation__source-heading"' in uc_page:
    raise SystemExit("single-source UC-001 list should not need document subheadings")
if 'class="eng-relation__document"' in uc_page or "<details" in uc_page:
    raise SystemExit("UC-001 object page renders a collapsible relation instead of flat rows")
for target in expected:
    if f'href="../{target}/"' not in uc_page:
        raise SystemExit("UC-001 object page missing visible link to " + target)
if uc_page.count('class="eng-relation"') < 5:
    raise SystemExit("UC-001 object page has fewer than five flat relation rows")

# Both small and large link sets use the same flat row presentation.
timing_node_groups = portal_view["objects"]["TimingNode"]["relation_groups"]
realizes = next(
    group for group in timing_node_groups if group["type"] == "realizes"
)
if len(realizes["related_ids"]) != 3 or realizes["document_groups"]:
    raise SystemExit("short architecture links differ from the flat relation contract")

if "SI02-REQ-001" not in objects:
    raise SystemExit("engineering graph missing first SI-02 requirement")
si02_page = (site / "objects" / "SI02-REQ-001" / "index.html").read_text(
    encoding="utf-8"
)
if "Use only the public SI-01 interface boundary" not in si02_page:
    raise SystemExit("portal SI02-REQ-001 page is missing authored requirement content")
if "DD-PresentationAccess" not in objects:
    raise SystemExit("engineering graph missing detailed-design object DD-PresentationAccess")
presentation_design = objects["DD-PresentationAccess"]
deep_design_text = "Node-scoped presentation access is exposed through `TimingNodeProxy`."
if deep_design_text not in presentation_design.get("content", ""):
    raise SystemExit(
        "engineering graph detailed-design object contains only an anchor/summary; "
        "full DD-PresentationAccess body is missing"
    )
presentation_design_page = (
    site / "objects" / "DD-PresentationAccess" / "index.html"
).read_text(encoding="utf-8")
if "Node-scoped presentation access is exposed through" not in presentation_design_page:
    raise SystemExit(
        "portal DD-PresentationAccess page is missing substantive detailed-design content"
    )
if not any(
    relation.get("type") == "elaborates"
    and relation.get("from") == "DD-PresentationAccess"
    and relation.get("to") == "PresentationGateway"
    for relation in graph["relations"]
):
    raise SystemExit(
        "engineering graph missing DD-PresentationAccess -> PresentationGateway elaborates relation"
    )
expected_tool_eng_docs = {
    "ref": "v0.10.0",
    "sha": "417feac3b9f8b277a544337968087d97b8204a3d",
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

for object_id, item in portal_view["objects"].items():
    source_context = item.get("source_context")
    if not source_context:
        raise SystemExit(
            f"portal view missing authored source context for {object_id}"
        )
    if source_context.get("definition") is not True:
        raise SystemExit(
            f"portal source context did not resolve exact Need definition for {object_id}"
        )
    if source_context.get("object_id") != object_id:
        raise SystemExit(
            f"portal source context identity mismatch for {object_id}: "
            f"{source_context.get('object_id')!r}"
        )

    option_ids = []
    for line in source_context["lines"]:
        text = line["text"].strip()
        if text.startswith(":id: "):
            option_ids.append(text[len(":id: "):].strip())
        elif text.startswith("id: "):
            option_ids.append(text[len("id: "):].strip())

    if option_ids != [object_id]:
        raise SystemExit(
            f"portal source definition for {object_id} contains wrong Need ids: "
            f"{option_ids!r}"
        )

source_context = portal_view["objects"]["IF05-REQ-007"]["source_context"]
if source_context.get("path") != "docs/32-05-ISD-timingdata-interchange.md":
    raise SystemExit("IF05-REQ-007 source context path mismatch")
source_lines = "\n".join(line["text"] for line in source_context["lines"])
if "Committed record immutability" not in source_lines:
    raise SystemExit("IF05-REQ-007 source context lost authored requirement heading")

uc020_context = portal_view["objects"]["UC-020"]["source_context"]
uc020_lines = "\n".join(line["text"] for line in uc020_context["lines"])
if ":id: UC-020" not in uc020_lines:
    raise SystemExit("UC-020 source definition lost its own id")
if ":id: UC-007" in uc020_lines:
    raise SystemExit("UC-020 source definition incorrectly contains UC-007")

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
if explorer.count('data-eng-explorer-resizer') != 1:
    raise SystemExit("Engineering Explorer missing architecture/detail pane resizer")
if 'aria-label="Resize architecture and object detail panes"' not in explorer:
    raise SystemExit("Engineering Explorer resizer missing accessible label")
if 'role="separator"' not in explorer:
    raise SystemExit("Engineering Explorer resizer missing separator semantics")
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
    "Registration operation",
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

for behavior in (
    "engineering-explorer-pane-shares-v1",
    "data-eng-explorer-resizer",
    "defaultShares = [0.75, 0.25]",
):
    if behavior not in explorer_js:
        raise SystemExit(
            f"Engineering Explorer pane resize behavior missing: {behavior}"
        )

explorer_css = (
    site / "assets" / "stylesheets" / "explorer.css"
).read_text(encoding="utf-8")
if "body.eng-explorer-page .md-typeset details.eng-source-context" in explorer_css:
    raise SystemExit(
        "source-context presentation is scoped to Engineering Explorer instead of shared detail panes"
    )
if ".md-typeset details.eng-source-context" not in explorer_css:
    raise SystemExit("shared source-context presentation selector missing")
if ".md-typeset details.eng-source-context > summary::after {\n  display: none;" not in explorer_css:
    raise SystemExit("source-context summary still renders the disclosure icon")
if "border-radius: 0 !important;" not in explorer_css:
    raise SystemExit("source-context disclosure lost square presentation")
if "grid-template-columns: minmax(0, 3fr) 4px minmax(18rem, 1fr);" not in explorer_css:
    raise SystemExit("Engineering Explorer layout lost the resizer column")

search = (site / "search/search_index.json").read_text(encoding="utf-8")
for object_id in ("TimingNode", "DD-PresentationAccess", "SI01-REQ-020", "SI02-REQ-001", "VC-ST1-001", "UC-001", "UC-008", "UC-014"):
    if object_id not in search:
        raise SystemExit(f"portal search index missing {object_id}")
for narrative in (
    "The browser-based Web client connects to the configured IF-04 Web binding.",
    "SI-02 connects through the system-defined application-control/status interface.",
    "Settings describe several independently addressed",
):
    if narrative not in search:
        raise SystemExit(
            f"portal search index missing use-case narrative: {narrative}"
        )

if not (site / "index.html").is_file():
    raise SystemExit("portal landing page missing")

