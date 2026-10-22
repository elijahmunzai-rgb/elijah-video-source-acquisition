import test from 'node:test';
import assert from 'node:assert/strict';
import {once} from 'node:events';
import {createServer} from '../server.mjs';
import {DURATIONS,startProject,validateProject,rebalance,buildProductionManifest,formatTime} from '../project-schema.mjs';
for(const duration of DURATIONS){
 test('full length '+duration+' seconds makes a distinct authored scene timeline',()=>{
  const p=startProject({title:'Short Film',duration,aspect:'portrait'});
  const v=validateProject(p);
  assert.equal(v.ok,true);
  assert.equal(v.total,duration);
  assert.equal(p.scenes.reduce((n,x)=>n+x.duration,0),duration);
  assert.ok(p.scenes.length >= {'15':3,'30':5,'60':8,'120':12,'300':20,'600':30}[duration]);
  assert.equal(new Set(p.scenes.map(s=>s.id)).size,p.scenes.length);
  assert.equal(p.release_approved,false);
  assert.equal(buildProductionManifest(p).scenes.at(-1).end,duration);
  assert.equal(buildProductionManifest(p).production_status,'DRAFT_NOT_RENDERED');
 });
}
test('bad media and absent audio cannot be certified as a mastered film',()=>{
 const p=startProject({duration:300});
 assert.equal(validateProject(p,{requireAssets:true}).ok,false);
 assert.equal(validateProject(p,{requireAssets:true}).render_ready,false);
});
test('all scene/media/audio rights and human review are mandatory before ready',()=>{
 const p=startProject({duration:15});
 for(const s of p.scenes){s.media_ref='cleared.mp4';s.media_rights='creator-permission';s.reviewed=true;s.direction='Unique real scene';}
 p.voice={mode:'licensed-recording',reference:'actual-voice.wav',rights:'voice-release'};
 p.music={mode:'licensed-track',reference:'actual-score.wav',rights:'music-license'};
 assert.equal(validateProject(p,{requireAssets:true}).render_ready,true);
 p.scenes[2].reviewed=false;
 assert.equal(validateProject(p,{requireAssets:true}).ok,false);
});
test('different scene lengths must exactly add up to selected duration',()=>{
 const p=startProject({duration:60});
 p.scenes[0].duration=1;
 const v=validateProject(p);
 assert.equal(v.ok,false);
 assert.match(v.errors.join(','),/Scene lengths add to/);
 const r=rebalance(p);
 assert.equal(validateProject(r).ok,true);
});
test('unknown format and fake 600 seconds must fail validation',()=>{
 const p=startProject({duration:600});p.duration=42;
 assert.equal(validateProject(p).ok,false);
 assert.throws(()=>startProject({duration:42}));
 assert.equal(formatTime(600),'10:00');
});
test('real server serves production editor and independent same-origin module safely',async()=>{
 const server=createServer({fetcher:async()=>{throw Error('No external network')}});
 server.listen(0,'127.0.0.1');await once(server,'listening');
 const origin='http://127.0.0.1:'+server.address().port;
 try{
  const page=await fetch(origin+'/studio');
  assert.equal(page.status,200);
  assert.match(await page.text(),/Make the whole film/);
  assert.match(page.headers.get('content-security-policy'),/script-src 'self'/);
  const js=await fetch(origin+'/project-schema.mjs');
  assert.equal(js.status,200);assert.match(await js.text(),/export const DURATIONS/);
  const app=await fetch(origin+'/studio-app.mjs');
  assert.equal(app.status,200);assert.match(await app.text(),/buildProductionManifest/);
  const main=await (await fetch(origin+'/')).text();
  assert.match(main,/Open Full-Length Production Workspace/);
  const post=await fetch(origin+'/studio',{method:'POST'});
  assert.equal(post.status,405);
 }finally{await new Promise(r=>server.close(r));}
});
