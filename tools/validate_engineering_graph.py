#!/usr/bin/env python3
import argparse, json, re
from pathlib import Path

ENG_RE = re.compile(r'<!-- eng (\{.*\}) -->')
ANCHOR_RE = re.compile(r'<a id="([^"]+)"></a>')
OBJECT_ID_RE = re.compile(r'^\s*object_id:\s*([^#\s]+)\s*$', re.M)

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--docs", default="docs")
    p.add_argument("--diagrams", default="docs/_diagrams")
    p.add_argument("--output")
    p.add_argument("--source-revision")
    a=p.parse_args()
    objects={}
    relations=[]
    for path in sorted(Path(a.docs).glob("*.md")):
        lines=path.read_text(encoding="utf-8").splitlines()
        current=None
        for n,line in enumerate(lines,1):
            m=ANCHOR_RE.fullmatch(line.strip())
            if m: current=m.group(1)
            m=ENG_RE.fullmatch(line.strip())
            if not m: continue
            if not current:
                raise SystemExit(f"{path}:{n}: eng metadata requires a preceding stable anchor")
            try: meta=json.loads(m.group(1))
            except json.JSONDecodeError as e:
                raise SystemExit(f"{path}:{n}: invalid eng JSON: {e}")
            if current in objects:
                raise SystemExit(f"{path}:{n}: duplicate engineering id {current}")
            objects[current]={"id":current,"type":meta["type"],"source":f"{path}:{n}"}
            for kind,targets in meta.get("relations",{}).items():
                if not isinstance(targets,list) or not all(isinstance(x,str) and x for x in targets):
                    raise SystemExit(f"{path}:{n}: relation {kind} must be a list of ids")
                relations += [{"from":current,"type":kind,"to":t,"source":f"{path}:{n}"} for t in targets]
    for path in sorted(Path(a.diagrams).glob("*.yaml")):
        text=path.read_text(encoding="utf-8")
        for m in OBJECT_ID_RE.finditer(text):
            oid=m.group(1).strip('"\'')
            line=text[:m.start()].count("\n")+1
            if oid in objects:
                raise SystemExit(f"{path}:{line}: duplicate engineering id {oid}")
            objects[oid]={"id":oid,"type":"architecture-element","source":f"{path}:{line}"}
    for r in relations:
        if r["to"] not in objects:
            raise SystemExit(f'{r["source"]}: unknown {r["type"]} target {r["to"]}')
    graph={
        "schema":"brainboxemb.engineering-graph-canary",
        "schema_version":1,
        "source_revision":a.source_revision,
        "object_count":len(objects),
        "relation_count":len(relations),
        "objects":[objects[k] for k in sorted(objects)],
        "relations":relations,
    }
    if a.output:
        out=Path(a.output); out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(graph,indent=2)+"\n",encoding="utf-8")
    print(f"engineering graph: {len(objects)} objects, {len(relations)} relations")

if __name__=="__main__": main()
