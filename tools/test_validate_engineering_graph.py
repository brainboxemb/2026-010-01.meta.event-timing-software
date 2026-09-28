#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path

VALIDATOR = Path(__file__).with_name("validate_engineering_graph.py")


def run_case(docs, diagrams="", source_revision=None, output=False, review=False):
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        d = root / "docs"
        g = root / "diagrams"
        d.mkdir()
        g.mkdir()
        for name, content in docs.items():
            (d / name).write_text(content, encoding="utf-8")
        if diagrams:
            (g / "diagram.yaml").write_text(diagrams, encoding="utf-8")

        command = [
            sys.executable,
            str(VALIDATOR),
            "--docs",
            str(d),
            "--diagrams",
            str(g),
        ]
        out = root / "graph.json"
        review_path = root / "review.md"
        if source_revision:
            command += ["--source-revision", source_revision]
        if output:
            command += ["--output", str(out)]
        if review:
            command += ["--review-output", str(review_path)]

        result = subprocess.run(command, text=True, capture_output=True)
        graph = json.loads(out.read_text(encoding="utf-8")) if output and out.is_file() else None
        review_text = review_path.read_text(encoding="utf-8") if review and review_path.is_file() else None
        return result, graph, review_text


valid, graph, review = run_case(
    {
        "requirements.md":
            '<a id="REQ-1"></a>\n'
            '**REQ-1 — Example**\n\n'
            '<!-- eng {"type":"requirement","relations":{"derived_from":["UC-1"]}} -->\n'
            '<a id="UC-1"></a>\n'
            '## UC-1 — Source\n\n'
            '<!-- eng {"type":"use-case"} -->\n',
        "design.md":
            '<!-- eng-rel {"id":"NodeA","relations":{"satisfies":["REQ-1"]}} -->\n'
            '<a id="VC-1"></a>\n'
            '## VC-1 — Verification\n\n'
            '<!-- eng {"type":"verification-case","relations":{"verifies":["REQ-1"]}} -->\n',
    },
    "nodes:\n  - id: node-a\n    object_id: NodeA\n",
    source_revision="example-revision",
    output=True,
    review=True,
)
assert valid.returncode == 0, valid.stderr
assert graph["schema"] == "brainboxemb.engineering-graph-canary"
assert graph["schema_version"] == 1
assert graph["source_revision"] == "example-revision"
assert graph["object_count"] == 4
assert graph["relation_count"] == 3
assert "eng-rel" in review
assert "satisfies -> **REQ-1**" in review
assert "satisfies <- **NodeA**" in review
assert "verifies <- **VC-1**" in review

duplicate, _, _ = run_case({
    "a.md": '<a id="REQ-1"></a>\n<!-- eng {"type":"requirement"} -->\n',
    "b.md": '<a id="REQ-1"></a>\n<!-- eng {"type":"requirement"} -->\n',
})
assert duplicate.returncode != 0 and "duplicate engineering id REQ-1" in duplicate.stderr + duplicate.stdout

unknown_target, _, _ = run_case({
    "a.md":
        '<a id="REQ-1"></a>\n'
        '<!-- eng {"type":"requirement","relations":{"derived_from":["Missing"]}} -->\n',
})
assert unknown_target.returncode != 0 and "unknown derived_from target Missing" in unknown_target.stderr + unknown_target.stdout

unknown_owner, _, _ = run_case({
    "a.md": '<!-- eng-rel {"id":"MissingDesign","relations":{"satisfies":[]}} -->\n',
})
assert unknown_owner.returncode != 0 and "eng-rel owner does not exist: MissingDesign" in unknown_owner.stderr + unknown_owner.stdout

print("engineering graph validator qualification cases: green")
