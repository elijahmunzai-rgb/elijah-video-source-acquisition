#!/usr/bin/env python3
"""Calibrated perspective-n-point camera pose regression, synthetic correspondences.
Not a claim of calibrated camera tracking on recorded humans.
"""
import cv2,numpy as np,json
from pathlib import Path
np.random.seed(91)
K=np.array([[920.,0,480.],[0,920.,270.],[0,0,1.]])
points=np.array([(x,y,z) for x in [-.8,0,.8] for y in [-.6,.4] for z in [0.,.5,1.2]],np.float64)
reproj=[];rot=[];trans=[]
for i in range(24):
  a=i/23
  r=np.array([.025+.05*a,-.08+.1*a,.02+.015*a])
  t=np.array([.1+.6*a,.05+.15*a,4.7+.25*a])
  xy,_=cv2.projectPoints(points,r,t,K,None)
  noisy=xy.reshape(-1,2)+np.random.normal(0,.24,(len(points),2))
  ok,R,T,inliers=cv2.solvePnPRansac(points,noisy,K,None,reprojectionError=1.6,iterationsCount=250,flags=cv2.SOLVEPNP_ITERATIVE)
  if not ok or len(inliers)<14:raise RuntimeError("pnp frame failure")
  p,_=cv2.projectPoints(points,R,T,K,None)
  reproj.append(np.median(np.linalg.norm(p.reshape(-1,2)-noisy,axis=1)))
  A,_=cv2.Rodrigues(R);B,_=cv2.Rodrigues(r)
  rot.append(np.degrees(np.arccos(np.clip((np.trace(A@B.T)-1)/2,-1,1))))
  trans.append(np.linalg.norm(T.ravel()-t))
report={"frames":24,"3d_points_per_frame":len(points),
 "median_reprojection_px":float(np.median(reproj)),
 "median_rotation_error_deg":float(np.median(rot)),
 "median_translation_error_world_units":float(np.median(trans)),
 "synthetic_correspondences_only":True,
 "calibrated_recorded_actor_footage_verified":False,
 "hollywood_grade_verified":False}
report["pass"]=report["median_reprojection_px"]<.5 and report["median_rotation_error_deg"]<.3 and report["median_translation_error_world_units"]<.1
out=Path("proof");out.mkdir(exist_ok=True)
(out/"calibrated_pnp_report.json").write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
if not report["pass"]:raise SystemExit(2)
