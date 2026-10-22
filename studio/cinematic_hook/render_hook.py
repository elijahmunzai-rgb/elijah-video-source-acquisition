#!/usr/bin/env python3
"""Rights-reviewed stock-footage editorial HOOK, not footage of agency employees.

Two distinct Mixkit Stock Video Free License clips, cut at 24fps with short
cinematic dissolves and original 48kHz soundtrack. No GPU or proprietary APIs.
NEVER represents featured people as actual agency staff or endorsers.
"""
import hashlib
import json
import math
import shutil
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT=Path(__file__).resolve().parent
OUT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else (ROOT/"output")
SRC=ROOT/"sources"
OUT.mkdir(parents=True,exist_ok=True)
SIZE=(1920,1080)
DURATION=6
FPS=24
SOURCES=[
 {"id":"mixkit-4610","title":"Woman and man working at a call center",
  "page":"https://mixkit.co/free-stock-video/woman-and-man-working-at-a-call-center-4610/",
  "asset":"https://assets.mixkit.co/videos/4610/4610-1080.mp4",
  "license":"https://mixkit.co/license/modal/videoFree/",
  "file":"office_call_center_4610.mp4","start":1.1},
 {"id":"mixkit-4603","title":"A pair of employees working in a call center",
  "page":"https://mixkit.co/free-stock-video/a-pair-of-employees-working-in-a-call-center-4603/",
  "asset":"https://assets.mixkit.co/videos/4603/4603-1080.mp4",
  "license":"https://mixkit.co/license/modal/videoFree/",
  "file":"office_call_center_4603.mp4","start":2.2},
]
def run(command):
    r=subprocess.run(command,text=True,capture_output=True)
    if r.returncode:
        raise RuntimeError("Command failed: "+' '.join(command[:10])+"\n"+r.stderr[-2400:])
    return r.stdout
def probe(path):
    x=json.loads(run(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(path)]))
    v=next(s for s in x["streams"] if s.get("codec_type")=="video")
    return {"width":v["width"],"height":v["height"],"codec":v["codec_name"],"duration":float(x["format"]["duration"]), "size":path.stat().st_size}
def source_gate():
    results=[]
    for s in SOURCES:
        p=SRC/s["file"]
        if not p.is_file():raise FileNotFoundError(f"Required source not downloaded: {p}")
        data=probe(p)
        if data["width"]<1700 or data["height"]<1000 or data["duration"]<6:
            raise RuntimeError(f"Insufficient actual stock clip quality/duration: {s['id']} {data}")
        if not p.stat().st_size>500000:raise RuntimeError("Source file tiny/invalid")
        results.append({**s,"media":data,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),
                        "rights_verification":"Mixkit individual clip page explicitly states Stock Video FREE License, commercial use permitted. Verify snapshot before reuse.",
                        "third_party_people":"Illustrative stock actors; NOT agency staff or endorsers"})
    (OUT/"SOURCE_AND_LICENSE_LEDGER.json").write_text(json.dumps(results,indent=2))
    return results
