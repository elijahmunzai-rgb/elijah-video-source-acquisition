#!/usr/bin/env python3
"""Evidence-based MP4 diagnostics; cannot certify artistic quality.

python engine/production_audit.py path.mp4 --output-json results.json --voice-required
"""
import argparse, json, re, subprocess
from pathlib import Path


def run(args):
    r=subprocess.run(args,capture_output=True,text=True,check=True)
    return r.stdout, r.stderr


def audit(path, voice_required=False):
    path = Path(path)
    if not path.exists(): raise FileNotFoundError(path)
    out,_=run(['ffprobe','-v','error','-show_format','-show_streams','-of','json',str(path)])
    probe=json.loads(out)
    streams=probe.get('streams',[])
    video=next((s for s in streams if s.get('codec_type')=='video'),None)
    audio=next((s for s in streams if s.get('codec_type')=='audio'),None)
    issues=[]; warnings=[]
    dur=float(probe['format'].get('duration',0))
    if not video: issues.append('Missing video stream')
    if not audio: issues.append('Missing audio stream')
    vbit=int(video.get('bit_rate',0) or 0) if video else 0
    if vbit==0 and video:
        fmt_bit=int(probe['format'].get('bit_rate',0) or 0)
        vbit=max(0, fmt_bit-(int(audio.get('bit_rate',0) or 0) if audio else 0))
    if video and video.get('codec_name')=='h264' and video.get('pix_fmt')!='yuv420p':warnings.append('H.264 output is not yuv420p (compatibility risk)')
    if video and video.get('width',0)>=1080 and video.get('height',0)>=1920 and vbit and vbit<4000000:
        warnings.append(f'Video bitrate {vbit/1e6:.2f} Mbps is low for detailed premium vertical H.264; review motion detail and output quality manually')
    if dur<=0:issues.append('Invalid duration')
    loudness=None
    if audio:
        _out, err=run(['ffmpeg','-hide_banner','-nostats','-i',str(path),'-vn',
                      '-af','loudnorm=I=-16:TP=-1.5:LRA=9:print_format=json','-f','null','-'])
        matches=re.findall(r'\{\s*"input_i"\s*:\s*"[^"]+".*?\}',err,re.S)
        if matches:
            d=json.loads(matches[-1]);
            loudness={k: float(d[k]) for k in ['input_i','input_tp','input_lra']}
            if loudness['input_i'] < -19: warnings.append(f'Audio is quiet ({loudness["input_i"]:.1f} LUFS), target commercial mix near -16 LUFS')
            if loudness['input_i'] > -12: warnings.append(f'Audio is loud ({loudness["input_i"]:.1f} LUFS), possible listener fatigue')
            if loudness['input_tp'] > -1: warnings.append('True peak too close to clipping')
            if loudness['input_lra'] < 2.5: warnings.append('Very low audio dynamics; inspect whether soundtrack is repetitive/overcompressed')
    if voice_required:
        # Speech detection requires ASR/VAD and listening, both not performed by this CLI.
        warnings.append('Voiceover requested: audible verified narration and accurate captions MUST be checked manually; an audio stream alone is insufficient')
    return {'file':str(path), 'duration_sec':dur, 'resolution':[video.get('width'),video.get('height')] if video else None,
            'video_codec':video.get('codec_name') if video else None,'video_bitrate_mbps':round(vbit/1e6,2),
            'audio_codec':audio.get('codec_name') if audio else None,'audio_measured':loudness,
            'technical_issues':issues,'review_flags':warnings,
            'creative_qa':'NOT_ASSESSED; requires human review of full video, licensed source footage, timing, originality and voice mix'}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('video')
    p.add_argument('--output-json',type=Path)
    p.add_argument('--voice-required',action='store_true')
    a=p.parse_args()
    d=audit(a.video,a.voice_required)
    msg=json.dumps(d,indent=2)
    print(msg)
    if a.output_json: a.output_json.write_text(msg+'\n')
    if d['technical_issues']: raise SystemExit(2)

if __name__=='__main__':main()
