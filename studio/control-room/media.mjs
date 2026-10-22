import {inflateRawSync} from 'node:zlib';

const MAX_ZIP=25*1024*1024;
const MAX_VIDEO=30*1024*1024;
const allowedHost=h=>h==='githubusercontent.com'||h.endsWith('.githubusercontent.com')||
  h==='actions.githubusercontent.com'||h.endsWith('.actions.githubusercontent.com')||
  h==='blob.core.windows.net'||h.endsWith('.blob.core.windows.net');

async function boundedBuffer(response){
 if(!response.ok)throw Error('Artifact download unavailable');
 if(Number(response.headers.get('content-length')||0)>MAX_ZIP)throw Error('Artifact too large');
 if(!response.body)throw Error('No artifact body');
 let length=0;const chunks=[];
 for await(const chunk of response.body){
  length+=chunk.byteLength;
  if(length>MAX_ZIP){await response.body.cancel?.().catch(()=>{});throw Error('Artifact exceeds byte budget');}
  chunks.push(Buffer.from(chunk));
 }
 return Buffer.concat(chunks,length);
}
export function extractPreview(zip){
 const b=Buffer.from(zip);
 if(b.length>MAX_ZIP||b.length<22)throw Error('Invalid ZIP size');
 const min=Math.max(0,b.length-65557);let eocd=-1;
 for(let i=b.length-22;i>=min;i--){
  if(b.readUInt32LE(i)===0x06054b50){eocd=i;break;}
 }
 if(eocd<0)throw Error('ZIP directory missing');
 const count=b.readUInt16LE(eocd+10),directorySize=b.readUInt32LE(eocd+12),directoryOffset=b.readUInt32LE(eocd+16);
 if(count>300||directoryOffset+directorySize>b.length)throw Error('Invalid ZIP directory');
 let offset=directoryOffset;
 for(let i=0;i<count;i++){
  if(offset+46>b.length||b.readUInt32LE(offset)!==0x02014b50)throw Error('Invalid central ZIP header');
  const flags=b.readUInt16LE(offset+8),method=b.readUInt16LE(offset+10);
  const packed=b.readUInt32LE(offset+20),unpacked=b.readUInt32LE(offset+24),nameLen=b.readUInt16LE(offset+28);
  const extra=b.readUInt16LE(offset+30),comment=b.readUInt16LE(offset+32),loc=b.readUInt32LE(offset+42);
  if(offset+46+nameLen+extra+comment>b.length)throw Error('ZIP entry truncated');
  const name=b.subarray(offset+46,offset+46+nameLen).toString('utf8');
  offset+=46+nameLen+extra+comment;
  if(name!=='preview-6s.mp4'&&!name.endsWith('/preview-6s.mp4'))continue;
  if(flags&1||!(method===0||method===8)||packed>MAX_ZIP||unpacked>MAX_VIDEO||loc+30>b.length)throw Error('Unsafe ZIP preview entry');
  if(b.readUInt32LE(loc)!==0x04034b50)throw Error('ZIP local header missing');
  const dataAt=loc+30+b.readUInt16LE(loc+26)+b.readUInt16LE(loc+28);
  if(dataAt+packed>b.length)throw Error('ZIP entry outside archive');
  const compressed=b.subarray(dataAt,dataAt+packed);
  const video=method===0?Buffer.from(compressed):inflateRawSync(compressed,{maxOutputLength:MAX_VIDEO});
  if(video.length!==unpacked||video.length<16||video.toString('latin1',4,8)!=='ftyp')throw Error('Invalid MP4 artifact');
  return video;
 }
 throw Error('Six-second preview not found in artifact');
}
export async function readDemoMp4({fetcher=fetch,api,artifactId,token}){
 if(!Number.isSafeInteger(Number(artifactId))||Number(artifactId)<1||!token)throw Error('Invalid request');
 const url=api+'/actions/artifacts/'+artifactId+'/zip';
 const controller=new AbortController(),timeout=setTimeout(()=>controller.abort(),12000);
 try{
  const response=await fetcher(url,{redirect:'manual',signal:controller.signal,headers:{
   Authorization:'Bearer '+token,Accept:'application/vnd.github+json',
   'User-Agent':'ElijahFilmStudioOperator/0.2','X-GitHub-Api-Version':'2022-11-28'
  }});
  let bodyResponse=response;
  if(response.status===302||response.status===301||response.status===307){
   const location=response.headers.get('location');
   if(!location)throw Error('Missing artifact redirect');
   const redirect=new URL(location);
   if(redirect.protocol!=='https:'||!allowedHost(redirect.hostname))throw Error('Untrusted artifact redirect');
   bodyResponse=await fetcher(redirect.href,{signal:controller.signal,redirect:'error',headers:{'User-Agent':'ElijahFilmStudioOperator/0.2'}});
  }
  const zipped=await boundedBuffer(bodyResponse);
  return extractPreview(zipped);
 }finally{clearTimeout(timeout);}
}
