#!/usr/bin/env python3
"""Public demo production agents: deterministic, no paid LLM or GPU."""
import argparse,json,math,hashlib
from pathlib import Path
from datetime import datetime,timezone

ROLES=["director","scriptwriter","storyboard","rights","camera-vfx","motion","audio","qa"]
ASPECTS={"landscape":(1920,1080),"portrait":(1080,1920),"square":(1080,1080)}
BEATS=["HOOK","WORLD","CHARACTER","GOAL","PROBLEM","DISCOVERY","TURN","PROOF","RESOLUTION","CLOSE"]
def brief(title,goal,duration,aspect,public):
    if not public:raise ValueError("Only approved PUBLIC demo briefs")
    if duration not in [15,30,60,120,600] or aspect not in ASPECTS:raise ValueError("Unsupported format")
    if not title.strip() or len(title)>80 or not goal.strip() or len(goal)>400:raise ValueError("Invalid brief")
    if any(t in title+goal for t in ["<script","; rm -rf"]):raise ValueError("Unsafe brief text")
    return {"title":title.strip(),"goal":goal.strip(),"duration":duration,"aspect":aspect,"privacy":"public-demo"}
def director(b):
    n=10 if b["duration"]<=60 else 16 if b["duration"]==120 else 20
    dur=b["duration"]/n
    return [{"id":"SHOT%03d"%(i+1),"start":i*dur,"duration":dur,"beat":BEATS[i%10],
             "camera":["locked","push","orbit","lateral","detail"][i%5],
             "asset_verified":False} for i in range(n)]
def motion(b):
    """Metadata for the original 1080p editorial-preview renderer.

    The final MP4 is produced by premium_preview.py, not the legacy JSON
    graphics renderer. Keep this manifest truthful about the content.
    """
    w,h=ASPECTS[b["aspect"]]
    return {"renderer":"studio/agents/premium_preview.py",
      "preview_type":"original editorial motion graphics (NOT photoreal film)",
      "canvas":{"width":w,"height":h,"fps":24},
      "audio":{"type":"original synthesized ambient soundtrack","copyright_cleared":True},
      "brief_title":b["title"],"brief_goal":b["goal"],
      "scenes":[
        {"duration":2,"purpose":"Imagine / story establishes visual world"},
        {"duration":2,"purpose":"Compose / kinetic typography and moving 3D-inspired layers"},
        {"duration":2,"purpose":"Create / public demo title and creative goal"}]}

def store(p,x):p.write_text(json.dumps(x,indent=2,ensure_ascii=False)+"\n")
def build(b,out):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    shots=director(b)
    script=[{"shot":s["id"],"instruction":s["beat"]+" in context of "+b["goal"],
       "actual_dialogue":None} for s in shots]
    rights={"source_assets_licensed":False,"talent_release_verified":False,
      "public_delivery_approved":False,"reason":"No approved footage assets attached"}
    camera={"calibrated_real_footage_tracking":False,
      "shot_moves":[{"shot":s["id"],"move":s["camera"]} for s in shots]}
    audio={"approved_narration":False,"approved_music":False,"stems":["dialogue","music","sfx"]}
    spec=motion(b)
    qa={"preflight":True,"full_film_rendered":False,"preview_only":True,
        "public_publish_approved":False,"visual_quality_review_required":True,
        "duration_correct":math.isclose(sum(s["duration"] for s in shots),b["duration"]),
        "unique_shots":len({s["id"] for s in shots})==len(shots)}
    if not qa["duration_correct"] or not qa["unique_shots"]:raise RuntimeError("QA failed")
    files={"brief.json":b,"director.json":shots,"scriptwriter.json":script,
           "storyboard.json":shots,"rights.json":rights,"camera-vfx.json":camera,
           "motion-preview.json":spec,"audio.json":audio,"qa.json":qa}
    for name,data in files.items():store(out/name,data)
    lines=["# "+b["title"],"",
      "Demo plan only; 6-second procedural preview. NOT a finished long film.","",
      "Director -> Scriptwriter -> Storyboard -> Rights -> Camera/VFX -> Motion -> Audio -> QA","",
      "| Shot | Start | Beat | Camera | Rights-cleared? |",
      "|---|---:|---|---|---|"]
    lines.extend("| %s | %.1f | %s | %s | No |"%(s["id"],s["start"],s["beat"],s["camera"]) for s in shots)
    lines+=["","Client footage/identity and publication need separate permission."]
    (out/"STORYBOARD.md").write_text("\n".join(lines)+"\n")
    hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.is_file()}
    store(out/"manifest.json",{"role_agents":ROLES,"no_llm_or_model_weights":True,
        "no_gpu":True,"no_paid_api":True,"full_film_rendered":False,
        "preview_duration":6,"preview_canvas":spec["canvas"],
        "preview_type":spec["preview_type"],"utc":datetime.now(timezone.utc).isoformat(),
        "files_sha256":hashes})
    return out
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--title",default="A NEW FRAME")
    p.add_argument("--goal",default="Demonstrate free professional film planning")
    p.add_argument("--duration",type=int,default=30)
    p.add_argument("--aspect",choices=ASPECTS,default="landscape")
    p.add_argument("--public-demo",action="store_true")
    p.add_argument("--output",default="out/agent-demo")
    a=p.parse_args()
    out=build(brief(a.title,a.goal,a.duration,a.aspect,a.public_demo),a.output)
    print(json.dumps({"agents":len(ROLES),"shot_count":len(director(brief(a.title,a.goal,a.duration,a.aspect,a.public_demo))),
      "preview_seconds":6,"full_film_rendered":False,"output":str(out)}))
if __name__=="__main__":main()
