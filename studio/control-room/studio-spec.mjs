// Shared Film Studio contract: planning is not a rendered finished film.
export const PRESETS = Object.freeze([15,30,60,120,300,600]);
export const ASPECTS = Object.freeze(['landscape','portrait','square']);
export const MAX_PLANNING_SECONDS = 3600;
export const MAX_CPU_JOB_SECONDS = 600;
export const MIN_SECONDS_PER_SHOT = 2;
export const MAX_SECONDS_PER_SHOT = 18;
export const FORMAT = {landscape:[1920,1080],portrait:[1080,1920],square:[1080,1080]};
export const LICENSED_DEMO_ASSETS = Object.freeze({
 'mixkit-4610':{name:'Call center pair',page:'https://mixkit.co/free-stock-video/woman-and-man-working-at-a-call-center-4610/',type:'real-stock-footage',label:'Illustrative stock actors, not agency employees'},
 'mixkit-4603':{name:'Operators and headsets',page:'https://mixkit.co/free-stock-video/a-pair-of-employees-working-in-a-call-center-4603/',type:'real-stock-footage',label:'Illustrative stock actors, not agency employees'}
});
export function requiredShots(seconds){return Math.ceil(seconds/MAX_SECONDS_PER_SHOT);}
export function suggestShotDurations(seconds){
 if(!Number.isInteger(seconds)||seconds<5||seconds>MAX_PLANNING_SECONDS)throw Error('Duration must be 5–3600 seconds');
 const count=Math.max(requiredShots(seconds),Math.ceil(seconds/8));const whole=Math.floor(seconds/count),rem=seconds%count;
 return Array.from({length:count},(_,i)=>whole+(i<rem?1:0));
}
export function cleanScene(s){
 if(!s||typeof s!=='object')throw Error('Scene object required');
 const x={id:String(s.id||'').trim(),seconds:Number(s.seconds),asset:String(s.asset||'').trim(),
 in_point:Number(s.in_point??0),caption:String(s.caption||'').trim(),
 narration:String(s.narration||'').trim(),rights_approved:s.rights_approved===true};
 if(!/^[a-zA-Z0-9_-]{1,36}$/.test(x.id))throw Error('Invalid shot ID');
 if(!Number.isInteger(x.seconds)||x.seconds<MIN_SECONDS_PER_SHOT||x.seconds>MAX_SECONDS_PER_SHOT)throw Error('Shot length must be 2–18s');
 if(!Number.isFinite(x.in_point)||x.in_point<0||x.in_point>9000)throw Error('Invalid footage in-point');
 if(x.caption.length>130||x.narration.length>450)throw Error('Scene copy too long');
 return x;
}
export function validateProject(input,{render=false}={}){
 const errors=[];const warn=[];
 if(!input||typeof input!=='object'||Array.isArray(input))return {ok:false,errors:['Project object required'],warnings:[],project:null};
 const title=String(input.title||'').trim();const goal=String(input.goal||'').trim();
 const duration_seconds=Number(input.duration_seconds);
 const aspect=String(input.aspect||'landscape'),audio=input.audio||{};
 if(!title||title.length>80||/[<>]/.test(title))errors.push('Title required, max 80 characters, no HTML');
 if(goal.length>500||/[<>]/.test(goal))errors.push('Goal max 500 characters, no HTML');
 if(!Number.isInteger(duration_seconds)||duration_seconds<5||duration_seconds>MAX_PLANNING_SECONDS)errors.push('Duration must be between 5 seconds and 60 minutes');
 if(!ASPECTS.includes(aspect))errors.push('Invalid aspect');
 if(!Array.isArray(input.scenes)||input.scenes.length>500)errors.push('Scenes array required, maximum 500');
 const scenes=[];if(Array.isArray(input.scenes)&&input.scenes.length<=500){
  for(const [i,s] of input.scenes.entries()){try{scenes.push(cleanScene(s));}catch(e){errors.push('Scene '+(i+1)+': '+e.message);}}
 }
 if(scenes.length){
  const ids=scenes.map(s=>s.id);if(new Set(ids).size!==ids.length)errors.push('Duplicate scene IDs');
  const total=scenes.reduce((n,s)=>n+s.seconds,0);
  if(total!==duration_seconds)errors.push('Shot durations sum to '+total+'s, not '+duration_seconds+'s');
  if(Number.isInteger(duration_seconds)&&scenes.length<requiredShots(duration_seconds))errors.push('Insufficient shots for requested runtime');
 }else errors.push('At least one actual scene required');
 const voice=String(audio.voice||'off');const music=String(audio.music||'off');
 if(!['off','espeak-en','recorded-voice'].includes(voice))errors.push('Unsupported voice mode');
 if(!['off','original-ambient','licensed-track'].includes(music))errors.push('Unsupported music mode');
 if(voice==='recorded-voice'||music==='licensed-track')warn.push('Private recordings/custom licensed tracks require separate authenticated private media store, unavailable in public beta');
 if(voice==='off')warn.push('Narration is OFF; client-facing commercials may need voiceover');
 if(music==='off')warn.push('Music is OFF');
 if(!input.public_demo)warn.push('Only non-confidential public demos currently dispatchable');
 const cleaned={schema:1,title,goal,duration_seconds,aspect,public_demo:input.public_demo===true,
  audio:{voice,music,voice_level_db:-3,music_level_db:-20},
  scenes};
 if(render){
  if(!cleaned.public_demo)errors.push('Rendering requires explicit non-confidential public-demo consent');
  if(duration_seconds>MAX_CPU_JOB_SECONDS)errors.push('CPU job length limit 600 seconds; export plan and split longer projects');
  if(voice==='off'&&music==='off')errors.push('At least one actual audio track required');
  if(voice==='recorded-voice'||music==='licensed-track')errors.push('Private media uploads are not supported in public demo worker');
  let visualSeconds=0;const parts=new Set(),uniq=new Set();
  for(const s of scenes){
   if(s.asset!=='unassigned'){
    if(!(s.asset in LICENSED_DEMO_ASSETS))errors.push(s.id+': only allowlisted approved stock clips currently renderable');
    else{
     if(!s.rights_approved)errors.push(s.id+': source rights not approved');
     visualSeconds+=s.seconds;uniq.add(s.asset);parts.add(s.asset+'@'+s.in_point.toFixed(2)+'+'+s.seconds);
    }
   }else errors.push(s.id+': shot has no real licensed media');
  }
  if(visualSeconds!==duration_seconds)errors.push('Every timeline second needs actual footage');
  if(parts.size!==scenes.length)errors.push('Duplicate footage/time segment used: do not fake unique shots by looping');
  // These two demonstrator clips are not a viable library for long storytelling.
  if(duration_seconds>30)errors.push('Two demo clips are insufficient for a unique '+duration_seconds+'s film. Add cleared scene sources and continuity before rendering.');
  if(duration_seconds>18 && uniq.size<2)errors.push('More than one genuine footage source required');
 }
 return {ok:errors.length===0,errors,warnings:warn,project:cleaned,
  required_shots:Number.isInteger(duration_seconds)&&duration_seconds>0?requiredShots(duration_seconds):null,
  coverage_seconds:scenes.filter(s=>s.asset in LICENSED_DEMO_ASSETS&&s.rights_approved).reduce((n,s)=>n+s.seconds,0),
  planning_only:!render};
}
