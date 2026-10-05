#!/usr/bin/env bash
# Verify assembled documentation output and retained producer evidence.
#
# SOURCE_REVISION is supplied by CI or by the local caller.
set -euo pipefail
test -f bld/engineering-graph.json
test -f bld/engineering-graph-review.md
test -f bld/docs/README.md
test -f bld/docs/source-sha.txt
test -f bld/docs/documents/README.md
test -f bld/docs/documents/software-document-set.md
test -f bld/docs/documents/architecture-book.md
test -f bld/docs/documents/50-SDE-01-software-development-environment.md
test -f bld/docs/documents/50-SDE-02-java-build-test-toolchain.md
test -f bld/docs/documents/41-01-SSD-timing-application-specification-document.md
test -f bld/docs/documents/32-03-ISD-application-control-status.md
test -f bld/docs/documents/33-03-IDD-api-http-websocket.md
test -f bld/docs/documents/32-04-ISD-web-interface.md
test -f bld/docs/documents/32-05-ISD-timingdata-interchange.md
test -f bld/docs/documents/33-05-IDD-timingdata-interchange.md
test -f bld/docs/documents/32-11-ISD-application-configuration.md
test -f bld/docs/documents/43-01-SDD-02-java-component-design.md
test -f bld/docs/documents/60-SVP-software-verification-plan.md
test -f bld/docs/documents/61-01-VTS-timing-application-verification-test-specification.md
test -f bld/docs/assets/architecture/system-overview.svg
test -f bld/docs/assets/architecture/system-overview.drawio
test -f bld/docs/assets/architecture/layered-architecture.svg
test -f bld/docs/assets/architecture/layered-architecture.drawio
for ui_diagram in \
  engineering-client-timing-closed \
  engineering-client-timing-open \
  engineering-client-timing-reconnecting; do
  test -f "bld/docs/assets/architecture/${ui_diagram}.svg"
  test -f "bld/docs/assets/architecture/${ui_diagram}.drawio"
done
for object_id in TimingNode PresentationGateway Conductor Api; do
  grep -F "data-engineering-id=\"$object_id\"" bld/docs/assets/architecture/layered-architecture.svg
  grep -F "data-engineering-id=\"$object_id\"" bld/docs/assets/architecture/layered-architecture.drawio
done
test -f bld/docs/planning/sip-roadmap.svg
test -s bld/docs/planning/sip-roadmap.pdf
test -f .moon/invocations/software_docs.assemble/materialization.json
test -f .moon/invocations/software_docs.assemble/moon.log

SOURCE_REVISION="$SOURCE_REVISION" python3 - <<'PY'
import json
import os
from pathlib import Path

from jsonschema import Draft202012Validator

root = Path.cwd()
schema = json.loads(
    (root / "tools/tool.git-project/schemas/execution-evidence.schema.json").read_text(encoding="utf-8")
)
Draft202012Validator.check_schema(schema)
validator = Draft202012Validator(schema)

