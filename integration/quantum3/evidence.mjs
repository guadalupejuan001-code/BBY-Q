// Published measurements belong to one checkpoint, never to a qubit count.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';

export function evaluationEvidence(root,checkpointSha256){
 const report=JSON.parse(fs.readFileSync(path.join(root,'docs/evidence/quantum3-evaluation/summary.json'),'utf8'));
 const sourcesMatch=Object.entries(report.xi_source_sha256).every(([name,digest])=>{
  const file=path.join(root,'ai/xi/quantum3',name);
  return fs.existsSync(file)&&crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex')===digest;
 });
 const applicable=report.checkpoint_sha256===checkpointSha256&&sourcesMatch;
 return {applicable,evaluated_sources_match:sourcesMatch,checkpoint_sha256:checkpointSha256,
  evaluated_checkpoint_sha256:report.checkpoint_sha256,
  ...(applicable?{results:report.results,limitations:report.limitations}:
   {reason:'The checkpoint or evaluated XI sources differ from the published evaluation; evaluate them separately.'}),
  evidence:report.evidence};
}
