#!/usr/bin/env python3
"""Dialogue-first FFmpeg audio postproduction, no paid services.

Requires source recordings/tracks with appropriate licenses and FFmpeg.
This is a *mixer*, not an original music composer or speech generator.

Examples:
python engine/audio_mix.py --voice voice.wav --music music.wav --output master.wav --duration 30
python engine/audio_mix.py --music music.wav --effects fx.wav --output master.wav --duration 30
"""
import argparse
import subprocess
from pathlib import Path


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument('--voice', type=Path, help='Recorded or licensed dialogue/audio')
    p.add_argument('--music', type=Path, help='Licensed soundtrack music')
    p.add_argument('--effects', type=Path, help='Optional ready-to-mix effects stem')
    p.add_argument('--output', required=True, type=Path)
    p.add_argument('--duration', required=True, type=float)
    p.add_argument('--target-lufs', type=float, default=-16.0)
    p.add_argument('--music-gain', type=float, default=0.22)
    p.add_argument('--effects-gain', type=float, default=0.48)
    return p.parse_args()


def build_command(a):
    assert a.duration > 0 and a.duration <= 600, 'Duration must be 0-600 seconds.'
    assert a.voice or a.music, 'Provide voice and/or music.'
    assert -25 <= a.target_lufs <= -10, 'Target LUFS outside safe range.'
    assert 0 < a.music_gain <= 1.0
    assert 0 < a.effects_gain <= 1.0
    inputs = [x for x in [a.voice, a.music, a.effects] if x]
    for x in inputs:
        if not x.is_file():
            raise FileNotFoundError(x)
    cmd = ['ffmpeg', '-hide_banner', '-loglevel', 'warning', '-y']
    for f in inputs:
        cmd += ['-i', str(f)]
    parts = []
    names = {}
    for i, (role, path) in enumerate([('voice', a.voice), ('music', a.music), ('effects', a.effects)]):
        if not path: continue
        input_idx = inputs.index(path)
        settings = f'atrim=duration={a.duration},asetpts=PTS-STARTPTS,aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo'
        if role == 'voice':
            settings += ',highpass=f=75,acompressor=threshold=0.09:ratio=2.7:attack=5:release=140,volume=1'
        if role == 'music':
            settings += f',volume={a.music_gain},afade=t=in:st=0:d=0.35,afade=t=out:st={max(0,a.duration-1.3)}:d=1.3'
        if role == 'effects': settings += f',volume={a.effects_gain}'
        parts.append(f'[{input_idx}:a]{settings}[{role}]')
        names[role] = role
    if a.voice and a.music:
        # Duck music *in reaction to speech*, not with fixed generic volume alone.
        parts.append('[music][voice]sidechaincompress=threshold=0.025:ratio=9:attack=15:release=320[duck]')
        parts.append('[voice][duck]amix=inputs=2:normalize=0:duration=longest[main]')
        main = 'main'
    elif a.voice: main = 'voice'
    else: main = 'music'
    if a.effects:
        parts.append(f'[{main}][effects]amix=inputs=2:normalize=0:duration=longest[fxmix]')
        main = 'fxmix'
    parts.append(f'[{main}]alimiter=limit=0.92:attack=3:release=80,'
                 f'loudnorm=I={a.target_lufs}:TP=-1.5:LRA=9:print_format=summary,'
                 'aresample=48000,atrim=duration='+str(a.duration)+'[out]')
    cmd += ['-filter_complex', ';'.join(parts), '-map', '[out]', '-t', str(a.duration),
            '-ac', '2', '-c:a', 'pcm_s24le', str(a.output)]
    return cmd


def main():
    a = parse_args()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(build_command(a), check=True)
    print('MIXED', a.output)

if __name__ == '__main__': main()
