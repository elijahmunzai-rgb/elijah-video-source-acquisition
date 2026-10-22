#!/usr/bin/env python3
"""Original CPU-only cinematic editorial motion-graphics preview, not photoreal film.

No external assets or paid API. Creates a six-second 1080p (landscape) H.264
MP4 with a novel synthesized soundtrack and substantive per-frame movement.
"""
import argparse
import json
import math
import subprocess
import tempfile
import wave
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

DURATION=6
FPS=24
PAPER=(239,237,228)
GOLD=(225,174,104)
SEA=(49,180,185)

def ease(t):
    t=max(0,min(1,t))
    return t*t*(3-2*t)

def font(px,weight='medium'):
    names={'bold':'InterDisplay-Black.otf','semibold':'InterDisplay-SemiBold.otf',
           'medium':'InterDisplay-Medium.otf'}
    paths=['/usr/share/fonts/opentype/inter/'+names[weight],
           '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf']
    for p in paths:
        if Path(p).is_file():return ImageFont.truetype(p,max(9,int(px)))
    return ImageFont.load_default()

def puttext(dr,xy,string,size,fill=PAPER,weight='semibold',maxwidth=None):
    f=font(size,weight)
    if maxwidth:
        while f.size>13 and dr.textbbox((0,0),string,font=f)[2]>maxwidth:
            f=font(f.size-2,weight)
    dr.text(xy,string,font=f,fill=fill)

def background(w,h,scene):
    yy,xx=np.mgrid[0:h,0:w].astype(np.float32)
    x=xx/w;y=yy/h
    glow=np.exp(-((x-(.76 if scene!=1 else .27))**2/.14+(y-.4)**2/.23))
    halo=np.exp(-((x-.66)**2/.35+(y-.9)**2/.29))
    bands=np.sin(8*x-3*y+scene*.9)*2
    grain=np.random.default_rng(1469+scene).normal(0,2,size=(h,w)).astype(np.float32)
    base=(8,15,26) if scene!=1 else (12,16,26)
    arr=np.empty((h,w,3),np.uint8)
    for k in range(3):
        v=base[k]+glow*(18,35,46)[k]+halo*(12,19,19)[k]+bands+grain-7*((x-.5)**2+(y-.5)**2)
        arr[:,:,k]=np.clip(v,0,255).astype('uint8')
    return Image.fromarray(arr,'RGB')

def text_layers(w,h,title,goal):
    def make(lines):
        layer=Image.new('RGBA',(w,h),(0,0,0,0));d=ImageDraw.Draw(layer)
        for x,y,msg,size,color,weight,width in lines:
            puttext(d,(int(x*w),int(y*h)),msg,int(size*h/720),color,weight,int(width*w))
        return layer
    line=' '.join(str(goal).strip().upper().split())
    if len(line)>64:line=line[:60].rsplit(' ',1)[0]+'…'
    line=line or 'ORIGINAL MOTION, FRAME BY FRAME.'
    title=title.strip().upper()[:80] or 'A NEW FRAME'
    return [
        make([(.074,.193,'A STORY IS NEVER',53,PAPER,'semibold',.74),
              (.074,.296,'JUST AN IDEA.',69,PAPER,'bold',.80),
              (.077,.404,'IT NEEDS A WORLD.',30,GOLD,'medium',.74)]),
        make([(.074,.208,'GIVE EVERY',62,PAPER,'semibold',.66),
              (.074,.319,'FRAME A',79,PAPER,'bold',.66),
              (.074,.448,'PURPOSE.',90,GOLD,'bold',.65)]),
        make([(.074,.241,'ELIJAH   /   FILM STUDIO',24,GOLD,'semibold',.83),
              (.074,.334,title,91,PAPER,'bold',.86),
              (.078,.485,line,27,(196,212,211),'medium',.85)])
    ]

