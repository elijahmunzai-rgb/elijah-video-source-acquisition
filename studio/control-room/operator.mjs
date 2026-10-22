import {randomBytes, createHash, timingSafeEqual} from 'node:crypto';
import {readDemoMp4} from './media.mjs';
import {validateProject} from './studio-spec.mjs';

const REPO='elijahmunzai-rgb/elijah-video-source-acquisition';
const API='https://api.github.com/repos/'+REPO;
const WORKFLOW='film-studio-agents.yml';
const FULL_WORKFLOW='film-studio-full-production.yml';
const BRANCH='studio-operator-phase2-20261022';
const ACTIONS='https://github.com/'+REPO+'/actions/workflows/'+WORKFLOW;
const COOKIE='__Host-studio';
const durations=new Set(['15','30','60','120','600']);
const aspects=new Set(['landscape','portrait','square']);
const jsonHeaders={'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store','X-Content-Type-Options':'nosniff','Referrer-Policy':'no-referrer','X-Frame-Options':'DENY','Content-Security-Policy':"default-src 'none'; frame-ancestors 'none'; base-uri 'none'"};
const hash=s=>createHash('sha256').update(s).digest('hex');
function send(res,code,body,extras={}){
 res.writeHead(code,{...jsonHeaders,...extras});res.end(JSON.stringify(body));
}
function reqUrl(req){return new URL(req.url||'/', 'http://localhost');}
function validOrigin(req){
 const origin=req.headers.origin;
 if(!origin||typeof origin!=='string')return false;
 try{
  const o=new URL(origin);
  const host=req.headers.host;
  return !!host && o.host===host && (o.protocol==='https:' || (o.protocol==='http:' && /^(localhost|127\.0\.0\.1)(:\d+)?$/.test(host)));
 }catch{return false;}
}
function action(req){return validOrigin(req)&&req.headers['x-studio-action']==='1';}
async function readBody(req,limit=4096){
 if(!String(req.headers['content-type']||'').startsWith('application/json'))throw Error('JSON body required');
 let total=0,body='';
 for await(const chunk of req){total+=chunk.length;if(total>limit)throw Error('Request too large');body+=chunk.toString('utf8');}
 return JSON.parse(body);
}
function authToken(req){const cookie=(req.headers.cookie||'').split(';').map(s=>s.trim()).find(x=>x.startsWith(COOKIE+'='));return cookie?.slice((COOKIE+'=').length);}
function validDemoRun(run){return run && Number.isSafeInteger(Number(run.id)) && run.event==='workflow_dispatch' && String(run.path||'').split('@')[0].endsWith('/'+WORKFLOW) && /^https:\/\/github\.com\/elijahmunzai-rgb\/elijah-video-source-acquisition\/actions\/runs\/[0-9]+$/.test(run.html_url||'');}
function cleanRun(run){
 return {id:Number(run.id),name:String(run.name||'').slice(0,150),status:String(run.status||'').slice(0,40),
 conclusion:run.conclusion==null?null:String(run.conclusion).slice(0,40),
 created_at:String(run.created_at||'').slice(0,40),updated_at:String(run.updated_at||'').slice(0,40),
 run_started_at:String(run.run_started_at||'').slice(0,40),
 url:run.html_url,run_number:Number(run.run_number)||0,attempt:Number(run.run_attempt)||1};
}
function cleanJob(job){return {name:String(job.name||'').slice(0,120),status:String(job.status||'').slice(0,30),conclusion:job.conclusion==null?null:String(job.conclusion).slice(0,30),steps:Array.isArray(job.steps)?job.steps.map(x=>({name:String(x.name||'').slice(0,120),status:String(x.status||'').slice(0,30),conclusion:x.conclusion==null?null:String(x.conclusion).slice(0,30)})).slice(0,30):[]};}
function cleanArtifact(a,runId){return {id:Number(a.id),name:String(a.name||'').slice(0,150),size_in_bytes:Number(a.size_in_bytes)||0,expired:!!a.expired,expires_at:String(a.expires_at||'').slice(0,40),download_page:'https://github.com/'+REPO+'/actions/runs/'+runId+'#artifacts'};}
export function createOperator({fetcher=fetch,env=process.env,now=()=>Date.now()}={}){
 const sessions=new Map(),failed=new Map(),launches=[];
 const admin=String(env.STUDIO_ADMIN_PASSWORD||'');
 const ghToken=String(env.GITHUB_STUDIO_TOKEN||'');
 const passwordSet=admin.length>=16;
 const canDispatch=passwordSet && ghToken.length>10;
 const passwordHash=hash(passwordSet?admin:'unconfigured-dummy-password');
 const auth=req=>{
  const token=authToken(req);if(!token||!/^[0-9a-f]{64}$/.test(token))return false;
  const key=hash(token),s=sessions.get(key);
  if(!s||s<now()){sessions.delete(key);return false;}return true;
 };
 function ghHeaders(write=false){
  const h={Accept:'application/vnd.github+json','User-Agent':'ElijahFilmStudioOperator/0.2','X-GitHub-Api-Version':'2022-11-28'};
  if(write&&ghToken)h.Authorization='Bearer '+ghToken;
  return h;
 }
 async function ghGet(path,privateToken=false){
  const ctrl=new AbortController(),timer=setTimeout(()=>ctrl.abort(),9000);
  try{
   const response=await fetcher(API+path,{headers:ghHeaders(privateToken),signal:ctrl.signal});
   if(!response.ok)throw Error('GitHub status '+response.status);
   return await response.json();
  }finally{clearTimeout(timer);}
 }
 async function verifiedRun(id){
  const run=await ghGet('/actions/runs/'+id);
  if(!validDemoRun(run)||Number(run.id)!==Number(id))return null;
  return run;
 }
 return async function handle(req,res){
  const pathname=reqUrl(req).pathname,method=req.method;
  if(pathname==='/api/session' && method==='GET'){
   send(res,200,{authenticated:auth(req),login_enabled:passwordSet,dispatch_enabled:canDispatch,preview_enabled:canDispatch,public_demo_only:true,actions_url:ACTIONS});return true;
  }
  if(pathname==='/api/session' && method==='POST'){
   if(!action(req)){send(res,403,{error:'Origin and action header required'});return true;}
   if(!passwordSet){send(res,503,{error:'Admin login not configured on this server'});return true;}
   const ip=String(req.socket.remoteAddress||'unknown');
   const bad=(failed.get(ip)||[]).filter(t=>now()-t<15*60*1000);
   if(bad.length>=8){send(res,429,{error:'Too many login attempts'});return true;}
   let body;try{body=await readBody(req);}catch{send(res,400,{error:'Invalid request'});return true;}
   const supplied=hash(typeof body.password==='string'&&body.password.length<=1024?body.password:'');
   if(!timingSafeEqual(Buffer.from(supplied,'hex'),Buffer.from(passwordHash,'hex'))){
    bad.push(now());failed.set(ip,bad);send(res,401,{error:'Invalid credentials'});return true;
   }
   failed.delete(ip);
   const token=randomBytes(32).toString('hex');
   for(const [k,expiry] of sessions){if(expiry<now())sessions.delete(k);}
   if(sessions.size>=20)sessions.delete(sessions.keys().next().value);
   sessions.set(hash(token),now()+8*60*60*1000);
   send(res,200,{authenticated:true,dispatch_enabled:canDispatch},{'Set-Cookie':COOKIE+'='+token+'; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=28800'});return true;
  }
  if(pathname==='/api/logout' && method==='POST'){
   if(!action(req)){send(res,403,{error:'Origin and action header required'});return true;}
   const token=authToken(req);if(token)sessions.delete(hash(token));
   send(res,200,{authenticated:false},{'Set-Cookie':COOKIE+'=; Path=/; Secure; HttpOnly; SameSite=Strict; Max-Age=0'});return true;
  }
  if(pathname==='/api/jobs' && method==='GET'){
   try{
    const d=await ghGet('/actions/workflows/'+WORKFLOW+'/runs?event=workflow_dispatch&per_page=25');
    const runs=(d.workflow_runs||[]).filter(validDemoRun).slice(0,20).map(cleanRun);
    send(res,200,{jobs:runs,actions_url:ACTIONS,public_demo_only:true});return true;
   }catch{send(res,503,{error:'Public GitHub jobs unavailable',actions_url:ACTIONS});return true;}
  }
  if(pathname==='/api/jobs' && method==='POST'){
   if(!action(req)){send(res,403,{error:'Origin and action header required'});return true;}
   if(!auth(req)){send(res,401,{error:'Admin login required'});return true;}
   if(!canDispatch){send(res,503,{error:'GitHub dispatch is not configured'});return true;}
   let b;try{b=await readBody(req);}catch{send(res,400,{error:'Invalid request'});return true;}
   const title=String(b.title||'').trim(),goal=String(b.goal||'').trim(),duration=String(b.duration||''),aspect=String(b.aspect||'');
   if(!b.public_demo||!title||title.length>80||!/^[\p{L}\p{N} .,:!?()&\-_'\/]+$/u.test(title)||!goal||goal.length>400||/[<>]/.test(goal)||!durations.has(duration)||!aspects.has(aspect)){
    send(res,400,{error:'Invalid or non-public demo brief'});return true;
   }
   const recent=launches.filter(t=>now()-t<24*60*60*1000);
   if(recent.length>=6||recent.filter(t=>now()-t<60*60*1000).length>=2){send(res,429,{error:'Demo job budget reached'});return true;}
   // Reserve quota before outbound call; fail closed rather than allow unbounded retries.
   launches.push(now());
   try{
    const ctrl=new AbortController(),timer=setTimeout(()=>ctrl.abort(),8000);let response;
    try{
     response=await fetcher(API+'/actions/workflows/'+WORKFLOW+'/dispatches',{method:'POST',headers:{...ghHeaders(true),'Content-Type':'application/json'},body:JSON.stringify({ref:BRANCH,inputs:{title,goal,duration,aspect}}),signal:ctrl.signal});
    }finally{clearTimeout(timer);}
    if(response.status!==204){send(res,502,{error:'GitHub rejected job dispatch. Check token permissions and workflow availability.'});return true;}
    send(res,202,{accepted:true,run_id:null,notice:'GitHub accepted demo request; discover run in recent jobs shortly',actions_url:ACTIONS});return true;
   }catch{send(res,502,{error:'GitHub dispatch temporarily unavailable'});return true;}
  }
  if(pathname==='/api/studio/jobs' && method==='GET'){
    try{
      const d=await ghGet('/actions/workflows/'+FULL_WORKFLOW+'/runs?per_page=30');
      const runs=(d.workflow_runs||[]).filter(x=>x.head_branch===BRANCH &&
        String(x.path||'').split('@')[0].endsWith('/'+FULL_WORKFLOW) &&
        /^https:\/\/github\.com\/elijahmunzai-rgb\/elijah-video-source-acquisition\/actions\/runs\/[0-9]+$/.test(x.html_url||''))
        .slice(0,20).map(cleanRun);
      send(res,200,{jobs:runs,workflow:FULL_WORKFLOW,public_demo_only:true});return true;
    }catch{send(res,503,{error:'GitHub full-production status temporarily unavailable'});return true;}
  }
  if(pathname==='/api/studio/render' && method==='POST'){
    if(!action(req)){send(res,403,{error:'Same-origin action required'});return true;}
    if(!auth(req)){send(res,401,{error:'Admin login required'});return true;}
    if(!canDispatch){send(res,503,{error:'Server-side GitHub dispatch not configured'});return true;}
    let body;try{body=await readBody(req,120000);}catch{send(res,400,{error:'Invalid project JSON or body too large'});return true;}
    const result=validateProject(body?.project,{render:true});
    if(!result.ok){send(res,422,{error:'Incomplete licensed footage/audio plan',blockers:result.errors.slice(0,20)});return true;}
    const recent=launches.filter(t=>now()-t<24*60*60*1000);
    if(recent.length>=6||recent.filter(t=>now()-t<60*60*1000).length>=2){
      send(res,429,{error:'Public render quota reached'});return true;
    }
    const spec_json=JSON.stringify(result.project);
    if(Buffer.byteLength(spec_json)>60000){send(res,413,{error:'Timeline too large for GitHub Actions input; split into projects'});return true;}
    launches.push(now());
    // A repo-scoped Contents:Write token creates one reviewed PUBLIC request.
    // A branch-scoped GitHub push workflow runs the actual renderer without
    // requiring the new workflow to be present on main/default branch.
    const requestPath='studio/full-workflow/requests/film-'+now()+'-'+randomBytes(5).toString('hex')+'.json';
    try{
      const ctrl=new AbortController(),timer=setTimeout(()=>ctrl.abort(),8000);let response;
      try{
        response=await fetcher(API+'/contents/'+requestPath,{
          method:'PUT',headers:{...ghHeaders(true),'Content-Type':'application/json'},
          body:JSON.stringify({message:'Queue approved nonconfidential film project',
            branch:BRANCH,content:Buffer.from(spec_json,'utf8').toString('base64')}),
          signal:ctrl.signal});
      }finally{clearTimeout(timer);}
      if(response.status!==201){send(res,502,{error:'GitHub project request rejected. Check repository-only Contents Write permission and workflow branch.'});return true;}
      send(res,202,{accepted:true,run_id:null,workflow:FULL_WORKFLOW,
        request_file:requestPath,notice:'GitHub accepted approved public project request; render workflow will launch on branch push.'});return true;
    }catch{send(res,502,{error:'GitHub request dispatch temporarily unavailable'});return true;}
  }
  const match=/^\/api\/jobs\/([1-9][0-9]{0,18})(?:\/(preview|download))?$/.exec(pathname);
  if(match){
   if(method!=='GET'&&method!=='HEAD'){send(res,405,{error:'Method not allowed'});return true;}
   const id=match[1];
   try{
    const run=await verifiedRun(id);
    if(!run){send(res,404,{error:'Public demo run not found'});return true;}
    if(match[2]==='preview'||match[2]==='download'){
     if(!auth(req)||!canDispatch){send(res,401,{error:'Admin login and preview configuration required'});return true;}
     const arts=await ghGet('/actions/runs/'+id+'/artifacts?per_page=30',true);
     const a=(arts.artifacts||[]).find(x=>x.name==='public-demo-studio-agents-storyboard-preview'&&!x.expired);
     if(!a){send(res,404,{error:'Preview artifact is not available yet'});return true;}
     const mp4=await readDemoMp4({fetcher,api:API,artifactId:a.id,token:ghToken});
     const range=req.headers.range;
     let start=0,end=mp4.length-1,code=200;
     if(range){
      const m=/^bytes=(\d*)-(\d*)$/.exec(range);
      if(!m){send(res,416,{error:'Invalid range'});return true;}
      if(m[1]===''&&m[2]===''){send(res,416,{error:'Invalid range'});return true;}
      if(m[1]===''){const suffix=Number(m[2]);start=Math.max(0,mp4.length-suffix);}
      else{start=Number(m[1]);end=m[2]===''?end:Math.min(end,Number(m[2]));}
      if(!Number.isSafeInteger(start)||!Number.isSafeInteger(end)||start>end||start>=mp4.length){send(res,416,{error:'Out-of-range'});return true;}
      code=206;
     }
     const headers={'Content-Type':'video/mp4','Cache-Control':'private, no-store','X-Content-Type-Options':'nosniff','Content-Disposition':(match[2]==='download'?'attachment':'inline')+'; filename="public-demo-preview-6s.mp4"','Accept-Ranges':'bytes','Content-Length':end-start+1};
     if(code===206)headers['Content-Range']='bytes '+start+'-'+end+'/'+mp4.length;
     res.writeHead(code,headers);res.end(method==='HEAD'?'':mp4.subarray(start,end+1));return true;
    }
    const [jobs,artifacts]=await Promise.all([ghGet('/actions/runs/'+id+'/jobs?per_page=30'),ghGet('/actions/runs/'+id+'/artifacts?per_page=30')]);
    send(res,200,{job:cleanRun(run),steps:(jobs.jobs||[]).map(cleanJob).slice(0,8),artifacts:(artifacts.artifacts||[]).map(x=>cleanArtifact(x,id)).slice(0,20),
     can_preview:canDispatch&&!!(artifacts.artifacts||[]).find(x=>x.name==='public-demo-studio-agents-storyboard-preview'&&!x.expired),public_demo_only:true});return true;
   }catch{send(res,503,{error:'Job details temporarily unavailable'});return true;}
  }
  return false;
 };
}
