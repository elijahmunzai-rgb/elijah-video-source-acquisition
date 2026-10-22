import {randomUUID} from 'node:crypto';
import {mkdir,readFile,readdir,rename,writeFile,unlink,stat} from 'node:fs/promises';
import {isAbsolute,join,resolve} from 'node:path';
import {validateProject} from './project-schema.mjs';

const ID=/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/;
const MAX_PROJECTS=50;
const MAX_BYTES=180000;

export function createProjectStore(root){
 // Fail closed unless the site operator explicitly provided a private absolute directory.
 const enabled=typeof root==='string'&&root.length>5&&root.length<500&&isAbsolute(root)&&
   !['/','/tmp','/var','/home','/root'].includes(resolve(root));
 if(!enabled)return {enabled:false};
 const dir=resolve(root);
 const file=id=>{
  if(!ID.test(id))throw Error('Invalid project ID');
  return join(dir,id+'.json');
 };
 async function prepare(){
  await mkdir(dir,{recursive:true,mode:0o700});
  const s=await stat(dir);
  if(!s.isDirectory())throw Error('Private project storage not a directory');
 }
 async function get(id){
  await prepare();
  const f=await readFile(file(id),'utf8');
  const p=JSON.parse(f);
  if(p.id!==id||!validateProject(p).ok)throw Error('Saved project is invalid');
  return p;
 }
 async function list(){
  await prepare();
  const files=(await readdir(dir)).filter(n=>n.endsWith('.json')&&ID.test(n.slice(0,-5)));
  if(files.length>MAX_PROJECTS)throw Error('Project quota exceeded');
  const results=[];
  for(const name of files){
   const raw=await readFile(join(dir,name),'utf8');
   if(Buffer.byteLength(raw)>MAX_BYTES)continue;
   let p;try{p=JSON.parse(raw);}catch{continue;}
   if(p.id!==name.slice(0,-5)||!validateProject(p).ok)continue;
   results.push({id:p.id,title:String(p.title||'').slice(0,80),
     duration:p.duration,aspect:p.aspect,scene_count:p.scenes.length,updated_at:p.updated_at||p.created_at||null});
  }
  results.sort((a,b)=>String(b.updated_at||'').localeCompare(String(a.updated_at||'')));
  return results;
 }
 async function save(input){
  if(!input||typeof input!=='object'||Array.isArray(input))throw Error('Invalid project body');
  const p=structuredClone(input);
  p.release_approved=false; // Save is never approval to publish or render.
  p.privacy='private-draft';
  const valid=validateProject(p);
  if(!valid.ok)throw Error('Project invalid: '+valid.errors.slice(0,3).join('; '));
  const dataBytes=Buffer.byteLength(JSON.stringify(p));
  if(dataBytes>MAX_BYTES)throw Error('Project exceeds storage size limit');
  await prepare();
  const files=await readdir(dir);
  const requested=typeof p.id==='string'&&ID.test(p.id)?p.id:null;
  let id;
  if(requested){
   try{await get(requested);id=requested;}
   catch(e){if(e.code!=='ENOENT')throw e;}
  }
  if(!id){
   if(files.filter(n=>n.endsWith('.json')).length>=MAX_PROJECTS)throw Error('Maximum stored projects reached');
   id=randomUUID();
  }
  p.id=id;p.updated_at=new Date().toISOString();
  p.created_at=p.created_at||p.updated_at;
  const bytes=JSON.stringify(p,null,2);
  const tmp=file(id)+'.'+randomUUID()+'.writing';
  try{
   await writeFile(tmp,bytes,{encoding:'utf8',mode:0o600,flag:'wx'});
   await rename(tmp,file(id));
  }catch(e){await unlink(tmp).catch(()=>{});throw e;}
  return {id,project:p};
 }
 return {enabled:true,get,list,save};
}
