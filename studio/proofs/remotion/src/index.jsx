import React from "react";
import {registerRoot,Composition,AbsoluteFill,useCurrentFrame,interpolate,spring,useVideoConfig} from "remotion";
const Scene=()=>{
  const frame=useCurrentFrame();
  const {fps}=useVideoConfig();
  const emerge=spring({frame,fps,config:{mass:1,damping:17,stiffness:85}});
  const angle=interpolate(frame,[0,72],[-12,14]);
  const line=interpolate(frame,[2,55],[0,520],{extrapolateLeft:"clamp",extrapolateRight:"clamp"});
  return <AbsoluteFill style={{background:"linear-gradient(135deg,#070c13,#152235)",color:"#f3efe6",fontFamily:"Arial,sans-serif",overflow:"hidden"}}>
    <div style={{position:"absolute",left:80,top:38,fontSize:16,fontWeight:700,letterSpacing:5,color:"#78dbef"}}>ELIJAH FILM STUDIO</div>
    <div style={{position:"absolute",width:300,height:300,border:"3px solid #ddbb82",borderRadius:80,top:30,left:250,transform:"rotate("+angle+"deg) scale("+emerge+")",boxShadow:"0 0 90px #5ec9e640, inset 0 0 60px #ffffff16"}}/>
    <div style={{position:"absolute",left:58,top:126,fontSize:54,fontWeight:800,transform:"translateY("+(1-emerge)*50+"px)",opacity:emerge}}>CODE-DRIVEN</div>
    <div style={{position:"absolute",left:62,top:189,fontSize:40,fontWeight:700,color:"#e0b57b",opacity:emerge}}>CINEMA MOTION.</div>
    <div style={{position:"absolute",top:277,left:60,width:line,height:3,background:"#81d7ef"}}/>
    <div style={{position:"absolute",bottom:18,left:60,fontSize:13,letterSpacing:2,color:"#99b1c0"}}>ACTUAL REMOTION 4 RUNTIME · FRAME-DETERMINISTIC ANIMATION</div>
  </AbsoluteFill>;
};
registerRoot(()=> <Composition id="Motion" component={Scene} durationInFrames={72} fps={24} width={640} height={360}/>);
