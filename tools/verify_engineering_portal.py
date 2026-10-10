#!/usr/bin/env python3
"""Verify that the built Engineering Portal faithfully presents engineering data.

Purpose: test the *transformation* from source Needs/normalized graph to portal
objects, relationships, navigation, provenance and search. It is not a second
requirements baseline: IDs, UC counts, chapter titles and complete relation
sets are owned by the source documents. Coverage of those sources against the
Needs export/graph belongs to validate_engineering_coverage.py.

A few named objects below are deliberate end-to-end examples, not an inventory
of every required UC or SI-01 requirement. Browser interactions are exercised
separately by verify_engineering_portal_workspace.sh.

Inputs: bld/engineering-graph.json, generated bld/engineering-portal, sources.
Environment: SOURCE_REVISION, set by CI to the revision being built.
"""

import json
import os
import re
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
if not use_cases:
    raise SystemExit("engineering graph contains no use cases")

# The source-formatting rule is project-wide, not a per-UC fixture list.
uc_source = Path("docs/30-UC-system-use-cases.md").read_text(encoding="utf-8")
uc_headers = re.findall(
    r"(?m)^(:::\\{uc\\}[^\\n]*\\n:id: UC-\\d+[^\\n]*\\n:status: [DRA][^\\n]*)\\n",
    uc_source,
)
if len(uc_headers) != len(use_cases):
    raise SystemExit("use-case source header count differs from generated objects")
for uc_header in uc_headers:
    if any(not line.endswith("  ") for line in uc_header.splitlines()):
        raise SystemExit("use-case header must have two trailing spaces per line")

# The only prescribed SSD order is functional capabilities before technical
# constraints and architecture. Individual requirement numbers/groups are free
# to evolve in the source; IDs and traceability are checked downstream.
si01_source = Path("docs/41-01-SSD-timing-application-specification-document.md").read_text(
    encoding="utf-8"
)
fun = si01_source.find("### Functional requirements")
tech = si01_source.find("### Technical requirements")
architecture = si01_source.find("## Software-item architecture")
if not (0 <= fun < tech < architecture):
    raise SystemExit("SI-01 requirements must precede architecture, functional before technical")

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
    "Detailed designs",
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

# One representative UC-to-software-to-interface route tests that links remain
# navigable. Do not list every UC and requirement here: source links are
# authoritative, and validate_engineering_coverage checks completeness.
sample_uc = "UC-001"
sample_req = "SI01-REQ-040"
sample_interface = "IF04-REQ-003"
sample_relations = (
    ("specifies", sample_req, sample_uc),
    ("refines", sample_interface, sample_req),
    ("realizes", "TimingNode", "SI01-REQ-024"),
)
for relation_type, source_id, target_id in sample_relations:
    if not any(
        r.get("type") == relation_type
        and r.get("from") == source_id
        and r.get("to") == target_id
        for r in graph["relations"]
    ):
        raise SystemExit(
            f"sample traceability path missing {source_id} --{relation_type}--> {target_id}"
        )

# Check portal relation groups against the actual graph for *every* object,
# without maintaining a second hand-authored list of expected relationships.
for object_id, view_object in portal_view["objects"].items():
    displayed = {
        (group["type"], group["direction"], other)
        for group in view_object["relation_groups"]
        for other in group["related_ids"]
    }
    from_graph = set()
    for rel in graph["relations"]:
        rel_type = rel["type"]
        if rel.get("from") == object_id:
            from_graph.add((rel_type, "outgoing", rel["to"]))
        if rel.get("to") == object_id:
            from_graph.add((rel_type, "incoming", rel["from"]))
    if displayed != from_graph:
        raise SystemExit(f"{object_id}: portal relations diverge from normalized graph")

uc_page = (site / "objects" / sample_uc / "index.html").read_text(encoding="utf-8")
if f'href="../{sample_req}/"' not in uc_page:
    raise SystemExit("UC sample page does not link to its software requirement")
req_page = (site / "objects" / sample_req / "index.html").read_text(encoding="utf-8")
if f'href="../{sample_interface}/"' not in req_page:
    raise SystemExit("requirement sample page does not link to its interface refinement")

# A single SI-02 example checks the client family is included in the portal.
if "SI02-REQ-001" not in objects:
    raise SystemExit("engineering graph missing the SI-02 sample requirement")
si02_page = (site / "objects" / "SI02-REQ-001" / "index.html").read_text(
    encoding="utf-8"
)
if "Use only supported public SI-01 boundaries" not in si02_page:
    raise SystemExit("portal SI02-REQ-001 page is missing authored requirement content")
if "IF03-REQ-001" not in objects:
    raise SystemExit("engineering graph missing IF-03 public-boundary requirement")
if "UC-009" not in objects:
    raise SystemExit("engineering graph missing Engineering Client use case UC-009")
engineering_page = (site / "objects" / "UC-009" / "index.html").read_text(
    encoding="utf-8"
)
if "Engineering Client connects to the registration system" not in engineering_page:
    raise SystemExit("portal UC-009 page is missing Engineering Client narrative")
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
# The build records the tool revision it actually used. Version pinning is
# verified by the CI bootstrap, not copied into a second list here.
tool_provenance = provenance.get("tool_eng_docs")
if not isinstance(tool_provenance, dict) or not all(
    tool_provenance.get(field) for field in ("ref", "sha")
):
    raise SystemExit("portal missing tool.eng-docs revision provenance")

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
    "Registration cabinet ↔ backoffice",
    "Errors and recovery",
    "Development, engineering and system testing",
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
# Representative identifiers from different engineering families are sufficient
# to catch a broken search index; its full contents follow the source graph.
for sample in (sample_uc, sample_req, sample_interface, "TimingNode", "SI02-REQ-001"):
    if sample not in search:
        raise SystemExit(f"portal search index missing sample object {sample}")

if not (site / "index.html").is_file():
    raise SystemExit("portal landing page missing")

