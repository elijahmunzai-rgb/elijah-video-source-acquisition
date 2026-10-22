"""Evidence-based activation tracker for all 318 upstream video-related sources.

Never installs, runs or imports upstream code. '318 accounted for' is not
'318 processes running'. Each actual runnable tool must have trusted source,
license inspection, sandbox run, artifact and visual review before activation.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

HERE=Path(__file__).resolve().parent
REGISTRY=HERE/"ACTIVATION-318.json"
PINNED={"hacimertgokhan/geomotion","AsadMoulviDev/reel-video",
        "diffusionstudio/lottie","jtydhr88/screenwriting-skills"}
SAFE_STAGES={"orchestration","commercial-creative","explainers",
             "editing-compositing","social-format","actors-avatars-lipsync",
             "story-shot-continuity","motion-vfx","screenwriting-direction","sound-music"}
BAD_LICENSES={"MISSING","NOASSERTION","AGPL-3.0","CC-BY-SA-4.0"}
ALLOWED_TYPES={"source_verified_historical","runnable_confirmed","installed",
               "integration_verified","cinematic_quality_verified"}
def load(path=REGISTRY):
    obj=json.loads(Path(path).read_text(encoding="utf-8"))
    entries=obj.get("records",[])
    if obj.get("total")!=318 or len(entries)!=318 or len({e["repo"] for e in entries})!=318:
        raise ValueError("Missing/duplicate source, all 318 expected")
    if set(int(e["id"]) for e in entries)!=set(range(1,319)):
        raise ValueError("Source IDs must cover 001..318")
    if any(e["stage"] not in SAFE_STAGES or any(type(e[k]) is not bool for k in ALLOWED_TYPES) for e in entries):
        raise ValueError("Invalid runtime state")
    if any(e["integration_verified"] and not (e["installed"] and e["runnable_confirmed"])
           for e in entries):
        raise ValueError("Cannot integrate a non-runnable or uninstalled tool")
    if any(e["cinematic_quality_verified"] and not e["integration_verified"] for e in entries):
        raise ValueError("Creative quality requires actual verified pipeline integration")
    if any(e["paid_calls_allowed"] or e["private_media_allowed"] for e in entries):
        raise ValueError("Unapproved external spending/private data in public source")
    if obj.get("allow_paid_services") or obj.get("allow_dan_gpu") or obj.get("allow_hostinger_heavy_render"):
        raise ValueError("Unexpected paid/GPU/Hostinger policy escalation")
    if obj.get("activated_count")!=sum(bool(e["integration_verified"]) for e in entries):
        raise ValueError("Activated count must be evidence-based")
    return obj
def report(obj):
    rs=obj["records"]
    fields=["runnable_confirmed","installed","integration_verified","cinematic_quality_verified"]
    return {"historical_source_snapshots":sum(e["source_verified_historical"] for e in rs),
            "component_entries":len(rs),
            "status_counts":{f:sum(e[f] for e in rs) for f in fields},
            "component_hypotheses_NOT_runtime_tests":dict(Counter(e["component_family_hypothesis"] for e in rs)),
            "license_caution_preliminary":sum(e["license_index"] in BAD_LICENSES for e in rs),
            "historically_selected_unit_tests":sum("previous upstream" in e["execution_status"] for e in rs),
            "operational_claim":"Only independent test artifacts can upgrade any component status"}
def plan(obj,stage,limit):
    candidates=[e for e in obj["records"] if e["stage"]==stage]
    rank={"P0-research-test":0,"P1-evaluate":1,"P2-experiment":2,"P3-catalog-only":3}
    candidates.sort(key=lambda e:(e["license_index"] in BAD_LICENSES,
                                  e["component_family_hypothesis"].startswith("provider"),
                                  rank.get(e["priority"],4),e["repo"]))
    return [{"id":e["id"],"repo":e["repo"],"license_index":e["license_index"],
             "status":e["execution_status"],"pin_sha":e["pin_sha"],
             "next":"manual code/license/dependency inspection -> pinned sandbox test -> real rendered artifact -> creative QA"}
            for e in candidates[:limit]]
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--registry",type=Path,default=REGISTRY)
    p.add_argument("--stage",choices=sorted(SAFE_STAGES))
    p.add_argument("--limit",type=int,default=12)
    a=p.parse_args()
    if a.limit<1 or a.limit>318:p.error("Invalid limit")
    obj=load(a.registry)
    value=report(obj)
    if a.stage:value["candidate_queue"]=plan(obj,a.stage,a.limit)
    print(json.dumps(value,indent=2,ensure_ascii=False))
if __name__=="__main__":main()
