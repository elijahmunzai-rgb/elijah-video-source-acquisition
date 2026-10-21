#!/usr/bin/env python3
"""Elijah Film Studio: fail-closed full-source acquisition, no upstream execution."""
import argparse, concurrent.futures, hashlib, json, os, pathlib, re, shutil, subprocess, time, urllib.request
from datetime import datetime, timezone

COMMIT="ffdf99cbc7879f611abba186e933695904cd638f"
URL=f"https://raw.githubusercontent.com/zhuyansen/awesome-claude-video-skills/{COMMIT}/data/skills.json"
EXPECTED=318
REPO=re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
POINTER=b"version https://git-lfs.github.com/spec/v1\n"

def sh(argv,cwd=None,timeout=1200):
    env=os.environ.copy()
    env.update(GIT_TERMINAL_PROMPT="0",GIT_LFS_SKIP_SMUDGE="1")
    p=subprocess.run(argv,cwd=cwd,env=env,encoding="utf8",errors="replace",capture_output=True,timeout=timeout)
    if p.returncode:
        raise RuntimeError(f"{argv[0:4]} exit={p.returncode}: {(p.stderr or p.stdout)[-1000:]}")
    return p.stdout.strip()

def digest(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""):h.update(b)
    return h.hexdigest()

def manifest():
    req=urllib.request.Request(URL,headers={"User-Agent":"ElijahFilmStudio/20261021"})
    with urllib.request.urlopen(req,timeout=65) as r:raw=r.read()
    obj=json.loads(raw); rows=obj["skills"]
    names=[r["repo_full_name"] for r in rows]
    if len(rows)!=EXPECTED or len(set(names))!=EXPECTED or any(not REPO.fullmatch(n) for n in names):
        raise ValueError("Frozen source manifest must have 318 unique valid repositories")
    return raw,rows

def check_files(root):
    staged=sh(["git","ls-files","--stage"],cwd=root)
    subs={line.split("\t",1)[1] for line in staged.splitlines() if line.startswith("160000 ")}
    tracked=subprocess.run(["git","ls-files","-z"],cwd=root,capture_output=True,check=True).stdout
    results=[]
    for relbytes in tracked.split(b"\0"):
        if not relbytes:continue
        rel=os.fsdecode(relbytes)
        f=root/rel
        if rel in subs:
            if not f.is_dir() or not (f/".git").exists():raise RuntimeError("Missing submodule: "+rel)
            child=check_files(f)
            results.append({"path":rel,"type":"submodule","head":sh(["git","rev-parse","HEAD"],cwd=f),"files":child})
        elif f.is_symlink():
            results.append({"path":rel,"type":"symlink","target":os.readlink(f)})
        elif f.is_file():
            with f.open("rb") as stream:hdr=stream.read(140)
            if hdr.startswith(POINTER):raise RuntimeError("Unresolved LFS pointer: "+rel)
            results.append({"path":rel,"type":"file","bytes":f.stat().st_size,"sha256":digest(f)})
        else:raise RuntimeError("Missing tracked source: "+rel)
    return results

def one(entry,out,retries):
    name=entry["repo_full_name"];owner,repo=name.split("/")
    root=out/"checkouts"/owner/repo
    root.parent.mkdir(parents=True,exist_ok=True)
    record={"repo":name,"kind":entry.get("kind"),"license_listed":entry.get("license"),"status":"failed"}
    for attempt in range(1,retries+1):
        try:
            if not (root/".git").exists():
                shutil.rmtree(root,ignore_errors=True)
                sh(["git","-c","protocol.file.allow=never","clone","--depth","1","--recurse-submodules","--shallow-submodules",f"https://github.com/{name}.git",str(root)],timeout=1800)
            sh(["git","-c","protocol.file.allow=never","submodule","update","--init","--recursive","--depth","1"],cwd=root,timeout=1800)
            allattrs=[f for f in root.rglob(".gitattributes") if "/.git/" not in str(f)]
            lfs=any("filter=lfs" in f.read_text(encoding="utf8",errors="replace") for f in allattrs)
            if lfs:
                sh(["git","lfs","pull"],cwd=root,timeout=1800)
                for subgit in root.rglob(".git"):
                    if subgit!=root/".git":sh(["git","lfs","pull"],cwd=subgit.parent,timeout=1800)
            files=check_files(root)
            tracked=sum(1 for f in files if f["type"]=="file")
            inv=out/"inventories"/owner/(repo+".json")
            inv.parent.mkdir(parents=True,exist_ok=True)
            commit=sh(["git","rev-parse","HEAD"],cwd=root)
            inv.write_text(json.dumps({"repository":name,"commit":commit,"files":files},ensure_ascii=False),encoding="utf8")
            record.update(status="verified",commit=commit,file_count=tracked,uses_lfs=lfs)
            record.pop("error",None)
            return record
        except Exception as exc:
            record.update(error=f"{type(exc).__name__}: {str(exc)[:850]}",attempt=attempt)
            time.sleep(min(25,attempt*4))
    return record

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--shard-index",type=int,default=0)
    ap.add_argument("--shard-count",type=int,default=10)
    ap.add_argument("--workers",type=int,default=2)
    ap.add_argument("--retries",type=int,default=4)
    ap.add_argument("--output",default="output")
    a=ap.parse_args()
    if a.shard_count<1 or a.shard_index not in range(a.shard_count):raise ValueError("bad shard")
    out=pathlib.Path(a.output);out.mkdir(parents=True,exist_ok=True)
    raw,allitems=manifest()
    (out/"manifest.frozen.json").write_bytes(raw)
    items=[r for i,r in enumerate(allitems) if i%a.shard_count==a.shard_index]
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,min(3,a.workers))) as pool:
        tasks={pool.submit(one,r,out,a.retries):r for r in items}
        for done in concurrent.futures.as_completed(tasks):
            try:r=done.result()
            except Exception as ex:r={"repo":tasks[done]["repo_full_name"],"status":"failed","error":str(ex)}
            results.append(r)
            (out/"results.json").write_text(json.dumps(sorted(results,key=lambda x:x["repo"]),indent=2),encoding="utf8")
            print(f"{len(results)}/{len(items)} {r['status']}: {r['repo']}",flush=True)
    passed=sum(r["status"]=="verified" for r in results)
    verdict={"expected_global":318,"expected_shard":len(items),"verified_shard":passed,
             "failed_shard":len(items)-passed,"complete_shard":passed==len(items),
             "run_utc":datetime.now(timezone.utc).isoformat(),"index_sha256":hashlib.sha256(raw).hexdigest()}
    (out/"summary.json").write_text(json.dumps(verdict,indent=2),encoding="utf8")
    if passed!=len(items):raise SystemExit(2)

if __name__=="__main__":main()
