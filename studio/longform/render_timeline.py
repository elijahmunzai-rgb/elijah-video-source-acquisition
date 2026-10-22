#!/usr/bin/env python3
"""Elijah Film Studio free CPU longform source-footage timeline renderer.

Accepts the same authored project JSON that /studio exports. Produces an MP4
only when actual licensed media files exist. No synthetic claims of actors,
no repeat-loop length fraud, no uploading data and no paid services.
'generate-local-draft' TTS uses espeak-ng and is ROBOTIC, not final voiceover.
"""
import argparse
import json
import math
import shutil
import subprocess
import sys
from pathlib import Path

VALID_DURATIONS={15,30,60,120,300,600}
MIN_SHOTS={15:3,30:5,60:8,120:12,300:20,600:30}
ASPECTS={'landscape':(1920,1080),'portrait':(1080,1920),'square':(1080,1080)}

def cmd(args):
    p=subprocess.run([str(a) for a in args],stdout=subprocess.PIPE,
                     stderr=subprocess.PIPE,text=True)
    if p.returncode:
        raise RuntimeError('Command failed: '+' '.join(map(str,args[:8]))+'\n'+p.stderr[-2200:])
    return p.stdout
def media(path):
    x=json.loads(cmd(['ffprobe','-v','error','-show_format','-show_streams','-of','json',path]))
    streams=x.get('streams',[])
    v=next((s for s in streams if s.get('codec_type')=='video'),None)
    return {'duration':float(x['format'].get('duration',0)),'video':v,'streams':streams}
def within_asset(path,root):
    if not isinstance(path,str) or not path or len(path)>300:
        raise ValueError('Missing or invalid local media reference')
    p=Path(path)
    if p.is_absolute() or any(x in ('..','.') for x in p.parts):
        raise ValueError('No absolute paths or traversal in scene media references')
    r=(root/p).resolve()
    if not r.is_relative_to(root.resolve()) or not r.is_file():
        raise ValueError('Asset is missing or escapes approved asset root: '+path)
    if r.suffix.lower() not in ('.mp4','.mov','.mkv','.webm','.wav','.mp3','.flac'):
        raise ValueError('Media type not supported: '+path)
    return r
