// Transport only. Gate execution, token prediction and SGD belong to native XI.
import path from 'node:path';
import {execFileSync} from 'node:child_process';
export function qchat100Command({root,argv}) {
 const output=execFileSync(process.env.BBYQ_PYTHON||'python3',
  [path.join(root,'integration/qchat100/cli.py'),...argv],
  {encoding:'utf8',timeout:120000,maxBuffer:2*1024*1024});
 return JSON.parse(output);
}