def stage(dr,w,h,t,scene):
    cx=(.67 if scene!=1 else .77)*w
    horizon=.67*h
    for k in range(-11,12):
        dr.line((cx,horizon,cx+(k*.11*w)*(1+.06*math.sin(t*.3)),h),fill=(18,66,70),width=1)
    for k in range(1,13):
        depth=((k*.14+t*.20)%1)**1.55
        y=horizon+depth*(h-horizon);v=int(28+80*depth)
        dr.line((0,y,w,y),fill=(12,v//2+8,v//2+14),width=1 if k<10 else 2)
    cx=(.80 if scene!=1 else .81)*w+math.sin(t*.8)*w*.02
    cy=.49*h+math.cos(t*.6)*h*.02
    radius=min(w,h)*(.32 if scene!=1 else .37)
    for r in (.67,.88,1.04,1.24,1.6):
        rr=radius*r
        dr.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=(32,81,89) if r<1 else (24,54,62),width=2 if r<1 else 1)
    for j in range(30):
        a=j*.44+t*(.57 if scene!=1 else -.45)
        depth=.35+.65*(.5+.5*math.sin(a))
        x=cx+radius*1.2*math.cos(a);y=cy+radius*.66*math.sin(a)
        size=1+4*depth
        col=GOLD if j%5==0 else (int(50+150*depth),int(112+63*depth),int(124+25*depth))
        dr.ellipse((x-size,y-size,x+size,y+size),fill=col)
    for j in range(28):
        a=j/27*math.pi*.96+t*.42+scene*.55
        x=cx+radius*.97*math.cos(a);y=cy+radius*.97*.79*math.sin(a)
        dr.ellipse((x-2,y-2,x+2,y+2),fill=GOLD if j%4 else SEA)
    if scene!=2:
        angle=t*1.8+scene*1.1
        x=cx+radius*.72*math.cos(angle);y=cy+radius*.43*math.sin(angle)
        dr.ellipse((x-15,y-15,x+15,y+15),fill=(245,192,115),outline=(255,228,182),width=2)
    left=int(.071*w);right=int(.929*w)
    dr.line((left,.085*h,right,.085*h),fill=(52,77,85),width=2)
    dr.line((left,.89*h,right,.89*h),fill=(52,77,85),width=2)
    size=lambda n:int(n*h/720)
    puttext(dr,(left,.064*h),'ELIJAH / MOTION LAB',size(14),GOLD,'medium')
    puttext(dr,(int(.79*w),.064*h),'24 FPS  •  ORIGINAL',size(14),(155,185,190),'medium')
    frame=int(t*24)+1
    puttext(dr,(left,.928*h),f'FRAME  {frame:03d}   /   144',size(15),(142,179,182),'medium')
    puttext(dr,(int(.76*w),.928*h),('01   /   IMAGINE','02   /   COMPOSE','03   /   CREATE')[scene],size(16),GOLD,'semibold')
    for i in range(30):
        x=(.71+i*.0073)*w;y=.105*h
        dr.rectangle((x,y,x+.003*w,y+.012*h),fill=GOLD if i/30<t/6 else (46,75,83))
    puttext(dr,(int(.738*w),int(.775*h)),str(scene+1).zfill(2),int(186*h/720),(27,62,72),'bold')

def sound(path,duration=DURATION,rate=32000):
    n=int(duration*rate);t=np.arange(n,dtype=np.float64)/rate
    env=np.clip(t/.75,0,1)**1.6*np.clip((duration-t)/.65,0,1)**1.7
    drone=np.zeros(n)
    for hz,amp in [(55,.21),(82.4069,.15),(110,.14),(164.814,.095),(220,.052),(330,.020)]:
        drone+=amp*np.sin(2*np.pi*hz*t+.008*np.sin(2*np.pi*.21*t))
    beat=np.zeros(n)
    for moment in (0,2,4):
        z=t-moment;mask=(z>=0)&(z<.48);zz=z[mask]
        beat[mask]+=.19*np.sin(2*np.pi*(65+40*np.exp(-zz*15))*zz)*np.exp(-zz*16)
    riser=.028*np.sin(2*np.pi*(340*t+95*t*t/6))*(t/6)**1.4
    pcm=(np.clip((drone*env+beat+riser)*.78,-.9,.9)*32767).astype('<i2')
    with wave.open(str(path),'wb') as wf:
        wf.setnchannels(1);wf.setsampwidth(2);wf.setframerate(rate);wf.writeframes(pcm.tobytes())

def render(brief,output,width=None,fps=FPS,preview_frames=()):
    if not isinstance(brief,dict) or not brief.get('title') or brief.get('privacy')!='public-demo':
        raise ValueError('Only approved public-demo briefs can render')
    aspect=brief.get('aspect')
    if aspect not in ('landscape','portrait','square'):raise ValueError('Invalid aspect')
    if width is None:width=1920 if aspect=='landscape' else 1080
    if width%2 or width<320 or width>1920 or fps not in (12,24,30):raise ValueError('Invalid size or fps')
    h=round(width*{'landscape':9/16,'portrait':16/9,'square':1}[aspect])
    h+=h%2
    if h>2160:raise ValueError('Canvas too large')
    bases=[background(width,h,i) for i in range(3)]
    type_layers=text_layers(width,h,brief['title'],brief.get('goal',''))
    output=Path(output);output.parent.mkdir(parents=True,exist_ok=True)
    captures=[]
    with tempfile.TemporaryDirectory() as d:
        wav=Path(d)/'original.wav';sound(wav)
        cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-pix_fmt','rgb24',
             '-s:v',f'{width}x{h}','-r',str(fps),'-i','pipe:0','-i',str(wav),
             '-map','0:v:0','-map','1:a:0','-c:v','libx264','-preset','fast','-crf','17',
             '-profile:v','high','-pix_fmt','yuv420p','-c:a','aac','-b:a','160k',
             '-t',str(DURATION),'-movflags','+faststart',str(output)]
        p=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            for n in range(DURATION*fps):
                t=n/fps;scene=min(int(t/2),2);local=t-scene*2
                frame=bases[scene].convert('RGBA')
                overlay=Image.new('RGBA',(width,h),(0,0,0,0));dr=ImageDraw.Draw(overlay)
                stage(dr,width,h,t,scene)
                frame.alpha_composite(overlay)
                opacity=max(0,min(1,local/.35,(2-local)/.33))
                text=type_layers[scene].copy()
                text.putalpha(text.getchannel('A').point(lambda px:int(px*opacity)))
                frame.alpha_composite(text,(0,int((1-ease(local/.45))*35*h/720)))
                dr=ImageDraw.Draw(frame);v=ease(local/.75)
                dr.rounded_rectangle((.075*width,.595*h,(.075+.23*v)*width,.6*h),radius=3,fill=GOLD)
                rgb=frame.convert('RGB')
                if n in preview_frames:captures.append((n,rgb.copy()))
                p.stdin.write(rgb.tobytes())
            p.stdin.close()
            err=p.stderr.read().decode(errors='replace');p.stderr.close()
            if p.wait():raise RuntimeError('FFmpeg failed: '+err[:600])
        except BaseException:
            p.kill();p.wait();raise
    return {'path':str(output),'duration':DURATION,'width':width,'height':h,'fps':fps,'preview':captures}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--brief',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--width',type=int,default=None)
    parser.add_argument('--fps',type=int,default=FPS)
    args=parser.parse_args()
    result=render(json.loads(args.brief.read_text(encoding='utf8')),args.output,args.width,args.fps)
    print(json.dumps({k:v for k,v in result.items() if k!='preview'}))

if __name__=='__main__':main()
