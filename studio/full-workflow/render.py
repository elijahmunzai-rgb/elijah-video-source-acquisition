#!/usr/bin/env python3
"""Public, rights-identified real-length CPU movie assembler.

Honest scope: edits licensed stock footage (no AI-generated people), creates
original synthesized music and eSpeak demonstrator narration, tests real
encoded duration and changes between actual nonrepeated source segments.
Requirements: ffmpeg/ffprobe, python3 stdlib, espeak-ng for opted-in voice.
No paid API, private media, model downloads, Daniel GPU or Hostinger workers.
"""
import argparse
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import urllib.request
import wave
from pathlib import Path

LICENSED = {
    "mixkit-4610": {
        "source": "https://assets.mixkit.co/videos/4610/4610-1080.mp4",
        "page": "https://mixkit.co/free-stock-video/woman-and-man-working-at-a-call-center-4610/",
        "license": "https://mixkit.co/license/modal/videoFree/",
        "filename": "4610-1080.mp4",
    },
    "mixkit-4603": {
        "source": "https://assets.mixkit.co/videos/4603/4603-1080.mp4",
        "page": "https://mixkit.co/free-stock-video/a-pair-of-employees-working-in-a-call-center-4603/",
        "license": "https://mixkit.co/license/modal/videoFree/",
        "filename": "4603-1080.mp4",
    },
}
SIZES = {"landscape":(1920,1080),"portrait":(1080,1920),"square":(1080,1080)}
MAX_JOB_SECONDS=600

def command(args,*,capture=False):
    r=subprocess.run([str(a) for a in args],capture_output=True,text=True)
    if r.returncode:
        raise RuntimeError(f"{args[0]} failed ({r.returncode}): {r.stderr[-1000:]}")
    return r.stdout if capture else None

def probe(path):
    return json.loads(command(["ffprobe","-v","error","-show_format","-show_streams","-of","json",path],capture=True))

def validate(project):
    if not isinstance(project,dict):raise ValueError("Project object required")
    seconds=project.get("duration_seconds")
    if not isinstance(seconds,int) or not 5<=seconds<=MAX_JOB_SECONDS:raise ValueError("Real CPU demo duration 5..600 s")
    if project.get("public_demo") is not True:raise ValueError("Only nonconfidential public-demo media")
    if project.get("aspect") not in SIZES:raise ValueError("Unknown aspect")
    title=project.get("title","")
    if not isinstance(title,str) or not 1<=len(title.strip())<=80 or "<" in title or ">" in title:raise ValueError("Invalid title")
    scenes=project.get("scenes")
    if not isinstance(scenes,list) or len(scenes)<math.ceil(seconds/18) or len(scenes)>500:
        raise ValueError("Insufficient real scenes for duration")
    audio=project.get("audio") or {}
    if audio.get("voice") not in ("off","espeak-en") or audio.get("music") not in ("off","original-ambient"):
        raise ValueError("Custom/private audio is unavailable in this public worker")
    if audio["voice"]=="off" and audio["music"]=="off":raise ValueError("Audio is missing")
    ids=set();ranges=set();visual=0;assets=set()
    for s in scenes:
        if not isinstance(s,dict):raise ValueError("Scene must be object")
        shot_id=s.get("id")
        if not isinstance(shot_id,str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,36}",shot_id) or shot_id in ids:
            raise ValueError("Missing or duplicate shot ID")
        ids.add(shot_id)
        n=s.get("seconds")
        if not isinstance(n,int) or not 2<=n<=18:raise ValueError("Each shot must be between 2 and 18 sec")
        asset=s.get("asset")
        if asset not in LICENSED or s.get("rights_approved") is not True:
            raise ValueError("Only exact rights-reviewed public stock clips accepted")
        start=s.get("in_point")
        if isinstance(start,bool) or not isinstance(start,(int,float)) or not 0<=start<=100:
            raise ValueError("Invalid source in-point")
        overlap=(asset,round(float(start),2),n)
        if overlap in ranges:raise ValueError("Duplicate exact source media interval (fake loop)")
        ranges.add(overlap);assets.add(asset)
        for k,limit in (("caption",130),("narration",450)):
            if not isinstance(s.get(k,""),str) or len(s.get(k,""))>limit:raise ValueError("Invalid scene text")
        visual+=n
    if visual!=seconds:raise ValueError("Rendered duration must match scenes, no filler loops")
    if seconds>30:raise ValueError("Only two approved source clips; add non-repeating cleared footage before >30s")
    if seconds>18 and len(assets)<2:raise ValueError("More than one unique footage source required")
    if audio["voice"]=="espeak-en" and not any(s.get("narration","").strip() for s in scenes):
        raise ValueError("Voice enabled without any spoken script")
    return project

