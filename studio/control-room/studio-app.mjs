import {DURATIONS,startProject,validateProject,rebalance,buildProductionManifest,formatTime} from './project-schema.mjs';

const $=id=>document.getElementById(id);
const KEY='elijah-film-studio-local-draft-v1';
let project=startProject(),tick=0,anim=null,since=0;
const errText=e=>e instanceof Error?e.message:String(e);
const fields=['title','duration','aspect','genre'];
function recover(){
 try{
  const saved=JSON.parse(localStorage.getItem(KEY)||'null');
  if(saved&&validateProject(saved).ok){project=saved;return;}
 }catch{}
}
function save(show=true){
 try{localStorage.setItem(KEY,JSON.stringify(project));if(show)$('savedAt').textContent='Saved locally';}
 catch(e){$('savedAt').textContent='Save blocked: '+errText(e);}
}
function node(tag,cls,text){
 const e=document.createElement(tag);
 if(cls)e.className=cls;if(text!==undefined)e.textContent=text;
 return e;
}
function capture(){
 project.title=$('filmTitle').value.trim();
 project.genre=$('filmGenre').value;
 project.aspect=$('filmAspect').value;
 project.voice={mode:$('voiceMode').value,reference:$('voiceRef').value.trim(),rights:$('voiceRights').value.trim()};
 project.music={mode:$('musicMode').value,reference:$('musicRef').value.trim(),rights:$('musicRights').value.trim()};
 project.subtitles=$('subtitles').checked;
 project.release_approved=false;
 save(false);showReadiness();
}
function refreshHeader(){
 $('filmTitle').value=project.title;$('filmDuration').value=String(project.duration);
 $('filmAspect').value=project.aspect;$('filmGenre').value=project.genre;
 $('voiceMode').value=project.voice?.mode||'none';$('voiceRef').value=project.voice?.reference||'';
 $('voiceRights').value=project.voice?.rights||'';
 $('musicMode').value=project.music?.mode||'none';$('musicRef').value=project.music?.reference||'';
 $('musicRights').value=project.music?.rights||'';
 $('subtitles').checked=project.subtitles!==false;
}
function updateScene(index,key,value,needsTimeline=false){
 project.scenes[index][key]=value;
 project.scenes[index].reviewed=false;
 save(false);showReadiness();if(needsTimeline)drawTimeline();drawPreview();
}
function sceneInput(index,key,{long=false,placeholder='',label='',type='text'}={}){
 const wrap=node('label');wrap.textContent=label;
 const el=node(long?'textarea':'input');
 if(!long)el.type=type;
 el.value=String(project.scenes[index][key]??'');
 el.placeholder=placeholder;if(!long)el.maxLength=900;
 el.addEventListener('input',()=>{
  const val=(key==='duration'||key==='source_in')?Number(el.value):el.value;
  updateScene(index,key,val,key==='duration');
 });
 wrap.append(el);return wrap;
}
function refreshScenes(){
 const root=$('scenes');root.replaceChildren();
 project.scenes.forEach((s,i)=>{
  const d=node('details','scene');if(i===0)d.open=true;
  const summary=node('summary'),left=node('div'),title=node('strong',null,String(i+1).padStart(2,'0')+' · '+s.beat),sub=node('div','minor',s.direction||'Direction not written');
  left.append(title,sub);
  const state=node('div','sceneState',s.duration+'s'+(s.reviewed?' · reviewed':' · needs review'));
  summary.append(left,state);d.append(summary);
  const body=node('div','sceneFields');
  const pair=node('div','pair');pair.append(sceneInput(i,'beat',{label:'Story beat',placeholder:'Hook / conflict / reveal'}),sceneInput(i,'duration',{label:'Seconds in shot',type:'number'}));
  body.append(pair,sceneInput(i,'direction',{label:'Scene direction and action',long:true,placeholder:'What actually happens in this shot? Character, camera, action and story...'}));
  body.append(sceneInput(i,'media_ref',{label:'Real source footage / scene asset',placeholder:'Approved original video file or Blender render path'}));
  body.append(sceneInput(i,'source_in',{label:'Start inside source footage (seconds)',type:'number',placeholder:'0'}));
  body.append(sceneInput(i,'media_rights',{label:'License / release reference',placeholder:'Creator, source license or written permission'}));
  const line=node('div','pair');line.append(sceneInput(i,'camera',{label:'Camera / VFX',placeholder:'Tracking / wide / close-up'}),sceneInput(i,'caption',{label:'On-screen subtitle / copy',placeholder:'Short purposeful copy'}));
  body.append(line,sceneInput(i,'narration',{label:'Voiceover / dialogue for this shot',long:true,placeholder:'Spoken words (audio assigned separately)'}));
  const tools=node('div','controls');
  const reviewed=node('button',null,s.reviewed?'Review approved ✓':'Mark shot reviewed');
  reviewed.addEventListener('click',()=>{project.scenes[i].reviewed=!project.scenes[i].reviewed;save();refreshScenes();showReadiness();});
  const del=node('button',null,'Remove shot');
  del.disabled=project.scenes.length<=1;
  del.addEventListener('click',()=>{if(project.scenes.length<2)return;project.scenes.splice(i,1);project=rebalance(project);save();refreshScenes();drawTimeline();showReadiness();});
  const duplicate=node('button',null,'Add shot after');
  duplicate.addEventListener('click',()=>{if(project.scenes.length>=Math.min(120,project.duration))return;
   project.scenes.splice(i+1,0,{id:'scene-'+Date.now().toString(36)+'-'+i,duration:1,beat:'NEW SHOT',direction:'',media_ref:'',source_in:0,media_rights:'',camera:'',narration:'',caption:'',reviewed:false});
   project=rebalance(project);save();refreshScenes();drawTimeline();showReadiness();});
  tools.append(reviewed,duplicate,del);body.append(tools);d.append(body);root.append(d);
 });
 $('sceneStats').textContent=project.scenes.length+' authored shots';
 $('durationPill').textContent=formatTime(project.duration);
 $('timing').textContent='Target: '+formatTime(project.duration)+' · actual: '+formatTime(project.scenes.reduce((s,x)=>s+Number(x.duration||0),0));
}
function drawTimeline(){
 const root=$('timeline');root.replaceChildren();
 for(const [i,s] of project.scenes.entries()){
  const b=node('div','tick',String(i+1));b.style.flex=String(Math.max(1,Number(s.duration)||1));
  b.title='Scene '+(i+1)+' · '+s.beat+' · '+s.duration+' sec';
  b.tabIndex=0;b.setAttribute('role','button');
  b.addEventListener('click',()=>seekScene(i));
  b.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();seekScene(i);}});
  root.append(b);
 }
}
function seekScene(i){tick=project.scenes.slice(0,i).reduce((s,c)=>s+Number(c.duration||0),0);since=performance.now();drawPreview();}
function drawPreview(){
 const canvas=$('storyboard'),c=canvas.getContext('2d'),w=canvas.width,h=canvas.height;
 c.fillStyle='#080f19';c.fillRect(0,0,w,h);
 const grad=c.createRadialGradient(590,170,20,430,210,490);
 grad.addColorStop(0,'#253c58');grad.addColorStop(1,'#08101a');c.fillStyle=grad;c.fillRect(0,0,w,h);
 c.strokeStyle='#305065';c.lineWidth=1;
 for(let k=0;k<18;k++){c.beginPath();c.moveTo(k*50-65,h);c.lineTo(w*.7,230);c.stroke();}
 c.fillStyle='#e5b779';c.font='16px sans-serif';c.fillText('STORYBOARD PROTOTYPE / NOT RENDERED FOOTAGE',40,45);
 let pos=0,index=0;for(const [i,s] of project.scenes.entries()){if(tick>=pos&&tick<pos+Math.max(1,s.duration)){index=i;break;}pos+=Math.max(1,s.duration);}
 const scene=project.scenes[index];if(!scene)return;
 c.fillStyle='#eef2f5';c.font='bold 35px sans-serif';c.fillText((scene.beat||'SHOT').slice(0,24),45,210);
 c.font='21px sans-serif';c.fillStyle='#bfcee0';
 const words=(scene.direction||'Add real visual direction and source footage').match(/.{1,47}(?:\s|$)/g)||[];
 words.slice(0,3).forEach((x,i)=>c.fillText(x.trim(),45,253+i*32));
 c.font='19px sans-serif';c.fillStyle='#cfae7b';
 c.fillText('SHOT '+String(index+1).padStart(2,'0')+' / '+project.scenes.length,45,h-55);
 c.fillText(formatTime(tick)+' / '+formatTime(project.duration),w-195,h-55);
 $('previewState').textContent='Storyboard · '+formatTime(tick)+' / '+formatTime(project.duration);
 Array.from($('timeline').children).forEach((n,i)=>n.classList.toggle('current',i===index));
}
function play(){
 if(anim)return;
 $('playStory').textContent='Playing timeline';
 since=performance.now();
 const frame=t=>{if(!anim)return;tick=Math.min(project.duration,tick+(t-since)/1000);since=t;drawPreview();
  if(tick>=project.duration){stop();return;}anim=requestAnimationFrame(frame);};
 anim=requestAnimationFrame(frame);
}
function stop(){if(anim)cancelAnimationFrame(anim);anim=null;$('playStory').textContent='Play animatic';if(tick>=project.duration)tick=0;drawPreview();}
function showReadiness(){
 const x=validateProject(project);$('readiness').textContent=
  (x.ok?'Timeline structurally valid.':'Timeline errors must be corrected.')+
  '\n'+(x.render_ready?'All scene references and reviews are present (not a rendered video).':'Not render-ready: missing actual footage/rights, reviewer approval and/or audio.')+
  '\n'+x.warnings.slice(0,6).map(s=>'• '+s).join('\n');
 return x;
}
function rebuild(){refreshHeader();refreshScenes();drawTimeline();drawPreview();showReadiness();}
function resetDuration(d){const value=Number(d);if(!DURATIONS.includes(value))return;
 const old=project;project=startProject({title:old.title,duration:value,aspect:old.aspect,genre:old.genre});
 project.voice=old.voice;project.music=old.music;project.subtitles=old.subtitles;
 $('validation').textContent='Duration changed. A fresh scene timeline was created because reusing short footage would be misleading.';
 save();stop();rebuild();
}
function exportJson(){
 capture();const q=validateProject(project);if(!q.ok){$('validation').textContent='Cannot export invalid project:\n'+q.errors.join('\n');return;}
 const data=JSON.stringify(buildProductionManifest(project),null,2);
 const blob=new Blob([data],{type:'application/json'}),url=URL.createObjectURL(blob);
 const a=document.createElement('a');a.href=url;
 a.download=(project.title.toLowerCase().replace(/[^a-z0-9]+/g,'-').slice(0,45)||'film')+'-'+project.duration+'s-production-project.json';
 document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1500);
 $('validation').textContent='Full project manifest exported. Rendering still needs real media files and a connected worker.';
}
$('filmDuration').addEventListener('change',e=>resetDuration(e.target.value));
for(const id of ['filmTitle','filmAspect','filmGenre','voiceMode','voiceRef','voiceRights','musicMode','musicRef','musicRights','subtitles']){
 $(id).addEventListener('input',capture);$(id).addEventListener('change',capture);
}
$('newProject').addEventListener('click',()=>{if(!confirm('Start a new locally stored draft? Export your current project first.'))return;stop();project=startProject();save();rebuild();});
$('balance').addEventListener('click',()=>{capture();try{project=rebalance(project);save();refreshScenes();drawTimeline();drawPreview();showReadiness();}catch(e){$('validation').textContent=errText(e);}});
$('addScene').addEventListener('click',()=>{if(project.scenes.length>=Math.min(120,project.duration))return;
 project.scenes.push({id:'scene-'+Date.now().toString(36),duration:1,beat:'NEW SHOT',direction:'',media_ref:'',source_in:0,media_rights:'',camera:'',narration:'',caption:'',reviewed:false});
 project=rebalance(project);save();refreshScenes();drawTimeline();showReadiness();});
