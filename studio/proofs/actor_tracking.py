#!/usr/bin/env python3
"""Recorded human footage test: measurable optical flow; NOT synthetic-human generation."""
import argparse,json,cv2,numpy as np,subprocess,time
from pathlib import Path
p=argparse.ArgumentParser()
p.add_argument("source");p.add_argument("output");p.add_argument("report");p.add_argument("--frames",type=int,default=72)
a=p.parse_args()
cap=cv2.VideoCapture(a.source)
if not cap.isOpened():raise RuntimeError("Cannot open real footage")
fps=cap.get(cv2.CAP_PROP_FPS) or 24; W,H=480,848
out=Path(a.output);out.parent.mkdir(parents=True,exist_ok=True)
tmp=out.with_suffix(".raw.mp4")
writer=cv2.VideoWriter(str(tmp),cv2.VideoWriter_fourcc(*"mp4v"),fps,(W,H))
if not writer.isOpened():raise RuntimeError("VideoWriter failed")
prev=None;features=None;count=0;flow=0;affine_ok=0;errors=[];inliers=[]
face=cv2.CascadeClassifier(cv2.data.haarcascades+"haarcascade_frontalface_default.xml")
face_detects=0;smoothed=None;t0=time.perf_counter()
while count<a.frames:
    ok,frame=cap.read()
    if not ok:break
    h,w=frame.shape[:2];scale=min(W/w,H/h)
    tw,th=round(w*scale),round(h*scale)
    resized=cv2.resize(frame,(tw,th),interpolation=cv2.INTER_AREA)
    canvas=np.full((H,W,3),(12,19,31),dtype=np.uint8)
    x0=(W-tw)//2;y0=(H-th)//2
    canvas[y0:y0+th,x0:x0+tw]=resized
    gray=cv2.cvtColor(canvas,cv2.COLOR_BGR2GRAY)
    if count%5==0:
        detections=face.detectMultiScale(gray,1.12,3,minSize=(32,32))
        if len(detections):
            x,y,fw,fh=max(detections,key=lambda f:f[2]*f[3])
            v=np.array((x,y,fw,fh),np.float32)
            smoothed=v if smoothed is None else (.76*smoothed+.24*v)
            face_detects+=1
    if prev is not None and features is not None and len(features)>=10:
        nxt,status,_=cv2.calcOpticalFlowPyrLK(prev,gray,features,None,winSize=(19,19),maxLevel=3)
        if nxt is not None:
            left=features[status.ravel()==1].reshape(-1,2)
            right=nxt[status.ravel()==1].reshape(-1,2)
            if len(left)>=10:
                M,mask=cv2.estimateAffinePartial2D(left,right,method=cv2.RANSAC,ransacReprojThreshold=3)
                flow+=1
                if M is not None and mask is not None and mask.sum()>=6:
                    valid=mask.ravel().astype(bool)
                    dist=np.linalg.norm(np.c_[left,np.ones(len(left))]@M.T-right,axis=1)[valid]
                    errors.append(float(np.median(dist)));inliers.append(int(valid.sum()));affine_ok+=1
        features=None
    if features is None:features=cv2.goodFeaturesToTrack(gray,140,.012,9)
    prev=gray
    cv2.rectangle(canvas,(0,0),(W,71),(12,20,36),-1)
    cv2.putText(canvas,"ELIJAH STUDIO  /  HUMAN-FOOTAGE TEST",(12,26),cv2.FONT_HERSHEY_SIMPLEX,.51,(247,244,236),1,cv2.LINE_AA)
    cv2.putText(canvas,"Measured optical flow, not AI actor synthesis",(12,51),cv2.FONT_HERSHEY_SIMPLEX,.42,(105,215,238),1,cv2.LINE_AA)
    if smoothed is not None:
        x,y,fw,fh=map(int,smoothed)
        cv2.rectangle(canvas,(max(x,0),max(y,72)),(min(W-1,x+fw),min(H-1,y+fh)),(105,215,238),1)
    cv2.rectangle(canvas,(0,H-42),(W,H),(12,20,36),-1)
    cv2.putText(canvas,f"FRAME {count:03d}   /   INLIERS {inliers[-1] if inliers else 0:03d}",(12,H-15),cv2.FONT_HERSHEY_SIMPLEX,.48,(224,212,172),1,cv2.LINE_AA)
    writer.write(canvas);count+=1
writer.release();cap.release()
if count<20:raise RuntimeError("Too few frames")
subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y","-i",str(tmp),"-c:v","libx264","-crf","20","-pix_fmt","yuv420p",str(out)],check=True)
tmp.unlink()
result={"proof":"licensed prerecorded actual human, optical flow tracking","frames":count,
"flow_frames":flow,"ransac_inlier_frames":affine_ok,"track_ratio":affine_ok/max(1,flow),
"median_inliers":float(np.median(inliers)) if inliers else None,
"median_reprojection_error_px":float(np.median(errors)) if errors else None,
"face_detection_sample_frames":face_detects,"elapsed_seconds":round(time.perf_counter()-t0,3),
"recorded_human":True,"synthetic_photoreal_actor_verified":False,
"hollywood_quality_verified":False,"license":"CC0 footage via Wikimedia Commons",
"passes_tracking":affine_ok>=count*.5}
Path(a.report).write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
if not result["passes_tracking"]:raise SystemExit(2)
