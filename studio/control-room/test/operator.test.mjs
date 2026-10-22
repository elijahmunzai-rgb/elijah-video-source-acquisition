import test from 'node:test';
import assert from 'node:assert/strict';
import {once} from 'node:events';
import {deflateRawSync} from 'node:zlib';
import {createServer} from '../server.mjs';
import {extractPreview,readDemoMp4} from '../media.mjs';

const PASSWORD='test-only-passphrase-very-long';
const GH='ghs_testing_mock_token_123456789';
const RUN={id:123,event:'workflow_dispatch',path:'.github/workflows/film-studio-agents.yml@main',name:'Eight Agent Team',status:'completed',conclusion:'success',created_at:'2026-10-22T02:00:00Z',updated_at:'2026-10-22T02:10:00Z',run_number:5,run_attempt:1,html_url:'https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition/actions/runs/123'};
async function app(fetcher,operatorEnv={}){
 const server=createServer({fetcher,operatorEnv});
 server.listen(0,'127.0.0.1');await once(server,'listening');
 const url='http://127.0.0.1:'+server.address().port;
 return {url,server,stop:()=>new Promise(r=>server.close(r))};
}
function writeReq(env,path,body,cookie=''){
 return fetch(env.url+path,{method:'POST',headers:{Origin:env.url,'X-Studio-Action':'1','Content-Type':'application/json',...(cookie?{Cookie:cookie}:{})},body:JSON.stringify(body)});
}
async function login(env){
 const r=await writeReq(env,'/api/session',{password:PASSWORD});
 assert.equal(r.status,200);
 return r.headers.get('set-cookie').split(';')[0];
}
function mkZip(name,data){
 const n=Buffer.from(name),x=Buffer.from(data);
 const packed=deflateRawSync(x),header=Buffer.alloc(30),central=Buffer.alloc(46),end=Buffer.alloc(22);
 header.writeUInt32LE(0x04034b50,0);header.writeUInt16LE(20,4);header.writeUInt16LE(8,8);header.writeUInt32LE(packed.length,18);header.writeUInt32LE(x.length,22);header.writeUInt16LE(n.length,26);
 const offset=header.length+n.length+packed.length;
 central.writeUInt32LE(0x02014b50,0);central.writeUInt16LE(20,4);central.writeUInt16LE(20,6);central.writeUInt16LE(8,10);central.writeUInt32LE(packed.length,20);central.writeUInt32LE(x.length,24);central.writeUInt16LE(n.length,28);central.writeUInt32LE(0,42);
 end.writeUInt32LE(0x06054b50,0);end.writeUInt16LE(1,8);end.writeUInt16LE(1,10);end.writeUInt32LE(central.length+n.length,12);end.writeUInt32LE(offset,16);
 return Buffer.concat([header,n,packed,central,n,end]);
}
test('public demo can browse jobs while writes are locked by default',async()=>{
 const env=await app(async()=>new Response(JSON.stringify({workflow_runs:[RUN,{...RUN,id:124,event:'push'}]}),{status:200}));
 try{
  const p=await (await fetch(env.url+'/api/session')).json();assert.equal(p.dispatch_enabled,false);assert.equal(p.login_enabled,false);
  const list=await (await fetch(env.url+'/api/jobs')).json();assert.equal(list.jobs.length,1);assert.equal(list.jobs[0].id,123);
  const r=await writeReq(env,'/api/jobs',{title:'A',goal:'Demo',duration:'30',aspect:'landscape',public_demo:true});assert.equal(r.status,401);
 }finally{await env.stop();}
});
test('operator login, CSRF gate and approved demo job dispatch',async()=>{
 let called=0;let submitted=null;
 const fetcher=async(url,options={})=>{
  if(url.includes('/dispatches')){called++;submitted=JSON.parse(options.body);return new Response(null,{status:204});}
  return new Response(JSON.stringify({workflow_runs:[RUN]}),{status:200});
 };
 const env=await app(fetcher,{STUDIO_ADMIN_PASSWORD:PASSWORD,GITHUB_STUDIO_TOKEN:GH});
 try{
  const cross=await fetch(env.url+'/api/session',{method:'POST',headers:{'Content-Type':'application/json',Origin:'https://evil.example'},body:JSON.stringify({password:PASSWORD})});assert.equal(cross.status,403);
  const bad=await writeReq(env,'/api/session',{password:'wrong'});assert.equal(bad.status,401);
  const cookie=await login(env);
  const good={title:'A NEW FRAME',goal:'Approved generic public demo',duration:'30',aspect:'landscape',public_demo:true};
  const invalid=await writeReq(env,'/api/jobs',{...good,public_demo:false},cookie);assert.equal(invalid.status,400);
  const r=await writeReq(env,'/api/jobs',good,cookie);assert.equal(r.status,202);
  assert.equal(called,1);assert.deepEqual(submitted,{ref:'studio-operator-phase2-20261022',inputs:{title:'A NEW FRAME',goal:'Approved generic public demo',duration:'30',aspect:'landscape'}});
  const s=await (await fetch(env.url+'/api/session',{headers:{Cookie:cookie}})).json();assert.equal(s.authenticated,true);
  const quit=await writeReq(env,'/api/logout',{},cookie);assert.equal(quit.status,200);
  const after=await writeReq(env,'/api/jobs',good,cookie);assert.equal(after.status,401);
 }finally{await env.stop();}
});
test('rate limits demo dispatch budget to two per hour',async()=>{
 let dispatches=0;const env=await app(async()=>{dispatches++;return new Response(null,{status:204});},{STUDIO_ADMIN_PASSWORD:PASSWORD,GITHUB_STUDIO_TOKEN:GH});
 try{
  const cookie=await login(env),b={title:'PUBLIC DEMO',goal:'Test',duration:'15',aspect:'square',public_demo:true};
  for(let i=0;i<2;i++){const r=await writeReq(env,'/api/jobs',b,cookie);assert.equal(r.status,202);}
  const third=await writeReq(env,'/api/jobs',b,cookie);assert.equal(third.status,429);assert.equal(dispatches,2);
 }finally{await env.stop();}
});
test('only allow public demo workflow runs for progress and artifacts',async()=>{
 const fetcher=async(url)=>{
  if(url.endsWith('/actions/runs/123'))return new Response(JSON.stringify(RUN),{status:200});
  if(url.includes('/jobs?'))return new Response(JSON.stringify({jobs:[{name:'Render',status:'completed',conclusion:'success',steps:[{name:'Output',status:'completed',conclusion:'success'}]}]}),{status:200});
  if(url.includes('/artifacts?'))return new Response(JSON.stringify({artifacts:[{id:42,name:'public-demo-studio-agents-storyboard-preview',size_in_bytes:800,expired:false}]}),{status:200});
  if(url.endsWith('/actions/runs/999'))return new Response(JSON.stringify({...RUN,id:999,event:'push'}),{status:200});
  return new Response('{}',{status:404});
 };
 const env=await app(fetcher,{STUDIO_ADMIN_PASSWORD:PASSWORD,GITHUB_STUDIO_TOKEN:GH});
 try{
  const r=await fetch(env.url+'/api/jobs/123');assert.equal(r.status,200);const d=await r.json();assert.equal(d.artifacts.length,1);assert.equal(d.steps[0].steps.length,1);
  const no=await fetch(env.url+'/api/jobs/999');assert.equal(no.status,404);
  const preview=await fetch(env.url+'/api/jobs/123/preview');assert.equal(preview.status,401);
 }finally{await env.stop();}
});
test('extract only bounded valid MP4, reject bad redirect',async()=>{
 const mp4=Buffer.concat([Buffer.from([0,0,0,24]),Buffer.from('ftypisom000000000000000000')]);
 const zipped=mkZip('preview-6s.mp4',mp4);
 assert.deepEqual(extractPreview(zipped),mp4);
 assert.throws(()=>extractPreview(mkZip('other.mp4',mp4)),/not found/);
 await assert.rejects(()=>readDemoMp4({api:'https://api.github.com/repos/test/test',artifactId:12,token:'test',fetcher:async()=>new Response(null,{status:302,headers:{Location:'https://attacker.example/evil'}})}),/Untrusted/);
});


