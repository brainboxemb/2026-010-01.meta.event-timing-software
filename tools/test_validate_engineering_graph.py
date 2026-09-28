#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path

VALIDATOR = Path(__file__).with_name("validate_engineering_graph.py")

def run_case(docs, diagrams="", source_revision=None, output=False):
    with tempfile.TemporaryDirectory() as td:
        root=Path(td)
        d=root/"docs"; g=root/"diagrams"
        d.mkdir(); g.mkdir()
        for name,content in docs.items():
            (d/name).write_text(content,encoding="utf-8")
        if diagrams:
            (g/"diagram.yaml").write_text(diagrams,encoding="utf-8")
        command=[sys.executable,str(VALIDATOR),"--docs",str(d),"--diagrams",str(g)]
        out=root/"graph.json"
        if source_revision:
            command += ["--source-revision",source_revision]
        if output:
            command += ["--output",str(out)]
        result=subprocess.run(command,text=True,capture_output=True)
        graph=json.loads(out.read_text(encoding="utf-8")) if output and out.is_file() else None
        return result,graph

valid,graph=run_case(
    {"a.md": '<a id="REQ-1"></a>\n**REQ-1 — Example**\n\n<!-- eng {"type":"requirement","relations":{"allocated_to":["NodeA"]}} -->\n'},
    "nodes:\n  - id: node-a\n    object_id: NodeA\n",
    source_revision="example-revision",
    output=True,
)
assert valid.returncode == 0, valid.stderr
assert graph["schema"] == "brainboxemb.engineering-graph-canary"
assert graph["schema_version"] == 1
assert graph["source_revision"] == "example-revision"
assert graph["object_count"] == 2
assert graph["relation_count"] == 1

duplicate,_=run_case({
    "a.md": '<a id="REQ-1"></a>\n<!-- eng {"type":"requirement"} -->\n',
    "b.md": '<a id="REQ-1"></a>\n<!-- eng {"type":"requirement"} -->\n',
})
assert duplicate.returncode != 0 and "duplicate engineering id REQ-1" in duplicate.stderr + duplicate.stdout

unknown,_=run_case({
    "a.md": '<a id="REQ-1"></a>\n<!-- eng {"type":"requirement","relations":{"allocated_to":["Missing"]}} -->\n',
})
assert unknown.returncode != 0 and "unknown allocated_to target Missing" in unknown.stderr + unknown.stdout

print("engineering graph validator negative cases: green")
