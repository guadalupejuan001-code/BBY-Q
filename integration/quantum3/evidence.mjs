// Published measurements belong to one checkpoint, never to a qubit count.
import fs from 'node:fs';
import path from 'node:path';

export function evaluationEvidence(root,checkpointSha256){
 const report=JSON.parse(fs.readFileSync(path.join(root,'docs/evidence/quantum3-evaluation/summary.json'),'utf8'));
 const applicable=report.checkpoint_sha256===checkpointSha256;
 return {applicable,checkpoint_sha256:checkpointSha256,
  evaluated_checkpoint_sha256:report.checkpoint_sha256,
  ...(applicable?{results:report.results,limitations:report.limitations}:
   {reason:'This checkpoint has not received the published evaluation; evaluate it separately.'}),
  evidence:report.evidence};
}
