#!/usr/bin/env python3
"""Creative release gate for source-media-led Film Studio output.

Run on explicitly reviewed shot manifest. Does not generate imaginary approvals
or copy private client files into public GitHub. A numeric technical codec pass
is not permission to describe a video as professional filmmaking.
"""
import argparse
import json
import re
from pathlib import Path

REQUIRED_SCORES=("story","cinematography","source_image_quality","compositing_typography","audio_voice_music","originality_brand")
RUN_LENGTH={"hook":(3,6,1),"commercial_30s":(28,32,6),"film_120s":(118,122,12),"film_600s":(598,602,30)}
VISUAL_MEDIA={"rights-cleared-recorded-footage","original-3d-render","original-animated-character","licensed-film-asset","local-ai-video-reviewed"}
AUDIO_MEDIA={"human-narration","rights-cleared-professional-voiceover","licensed-score","original-composed-score","approved-live-audio","original-sound-design"}

def assess_manifest(cfg):
    faults=[]
    def problem(msg):faults.append(msg)
    if not isinstance(cfg,dict):return ["Manifest must be JSON object"]
    typ=cfg.get("deliverable_type")
    if typ not in RUN_LENGTH:return ["Invalid deliverable_type: hook, commercial_30s, film_120s, film_600s"]
    lo,hi,min_shots=RUN_LENGTH[typ]
    shots=cfg.get("shots")
    if not isinstance(shots,list) or len(shots)<min_shots:problem(f"Need at least {min_shots} distinct filmed/3D/animated shots")
    if shots and isinstance(shots,list):
        seen=set()
        for i,s in enumerate(shots):
            if not isinstance(s,dict):problem(f"Shot {i} invalid");continue
            sid=s.get("id");media=s.get("media_type")
            if not isinstance(sid,str) or not re.fullmatch(r"[a-zA-Z0-9_-]{1,50}",sid):problem(f"Shot {i} needs stable ID")
            elif sid in seen:problem(f"Duplicate shot ID: {sid}")
            seen.add(sid)
            if media not in VISUAL_MEDIA:problem(f"Shot {i}: genuine rights-reviewed shot media required, not generic typography slide")
            if not s.get("media_reference") or not s.get("rights_reference"):problem(f"Shot {i}: source asset and rights provenance missing")
            if s.get("rights_approved") is not True:problem(f"Shot {i}: rights/release unapproved")
            if s.get("visual_review_passed") is not True:problem(f"Shot {i}: human visual review required")
            if s.get("reuses_identical_frames") is True:problem(f"Shot {i}: repeated footage/loop not an original new story beat")
    audio=cfg.get("audio")
    if not isinstance(audio,dict):problem("Reviewed soundtrack/voice evidence missing")
    else:
        if audio.get("type") not in AUDIO_MEDIA:problem("Real reviewed narration or composed/licensed soundtrack missing")
        if not audio.get("source_reference") or audio.get("rights_approved") is not True:problem("Audio source or rights approval missing")
        if audio.get("human_listen_passed") is not True:problem("Human listening and mix acceptance missing")
        if typ!="hook" and audio.get("dialogue_required",True) and not audio.get("intelligible_narration_verified"):
            problem("Full film claims narration but narration has not been verified")
    qc=cfg.get("review")
    if not isinstance(qc,dict):problem("Real reviewer quality scores missing")
    else:
        if not qc.get("real_reviewer_id") or qc.get("watched_entire_video") is not True:
            problem("Film must be watched in full by an identified responsible reviewer")
        scores=qc.get("scores")
        if not isinstance(scores,dict):problem("Six category quality scores missing")
        else:
            for cat in REQUIRED_SCORES:
                v=scores.get(cat)
                if not isinstance(v,(int,float)) or isinstance(v,bool) or not 0<=v<=5 or v<4:
                    problem(f"Creative quality not accepted: {cat} must be >=4/5")
    video=cfg.get("media_probe")
    if not isinstance(video,dict):problem("Measured final media probe missing")
    else:
        d=video.get("duration_seconds")
        if not isinstance(d,(int,float)) or not lo<=d<=hi:
            problem("Actual encoded duration does not match deliverable, no timeline-only proofs")
        w=video.get("width");h=video.get("height")
        if not isinstance(w,int) or not isinstance(h,int) or min(w,h)<1080:
            problem("Minimum 1080p measured output required")
        if video.get("codec")!="h264":problem("Require a measured playable H264 video master")
        if video.get("audio_codec") not in ("aac","pcm_s16le","flac"):problem("Require measured actual audio stream")
        if video.get("manually_played") is not True:problem("Actual rendered video must be played and listened to")
    if cfg.get("public_publish_approved") is not True:problem("Explicit human release approval missing (rendering does not grant publication)")
    return faults

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest",type=Path)
    args=parser.parse_args()
    faults=assess_manifest(json.loads(args.manifest.read_text(encoding="utf8")))
    print(json.dumps({"approved":not bool(faults),"blockers":faults},indent=2))
    return 1 if faults else 0

if __name__=="__main__":
    raise SystemExit(main())
