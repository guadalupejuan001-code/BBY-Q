import {execFileSync} from 'node:child_process';
import path from 'node:path';
export function balancedCommand({root,argv}){
 const result=execFileSync('python3',[path.join(root,'integration/balance/cli.py'),...argv],{encoding:'utf8',timeout:120000,maxBuffer:8*1024*1024});
 return JSON.parse(result);
}