def download_sources(project, folder):
    folder.mkdir(parents=True,exist_ok=True)
    log=[]
    for asset in sorted({s["asset"] for s in project["scenes"]}):
        a=LICENSED[asset];p=folder/a["filename"] 
        if not p.is_file():
            request=urllib.request.Request(a["source"],headers={"User-Agent":"ElijahFilmStudio-NonconfidentialPublicDemo/1.0"})
            with urllib.request.urlopen(request,timeout=90) as response,p.open("wb") as writer:
                total=0
                while True:
                    block=response.read(1024*1024)
                    if not block:break
                    total+=len(block)
                    if total>75_000_000:raise ValueError("Footage larger than source budget")
                    writer.write(block)
        meta=probe(p)
        stream=next(s for s in meta["streams"] if s["codec_type"]=="video")
        if stream["width"]<1600 or stream["height"]<900:raise ValueError("Recorded source footage not 1080-class")
        duration=float(meta["format"]["duration"])
        for shot in [s for s in project["scenes"] if s["asset"]==asset]:
            if shot["in_point"]+shot["seconds"]>duration-.08:
                raise ValueError(f"{asset}: source too short at {shot['in_point']}+{shot['seconds']} > {duration:.2f}")
        log.append({**a,"asset_id":asset,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
                    "duration_seconds":duration,"rights_scope":"Mixkit Free License public illustrative footage, not actual agency employees",
                    "valid_external_source":True})
    return log

def make_music(destination,seconds,rate=24000,active=True):
    frames=int(rate*seconds)
    import struct
    with wave.open(str(destination),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
        payload=bytearray()
        for k in range(frames):
            t=k/rate
            fade=min(1,t/.8,max(0,(seconds-t)/.7))
            value=(.11*math.sin(2*math.pi*55*t)+.085*math.sin(2*math.pi*82.407*t)
                   +.035*math.sin(2*math.pi*110*t)+.020*math.sin(2*math.pi*164.814*t))
            swell=(.65+.15*math.sin(2*math.pi*.22*t))
            n=int(32767*max(-.9,min(.9,value*swell*fade if active else 0)))
            payload.extend(struct.pack("<h",n))
            if len(payload)>=24000*2:
                w.writeframesraw(payload);payload.clear()
        if payload:w.writeframesraw(payload)

def make_scene(shot,i,source,destination,width,height,workdir):
    # Real shots, unique in-point; text is an optional subtle cinematic lower third.
    caption=shot.get("caption","").strip()
    base=(f"fps=24,scale={width}:{height}:force_original_aspect_ratio=increase,"
          f"crop={width}:{height},setsar=1,eq=contrast=1.05:saturation=.90,"
          "format=yuv420p")
    if caption:
        textfile=workdir/f"caption-{i:03}.txt";textfile.write_text(caption,encoding="utf-8")
        # Textfile sourced from generated local path, not arbitrary shell data.
        vf=(base+f",drawtext=textfile='{textfile}':fontcolor=white:fontsize={int(height*.048)}:"
            f"x={int(width*.07)}:y=h-{int(height*.16)}:"
            "box=1:boxcolor=black@0.42:boxborderw=18")
    else:vf=base
    command(["ffmpeg","-y","-hide_banner","-loglevel","error","-ss",shot["in_point"],
             "-i",source,"-t",shot["seconds"],"-vf",vf,"-an","-r","24",
             "-c:v","libx264","-preset","veryfast","-crf","19","-pix_fmt","yuv420p",
             "-video_track_timescale","12288",destination])

def make_voice_scenes(project,workdir):
    voices=[]
    for i,shot in enumerate(project["scenes"]):
        out=workdir/f"voice-{i:03}.wav"
        text=shot.get("narration","").strip()
        if project["audio"]["voice"]=="espeak-en" and text:
            wav=workdir/f"raw-voice-{i:03}.wav"
            command(["espeak-ng","-v","en-us","-s","150","-w",wav,text])
            raw=probe(wav)
            actual=float(raw["format"]["duration"])
            if actual>shot["seconds"]-.15:
                raise ValueError(f"Scene {i+1} narration ({actual:.1f}s) exceeds its {shot['seconds']}s shot")
            command(["ffmpeg","-y","-hide_banner","-loglevel","error","-i",wav,
                     "-af",f"aresample=24000,adelay=250,apad,atrim=duration={shot['seconds']}",
                     "-ar","24000","-ac","1","-c:a","pcm_s16le",out])
        else:
            command(["ffmpeg","-y","-hide_banner","-loglevel","error",
                     "-f","lavfi","-i","anullsrc=r=24000:cl=mono",
                     "-t",shot["seconds"],"-ar","24000","-ac","1","-c:a","pcm_s16le",out])
        voices.append(out)
    lst=workdir/"voice-list.txt"
    lst.write_text("".join("file '"+str(f)+"'\n" for f in voices))
    voice=workdir/"narration.wav"
    command(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","concat","-safe","0",
             "-i",lst,"-ar","24000","-ac","1","-c:a","pcm_s16le",voice])
    return voice

