// Validate the approved credential using read-only requests. Never log its value.
import {mkdir,writeFile} from 'node:fs/promises';
const token=process.env.CLOUDFLARE_API_TOKEN, account=process.env.CLOUDFLARE_ACCOUNT_ID;
if(!token||!/^[a-f0-9]{32}$/.test(account||''))throw new Error('Protected Cloudflare CI variables are unavailable on this ref.');
const routes=[['token','/user/tokens/verify'],['account',`/accounts/${account}`],['workers',`/accounts/${account}/workers/scripts`],['pages',`/accounts/${account}/pages/projects`],['kv',`/accounts/${account}/storage/kv/namespaces`],['d1',`/accounts/${account}/d1/database`],['zones',`/zones?account.id=${account}`]];
const results=[];
for(const [name,path] of routes){
  const response=await fetch('https://api.cloudflare.com/client/v4'+path,{headers:{authorization:`Bearer ${token}`},signal:AbortSignal.timeout(30000)});
  const body=await response.json().catch(()=>({}));
  if(!response.ok||body.success!==true)throw new Error(`Cloudflare ${name} credential check failed: HTTP ${response.status}`);
  if(name==='token'&&body.result?.status!=='active')throw new Error('Cloudflare token is not active');
  results.push({resource:name,status:'verified'});
}
await mkdir('.ci-results',{recursive:true});
await writeFile('.ci-results/cloudflare-ci-access.json',JSON.stringify({checked_at:new Date().toISOString(),results},null,2));
console.log('Cloudflare CI access verified: token, account, Workers, Pages, KV, D1, and zone metadata.');
