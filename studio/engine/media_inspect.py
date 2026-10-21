#!/usr/bin/env python3
"""Verify real exported video properties and sample a contact sheet with ffmpeg."""
import argparse,json,subprocess,shutil
from pathlib import Path

def probe(path):
    return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(path)],text=True))

def main():
    p=argparse.ArgumentParser();p.add_argument('video',type=Path);p.add_argument('--width',type=int)
    p.add_argument('--height',type=int);p.add_argument('--expected-seconds',type=float)
    p.add_argument('--audio',action='store_true',help='Require audio track')
    p.add_argument('--contact-sheet',type=Path);args=p.parse_args()
    if not args.video.is_file() or args.video.stat().st_size<5000:raise SystemExit('BAD: video missing or too small')
    info=probe(args.video); videos=[s for s in info.get('streams',[]) if s.get('codec_type')=='video']
    audio=[s for s in info.get('streams',[]) if s.get('codec_type')=='audio']
    if len(videos)!=1:raise SystemExit('BAD: expected exactly one video stream')
    stream=videos[0];duration=float(info['format']['duration'])
    if args.width is not None and stream['width']!=args.width:raise SystemExit('BAD: width mismatch')
    if args.height is not None and stream['height']!=args.height:raise SystemExit('BAD: height mismatch')
    if args.expected_seconds is not None and abs(duration-args.expected_seconds)>.075:raise SystemExit(f'BAD: duration {duration}')
    if args.audio and not audio:raise SystemExit('BAD: missing audio')
    if stream.get('codec_name')!='h264':raise SystemExit('BAD: expected h264')
    print(json.dumps({'QA':'STRUCTURAL_PASS','duration':duration,'width':stream['width'],'height':stream['height'],'codec':stream.get('codec_name'),'fps':stream.get('avg_frame_rate'),'audio_tracks':len(audio),'size_bytes':args.video.stat().st_size},indent=2))
    if args.contact_sheet:
        from PIL import Image, ImageOps, ImageDraw
        from io import BytesIO
        frames=[]
        for i in range(6):
            secs=(i+.5)/6*duration
            frame=subprocess.check_output(['ffmpeg','-hide_banner','-loglevel','error','-ss',str(secs),'-i',str(args.video),'-frames:v','1','-f','image2pipe','-vcodec','png','-'])
            im=Image.open(BytesIO(frame)).convert('RGB')
            im.thumbnail((270,480))
            canvas=Image.new('RGB',(292,520),'#1b1b1d');canvas.paste(im,((292-im.width)//2,12))
            ImageDraw.Draw(canvas).text((8,493),f'{secs:.2f}s',fill='white')
            frames.append(canvas)
        sheet=Image.new('RGB',(292*3,520*2),'#0c0c0e')
        for i,im in enumerate(frames):sheet.paste(im,((i%3)*292,(i//3)*520))
        args.contact_sheet.parent.mkdir(parents=True,exist_ok=True)
        sheet.save(args.contact_sheet);print('CONTACT_SHEET',args.contact_sheet)
if __name__=='__main__':main()
