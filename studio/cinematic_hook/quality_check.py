"""Technical film quality checks; never auto-certifies creative quality."""
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
def ffprobe(path):
    return json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(path)]))
def check(media,ledger):
    media=Path(media);ledger=Path(ledger)
    p=ffprobe(media)
    streams=p["streams"];v=next((x for x in streams if x.get("codec_type")=="video"),{})
    a=next((x for x in streams if x.get("codec_type")=="audio"),{})
    faults=[]
    if (v.get("width"),v.get("height"))!=(1920,1080):faults.append("Not true source-based Full HD")
    if v.get("codec_name")!="h264":faults.append("H264 missing")
    if a.get("codec_name")!="aac":faults.append("AAC missing")
    if not 5.95 <= float(p["format"]["duration"]) <= 6.05:faults.append("Incorrect duration")
    if media.stat().st_size<1_800_000:faults.append("Insufficient video data to support quality proof")
    provenance=json.loads(ledger.read_text(encoding="utf8"))
    if len(provenance)!=2 or len({x["id"] for x in provenance})!=2:faults.append("Two distinct original media IDs required")
    for asset in provenance:
        if "Mixkit" not in asset["rights_verification"] or asset["media"]["width"]<1700 or "sha256" not in asset:
            faults.append("Missing credible license/source evidence: "+asset.get("id","unknown"))
    result=subprocess.check_output(["ffmpeg","-hide_banner","-loglevel","error","-i",str(media),
                                    "-vf","fps=3,scale=320:180","-f","rawvideo","-pix_fmt","rgb24","pipe:1"])
    frame_bytes=320*180*3
    frames=np.frombuffer(result,dtype=np.uint8)
    if len(frames)%frame_bytes:raise ValueError("Decoded frames misaligned")
    frames=frames.reshape(-1,180,320,3).astype(np.float32)
    diffs=[float(np.abs(frames[i]-frames[i-1]).mean()) for i in range(1,len(frames))]
    if len(diffs)<14 or min(diffs)<0.8 or sum(x>2.5 for x in diffs)<13:
        faults.append("Motion/freeze gate failed")
    # Basic cut detection: one editorial transition should cause distinct change.
    if not diffs or max(diffs)<9:faults.append("No material scene variation detected")
    return {"technical_pass":not faults,"faults":faults,"visual_motion_median_rgb_delta":round(float(np.median(diffs)),2),
            "visual_motion_frames_analyzed":len(frames),"source_count":len(provenance),
            "film_approved":False,
            "creative_review_required":"Whole-video visual check, soundtrack listening, actual brand approval, person/no-endorsement review and any required VO"}
if __name__=="__main__":
    output=Path(sys.argv[3]) if len(sys.argv)>3 else Path("quality-check.json")
    report=check(sys.argv[1],sys.argv[2]);output.write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))
    if not report["technical_pass"]:raise SystemExit(2)
