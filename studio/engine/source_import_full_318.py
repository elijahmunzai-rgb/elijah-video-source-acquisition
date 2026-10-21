#!/usr/bin/env python3
"""Acquire all code, submodules, and LFS assets for a frozen 318-repository manifest.

No source code is executed. Strictly fail closed: NEVER say 318/318 unless every
repository has been acquired and its checked-out files individually audited.
Requires git, Python >=3.10, optionally git-lfs for repositories that use LFS.
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import time
from datetime import datetime, timezone
from urllib.request import Request, urlopen

FROZEN_COMMIT = 'ffdf99cbc7879f611abba186e933695904cd638f'
MANIFEST_URL = f'https://raw.githubusercontent.com/zhuyansen/awesome-claude-video-skills/{FROZEN_COMMIT}/data/skills.json'
EXPECTED = 318
REPO_RE = re.compile(r'^[a-zA-Z0-9_.-]+/[a-zA-Z0-9_.-]+$')
POINTER_RE = re.compile(rb'^version https://git-lfs.github.com/spec/v1\n')


def cmd(args, cwd=None, timeout=1200):
    p = subprocess.run(args, cwd=cwd, env={**os.environ, 'GIT_TERMINAL_PROMPT':'0', 'GIT_LFS_SKIP_SMUDGE':'1', 'GIT_CONFIG_NOSYSTEM':'1'},
                       capture_output=True, timeout=timeout, text=True)
    if p.returncode:
        raise RuntimeError(f"{' '.join(map(str,args[:6]))}: {p.stderr[-1400:] or p.stdout[-700:]}")
    return p.stdout.strip()


def manifest(path):
    if path:
        data=Path(path).read_bytes()
    else:
        with urlopen(Request(MANIFEST_URL,headers={'User-Agent':'ElijahFilmStudio-Auditor/2'}),timeout=40) as r:
            data=r.read()
    src=json.loads(data)
    items=src.get('skills')
    if not isinstance(items,list) or len(items)!=EXPECTED:
        raise ValueError(f'Expected exactly {EXPECTED} index entries, received {len(items) if isinstance(items,list) else "invalid"}')
    names=[it.get('repo_full_name') for it in items]
    if len(set(names))!=EXPECTED or any(not isinstance(n,str) or not REPO_RE.fullmatch(n) for n in names):
        raise ValueError('Duplicate or malformed repo names in frozen manifest')
    return data,items


def file_hash(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def audit_checkout(root):
    tracked=cmd(['git','ls-files','--cached','-z'],cwd=root).split('\x00')
    stage=cmd(['git','ls-files','--stage'],cwd=root)
    submodule_paths={line.split('\t',1)[1] for line in stage.splitlines() if line.startswith('160000 ')}
    inventory=[]
    for rel in tracked:
        if not rel:continue
        path=root/rel
        if rel in submodule_paths:
            if not path.is_dir() or not (path/'.git').exists():
                raise RuntimeError(f'Submodule is missing: {rel}')
            commit=cmd(['git','rev-parse','HEAD'],cwd=path)
            child=audit_checkout(path)
            inventory.append({'path':rel,'type':'submodule','commit':commit,'files':child['files'],'file_count':child['file_count']})
        elif path.is_symlink():
            inventory.append({'path':rel,'type':'symlink','target':os.readlink(path)})
        elif path.is_file():
            with path.open('rb') as fp:
                data_head=fp.read(128)
            if POINTER_RE.match(data_head):
                raise RuntimeError(f'Unresolved Git LFS pointer: {rel}')
            inventory.append({'path':rel,'type':'file','bytes':path.stat().st_size,'sha256':file_hash(path)})
        else:
            raise RuntimeError(f'Tracked source missing: {rel}')
    return {'file_count':sum(1 if x['type']!='submodule' else x['file_count'] for x in inventory), 'files':inventory}


def acquire(item, target, retries=3):
    repo=item['repo_full_name']
    owner,name=repo.split('/')
    dest=Path(target)/'checkouts'/owner/name
    dest.parent.mkdir(parents=True,exist_ok=True)
    record={'repo':repo,'kind':item.get('kind'),'license_listed':item.get('license'),'status':'failed'}
    for attempt in range(1,retries+1):
        try:
            if not (dest/'.git').exists():
                shutil.rmtree(dest,ignore_errors=True)
                try:
                    cmd(['git','-c','protocol.file.allow=never','clone','--depth','1','--recurse-submodules','--shallow-submodules',f'https://github.com/{repo}.git',str(dest)],timeout=1500)
                except Exception:
                    shutil.rmtree(dest,ignore_errors=True)
                    cmd(['git','-c','protocol.file.allow=never','clone','--recurse-submodules',f'https://github.com/{repo}.git',str(dest)],timeout=1500)
            # Explicitly verify recursively populated submodules; does not execute their code.
            cmd(['git','-c','protocol.file.allow=never','submodule','update','--init','--recursive','--depth','1'],cwd=dest,timeout=1500)
            allattrs=list(dest.rglob('.gitattributes'))
            uses_lfs=any('filter=lfs' in p.read_text(encoding='utf-8',errors='replace') for p in allattrs if '.git/' not in str(p))
            if uses_lfs:
                if shutil.which('git') is None:
                    raise RuntimeError('git must be installed')
                cmd(['git','lfs','version'],cwd=dest,timeout=60)
                cmd(['git','lfs','pull'],cwd=dest,timeout=1500)
                git_submodules=[x for x in dest.rglob('.git') if x!=dest/'.git']
                for git_meta in git_submodules:
                    cmd(['git','lfs','pull'],cwd=git_meta.parent,timeout=1500)
            commit=cmd(['git','rev-parse','HEAD'],cwd=dest)
            tree=cmd(['git','rev-parse','HEAD^{tree}'],cwd=dest)
            audit=audit_checkout(dest)
            audit_file=Path(target)/'inventories'/owner/f'{name}.json'
            audit_file.parent.mkdir(parents=True,exist_ok=True)
            audit_file.write_text(json.dumps({'repo':repo,'commit':commit,'tree':tree,**audit},ensure_ascii=False,indent=2),encoding='utf-8')
            record.update(status='verified',commit=commit,tree=tree,files=audit['file_count'],inventory=str(audit_file),lfs=uses_lfs)
            return record
        except Exception as e:
            record['error']=f'{type(e).__name__}: {e}'[:1600]
            if attempt<retries:time.sleep(attempt*3)
    return record


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--manifest',default=None)
    p.add_argument('--output',default='verified-video-sources')
    p.add_argument('--shard-index',type=int,default=0)
    p.add_argument('--shard-count',type=int,default=1)
    p.add_argument('--workers',type=int,default=2)
    p.add_argument('--retries',type=int,default=3)
    p.add_argument('--dry-run',action='store_true')
    args=p.parse_args()
    if args.shard_count<1 or not 0<=args.shard_index<args.shard_count:raise ValueError('Invalid shard index/count')
    data,items=manifest(args.manifest)
    dest=Path(args.output)
    dest.mkdir(parents=True,exist_ok=True)
    (dest/'manifest.frozen.json').write_bytes(data)
    selected=[it for i,it in enumerate(items) if i%args.shard_count==args.shard_index]
    if args.dry_run:
        print(json.dumps({'index_sha256':hashlib.sha256(data).hexdigest(),'total':len(items),'selected':len(selected),'shard':args.shard_index,'shard_count':args.shard_count}));return
    results=[]
    with concurrent.futures.ThreadPoolExecutor(max_workers=min(4,max(1,args.workers))) as pool:
        for result in concurrent.futures.as_completed([pool.submit(acquire,it,dest,args.retries) for it in selected]):
            info=result.result()
            results.append(info)
            (dest/'results.json').write_text(json.dumps(sorted(results,key=lambda x:x['repo']),indent=2),encoding='utf-8')
            print(f"{len(results)}/{len(selected)} {info['status']} {info['repo']}",flush=True)
    success=sum(x['status']=='verified' for x in results)
    report={'expected_global':EXPECTED,'expected_shard':len(selected),'verified_shard':success,'failed_shard':len(selected)-success,
            'complete_shard':success==len(selected),'complete_all_318':success==EXPECTED and args.shard_count==1,
            'generated_utc':datetime.now(timezone.utc).isoformat(),'index_sha256':hashlib.sha256(data).hexdigest()}
    (dest/'summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report,indent=2))
    if not report['complete_shard']:raise SystemExit(2)

if __name__=='__main__':main()