def validate(project,root):
    if not isinstance(project,dict) or project.get('schema')!='elijah-film-project-v1':
        raise ValueError('Export a Film Studio project JSON first')
    duration=project.get('duration')
    if type(duration) is not int or duration not in VALID_DURATIONS:
        raise ValueError('Choose exact 15, 30, 60, 120, 300 or 600-second master')
    aspect=project.get('aspect')
    if aspect not in ASPECTS:raise ValueError('Invalid aspect')
    scenes=project.get('scenes',[])
    if not isinstance(scenes,list) or len(scenes)<MIN_SHOTS[duration] or len(scenes)>120:
        raise ValueError('Insufficient genuinely different scenes for requested film length')
    if sum(s.get('duration',0) for s in scenes)!=duration:
        raise ValueError('Scene time must exactly equal requested video duration')
    if any(type(s.get('duration')) is not int or not 1<=s['duration']<=60 for s in scenes):
        raise ValueError('Each scene duration must be a positive integer no greater than 60')
    if not all(s.get('media_rights') and s.get('reviewed') is True and s.get('direction') for s in scenes):
        raise ValueError('Each shot needs written direction, rights proof and human scene review')
    if len({s.get('id') for s in scenes})!=len(scenes):
        raise ValueError('Scene IDs must be unique')
    voice=project.get('voice') or {}
    music=project.get('music') or {}
    if voice.get('mode') not in ('licensed-recording','generate-local-draft'):
        raise ValueError('Voice track required: approved recording or local draft TTS')
    if music.get('mode') not in ('licensed-track','generate-original-draft'):
        raise ValueError('Soundtrack required: approved recording or original draft score')
    if voice['mode']=='licensed-recording' and (not voice.get('rights') or not voice.get('reference')):
        raise ValueError('Voice rights and real WAV file required')
    if music['mode']=='licensed-track' and (not music.get('rights') or not music.get('reference')):
        raise ValueError('Music rights and soundtrack file required')
    if voice['mode']=='generate-local-draft' and not shutil.which('espeak-ng'):
        raise RuntimeError('Install free espeak-ng for a ROBOTIC technical narration draft')
    checked=[];ranges={}
    for i,s in enumerate(scenes):
        p=within_asset(s.get('media_ref'),root)
        if p.suffix.lower() not in ('.mp4','.mov','.mkv','.webm'):
            raise ValueError('Scene footage must be an actual video file')
        m=media(p)
        if not m['video']:raise ValueError('No real video track in scene media')
        start=s.get('source_in',0)
        if type(start) not in (float,int) or not math.isfinite(start) or start<0:
            raise ValueError('Invalid scene source_in point')
        if m['duration']+0.04 < start+s['duration']:
            raise ValueError(f'Shot {i+1} requests more footage than actual source contains')
        for previous in ranges.get(str(p),[]):
            if max(previous[0],start)<min(previous[1],start+s['duration'])-.05:
                raise ValueError('Repeated/overlapping exact footage is not an authored longer movie')
        ranges.setdefault(str(p),[]).append((start,start+s['duration']))
        checked.append({'path':p,'start':start,'duration':s['duration'],'narration':str(s.get('narration') or '')[:500]})
    if duration>=120 and len(ranges)<max(3,MIN_SHOTS[duration]//3):
        raise ValueError('Longform project lacks enough distinct source footage; cannot loop short clips')
    for mode,obj in [('voice',voice),('music',music)]:
        if obj['mode'].startswith('licensed-'):
            p=within_asset(obj.get('reference'),root)
            if p.suffix.lower() not in ('.wav','.mp3','.flac'):
                raise ValueError(mode+' track must be genuine approved audio')
            if media(p)['duration']+0.04<duration:
                raise ValueError(mode+' music/voice audio too short for full film; no hidden looping')
    return checked
def encode_scene(item,path,size,fps,quality):
    w,h=size;ss=float(item['start']);d=int(item['duration'])
    cmd(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(ss),
         '-i',str(item['path']),'-an',
         '-vf',f'fps={fps},scale={w}:{h}:force_original_aspect_ratio=increase,crop={w}:{h},setsar=1,format=yuv420p',
         '-frames:v',str(d*fps),'-r',str(fps),'-c:v','libx264',
         '-preset','ultrafast' if quality=='preview' else 'veryfast',
         '-crf','24' if quality=='preview' else '19',
         '-pix_fmt','yuv420p','-movflags','+faststart',str(path)])
    return path
def write_concat(paths,file):
    def safe(s):
        return str(s).replace("'", "'\\''")
    file.write_text(''.join("file '"+safe(x)+"'\n" for x in paths),encoding='utf8')
def build_voice(items,voice,assetroot,work,duration):
    out=work/'voice.wav'
    if voice['mode']=='licensed-recording':
        p=within_asset(voice['reference'],assetroot)
        cmd(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(p),'-t',str(duration),
             '-ar','48000','-ac','2','-c:a','pcm_s16le',str(out)])
        return out
    snippets=[]
    for i,s in enumerate(items):
        dest=work/f'narration-{i:03d}.wav'
        raw=work/f'robotic-{i:03d}.wav'
        if s['narration'].strip():
            cmd(['espeak-ng','-v','en-us','-s','152','-w',str(raw),s['narration'].strip()])
            voice_length=media(raw)['duration']
            if voice_length>s['duration']*1.32:
                raise ValueError(f'Scene {i+1} narration is too long; shorten spoken script or extend shot duration')
            speed=max(1.0,voice_length/s['duration'])
            cmd(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(raw),
                 '-af',f'atempo={speed:.5f},aresample=48000,apad,atrim=duration={s["duration"]}',
                 '-ac','2','-ar','48000','-c:a','pcm_s16le',str(dest)])
        else:
            cmd(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','lavfi',
                 '-i','anullsrc=r=48000:cl=stereo','-t',str(s['duration']),
                 '-c:a','pcm_s16le',str(dest)])
        snippets.append(dest)
    playlist=work/'voice-concat.txt';write_concat(snippets,playlist)
    cmd(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','concat','-safe','0',
         '-i',str(playlist),'-t',str(duration),'-c:a','pcm_s16le',str(out)])
    return out
