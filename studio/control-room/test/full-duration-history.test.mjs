import test from 'node:test';
import assert from 'node:assert/strict';
import {once} from 'node:events';
import {createServer} from '../server.mjs';

test('studio safely loads only genuine public full-film GitHub run status',async()=>{
 let urlSeen='';
 const upstream={
  workflow_runs:[
   {id:39819926113,run_number:71,status:'completed',conclusion:'success',created_at:'2026-10-22T16:00:00Z',
    html_url:'https://github.com/elijahmunzai-rgb/elijah-video-source-acquisition/actions/runs/39819926113'},
   {id:123,status:'completed',conclusion:'success',html_url:'https://attacker.invalid/malware'}
  ]
 };
 const server=createServer({fetcher:async url=>{
  urlSeen=url;return new Response(JSON.stringify(upstream),{status:200});
 }});
 server.listen(0,'127.0.0.1');await once(server,'listening');
 const base='http://127.0.0.1:'+server.address().port;
 try{
  const response=await fetch(base+'/api/films/history');
  assert.equal(response.status,200);
  const j=await response.json();
  assert.match(urlSeen,/film-longform-15s-proof\.yml\/runs/);
  assert.equal(j.jobs.length,1);
  assert.equal(j.jobs[0].id,39819926113);
  assert.equal(j.jobs[0].conclusion,'success');
  assert.equal(j.public_demo_only,true);
  assert.equal((await fetch(base+'/api/films/history',{method:'POST'})).status,405);
 }finally{await new Promise(resolve=>server.close(resolve));}
});
test('GitHub unavailable does not leak errors or private data',async()=>{
 const server=createServer({fetcher:async()=>new Response('none',{status:403})});
 server.listen(0,'127.0.0.1');await once(server,'listening');
 try{
  const res=await fetch('http://127.0.0.1:'+server.address().port+'/api/films/history');
  assert.equal(res.status,503);
  assert.equal((await res.json()).jobs.length,0);
 }finally{await new Promise(resolve=>server.close(resolve));}
});
