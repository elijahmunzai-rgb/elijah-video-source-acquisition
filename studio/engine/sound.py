#!/usr/bin/env python3
"""Create an original algorithmic instrumental WAV bed with no samples or network."""
import argparse, json, math, wave, struct
from pathlib import Path
import numpy as np

def compose(duration=7.,sample_rate=22050,seed=3):
    n=int(duration*sample_rate); t=np.arange(n)/sample_rate
    out=np.zeros(n,dtype=np.float64)
    # a restrained harmonic bed: A minor chord with evolving filtered overtones
    freqs=(110,164.814,220,261.626,329.628)
    for i,f in enumerate(freqs):
        vibrato=1+.002*np.sin(2*math.pi*(.16+i*.042)*t+i)
        phase=2*math.pi*f*t*vibrato
        out+=(.045/(1+i*.28))*np.sin(phase + .2*np.sin(phase*.25))
    # purposeful soft pulse accents every two beats, synthetic signal only
    rng=np.random.default_rng(seed)
    for offset in np.arange(.0,duration,.78):
        idx=int(offset*sample_rate); span=min(int(.23*sample_rate),n-idx)
        if span<1:continue
        u=np.arange(span)/sample_rate
        puff=np.sin(2*math.pi*(65+115*np.exp(-u*22))*u)*np.exp(-u*22)
        out[idx:idx+span] += .11*puff
    start=np.clip(t/.20,0,1); end=np.clip((duration-t)/.58,0,1)
    out*=start*end
    maxv=max(.01,float(np.max(np.abs(out))))
    return (np.clip(out*.56/maxv,-.9,.9)*32767).astype('<i2')

def main():
    p=argparse.ArgumentParser();p.add_argument('output',type=Path);p.add_argument('--duration',type=float,default=7)
    args=p.parse_args();args.output.parent.mkdir(parents=True,exist_ok=True)
    sr=22050; data=compose(args.duration,sr)
    with wave.open(str(args.output),'wb') as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(sr);w.writeframes(data.tobytes())
    print('OK WAV',args.output)
if __name__=='__main__':main()
