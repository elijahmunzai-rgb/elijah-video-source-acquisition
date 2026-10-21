#!/usr/bin/env python3
"""Audit independently-produced GitHub Actions results for a frozen 318-repo source vault.

Does not declare success based on filenames, zip counts or shard job exit status.
Requires coverage of all 318 expected repositories, unique per repo, and an
explicit verified result for each. The manifest is pinned and validated.
"""
import argparse
import hashlib
import json
from pathlib import Path
from import_verified_sources import manifest, EXPECTED


def combine(expected_manifest, results_paths):
    original, entries=manifest(expected_manifest)
    expected={e['repo_full_name'] for e in entries}
    observed={}
    dupes=[]
    for p in results_paths:
        data=json.loads(Path(p).read_text(encoding='utf-8'))
        if not isinstance(data,list):
            raise ValueError(f'{p}: expected a list')
        for entry in data:
            repo=entry.get('repo')
            if repo in observed:
                dupes.append(repo)
            else:
                observed[repo]=entry
    missing=sorted(expected-set(observed))
    extra=sorted(set(observed)-expected)
    failures=sorted(r for r in expected.intersection(observed) if observed[r].get('status')!='verified' or not observed[r].get('commit') or not observed[r].get('tree') or not isinstance(observed[r].get('files'),int))
    success=not (missing or extra or dupes or failures) and len(observed)==EXPECTED
    return {'expected':EXPECTED,'indexed':len(entries),'verified':sum(1 for r in expected if r in observed and observed[r].get('status')=='verified' and bool(observed[r].get('commit')) and bool(observed[r].get('tree'))),'complete_318':success,'missing':missing,'failed_or_unverifiable':failures,'unexpected':extra,'duplicate_entries':sorted(set(dupes)),'manifest_sha256':hashlib.sha256(original).hexdigest()}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--manifest',required=True)
    ap.add_argument('--results',required=True,nargs='+')
    ap.add_argument('--output',required=True)
    args=ap.parse_args()
    report=combine(args.manifest,args.results)
    Path(args.output).write_text(json.dumps(report,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if not isinstance(v,list)},indent=2))
    if not report['complete_318']:
        raise SystemExit(2)

if __name__=='__main__': main()