def build_music(music,root,work,duration):
    out=work/'music.wav'
    if music['mode']=='licensed-track':
        input=within_asset(music['reference'],root)
        cmd(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(input),
             '-t',str(duration),'-ar','48000','-ac','2','-c:a','pcm_s16le',str(out)])
    else:
        # Original source-free harmonic drone: clearly a DRAFT mix, not commercial music.
        cmd(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','lavfi',
             '-i',f'sine=frequency=82.41:sample_rate=48000:duration={duration}',
             '-f','lavfi','-i',f'sine=frequency=123.47:sample_rate=48000:duration={duration}',
             '-filter_complex','[0:a]volume=0.11[a];[1:a]volume=0.065[b];'
               '[a][b]amix=inputs=2:normalize=0,afade=t=in:st=0:d=1,'
               f'afade=t=out:st={max(0,duration-2)}:d=2,'
               'aformat=channel_layouts=stereo[m]',
             '-map','[m]','-ar','48000','-c:a','pcm_s16le',str(out)])
    return out
def render(project,assets,out,work,quality='preview'):
    assets=assets.resolve();work=work.resolve();work.mkdir(parents=True,exist_ok=True)
    checked=validate(project,assets)
    width,height=ASPECTS[project['aspect']]
    if quality=='preview':width//=2;height//=2
    fps=24;segments=[]
    for i,item in enumerate(checked):
        p=work/f'scene-{i:03d}.mp4'
        encode_scene(item,p,(width,height),fps,quality);segments.append(p)
    playlist=work/'scene-concat.txt';write_concat(segments,playlist)
    picture=work/'picture.mp4'
    cmd(['ffmpeg','-y','-hide_banner','-loglevel','error','-f','concat','-safe','0',
         '-i',str(playlist),'-c:v','copy',str(picture)])
    voice=build_voice(checked,project['voice'],assets,work,project['duration'])
    music=build_music(project['music'],assets,work,project['duration'])
    out=out.resolve();out.parent.mkdir(parents=True,exist_ok=True)
    cmd(['ffmpeg','-hide_banner','-loglevel','error','-y',
         '-i',str(picture),'-i',str(voice),'-i',str(music),
         '-filter_complex','[1:a]volume=0.96[vo];[2:a]volume=0.36[mu];'
             '[vo][mu]amix=inputs=2:duration=first:normalize=0,'
             'alimiter=limit=0.90:level=0[a]',
         '-map','0:v:0','-map','[a]','-t',str(project['duration']),
         '-c:v','copy','-c:a','aac','-b:a','160k','-movflags','+faststart',str(out)])
    master=media(out)
    streams=master['streams']
    v=next((s for s in streams if s.get('codec_type')=='video'),{})
    a=next((s for s in streams if s.get('codec_type')=='audio'),{})
    if (v.get('width'),v.get('height'))!=(width,height) or a.get('codec_name')!='aac':
        raise RuntimeError('Master H264/AAC verification failed')
    if abs(master['duration']-project['duration'])>.1:raise RuntimeError('Rendered length differs from authored timeline')
    report={'title':project.get('title'),'expected_duration':project['duration'],
        'actual_duration':master['duration'],'scenes':len(checked),
        'actual_video':str(out),'media_bytes':out.stat().st_size,
        'video_width':width,'video_height':height,'video_fps':fps,
        'video_codec':v.get('codec_name'),'audio_codec':a.get('codec_name'),
        'has_actual_voice_track':True,'has_actual_music_track':True,
        'voice_mode':project['voice']['mode'],'music_mode':project['music']['mode'],
        'paid_services_used':False,'gpu_used':False,
        'robotic_voice_is_a_demo_not_professional_voice':project['voice']['mode']=='generate-local-draft',
        'technically_verified':True,'human_creative_approved':False,
        'full_length_authored_footage_not_looped':True,
        'warning':'Audio and source rights must be independently reviewed. An MP4 pass does not mean commercial quality.'}
    (out.parent/(out.stem+'.qa.json')).write_text(json.dumps(report,indent=2)+'\n')
    return report
def main():
    p=argparse.ArgumentParser()
    p.add_argument('project',type=Path);p.add_argument('--assets',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True)
    p.add_argument('--work',type=Path,required=True)
    p.add_argument('--quality',choices=['preview','master'],default='preview')
    a=p.parse_args()
    f=a.project.read_bytes()
    if len(f)>200000:raise ValueError('Project too large')
    project=json.loads(f)
    report=render(project,a.assets,a.output,a.work,a.quality)
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