def inter_font(px,bold=False):
    names=("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
           else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    return ImageFont.truetype(names,px)
def overlay_file(path,topline,headline,subline):
    W,H=SIZE
    img=Image.new("RGBA",(W,H))
    d=ImageDraw.Draw(img,"RGBA")
    # Sparse dark gradient under credits, no UI cards / speech bubbles.
    for y in range(490,H):
        a=int(180*max(0,min(1,(y-490)/420))**1.5)
        d.line([(0,y),(W,y)], fill=(3,13,20,a),width=1)
    d.rectangle((124,800,139,915),fill=(0,209,255,250))
    white=(241,249,251,250)
    sky=(129,230,249,236)
    d.text((166,700),topline,font=inter_font(28),fill=sky)
    d.text((163,764),headline,font=inter_font(66,True),fill=white,stroke_width=0)
    d.text((166,867),subline,font=inter_font(29),fill=(221,230,236,240))
    d.text((124,995),"INBOUND OUTBOUND SALES AGENCY  /  CONCEPT FILM",
           font=inter_font(22),fill=(205,216,227,204))
    img.save(path)
def create_audio(path, sr=48000, duration=6):
    # Non-melodic film-score design: velvet minor drone with atmospheric noise,
    # bowed-glass overtones and filtered transient at editorial cut, no shrill beeps.
    n=int(sr*duration)
    t=np.arange(n,dtype=np.float64)/sr
    rng=np.random.default_rng(778)
    phase=np.sin(2*np.pi*.12*t)
    drone=np.zeros(n)
    for f,a in [(55,.20),(82.4,.13),(110,.10),(164.8,.045),(220,.019)]:
        drone+=a*np.sin(2*np.pi*f*t+.03*phase)
    noise=rng.normal(0,1,n)
    # smoothed air / granular material rather than raw hiss
    filtered=np.convolve(noise[:0], [1],mode="full") if False else np.zeros(n)
    alpha=.005; s=0.
    for i in range(n):
        s=s*(1-alpha)+noise[i]*alpha
        filtered[i]=s
    def bump(center,width):
        return np.exp(-.5*((t-center)/width)**2)
    swell=.6+.5*bump(2.8,.38)+.48*bump(5.35,.8)
    # Two organic transient swishes bridge source cuts.
    whoosh=filtered*(.8*bump(2.8,.16)+.6*bump(0.35,.2))
    env=np.clip(t/.42,0,1)*np.clip((duration-t)/.44,0,1)
    signal=(drone*swell+whoosh+.13*filtered)*env
    signal/=max(np.abs(signal).max(),1e-8)
    signal*=.43
    # modest stereo separation, phase micro shift
    left=np.int16(np.clip(signal,-1,1)*32767)
    right=np.int16(np.clip(np.roll(signal,165)*.97,-1,1)*32767)
    stereo=np.stack([left,right],axis=-1)
    with wave.open(str(path),"wb") as w:
        w.setnchannels(2);w.setsampwidth(2);w.setframerate(sr);w.writeframes(stereo.tobytes())
def produce():
    inputs=source_gate()
    pngs=[OUT/"scene1-title.png",OUT/"scene2-title.png"]
    overlay_file(pngs[0],"A BETTER CONNECTION BEGINS HERE.","EVERY CONVERSATION","An opportunity to understand, support and grow.")
    overlay_file(pngs[1],"PEOPLE FIRST. ALWAYS.","HUMAN CONNECTION","Sales outreach  /  customer support  /  real conversations")
    wav=OUT/"original-score.wav";create_audio(wav)
    clips=[]
    for i,s in enumerate(inputs):
        p=OUT/f"shot{i+1}.mp4";clips.append(p)
        # Keep natural camera movement; lens is source recorded, grade subtly.
        vf=(f"trim=start={s['start']}:duration=3.20,setpts=PTS-STARTPTS,"
            f"fps={FPS},scale=1920:1080:force_original_aspect_ratio=increase,"
            f"crop=1920:1080,setsar=1,"
            "eq=contrast=1.07:saturation=.84:brightness=-.015,"
            f"format=yuv420p")
        cmd=["ffmpeg","-y","-hide_banner","-loglevel","error","-ss",str(s["start"]),"-i",str(SRC/s["file"]),
             "-loop","1","-framerate","24","-i",str(pngs[i]),"-filter_complex",
             "[0:v]fps=24,scale=1920:1080:force_original_aspect_ratio=increase,"
             "crop=1920:1080,setsar=1,eq=contrast=1.055:saturation=.88:brightness=-.018,"
             "format=yuv420p[v];"
             "[1:v]format=rgba,fade=t=in:st=0.24:d=0.46:alpha=1,"
             "fade=t=out:st=2.76:d=0.36:alpha=1[title];"
             "[v][title]overlay=0:0:shortest=1:format=auto,format=yuv420p[out]",
             "-map","[out]","-frames:v","77","-r","24","-c:v","libx264",
             "-preset","medium","-crf","17","-pix_fmt","yuv420p",str(p)]
        run(cmd)
    film=OUT/"film-studio-real-footage-hook-6s.mp4"
    # exact duration of 6 sec; 77 frames per source, fade overlaps 0.4167 sec
    cmd=["ffmpeg","-y","-hide_banner","-loglevel","error",
         "-i",str(clips[0]),"-i",str(clips[1]),"-i",str(wav),
         "-filter_complex",
         "[0:v][1:v]xfade=transition=fade:duration=0.416667:offset=2.791667,"
         "format=yuv420p,trim=duration=6,setpts=PTS-STARTPTS[v];"
         "[2:a]atrim=duration=6,asetpts=PTS-STARTPTS,"
         "loudnorm=I=-16:TP=-1.5:LRA=9:print_format=summary[a]",
         "-map","[v]","-map","[a]","-t","6","-r","24",
         "-c:v","libx264","-preset","medium","-crf","17","-profile:v","high",
         "-pix_fmt","yuv420p","-c:a","aac","-b:a","192k",
         "-movflags","+faststart","-metadata","title=Film Studio original call-center hook (stock footage concept)",
         str(film)]
    run(cmd)
    actual=json.loads(run(["ffprobe","-v","error","-show_format","-show_streams","-of","json",str(film)]))
    v=next(s for s in actual["streams"] if s.get("codec_type")=="video")
    a=next(s for s in actual["streams"] if s.get("codec_type")=="audio")
    dur=float(actual["format"]["duration"])
    if (v["width"],v["height"])!=(1920,1080) or v["codec_name"]!="h264" or a["codec_name"]!="aac" or not 5.8<=dur<=6.05:
        raise RuntimeError(f"Technical QA failed: {v['width']}x{v['height']} {dur}sec {a['codec_name']}")
    if film.stat().st_size<1600000:raise RuntimeError("Encoded asset suspiciously small")
    thumbs=[]
    for sec in (.75,2.1,3.5,5.45):
        thumbnail=OUT/("frame-"+str(sec).replace(".","-")+".jpg")
        run(["ffmpeg","-y","-hide_banner","-loglevel","error","-ss",str(sec),"-i",str(film),"-frames:v","1","-q:v","2",str(thumbnail)])
        thumbs.append(str(thumbnail))
    report={"result":"TECHNICAL_RENDER_PASS_CREATIVE_REVIEW_REQUIRED","duration":dur,
            "width":v["width"],"height":v["height"],"video_codec":v["codec_name"],"audio_codec":a["codec_name"],
            "fps":v.get("r_frame_rate"),"bytes":film.stat().st_size,
            "source_count":2,"shots":2,"source_type":"Mixkit Free License illustrative stock human footage, not actual agency employees",
            "creative_review":"NOT APPROVED until real viewer reviews visuals/audio; no VO in this six-second HOOK",
            "no_paid_api":True,"no_nvidia_gpu":True,"thumbnails":thumbs}
    (OUT/"TECHNICAL_AND_CREATIVE_REVIEW.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=="__main__":produce()
