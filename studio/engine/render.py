#!/usr/bin/env python3
"""Video Production Mastery: deterministic JSON -> H.264 MP4. Local-only.
Requires Pillow, numpy, FFmpeg. No credentials, video models or external calls.
Examples: python engine/render.py examples/agency-launch.json /tmp/launch.mp4
          python engine/render.py --validate examples/agency-launch.json
"""
import argparse
import json
import math
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps
import numpy as np

MAX_DURATION = 600
MAX_SIDE = 2160
MAX_FPS = 60


def color(s, alpha=255):
    if not isinstance(s, str) or len(s) not in (4, 7) or not s.startswith('#'):
        raise ValueError('Colors must be #RGB or #RRGGBB')
    if len(s) == 4:
        s = '#' + ''.join(z*2 for z in s[1:])
    return (*tuple(int(s[n:n+2],16) for n in (1,3,5)), max(0, min(255, int(alpha))))


def clamp(x, lo=0.0, hi=1.0):
    return max(lo,min(hi,x))


def smooth(x):
    x = clamp(x)
    return x*x*(3-2*x)


def resolve_path(root, value):
    # Assets must stay under supplied project folder; do not read system/private files.
    full = (root / value).resolve()
    if not full.is_relative_to(root.resolve()):
        raise ValueError(f'Asset outside project directory: {value}')
    if not full.is_file():
        raise FileNotFoundError(full)
    return full


def validate(cfg, root):
    canvas = cfg.get('canvas', {})
    w = canvas.get('width'); h = canvas.get('height'); fps = canvas.get('fps',24)
    if not all(isinstance(x,int) for x in (w,h,fps)):
        raise ValueError('width, height and fps must be integers')
    if not (128<=w<=MAX_SIDE and 128<=h<=MAX_SIDE and w%2==0 and h%2==0 and 8<=fps<=MAX_FPS and w*h<=2_300_000):
        raise ValueError('Canvas must have even dimensions >=128, <=2160, area <=2.3MP, fps 8..60')
    scenes=cfg.get('scenes',[])
    if not isinstance(scenes,list) or not scenes or len(scenes)>100:
        raise ValueError('scenes: 1..100 scenes required')
    total=0.0
    for si,sc in enumerate(scenes):
        d=sc.get('duration',0)
        if not isinstance(d,(int,float)) or not 0.25<=d<=30 or not math.isfinite(d):
            raise ValueError(f'Scene {si}: duration must be 0.25..30 seconds')
        total += d
        layers=sc.get('layers', [])
        if not isinstance(layers,list) or len(layers)>60:
            raise ValueError(f'Scene {si}: layers must be a list of <=60 elements')
        for li,la in enumerate(layers):
            typ=la.get('type')
            if typ not in {'text','rect','circle','orbit','rule','image','pill','counter','sparkles'}:
                raise ValueError(f'Scene {si} layer {li}: unknown type {typ}')
            for a in ['x','y','cx','cy']:
                if a in la and not isinstance(la[a],(int,float)):
                    raise ValueError(f'{a} must be normalized number')
            if typ=='image': resolve_path(root,la['path'])
            if typ in {'text','pill','counter'} and not isinstance(la.get('text',''),str):
                raise ValueError(f'Scene {si} layer {li}: text must be string')
    if total>MAX_DURATION:
        raise ValueError(f'Total duration exceeds {MAX_DURATION}s')
    if cfg.get('audio',{}).get('path'):
        resolve_path(root,cfg['audio']['path'])
    return w,h,fps,total


def font(size, weight='regular'):
    paths = [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        '/usr/share/fonts/truetype/lato/Lato-Heavy.ttf',
    ] if weight in ('bold','heavy') else [
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        '/usr/share/fonts/truetype/lato/Lato-Regular.ttf',
    ]
    for f in paths:
        if Path(f).exists():
            return ImageFont.truetype(f,max(6,int(size)))
    return ImageFont.load_default()


def render_bg(w,h,theme,scene):
    top=np.asarray(color(scene.get('background',theme.get('background','#0B1018')))[:3],dtype=np.float32)
    lower=np.asarray(color(scene.get('background_bottom',theme.get('background_bottom','#151F2E')))[:3],dtype=np.float32)
    y=np.linspace(0,1,h,dtype=np.float32)[:,None,None]
    rgb=top.reshape(1,1,3)*(1-y)+lower.reshape(1,1,3)*y
    arr=np.broadcast_to(rgb,(h,w,3)).copy()
    # Very restrained light pool; narrative motion itself lives in layers.
    yy,xx=np.ogrid[:h,:w]
    glow=np.clip(1-np.sqrt(((xx-w*0.64)/(w*0.95))**2+((yy-h*0.30)/(h*0.85))**2),0,1)
    arr+= (glow**3)[...,None]*7
    return Image.fromarray(np.uint8(np.clip(arr,0,255)),'RGB').convert('RGBA')


