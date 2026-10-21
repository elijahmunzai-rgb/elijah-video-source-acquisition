#!/usr/bin/env python3
"""Strict 318 static source audit: never claim 318 runtime installs."""
import glob,json,collections,sys
from pathlib import Path
files=sorted(glob.glob("audit/catalog-*/catalog.json"))
data=[json.loads(Path(f).read_text()) for f in files]
rows=sum((d["rows"] for d in data),[])
names=[x["original"] for x in rows]
bad=[x["original"] for x in rows if x["status"]!="static_tree_complete"]
ok=len(files)==10 and len(rows)==318 and len(set(names))==318 and not bad
result={"original_sources":318,"static_source_trees_inspected":sum(x["status"]=="static_tree_complete" for x in rows),
        "total_records":len(rows),"unique":len(set(names)),"shards":len(files),"complete":ok,
        "identified_dependency_manifests":sum(x.get("install_manifests",0)>0 for x in rows),
        "with_code_files":sum(x.get("code_files",0)>0 for x in rows),
        "upstream_packages_installed_and_executed":0,
        "upstream_cinematic_quality_verified":0,
        "failures":bad,
        "notice":"Static file/manifest classification is not installation, safety approval, real model inference or Hollywood visual quality.",
        "entries":rows}
Path("audit/summary-318.json").write_text(json.dumps(result,indent=2))
print(json.dumps({k:v for k,v in result.items() if k!="entries"},indent=2))
if not ok:sys.exit(2)
