import test from 'node:test';
import assert from 'node:assert/strict';
import {once} from 'node:events';
import {createServer} from '../server.mjs';
import {validateProject,PRESETS,suggestShotDurations} from '../studio-spec.mjs';

const password='test-password-long-for-studio';
const GH='ghs_public_test_token_only_never_real';
const good15={
 schema:1,title:'CONVERSATIONS THAT COUNT',goal:'Original nonconfidential demo brief',duration_seconds:15,
 aspect:'landscape',public_demo:true,audio:{voice:'espeak-en',music:'original-ambient'},
 scenes:[
 {id:'s1',seconds:5,asset:'mixkit-4610',in_point:0,caption:'REAL CONVERSATIONS',
 narration:'Real connection starts with one conversation.',rights_approved:true},
 {id:'s2',seconds:5,asset:'mixkit-4603',in_point:0,caption:'PEOPLE FIRST',
 narration:'Good teams listen before they sell.',rights_approved:true},
 {id:'s3',seconds:5,asset:'mixkit-4610',in_point:5.5,caption:'BUILT ON TRUST',
 narration:'Bring a human touch to outreach.',rights_approved:true}
 ]};
function post(url,body,cookie=''){return fetch(url,{method:'POST',headers:{'Content-Type':'application/json','Origin':new URL(url).origin,
 'X-Studio-Action':'1',...(cookie?{Cookie:cookie}:{})},body:JSON.stringify(body)});}
async function app(fetcher=async()=>{throw Error('Network should not be used')},operatorEnv={}){
 const srv=createServer({fetcher,operatorEnv});srv.listen(0,'127.0.0.1');await once(srv,'listening');
 return {url:'http://127.0.0.1:'+srv.address().port,stop:()=>new Promise(r=>srv.close(r))};
}
test('all production duration presets and custom timeline partitions preserve exact seconds',()=>{
 assert.deepEqual(PRESETS,[15,30,60,120,300,600]);
 for(const sec of [...PRESETS,7,45,900,3600]){
  const durations=suggestShotDurations(sec);
  assert.equal(durations.reduce((a,b)=>a+b,0),sec);
  assert.ok(durations.length>=Math.ceil(sec/18));
  assert.ok(durations.every(n=>n>=2&&n<=18));
 }
 assert.throws(()=>suggestShotDurations(3601));
});
test('real 15 second brief accepted, higher durations plan but cannot silently loop inadequate media',()=>{
 const r=validateProject(good15,{render:true});assert.equal(r.ok,true,r.errors.join(';'));
 for(const sec of [30,60,120,300,600,1800]){
  const durations=suggestShotDurations(sec);
  const p={...good15,duration_seconds:sec,scenes:durations.map((n,i)=>({
   id:'scene-'+i,seconds:n,asset:'unassigned',rights_approved:false,caption:'Unique idea '+i,narration:'Line '+i,in_point:0}))};
  assert.equal(validateProject(p).ok,true,'planning '+sec);
  const s=validateProject(p,{render:true});
  assert.equal(s.ok,false,'render should fail when source assets absent');
  assert.ok(s.errors.some(x=>/unassigned|footage|sources/.test(x)));
 }
});
test('actual narration, rights, fake loops and private media gated',()=>{
 for(const change of [
 p=>{p.scenes[0].rights_approved=false},
 p=>{p.scenes[2].in_point=0;p.scenes[2].seconds=5},
 p=>{p.audio.voice='espeak-en';p.scenes.forEach(s=>s.narration='')},
 p=>{p.audio.voice='recorded-voice'},
 p=>{p.public_demo=false},
 p=>{p.scenes[0].seconds=3}
 ]){
  const p=structuredClone(good15);change(p);
  assert.equal(validateProject(p,{render:true}).ok,false);
 }
});
test('studio web page and capability API served with no token and safe headers',async()=>{
 const env=await app();
 try{
  const p=await fetch(env.url+'/studio');assert.equal(p.status,200);
  const html=await p.text();assert.match(html,/Production Workspace/);assert.match(html,/10 min/);
  assert.match(html,/Submit public CPU render/);assert.match(html,/narration/);
  assert.equal((await fetch(env.url+'/studio.html')).status,200);
  const caps=await (await fetch(env.url+'/api/studio/capabilities')).json();
  assert.deepEqual(caps.presets,PRESETS);assert.equal(caps.custom_max_seconds,3600);
  assert.equal(caps.private_media_uploads,false);
  const v=await (await post(env.url+'/api/studio/validate',good15)).json();
  assert.equal(v.plan.ok,true);assert.equal(v.render.ok,true);
 }finally{await env.stop();}
});
test('actual project launch requires login, origin, approved footage and scoped GitHub dispatch',async()=>{
 let called=0,body=null;
 const fetcher=async(url,options)=>{
  if(url.includes('/dispatches')){called++;body=JSON.parse(options.body);return new Response(null,{status:204});}
  throw Error('Unexpected URL '+url);
 };
 const env=await app(fetcher,{STUDIO_ADMIN_PASSWORD:password,GITHUB_STUDIO_TOKEN:GH});
 try{
  const unauth=await post(env.url+'/api/studio/render',{project:good15});assert.equal(unauth.status,401);
  const signin=await post(env.url+'/api/session',{password});assert.equal(signin.status,200);
  const cookie=signin.headers.get('set-cookie').split(';')[0];
  const fail=await post(env.url+'/api/studio/render',{project:{...good15,scenes:[]}},cookie);
  assert.equal(fail.status,422);
  const success=await post(env.url+'/api/studio/render',{project:good15},cookie);
  assert.equal(success.status,202);
  assert.equal(called,1);
  assert.equal(body.ref,'studio-operator-phase2-20261022');
  assert.equal(body.inputs.spec_json&&JSON.parse(body.inputs.spec_json).duration_seconds,15);
  const cross=await fetch(env.url+'/api/studio/render',{method:'POST',
    headers:{'Origin':'https://evil.example','X-Studio-Action':'1','Content-Type':'application/json',Cookie:cookie},
    body:JSON.stringify({project:good15})});
  assert.equal(cross.status,403);
 }finally{await env.stop();}
});
