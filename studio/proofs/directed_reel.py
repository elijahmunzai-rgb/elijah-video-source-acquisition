#!/usr/bin/env python3
"""Film Studio 30-second edited technical proof and explicitly repeated duration tests.
Inputs are separately verified/rights-cleared short recorded/3D/motion media.
Not a photoreal synthetic actor movie, not two independently authored long films.
"""
import json, subprocess,sys
from pathlib import Path
def run(cmd):subprocess.run(cmd,check=True)
def probe(p):
    d=json.loads(subprocess.check_output(["ffprobe","-v","error","-show_streams","-show_format","-of","json",str(p)]))
    v=next(x for x in d["streams"] if x["codec_type"]=="video")
    a=next(x for x in d["streams"] if x["codec_type"]=="audio")
    return {"seconds":float(d["format"]["duration"]),"width":v["width"],"height":v["height"],"codec":v["codec_name"],"audio":a["codec_name"],"bytes":p.stat().st_size}
def main():
    if len(sys.argv)!=5:raise SystemExit("Usage: directed_reel.py recorded-human.mp4 cycles.mp4 remotion.mp4 output_dir")
    a,b,c=map(Path,sys.argv[1:4]);o=Path(sys.argv[4]);o.mkdir(parents=True,exist_ok=True)
    for f in [a,b,c]:
        if not f.is_file() or f.stat().st_size<6000:raise RuntimeError(f"Missing source: {f}")
    sound=o/"original_synthesized_music.wav"
    run(["ffmpeg","-hide_banner","-loglevel","error","-y","-f","lavfi","-i",
       "aevalsrc=0.14*sin(2*PI*110*t)+0.06*sin(2*PI*165*t)+0.045*sin(2*PI*220*t):s=48000:d=30",
       "-af","afade=t=in:st=0:d=.5,afade=t=out:st=29.2:d=.8","-ac","2",str(sound)])
    seq=["motion","human","3d","human","motion","3d","human","3d","human","motion"]
    titles=["THE INTENT","REAL HUMAN FOOTAGE","PHYSICAL 3D WORLD","TRACKING THE FRAME",
        "MOTION AS LANGUAGE","CAMERA AND DEPTH","SOURCE TRUTH","RAY-TRACED LIGHT",
        "HUMAN PRESENCE","THE NEXT FRAME"]
    captions=["A cinematic decision begins with a frame","A real recorded subject; no synthetic actors",
      "Genuine Blender Cycles PBR scene","Optical flow on recorded video",
      "Frame-exact Remotion animation","Real geometry, camera and lighting",
      "A recorded person, not a generative model","True ray-tracing on free CPU",
      "Evaluated under explicit source rights","Technical proof, not Hollywood certification"]
    cmd=["ffmpeg","-hide_banner","-loglevel","error","-y"]
    for p in [a,b,c]:cmd+=["-stream_loop","-1","-i",str(p)]
    cmd+=["-i",str(sound)]
    labels={"human":0,"3d":1,"motion":2};fs=[];avail={}
    for k,n in labels.items():
        tags=[f"{k}{i}" for i in range(seq.count(k))]
        avail[k]=tags
        fs.append(f"[{n}:v]split={len(tags)}"+''.join(f"[{x}]" for x in tags))
    for i,k in enumerate(seq):
        fs.append(f"[{avail[k].pop(0)}]fps=24,scale=960:540:force_original_aspect_ratio=decrease,"
                  f"pad=960:540:(ow-iw)/2:(oh-ih)/2:color=0x0c1723,setsar=1,"
                  f"trim=duration=3,setpts=PTS-STARTPTS,format=yuv420p[v{i}]")
    fs.append(''.join(f"[v{i}]" for i in range(10))+"concat=n=10:v=1:a=0[base]")
    fs.append("[base]drawbox=x=0:y=0:w=iw:h=84:color=0x08131e@.87:t=fill,"
              "drawbox=x=0:y=427:w=iw:h=113:color=0x08131e@.86:t=fill[framed]")
    last="framed"
    font="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    bold="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    for i,(title,caption) in enumerate(zip(titles,captions)):
        for j,(line,size,y,col,tf) in enumerate(((title,26,447,"dfbc7f",bold),(caption,16,491,"f3f7f9",font))):
            dest=f"txt{i}_{j}"
            fs.append(f"[{last}]drawtext=fontfile={tf}:text='{line}':x=44:y={y}:"
                      f"fontsize={size}:fontcolor=0x{col}:enable='between(t,{i*3},{i*3+2.96})'[{dest}]")
            last=dest
    fs.append(f"[{last}]drawtext=fontfile={bold}:text='ELIJAH FILM STUDIO':x=32:y=29:fontsize=22:fontcolor=0xffffff,"
              f"drawtext=fontfile={font}:text='ENGINEERING PROOF | NOT PHOTOREAL ACTOR GENERATION':"
              f"x=32:y=61:fontsize=15:fontcolor=0x9fdfec,fade=t=in:st=0:d=.4,"
              f"fade=t=out:st=29.5:d=.5[out]")
    film=o/"studio-authored-30s.mp4"
    cmd+=["-filter_complex",';'.join(fs),"-map","[out]","-map","3:a:0",
         "-t","30","-c:v","libx264","-preset","veryfast","-crf","26",
         "-pix_fmt","yuv420p","-c:a","aac","-b:a","128k","-movflags","+faststart",str(film)]
    run(cmd)
    report={"30s_authored_edit":True,"long_outputs_repeated_source_duration_tests_only":True,
            "synthetic_photoreal_actor_proven":False,"upstream_318_installed":False,
            "assets":{film.name:probe(film)}}
    for seconds in (120,600):
        target=o/f"studio-{seconds}s-LOOP-BENCHMARK.mp4"
        run(["ffmpeg","-hide_banner","-loglevel","error","-y","-stream_loop","-1",
             "-i",str(film),"-t",str(seconds),"-map","0:v:0","-map","0:a:0","-c","copy",str(target)])
        report["assets"][target.name]=probe(target)
        if abs(report["assets"][target.name]["seconds"]-seconds)>.2:raise RuntimeError("Invalid duration")
    (o/"verification.json").write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
if __name__=="__main__":main()
