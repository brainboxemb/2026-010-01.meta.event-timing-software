#!/usr/bin/env bash
# Stage the validated, generated documentation and traceability evidence for
# publication on the PR preview or production docs branch.
# Input: bld/docs, bld/sphinx-needs and bld/engineering-portal, already built.
# Output: RUNNER_TEMP/software-docs-publication; never edits authored docs.
set -euo pipefail

: "${SOURCE_REVISION:?SOURCE_REVISION must be set}"
: "${RUNNER_TEMP:?RUNNER_TEMP must be set}"

staging="${RUNNER_TEMP}/software-docs-publication"
rm -rf "${staging}"
mkdir -p   "${staging}/orchestration"   "${staging}/evidence/traceability/native"   "${staging}/evidence/traceability/input"   "${staging}/evidence/portal"

cp -a bld/docs/. "${staging}/"
cp bld/engineering-graph.json "${staging}/evidence/traceability/engineering-graph.json"
cp bld/engineering-graph-review.md "${staging}/evidence/traceability/review.md"
cp bld/sphinx-needs/needs/needs.json "${staging}/evidence/traceability/needs.json"
cp -a bld/sphinx-needs/html/. "${staging}/evidence/traceability/native/"
cp docs/_sphinx-needs/conf.py "${staging}/evidence/traceability/input/conf.py"
cp docs/_sphinx-needs/schemas.json "${staging}/evidence/traceability/input/schemas.json"
cp docs/_sphinx-needs/requirements.txt "${staging}/evidence/traceability/input/requirements.txt"

cat > "${staging}/evidence/traceability/README.md" <<EOF
# Engineering graph review evidence

This is Migration 013 native MyST/Sphinx-Needs production-canary evidence.

- source revision: ${SOURCE_REVISION}
- authoritative authoring: selected MyST/Sphinx-Needs objects in the event-timing engineering documents
- native Sphinx reader: [native/index.html](native/index.html)
- Sphinx-Needs export: [needs.json](needs.json)
- normalized human review: [review.md](review.md)
- normalized graph: [engineering-graph.json](engineering-graph.json)
- consumer-owned Needs configuration: [input/conf.py](input/conf.py) · [input/schemas.json](input/schemas.json)

Requirements own derived_from, design owns satisfies, and verification owns verifies.
Sphinx-Needs generates the inverse/backlink context. Diagram object_id values reference the same engineering objects.
EOF

cp .moon/invocations/software_docs.assemble/moon.log "${staging}/orchestration/moon.log"
cp .moon/invocations/software_docs.assemble/materialization.json "${staging}/orchestration/materialization.json"
cp -a bld/engineering-portal/site "${staging}/portal"
cp bld/engineering-portal/explorer-TimingNode.png "${staging}/evidence/portal/explorer-TimingNode.png"
cp bld/engineering-portal/workspace-IF05-REQ-007.png "${staging}/evidence/portal/workspace-IF05-REQ-007.png"
cp bld/engineering-portal/engineering-client-ui.png "${staging}/evidence/portal/engineering-client-ui.png"
cp bld/engineering-portal/docs/assets/provenance.json "${staging}/evidence/portal/provenance.json"
cp docs/_portal/mkdocs.yml "${staging}/evidence/portal/mkdocs.yml"
cp docs/_portal/requirements.txt "${staging}/evidence/portal/requirements.txt"
cp docs/_portal/hooks/engineering_workspace.py "${staging}/evidence/portal/engineering_workspace.py"
