#!/usr/bin/env python3
"""Read-only metadata audit, not execution or dependency installation."""
import argparse,concurrent.futures,json,os,re,time,urllib.request
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--shard",type=int,required=True);p.add_argument("--out",required=True);args=p.parse_args()
head={"User-Agent":"ElijahFilmStudio/static-audit","Accept":"application/vnd.github+json"}
if os.getenv("GITHUB_TOKEN"):head["Authorization"]="Bearer "+os.environ["GITHUB_TOKEN"]
def req(url):
    last=None
    for i in range(4):
        try:
            with urllib.request.urlopen(urllib.request.Request(url,headers=head),timeout=35) as r:return json.load(r)
        except Exception as e:
            last=e;time.sleep((i+1)*2)
    raise RuntimeError(str(last))
manifest=json.loads((Path(__file__).parent/"pinned-original-318.json").read_text())["skills"]
assert len(manifest)==318 and len({x["repo_full_name"] for x in manifest})==318
def inspect(x):
    original=x["repo_full_name"];repo="mysticalsin/Motion-graphics-skill" if original=="Miftahul-Islam-Efaz/Motion-graphics-skill" else original
    out={"original":original,"source":repo,"status":"failed","runtime_installed":False,"runtime_executed":False,"hollywood_quality_verified":False}
    try:
        metadata=req(f"https://api.github.com/repos/{repo}")
        ref="4fe427bcda356b8a53ce65705eecced2e10be572" if repo!=original else metadata["default_branch"]
        tree=req(f"https://api.github.com/repos/{repo}/git/trees/{ref}?recursive=1")
        if tree.get("truncated"):raise ValueError("Git tree truncated")
        files=[y["path"] for y in tree.get("tree",[]) if y["type"]=="blob"]
        if not files:raise ValueError("no source files")
        code=[y for y in files if Path(y).suffix.lower() in {".py",".ts",".tsx",".js",".mjs",".sh",".rs",".cpp",".c",".go"}]
        manifestfiles=[y for y in files if Path(y).name.lower() in {"package.json","pyproject.toml","requirements.txt","setup.py","cargo.toml","dockerfile","cmakelists.txt"}]
        testfiles=[y for y in files if re.search(r"(^|/)(tests?/|test_|.+\.test\.)",y)]
        out.update(status="static_tree_complete",files=len(files),code_files=len(code),install_manifests=len(manifestfiles),manifest_names=manifestfiles[:20],tests=len(testfiles),skill_docs=sum(y.endswith("/SKILL.md") or y=="SKILL.md" for y in files),
                   license=(metadata.get("license") or {}).get("spdx_id"),
                   probable_runtime="node" if any(z.endswith("package.json") for z in manifestfiles) else "python" if any(z.endswith(("requirements.txt","pyproject.toml","setup.py")) for z in manifestfiles) else "other",
                   attempted_install=False,executed_performance_benchmark=False)
    except Exception as e:out["error"]=str(e)[:300]
    return out
items=[x for i,x in enumerate(manifest) if i%10==args.shard]
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:rows=list(pool.map(inspect,items))
Path(args.out).write_text(json.dumps({"shard":args.shard,"rows":rows},indent=2))
for x in rows:print(x["original"],x["status"],flush=True)
if any(x["status"]!="static_tree_complete" for x in rows):raise SystemExit(2)
