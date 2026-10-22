import test from 'node:test';
import assert from 'node:assert/strict';
import {mkdtemp,rm,readdir} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {once} from 'node:events';
import {createServer} from '../server.mjs';
import {startProject} from '../project-schema.mjs';
import {createProjectStore} from '../project-store.mjs';

test('private project store fails closed without explicit absolute storage path',()=>{
 assert.equal(createProjectStore('').enabled,false);
 assert.equal(createProjectStore('./relative-data').enabled,false);
 assert.equal(createProjectStore('/').enabled,false);
});
test('create/list/load/update a REAL 10m timeline only in site-private directory',async()=>{
 const dir=await mkdtemp(join(tmpdir(),'film-private-store-'));
 try{
  const store=createProjectStore(dir);
  const p=startProject({title:'Real ten-minute film',duration:600});
  const saved=await store.save(p);
  assert.match(saved.id,/^[0-9a-f-]{36}$/);
  assert.equal(saved.project.privacy,'private-draft');
  assert.equal(saved.project.release_approved,false);
  const file=await readdir(dir);assert.equal(file.length,1);
  assert.equal((await store.list())[0].duration,600);
  assert.equal((await store.get(saved.id)).scenes.length,30);
  saved.project.title='Refined cut';
  const update=await store.save(saved.project);
  assert.equal(update.id,saved.id);
  assert.equal((await store.get(saved.id)).title,'Refined cut');
  assert.equal((await readdir(dir)).length,1);
  await assert.rejects(()=>store.get('../../etc/passwd'),/Invalid project ID/);
 }finally{await rm(dir,{recursive:true,force:true});}
});
test('project saving API enforces configured operator login, CSRF and no public GitHub upload',async()=>{
 const dir=await mkdtemp(join(tmpdir(),'film-auth-project-store-'));
 const server=createServer({operatorEnv:{
  STUDIO_ADMIN_PASSWORD:'test-only-operator-passphrase-123456',
  STUDIO_PROJECT_DIR:dir
 },fetcher:async()=>{throw Error('no internet permitted')}});
 server.listen(0,'127.0.0.1');await once(server,'listening');
 const base='http://127.0.0.1:'+server.address().port;
 const headers={Origin:base,'X-Studio-Action':'1','Content-Type':'application/json'};
 try{
  const session=await (await fetch(base+'/api/session')).json();
  assert.equal(session.projects_enabled,true);
  assert.equal((await fetch(base+'/api/projects')).status,401);
  const unauthorized=await fetch(base+'/api/projects',{method:'POST',headers,body:JSON.stringify(startProject())});
  assert.equal(unauthorized.status,401);
  const login=await fetch(base+'/api/session',{method:'POST',headers,body:JSON.stringify({password:'test-only-operator-passphrase-123456'})});
  assert.equal(login.status,200);
  const cookie=login.headers.get('set-cookie').split(';')[0];
  const invalid=await fetch(base+'/api/projects',{method:'POST',headers:{...headers,Origin:'https://evil.example',Cookie:cookie},body:'{}'});
  assert.equal(invalid.status,403);
  const good=await fetch(base+'/api/projects',{method:'POST',headers:{...headers,Cookie:cookie},body:JSON.stringify(startProject({duration:300}))});
  assert.equal(good.status,201);
  const saved=await good.json();
  assert.equal(saved.saved,true);
  const list=await fetch(base+'/api/projects',{headers:{Cookie:cookie}});
  assert.equal(list.status,200);assert.equal((await list.json()).projects[0].duration,300);
  const opened=await fetch(base+'/api/projects/'+saved.id,{headers:{Cookie:cookie}});
  assert.equal(opened.status,200);
  const obj=await opened.json();
  assert.equal(obj.project.scenes.length,20);
  assert.equal(obj.project.release_approved,false);
  assert.equal(obj.project.privacy,'private-draft');
  assert.equal((await fetch(base+'/api/projects/'+saved.id)).status,401);
 }finally{await new Promise(resolve=>server.close(resolve));await rm(dir,{recursive:true,force:true});}
});