expected = {
    "docs-diagrams": ("docs.diagrams", "diagrams"),
    "docs-planning": ("docs.planning", "planning"),
    "docs-assemble": ("docs.assemble", "assemble"),
}
revisions = {}
for execution_id, (capability, action) in expected.items():
    path = root / "bld/docs/evidence/executions" / execution_id / "execution.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    validator.validate(data)
    if data["capability"] != capability or data["action"] != action:
        raise SystemExit(f"execution identity mismatch: {execution_id}")
    if data["owner"] != "brainboxemb/2026-010-01.meta.event-timing-software":
        raise SystemExit(f"execution owner mismatch: {execution_id}")
    if data["owner_revision"] != data["source_revision"]:
        raise SystemExit(f"project-owned execution revision mismatch: {execution_id}")
    if data["status"] != "success" or data["exit_code"] != 0:
        raise SystemExit(f"producer execution failed: {execution_id}")
    allowed_tool_eng_docs_producers = {
        # Pre-release owner head used to produce the reusable cached Book tree.
        "a5224de7d62973a1836ec023801324adaa6ebebd",
        # Immutable v0.6.6 release may still appear in older cached evidence.
        "d619e97020afd343000ff90288555970c5cb32a7",
        # Temporary sequence-renderer qualification evidence may remain cached.
        "93e63aeeb990cbad1f00c63ed947c3287e3ffdce",
        # Immutable v0.7.0 release used by this consumer.
        "a9b6dcf94f9a0b5986b1cadd76bde47102566977",
        # Pre-release v0.8.0 qualification evidence may remain cached.
        "5f53275ac5998b56ee2b7344f8819a8ee0e16270",
        # Immutable v0.8.0 release used by this consumer.
        "b36ee6828d15b4179e9e975c0ba76193b1bc2213",
        # Immutable v0.8.0 native-UML sequence renderer release.
        "b36ee6828d15b4179e9e975c0ba76193b1bc2213",
        # Temporary compact-sequence renderer qualification head.
        "dcbe8505f9ac26a3764bc7528b5f4ee286c02a87",
        # Immutable v0.9.0 wireframe-capable engineering-docs release.
        "b4645d8810fd0e235605e5f03646e14f9653ddea",
        # Immutable v0.9.1 multi-page BoardView release.
        "7d13ae32c5ac3ac3fea0192559a034b9778a517d",
        # Qualified v0.9.2 content tree before squash; retained cache evidence
        # must keep the exact producer revision that originally created it.
        "9e900d24610aaa311c5f241ef4b8b61f196c3b29",
        # Immutable v0.9.2 obstacle-aware routing release (same source tree).
        "d90e6caa07fc109febcd213d3ad212a6a42bc5a4",
        # Immutable v0.9.3 whitespace-corridor routing release.
        "6b87c723d8687f7751dfb3e67da2013a5781f75a",
        # Immutable v0.9.4 polygon-aware explicit-anchor release.
        "787b5cc0378f9dedaaee1d0dab49707c21c92804",
    }
    if data["tool_eng_docs_sha"] not in allowed_tool_eng_docs_producers:
        raise SystemExit(f"tool.eng-docs revision mismatch: {execution_id}")
    log_path = path.parent / data["log"]
    if not log_path.is_file() or log_path.stat().st_size == 0:
        raise SystemExit(f"producer execution log missing: {execution_id}")
    revisions[execution_id] = data["source_revision"]

assembled_source = (root / "bld/docs/source-sha.txt").read_text(encoding="utf-8").strip()
if assembled_source != revisions["docs-assemble"]:
    raise SystemExit("assembled source SHA does not match assemble producer evidence")

graph = json.loads((root / "bld/engineering-graph.json").read_text(encoding="utf-8"))
if graph.get("schema") != "brainboxemb.engineering-graph" or graph.get("schema_version") != 1:
    raise SystemExit("unexpected engineering graph evidence schema")
if graph.get("source_revision") != os.environ["SOURCE_REVISION"]:
    raise SystemExit("engineering graph evidence revision mismatch")
if graph.get("source_graph") != {
    "kind": "sphinx-needs",
    "project": "Event timing engineering graph",
    "version": "migration-013",
}:
    raise SystemExit("unexpected Sphinx-Needs graph provenance")
actual_ids = {item["id"] for item in graph["objects"]}
if graph.get("object_count") != len(actual_ids):
    raise SystemExit("engineering graph object count mismatch")
if graph.get("relation_count") != len(graph["relations"]):
    raise SystemExit("engineering graph relation count mismatch")
objects = {item["id"]: item for item in graph["objects"]}
diagram_ids = {
    object_id for object_id, item in objects.items() if item.get("diagram_refs")
}
if not diagram_ids:
    raise SystemExit("engineering graph contains no diagram-linked architecture objects")
needs = json.loads((root / "bld/sphinx-needs/needs/needs.json").read_text(encoding="utf-8"))
current = needs.get("current_version")
if set(needs["versions"][current]["needs"]) != actual_ids:
    raise SystemExit("Sphinx-Needs object set does not match normalized graph")

materialization = json.loads(
    (root / ".moon/invocations/software_docs.assemble/materialization.json").read_text(encoding="utf-8")
)
if materialization.get("task") != "software:docs.assemble":
    raise SystemExit("materialization task mismatch")
if materialization.get("source_revision") != os.environ["SOURCE_REVISION"]:
    raise SystemExit("current materialization revision mismatch")
if materialization.get("status") != "success" or materialization.get("exit_code") != 0:
    raise SystemExit("current materialization failed")
if materialization.get("tool_git_project_version") != "0.2.4":
    raise SystemExit("unexpected tool.git-project materialization version")
PY