test('signed-in preview streams bounded MP4 ranges and direct download',async()=>{
 const mp4=Buffer.concat([Buffer.from([0,0,0,24]),Buffer.from('ftypisom000000000000000000')]),archive=mkZip('preview-6s.mp4',mp4);
 const fetcher=async(url)=>{
  if(url.endsWith('/actions/runs/123'))return new Response(JSON.stringify(RUN),{status:200});
  if(url.includes('/actions/runs/123/artifacts?'))return new Response(JSON.stringify({artifacts:[{id:42,name:'public-demo-studio-agents-storyboard-preview',expired:false}]}),{status:200});
  if(url.endsWith('/actions/artifacts/42/zip'))return new Response(null,{status:302,headers:{Location:'https://results-receiver.actions.githubusercontent.com/approved.zip'}});
  if(url==='https://results-receiver.actions.githubusercontent.com/approved.zip')return new Response(archive,{status:200});
  throw new Error('Unexpected external URL '+url);
 };
 const env=await app(fetcher,{STUDIO_ADMIN_PASSWORD:PASSWORD,GITHUB_STUDIO_TOKEN:GH});
 try{
  const cookie=await login(env);
  const v=await fetch(env.url+'/api/jobs/123/preview',{headers:{Cookie:cookie,Range:'bytes=0-9'}});
  assert.equal(v.status,206);assert.equal(v.headers.get('content-range'),'bytes 0-9/'+mp4.length);
  assert.deepEqual(Buffer.from(await v.arrayBuffer()),mp4.subarray(0,10));
  const d=await fetch(env.url+'/api/jobs/123/download',{headers:{Cookie:cookie}});
  assert.equal(d.status,200);assert.match(d.headers.get('content-disposition'),/attachment/);
  assert.deepEqual(Buffer.from(await d.arrayBuffer()),mp4);
 }finally{await env.stop();}
});