def enter_exit(t,d,anim):
    delay=float(anim.get('delay',0)); duration=float(anim.get('enter',0.38)); exit_d=float(anim.get('exit',0.26))
    entrance=smooth((t-delay)/max(.001,duration))
    disappearance=1-smooth((t-(d-exit_d))/max(.001,exit_d)) if anim.get('out','fade')!='none' else 1
    return entrance, clamp(entrance*disappearance)


def centered_text(draw,text,xy,sz,fg,maxw,weight='bold',align='center',spacing=1.18):
    raw=str(text).split('\n'); selected=None
    for size in range(int(sz), 8, -1):
        f=font(size,weight)
        if max(draw.textbbox((0,0),line or ' ',font=f)[2] for line in raw)<=maxw:
            selected=f;break
    if selected is None:selected=font(9,weight)
    f=selected
    line_h=int(f.size*spacing); height=line_h*len(raw)
    x,y=xy
    for n,line in enumerate(raw):
        anchor={'left':'lm','right':'rm','center':'mm'}.get(align,'mm')
        draw.text((x,y-height/2+(n+.5)*line_h),line,fill=fg,font=f,anchor=anchor,stroke_width=0)


def layer_image(layer,local,duration,w,h,theme,root,cache,scene_idx,layer_idx):
    a=layer.get('animation',{})
    v,opacity=enter_exit(local,duration,a)
    mode=a.get('in','rise')
    if opacity<.002:return None
    shiftx,shifty=0,0
    if mode=='rise': shifty=int((1-v)*min(80,h*.06))
    elif mode=='slide-left': shiftx=int((1-v)*min(130,w*.15))
    elif mode=='slide-right': shiftx=-int((1-v)*min(130,w*.15))
    scale= 0.86 + 0.14*v if mode=='pop' else 1
    im=Image.new('RGBA',(w,h),(0,0,0,0)); dr=ImageDraw.Draw(im)
    x=int(layer.get('x',.5)*w)+shiftx
    y=int(layer.get('y',.5)*h)+shifty
    fill=color(layer.get('color',theme.get('foreground','#F8F9FD')))
    accent=color(layer.get('color',theme.get('accent','#F0BC6B')))
    typ=layer['type']
    if typ in ('text','pill','counter'):
        txt=layer.get('text','')
        if typ=='counter':
            start=float(layer.get('from',0)); end=float(layer.get('to',100))
            txt=layer.get('prefix','')+f'{start+(end-start)*smooth(local/duration):,.0f}'+layer.get('suffix','')
        sz=int(layer.get('size',w*.085))*scale
        if typ=='pill':
            tw=min(w*.86,w*.025*len(txt)+sz*.67*len(txt))
            height=int(sz*1.75)
            rect=(int(x-tw/2),int(y-height/2),int(x+tw/2),int(y+height/2))
            dr.rounded_rectangle(rect,radius=height//2,fill=accent)
            fill=color(layer.get('text_color',theme.get('background','#0B1018')))
        centered_text(dr,txt,(x,y),sz,fill,w*float(layer.get('max_width',.86)),weight=layer.get('weight','bold'),align=layer.get('align','center'))
    elif typ=='rect':
        ww=int(layer.get('w',.65)*w*scale);hh=int(layer.get('h',.05)*h*scale)
        rect=(x-ww//2,y-hh//2,x+ww//2,y+hh//2)
        dr.rounded_rectangle(rect,radius=int(layer.get('radius',.012)*w),fill=accent)
    elif typ=='circle':
        r=int(layer.get('r',.08)*min(w,h)*scale)
        dr.ellipse((x-r,y-r,x+r,y+r),fill=accent if layer.get('filled',True) else None,outline=accent,width=max(1,int(layer.get('stroke',3))))
    elif typ=='rule':
        width=int(layer.get('w',.25)*w*v)
        dr.line((x-width//2,y,x+width//2,y),fill=accent,width=int(layer.get('stroke',3)))
    elif typ=='orbit':
        r=int(layer.get('r',.32)*min(w,h)); cy=y;cx=x
        clr=color(layer.get('color',theme.get('accent','#F0BC6B')))
        for multiple,alpha in [(1,70),(1.18,28)]:
            rr=int(r*multiple)
            dr.ellipse((cx-rr,cy-rr,cx+rr,cy+rr),outline=(*clr[:3],alpha),width=max(1,int(layer.get('stroke',2))))
        theta=local*float(layer.get('speed',0.9))*2*math.pi + float(layer.get('phase',0))
        px=int(cx+r*math.cos(theta));py=int(cy+r*math.sin(theta))
        point=max(3,int(w*.012));dr.ellipse((px-point,py-point,px+point,py+point),fill=clr)
    elif typ=='sparkles':
        count=min(70,int(layer.get('count',34)))
        for i in range(count):
            # Deterministic motion: same inputs -> same scene render.
            sx=((i*0.61803398875+scene_idx*.137)%1)*w
            sy=((i*.754877666+scene_idx*.231)%1)*h
            sway=math.sin(local*1.25+i*.39)*6
            pulse=.25+.65*(.5+.5*math.sin(local*2.0+i*.7))
            r=max(1,int(1+2*pulse))
            dr.ellipse((sx-r,sy+sway-r,sx+r,sy+sway+r),fill=(*accent[:3],int(150*pulse)))
    elif typ=='image':
        key=(scene_idx,layer_idx)
        if key not in cache:
            source=Image.open(resolve_path(root,layer['path'])).convert('RGBA')
            cache[key]=source
        source=cache[key]
        size=(max(1,int(layer.get('w',.7)*w*scale)),max(1,int(layer.get('h',.3)*h*scale)))
        sized=ImageOps.contain(source,size,Image.Resampling.LANCZOS)
        im.alpha_composite(sized,(int(x-sized.width/2),int(y-sized.height/2))) if 0<=x-sized.width/2 and 0<=y-sized.height/2 and x+sized.width/2<=w and y+sized.height/2<=h else im.paste(sized,(int(x-sized.width/2),int(y-sized.height/2)),sized)
    if opacity < .999:
        im.putalpha(im.getchannel('A').point(lambda px:int(px*opacity)))
    return im


def render(cfg,path,root,preview=None):
    w,h,fps,total=validate(cfg,root)
    if not shutil.which('ffmpeg'):
        raise RuntimeError('FFmpeg not found on PATH')
    scenes=cfg['scenes'];theme=cfg.get('theme',{})
    timing=[];cursor=0.0
    for sc in scenes:
        timing.append((cursor,cursor+sc['duration']));cursor+=sc['duration']
    bgs=[render_bg(w,h,theme,sc) for sc in scenes]
    tmp = path.with_name(path.stem+'.silent.mp4') if cfg.get('audio',{}).get('path') else path
    cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-f','rawvideo','-pixel_format','rgb24', '-video_size',f'{w}x{h}','-framerate',str(fps),'-i','-', '-an','-c:v','libx264','-preset','veryfast','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(tmp)]
    cache={};frames=[]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
    try:
        for ix in range(round(total*fps)):
            t=ix/fps
            scene_idx=next((i for i,(_start,end) in enumerate(timing) if t<end),len(timing)-1)
            sc=scenes[scene_idx]; local=t-timing[scene_idx][0]
            output=bgs[scene_idx].copy()
            for layer_idx,layer in enumerate(sc.get('layers',[])):
                part=layer_image(layer,local,sc['duration'],w,h,theme,root,cache,scene_idx,layer_idx)
                if part is not None: output.alpha_composite(part)
            if preview is not None and ix in preview:
                frames.append((ix,output.convert('RGB').copy()))
            proc.stdin.write(output.convert('RGB').tobytes())
    except (BrokenPipeError,BaseException):
        proc.kill()
        raise
    finally:
        if proc.stdin and not proc.stdin.closed:proc.stdin.close()
    err=proc.stderr.read().decode(errors='replace'); rc=proc.wait()
    if rc:raise RuntimeError('FFmpeg rendering error: '+err)
    audio=cfg.get('audio',{})
    if audio.get('path'):
        volume=clamp(float(audio.get('volume',.24)),0,2)
        fade=max(0,total-.45)
        source=str(resolve_path(root,audio['path']))
        cmd=['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(tmp),'-stream_loop','-1','-i',source,'-filter_complex',f'[1:a]volume={volume},atrim=0:{total:.4f},afade=t=out:st={fade:.4f}:d=0.45[a]','-map','0:v:0','-map','[a]','-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(path)]
        subprocess.run(cmd,check=True);tmp.unlink()
    return {'path':str(path),'duration':total,'width':w,'height':h,'fps':fps,'preview':frames}


def main():
    pa=argparse.ArgumentParser(description=__doc__)
    pa.add_argument('config',type=Path)
    pa.add_argument('output',type=Path,nargs='?')
    pa.add_argument('--validate',action='store_true')
    args=pa.parse_args()
    with args.config.open(encoding='utf-8') as f:cfg=json.load(f)
    w,h,fps,d=validate(cfg,args.config.parent)
    if args.validate:
        print(f'VALID {w}x{h} {fps}fps {d:.3f}s');return
    if not args.output: pa.error('Output MP4 is required unless --validate is passed')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    result=render(cfg,args.output,args.config.parent)
    print(f'OK {result["path"]} {result["width"]}x{result["height"]} {result["duration"]:.3f}s')

if __name__=='__main__':main()
