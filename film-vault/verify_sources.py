#!/usr/bin/env python3
"""Aggregate shard results; 318/318 only when original source manifests match."""
import argparse,glob,hashlib,json,pathlib,sys
p=argparse.ArgumentParser()
p.add_argument("directory")
a=p.parse_args()
base=pathlib.Path(a.directory)
sources=sorted(base.glob("source-shard-*/output/results.json"))
manifests=sorted(base.glob("source-shard-*/output/manifest.frozen.json"))
if len(sources)!=10 or len(manifests)!=10:
    print(json.dumps({"expected":318,"complete":False,"error":"10 result files and 10 manifests required","results":len(sources),"manifests":len(manifests)}))
    sys.exit(2)
raw=[f.read_bytes() for f in manifests]
fingerprints=[hashlib.sha256(b).hexdigest() for b in raw]
if len(set(fingerprints))!=1:
    print(json.dumps({"expected":318,"complete":False,"error":"Shard source manifests differ"}))
    sys.exit(2)
expected=[x["repo_full_name"] for x in json.loads(raw[0])["skills"]]
rows=sum((json.loads(f.read_text()) for f in sources),[])
names=[r["repo"] for r in rows]
verified=[r["repo"] for r in rows if r["status"]=="verified"]
missing=sorted(set(expected)-set(verified))
unexpected=sorted(set(names)-set(expected))
duplicates=sorted({name for name in names if names.count(name)>1})
failures=[{"repo":r.get("repo"),"error":r.get("error")} for r in rows if r.get("status")!="verified"]
complete=len(rows)==318 and len(expected)==318 and len(verified)==318 and not(missing or unexpected or duplicates or failures)
report={"expected":318,"received":len(rows),"verified":len(verified),"missing":missing,"unexpected":unexpected,
        "duplicates":duplicates,"failed":failures,"complete":complete,"manifest_sha256":fingerprints[0]}
out=base/"FINAL_VERDICT.json"
out.write_text(json.dumps(report,indent=2),encoding="utf8")
print(json.dumps({k:v if not isinstance(v,list) else len(v) for k,v in report.items()},indent=2))
sys.exit(0 if complete else 2)
