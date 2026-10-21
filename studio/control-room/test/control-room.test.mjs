import test from 'node:test';
import assert from 'node:assert/strict';
import {once} from 'node:events';
import {createServer} from '../server.mjs';
async function start(fetcher) {
 const server=createServer({fetcher,cacheMs:120000});
 server.listen(0,'127.0.0.1');
 await once(server,'listening');
 const url='http://127.0.0.1:'+server.address().port;
 return {server,url,stop:()=>new Promise(r=>server.close(r))};
}
test('health and front page are served with security headers', async()=>{
 const env=await start(async()=>{throw Error('should not call network')});
 try {
  const h=await fetch(env.url+'/healthz');assert.equal(h.status,200);assert.equal((await h.json()).rendering,'external-github-actions');
  const p=await fetch(env.url+'/');assert.equal(p.status,200);
  assert.match(await p.text(),/ELIJAH FILM STUDIO/);
  assert.match(p.headers.get('content-security-policy'),/connect-src 'self'/);
  assert.equal(p.headers.get('x-content-type-options'),'nosniff');
 } finally {await env.stop();}
});
test('public GitHub run data sanitized and cached',async()=>{
 let calls=0;
 const env=await start(async(url)=>{
  calls++;assert.match(url,/api.github.com\/repos\/elijahmunzai-rgb\/elijah-video-source-acquisition/);
  return new Response(JSON.stringify({workflow_runs:[
   {id:123,name:'Film agents',status:'completed',conclusion:'success',updated_at:'2026-10-22T01:00:00Z',
    html_url:'https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition/actions/runs/123'},
   {id:124,name:'Invalid URL',status:'completed',html_url:'https://attacker.example/'}
  ]}),{status:200});
 });
 try {
  const a=await (await fetch(env.url+'/api/status')).json();
  const b=await (await fetch(env.url+'/api/status')).json();
  assert.equal(a.runs.length,2);assert.equal(a.runs[0].id,123);assert.equal(a.runs[1].url,null);
  assert.equal(a.can_dispatch,false);assert.equal(b.cache,'hit');assert.equal(calls,1);
 } finally {await env.stop();}
});
test('write operations and unknown routes blocked',async()=>{
 const env=await start(async()=>{throw Error('unexpected fetch')});
 try{
  const post=await fetch(env.url+'/api/run',{method:'POST'});
  assert.equal(post.status,405);
  const unknown=await fetch(env.url+'/api/secrets');
  assert.equal(unknown.status,404);
 }finally{await env.stop();}
});
test('upstream errors do not leak details or cause server crash',async()=>{
 const env=await start(async()=>{throw Error('fake internal secret would leak')});
 try{
  const r=await fetch(env.url+'/api/status');
  const payload=await r.text();
  assert.equal(r.status,503);
  assert.doesNotMatch(payload,/fake internal secret/);
  assert.match(payload,/temporarily unavailable/);
 }finally{await env.stop();}
});
