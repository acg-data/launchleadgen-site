// Read-only deployment credential checks; never print the credential or response bodies.
import {mkdir,writeFile} from 'node:fs/promises';
const token=process.env.CLOUDFLARE_API_TOKEN,account=process.env.CLOUDFLARE_ACCOUNT_ID;
if(!token||!/^[a-f0-9]{32}$/.test(account||''))throw new Error('Cloudflare deployment secrets are unavailable in this repository.');
const required=(process.env.CLOUDFLARE_REQUIRED_SERVICES||'workers').split(',');
const routes=[['token','/user/tokens/verify'],['account','/accounts/'+account],['workers','/accounts/'+account+'/workers/scripts'],['pages','/accounts/'+account+'/pages/projects'],['kv','/accounts/'+account+'/storage/kv/namespaces'],['d1','/accounts/'+account+'/d1/database'],['zones','/zones?account.id='+account]];
const results=[];
for(const [resource,route] of routes){
 const response=await fetch('https://api.cloudflare.com/client/v4'+route,{headers:{authorization:'Bearer '+token},signal:AbortSignal.timeout(30000)});
 const body=await response.json().catch(()=>({}));
 const verified=response.ok&&body.success===true;
 results.push({resource,verified,httpStatus:response.status,required:required.includes(resource)});
 console.log(resource+': '+(verified?'verified':'HTTP '+response.status)+(required.includes(resource)?' (required)':' (informational)'));
}
await mkdir('.ci-results',{recursive:true});
await writeFile('.ci-results/cloudflare-ci-access.json',JSON.stringify({checked_at:new Date().toISOString(),results},null,2));
if(results.some(r=>r.required&&!r.verified))throw new Error('Required Cloudflare deployment resource is inaccessible. No deployment was attempted.');
console.log('Required Cloudflare resource access verified without deployment. Write permissions require the separate deployment workflow.');
