// Process framing only. The autonomous budget, models and learning run in XI/Python.
import path from 'node:path';
import {execFileSync} from 'node:child_process';

export function qmemoryCommand({root,argv}){
 if(!['auto','status','demo','prepare'].includes(argv[0]))throw Error('quantum memory auto NEW_RUN --runtime=REVERSE_PC [--resume] | prepare NEW_SESSION --runtime=REVERSE_PC | status RUN | demo RUN --runtime=REVERSE_PC');
 const script=argv[0]==='demo'?'demo.py':'controller.py';
 const args=argv[0]==='demo'?argv.slice(1):argv;
 const output=execFileSync(process.env.BBYQ_PYTHON||'python3',[path.join(root,'integration/qmemory',script),...args],
  {encoding:'utf8',timeout:1800000,maxBuffer:16*1024*1024});
 // auto emits JSON progress lines; status and demo emit one complete JSON object.
 const value=argv[0]==='auto'?output.trim().split('\n').at(-1):output;
 return {ok:true,...JSON.parse(value)};
}