$('saveBtn').addEventListener('click',()=>{capture();save();});
$('downloadBtn').addEventListener('click',exportJson);
$('preflightBtn').addEventListener('click',()=>{capture();const v=validateProject(project,{requireAssets:true});
 $('validation').textContent=(v.ok?'Production preflight structurally approved; no video was rendered.':'Production BLOCKED:')+'\n'+v.errors.map(s=>'✕ '+s).join('\n')+'\n'+v.warnings.map(s=>'• '+s).join('\n');});
$('playStory').addEventListener('click',()=>anim?stop():play());
$('stopStory').addEventListener('click',stop);
$('importBtn').addEventListener('click',()=>$('importFile').click());
$('importFile').addEventListener('change',async e=>{
 const file=e.target.files?.[0];if(!file)return;
 if(file.size>200000){$('validation').textContent='File too large';return;}
 try{const value=JSON.parse(await file.text());const v=validateProject(value);
  if(!v.ok)throw Error(v.errors.join('; '));
  stop();project=value;project.privacy='local-browser-only';project.release_approved=false;save();rebuild();
  $('validation').textContent='Imported and saved locally. Original footage was NOT uploaded.';
 }catch(ex){$('validation').textContent='Import rejected: '+errText(ex);}
 e.target.value='';
});
recover();rebuild();
