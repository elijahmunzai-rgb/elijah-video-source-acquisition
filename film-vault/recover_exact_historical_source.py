#!/usr/bin/env python3
"""Reconstruct exact original snapshot from a surviving fork, read-only audit only.
The third-party project's license forbids broad redistribution of its materials.
Do not upload, vendor, redistribute, or execute fetched upstream code.
"""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from datetime import datetime, timezone

ORIGINAL="Miftahul-Islam-Efaz/Motion-graphics-skill"
MIRROR="mysticalsin/Motion-graphics-skill"
REVISION="4fe427bcda356b8a53ce65705eecced2e10be572"
TREE="fe56211a50c8123afc42efc87a9659730c8ddd52"
HISTORICAL={
  "README.md":"e4fe71aca318ad35c1c293c1cc101d5f09cf49133767823f43a77a32bd280f6e",
  "skills/motion-video-director/SKILL.md":"31b74d14701d3d98ef40ddec8416168cb912f6a4cc4e60b335add0c03849dc61",
  "LICENSE.md":"45b2cf4e6db8a71c2bd8b66915dd8e3a17ceae327f00d163dc36ddb8e2eacd45"
}

def cmd(args, cwd=None, timeout=420):
    env=os.environ.copy()
    env["GIT_TERMINAL_PROMPT"]="0"
    env["GIT_LFS_SKIP_SMUDGE"]="1"
    r=subprocess.run(args,cwd=cwd,check=True,timeout=timeout,
                     capture_output=True,text=True,env=env)
    return r.stdout.strip()

def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for data in iter(lambda:f.read(1048576),b""):
            h.update(data)
    return h.hexdigest()

def audit():
    with tempfile.TemporaryDirectory(prefix="elijah-historical-318-") as scratch:
        root=Path(scratch)/"source"
        cmd(["git","-c","protocol.file.allow=never","clone","--no-checkout",
             f"https://github.com/{MIRROR}.git",str(root)],timeout=1200)
        cmd(["git","checkout","--detach",REVISION],cwd=root)
        cmd(["git","-c","protocol.file.allow=never","submodule","update","--init","--recursive"],cwd=root,timeout=1200)
        if cmd(["git","rev-parse","HEAD"],cwd=root)!=REVISION:raise RuntimeError("Historical commit mismatch")
        if cmd(["git","rev-parse","HEAD^{tree}"],cwd=root)!=TREE:raise RuntimeError("Historical Git tree hash mismatch")
        # Explicitly avoid dynamic code execution or credential injection from upstream.
        if any("filter=lfs" in x.read_text(errors="replace") for x in root.rglob(".gitattributes") if ".git" not in x.parts):
            cmd(["git","lfs","pull"],cwd=root,timeout=1200)
        check={p:sha256(root/p) for p in HISTORICAL}
        if check!=HISTORICAL:
            raise RuntimeError("Original file SHA256 mismatch: expected pinned evidence")
        stream=subprocess.check_output(["git","ls-files","-z"],cwd=root)
        names=[os.fsdecode(x) for x in stream.split(b"\0") if x]
        files=[]; total_bytes=0
        for rel in names:
            p=root/rel
            if p.is_symlink():
                raise RuntimeError(f"Unexpected symlink in exact snapshot: {rel}")
            if not p.is_file():
                raise RuntimeError(f"Missing original tracked source file: {rel}")
            with p.open("rb") as f:
                if f.read(60).startswith(b"version https://git-lfs.github.com/spec/v1"):
                    raise RuntimeError(f"Unresolved LFS pointer: {rel}")
            size=p.stat().st_size
            total_bytes+=size
            files.append({"path":rel,"bytes":size,"sha256":sha256(p)})
        if len(files)<3:raise RuntimeError("Unexpectedly incomplete original source")
        return {
          "status":"verified_historical_original_snapshot",
          "original_repository":ORIGINAL,
          "original_repository_available":False,
          "recovery_mirror":MIRROR,
          "recovery_method":"surviving_git_fork_exact_historical_commit_and_tree",
          "commit":REVISION,"tree":TREE,
          "verified_historical_sha256":check,
          "file_count":len(files),
          "total_tracked_bytes":total_bytes,
          "original_file_inventory":files,
          "rights":"original_source_studied_and_verified; no copying into public repository or upload artifact",
          "verified_at":datetime.now(timezone.utc).isoformat()
        }

if __name__=="__main__":
    out=Path(sys.argv[1] if len(sys.argv)>1 else "recovery-audit.json")
    out.parent.mkdir(parents=True,exist_ok=True)
    data=audit()
    out.write_text(json.dumps(data,indent=2,ensure_ascii=False),encoding="utf8")
    print(json.dumps({k:v for k,v in data.items() if k not in ("original_file_inventory","verified_historical_sha256")},indent=2))
