// Only transports the certified profile. Every quantum gate runs in native XI.
import path from 'node:path';
import {execFileSync} from 'node:child_process';
export function exact100Command({root,argv}) {
 const output=execFileSync(process.env.BBYQ_PYTHON||'python3',
  [path.join(root,'integration/exact100/cli.py'),...argv],
  {encoding:'utf8',timeout:120000,maxBuffer:1024*1024});
 return JSON.parse(output);
}