def render(project,out):
    project=validate(project)
    out=Path(out).resolve();out.mkdir(parents=True,exist_ok=True)
    workdir=out/"working";workdir.mkdir(exist_ok=True)
    source=download_sources(project,workdir)
    (out/"SOURCE_RIGHTS.json").write_text(json.dumps(source,indent=2))
    (out/"SHOT_PLAN.json").write_text(json.dumps(project,indent=2))
    width,height=SIZES[project["aspect"]]
    scenes=[]
    for i,shot in enumerate(project["scenes"]):
        file=workdir/f"shot-{i:03}.mp4"
        make_scene(shot,i,workdir/LICENSED[shot["asset"]]["filename"],file,width,height,workdir)
        scenes.append(file)
    lst=workdir/"video-list.txt";lst.write_text("".join("file '"+str(p)+"'\n" for p in scenes))
    silent=workdir/"assembled-video.mp4"
    command(["ffmpeg","-y","-hide_banner","-loglevel","error","-f","concat","-safe","0",
             "-i",lst,"-c","copy","-movflags","+faststart",silent])
    music=workdir/"original-score.wav"
    make_music(music,project["duration_seconds"],active=project["audio"]["music"]=="original-ambient")
    narration=make_voice_scenes(project,workdir)
    output=out/"film-studio-public-demo.mp4"
    command(["ffmpeg","-y","-hide_banner","-loglevel","error",
             "-i",silent,"-i",music,"-i",narration,
             "-filter_complex","[1:a]volume=0.9[score];[2:a]volume=1.25[voice];"
                "[score][voice]amix=inputs=2:duration=first:normalize=0,"
                "loudnorm=I=-16:TP=-1.5:LRA=9[a]",
             "-map","0:v:0","-map","[a]","-t",project["duration_seconds"],
             "-c:v","copy","-c:a","aac","-b:a","160k","-movflags","+faststart",output])
    final=probe(output)
    v=next((x for x in final["streams"] if x["codec_type"]=="video"),{})
    a=next((x for x in final["streams"] if x["codec_type"]=="audio"),{})
    duration=float(final["format"]["duration"])
    errors=[]
    if abs(duration-project["duration_seconds"])>.18:errors.append("Wrong encoded film duration")
    if (v.get("width"),v.get("height"))!=(width,height):errors.append("Incorrect true video dimensions")
    if v.get("codec_name")!="h264" or a.get("codec_name")!="aac":errors.append("Missing H264/AAC")
    if int(v.get("nb_frames",0) or 0)<(project["duration_seconds"]*24-2):errors.append("Encoded frame count too short")
    qa={"technical_pass":not errors,"errors":errors,"duration_seconds":duration,
        "requested_seconds":project["duration_seconds"],"width":width,"height":height,
        "source_segments":len(scenes),"source_reuse_as_different_segments_only":True,
        "audio_voice_engine":project["audio"]["voice"],
        "score":project["audio"]["music"],"footage_license_check":"Allowed Mixkit Free-License demo entries only",
        "narration_quality":"eSpeak demonstration voice, not professional narration",
        "manual_review_required":True,"cinematic_quality_approved":False,
        "public_publish_approved":False,
        "no_gpu_no_paid_api":True,"output_size_bytes":output.stat().st_size}
    (out/"RENDER_QA.json").write_text(json.dumps(qa,indent=2))
    if errors:raise RuntimeError("Final QA failed: "+str(errors))
    print(json.dumps(qa,indent=2))
    return qa

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--validate-only",action="store_true")
    args=parser.parse_args()
    project=json.loads(args.project.read_text(encoding="utf8"))
    validate(project)
    if args.validate_only:
        print(json.dumps({"validated":True,"requested_seconds":project["duration_seconds"],"real_render_completed":False}))
        return
    render(project,args.output)

if __name__=="__main__":main()
