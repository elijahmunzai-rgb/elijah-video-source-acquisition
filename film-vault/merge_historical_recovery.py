#!/usr/bin/env python3
"""Fail-closed merger of previously audited 317 unique source snapshots and
original historical commit recovered from its surviving fork.
"""
import json
from pathlib import Path
import sys

ORIGINAL="Miftahul-Islam-Efaz/Motion-graphics-skill"
SHA="4fe427bcda356b8a53ce65705eecced2e10be572"
TREE="fe56211a50c8123afc42efc87a9659730c8ddd52"

def verified_result(previous,recovery):
    assert previous["expected"]==318,previous
    assert previous["verified"]==317,previous
    assert len(previous["missing"])==1, previous["missing"]
    assert previous["missing"][0]==ORIGINAL,previous["missing"]
    assert len(previous["failed"])==1,previous["failed"]
    assert previous["failed"][0]["repo"]==ORIGINAL,previous["failed"]
    assert previous["unexpected"]==[],previous
    assert previous["duplicates"]==[],previous
    assert previous["complete"] is False,previous
    assert recovery["status"]=="verified_historical_original_snapshot",recovery
    assert recovery["original_repository"]==ORIGINAL,recovery
    assert recovery["recovery_mirror"]=="mysticalsin/Motion-graphics-skill",recovery
    assert recovery["commit"]==SHA,recovery
    assert recovery["tree"]==TREE,recovery
    assert len(recovery["original_file_inventory"])==recovery["file_count"],recovery
    assert recovery["file_count"]>=3,recovery
    inventory={x["path"]:x for x in recovery["original_file_inventory"]}
    for path,digest in recovery["verified_historical_sha256"].items():
        assert inventory[path]["sha256"]==digest, (path,digest)
    return {
        "expected_original_repositories":318,
        "verified_direct_original_sources":317,
        "recovered_original_snapshot_from_historical_fork":1,
        "verified_source_snapshots_total":318,
        "complete_318_historical_source_snapshots":True,
        "original_repository_currently_unavailable":ORIGINAL,
        "verified_fork_snapshot":{"mirror":recovery["recovery_mirror"],"commit":SHA,"tree":TREE,
          "file_count":recovery["file_count"],"total_tracked_bytes":recovery["total_tracked_bytes"],
          "license_note":"historical exact source retained in independent fork; no upstream redistribution in public studio"},
        "previous_audit_manifest_sha256":previous["manifest_sha256"],
        "historical_audit":"film-source-final-verdict from original run 39658143891",
        "scope":"Git tracked source, submodules and LFS; does NOT assert all 318 dependencies installed or film renderers tested",
    }

if __name__=="__main__":
    if len(sys.argv)!=4:raise SystemExit("usage: merge_historical_recovery.py previous.json recovery.json output.json")
    p=json.loads(Path(sys.argv[1]).read_text())
    r=json.loads(Path(sys.argv[2]).read_text())
    v=verified_result(p,r)
    Path(sys.argv[3]).write_text(json.dumps(v,indent=2),encoding="utf8")
    print(json.dumps(v,indent=2))
