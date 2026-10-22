// Studio project contracts. Local/private drafts are NEVER sent to public GitHub by this module.
export const DURATIONS=Object.freeze([15,30,60,120,300,600]);
export const ASPECTS=Object.freeze(['landscape','portrait','square']);
export const MIN_SHOTS=Object.freeze({'15':3,'30':5,'60':8,'120':12,'300':20,'600':30});
const MAX_SCENES=120;
const clean=(s,n=700)=>String(s??'').trim().slice(0,n);
export function formatTime(n){const s=Math.max(0,Math.floor(Number(n)||0));return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0');}
export function startProject({title='Untitled Film',duration=30,aspect='portrait',genre='Commercial'}={}){
  if(!DURATIONS.includes(Number(duration)))throw Error('Unsupported duration');
  if(!ASPECTS.includes(aspect))throw Error('Unsupported aspect');
  const n=MIN_SHOTS[String(duration)];
  const base=Math.floor(Number(duration)/n),extra=Number(duration)-base*n;
  const scenes=Array.from({length:n},(_,i)=>({
   id:'scene-'+String(i+1).padStart(3,'0'),duration:base+(i<extra?1:0),
   beat:i===0?'HOOK':i===n-1?'CLOSE':i<Math.ceil(n*.25)?'SETUP':i<Math.ceil(n*.72)?'STORY':'PAYOFF',
   direction:'',media_ref:'',media_rights:'',camera:'',narration:'',caption:'',reviewed:false
  }));
  return {schema:'elijah-film-project-v1',id:'draft-'+Date.now().toString(36),title:clean(title,80),
   duration:Number(duration),aspect,genre:clean(genre,40),privacy:'local-browser-only',
   voice:{mode:'none',reference:'',rights:''},music:{mode:'none',reference:'',rights:''},
   subtitles:true,scenes,release_approved:false,created_at:new Date().toISOString()};
}
export function validateProject(project,{requireAssets=false}={}){
 const errors=[],warn=[];
 if(!project||typeof project!=='object'||Array.isArray(project))return{ok:false,errors:['Project must be an object'],warnings:[]};
 if(project.schema!=='elijah-film-project-v1')errors.push('Invalid project schema');
 if(!DURATIONS.includes(project.duration))errors.push('Choose 15s, 30s, 60s, 2m, 5m or 10m');
 if(!ASPECTS.includes(project.aspect))errors.push('Invalid format');
 if(!clean(project.title))errors.push('Project title required');
 if(!Array.isArray(project.scenes)||!project.scenes.length||project.scenes.length>MAX_SCENES){errors.push('Scene count invalid');return{ok:false,errors,warnings:warn};}
 const min=MIN_SHOTS[String(project.duration)]||3;
 if(project.scenes.length<min)warn.push('Only '+project.scenes.length+' scenes; recommend at least '+min+' genuinely distinct shots');
 const ids=new Set();
 let elapsed=0,missingAssets=0,notApproved=0;
 for(let i=0;i<project.scenes.length;i++){
  const s=project.scenes[i];
  if(!s||typeof s!=='object'){errors.push('Scene '+(i+1)+' invalid');continue;}
  if(!Number.isInteger(s.duration)||s.duration<=0||s.duration>60)errors.push('Scene '+(i+1)+' duration must be 1..60 seconds');
  else elapsed+=s.duration;
  if(!clean(s.id,80)||ids.has(s.id))errors.push('Duplicate/missing scene ID');
  ids.add(s.id);
  if(!clean(s.direction))warn.push('Scene '+(i+1)+' missing creative direction');
  if(!clean(s.media_ref,450)||!clean(s.media_rights,250)){missingAssets++;if(requireAssets)errors.push('Scene '+(i+1)+' requires actual approved source asset and licensing');}
  if(!s.reviewed)notApproved++;
 }
 if(elapsed!==project.duration)errors.push('Scene lengths add to '+elapsed+'s, need '+project.duration+'s');
 if(!project.voice||project.voice.mode==='none')warn.push('No voice/narration selected');
 else if(project.voice.mode!=='generate-local-draft'&&(!clean(project.voice.reference)||!clean(project.voice.rights)))errors.push('Narration source and license required');
 if(!project.music||project.music.mode==='none')warn.push('No music/soundtrack selected');
 else if(project.music.mode!=='generate-original-draft'&&(!clean(project.music.reference)||!clean(project.music.rights)))errors.push('Soundtrack source and license required');
 if(notApproved)warn.push(notApproved+' scenes still require visual/creative review');
 if(missingAssets)warn.push(missingAssets+' scenes missing rights-cleared visual media');
 if(requireAssets && notApproved)errors.push('Cannot approve film without reviewing every scene');
 if(requireAssets && (!project.voice||project.voice.mode==='none'||!project.music||project.music.mode==='none'))errors.push('A film master must include a selected voice and soundtrack');
 if(project.release_approved!==true)warn.push('Release not approved; no auto-publishing');
 return {ok:errors.length===0,errors,warnings:warn,total:elapsed,scene_count:project.scenes.length,render_ready:errors.length===0&&missingAssets===0&&notApproved===0&&!!project.voice&&project.voice.mode!=='none'&&!!project.music&&project.music.mode!=='none'};
}
export function rebalance(project){
 const scenes=project.scenes;const n=scenes.length,base=Math.floor(project.duration/n),extra=project.duration-base*n;
 if(n>project.duration)throw Error('More scenes than seconds');
 return {...project,scenes:scenes.map((s,i)=>({...s,duration:base+(i<extra?1:0)}))};
}
export function buildProductionManifest(project){
 const status=validateProject(project);if(!status.ok)throw Error(status.errors.join('; '));
 let t=0;return {...project,scenes:project.scenes.map(s=>{const result={...s,start:t,end:t+s.duration};t+=s.duration;return result;}),
   production_status:'DRAFT_NOT_RENDERED',technical_master_verified:false,creative_approved:false,
   note:'An editor timeline is not an MP4. Rendering requires real rights-cleared source media, narration, music, and a connected worker.'};
}
