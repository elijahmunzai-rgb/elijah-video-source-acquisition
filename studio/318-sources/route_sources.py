#!/usr/bin/env python3
"""Offline research router for ALL frozen 318 upstream filmmaking references.

This program NEVER executes upstream project code or installs packages. Its
results are research priorities and must be manually assessed for security,
licensing, compatibility, cost, film quality and actual test evidence.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

CATALOG=Path(__file__).with_name("ROUTED-318-INVENTORY.json")
STAGES=(
 "orchestration","commercial-creative","explainers","editing-compositing",
 "social-format","actors-avatars-lipsync","story-shot-continuity",
 "motion-vfx","screenwriting-direction","sound-music"
)

def read_catalog(file=CATALOG):
    data=json.loads(Path(file).read_text(encoding="utf8"))
    items=data.get("items")
    if data.get("source_count")!=318 or not isinstance(items,list) or len(items)!=318:
        raise ValueError("Exactly 318 frozen upstream references required")
    repos=[r.get("repo") for r in items]
    if any(not isinstance(name,str) or name.count("/")!=1 for name in repos) or len(set(repos))!=318:
        raise ValueError("The 318 source names must be complete and unique")
    if set(r.get("production_stage") for r in items)!=set(STAGES):
        raise ValueError("Missing stage classification")
    if any(r.get("integration_status")!="not integrated by audit alone" for r in items):
        raise ValueError("Catalog cannot falsely claim activation")
    return items

def research_candidates(items, stage, limit=12):
    if stage not in STAGES:raise ValueError("Unknown filmmaking stage")
    if not 1<=limit<=318:raise ValueError("Invalid result limit")
    ranked=sorted((x for x in items if x["production_stage"]==stage),
                  key=lambda x:(-x["initial_priority_score"],x["repo"]))
    return [{"repo":x["repo"],"license_index":x["original_index_license"],
             "score_heuristic":x["initial_priority_score"],
             "review_before_use":x["review_before_use"],
             "assessed_runtime":x["runtime_status"],
             "readme":"https://github.com/"+x["repo"],
             "next_action":"Read complete license and source, inspect dependencies; run isolated tests; inspect actual outputs; never install directly"} for x in ranked[:limit]]

def coverage(items):
    by_stage=Counter(x["production_stage"] for x in items)
    by_license=Counter(x["original_index_license"] for x in items)
    by_tier=Counter(x["assessment_tier"] for x in items)
    return {"total_upstream":len(items),"production_categories":dict(sorted(by_stage.items())),
            "license_index":dict(sorted(by_license.items())),
            "research_tiers":dict(sorted(by_tier.items())),
            "fully_runtime_certified_upstream":0,
            "source_archive_coverage_claim":"Prior archive audit 318/318; current static routing alone certifies no runtime"}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--stage",choices=STAGES,help="Stage to prioritize")
    p.add_argument("--limit",type=int,default=12)
    p.add_argument("--catalog",type=Path,default=CATALOG)
    a=p.parse_args()
    items=read_catalog(a.catalog)
    data={"audit":coverage(items)}
    if a.stage:data["research_queue"]=research_candidates(items,a.stage,a.limit)
    print(json.dumps(data,indent=2,ensure_ascii=False))

if __name__=="__main__":main()
