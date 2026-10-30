import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {execFileSync} from 'node:child_process';
import {BASE as B,PRIMARY,SCRATCH,SCRATCH_BYTES,SOURCE_ARCHIVE,REGION_END,ID_OFFSET,SCHEMA,HANDLED,STATUS,BANK,WITNESS,PROOF,F,C} from './schema.mjs';
import {readState,byte,readBytes,sha256} from './state.mjs';
import {roleSource} from './role.mjs';
const here=path.dirname(fileURLToPath(import.meta.url));

export function decodeCampaign(file){
 const s=readState(file);
 if(byte(s,PRIMARY)!==76||byte(s,PRIMARY+1n)!==71||byte(s,PRIMARY+2n)!==1)throw Error('The source is not an E009 learned state');
 const words=byte(s,PRIMARY+16n),concepts=byte(s,PRIMARY+17n),facts=byte(s,PRIMARY+18n);
 if(words<1||words>32||concepts<1||concepts>16||facts>24)throw Error('Source E009 capacity is incompatible');
 const vocabulary=Array.from({length:words},(_,i)=>{const p=PRIMARY+1000n+BigInt(i*16),len=byte(s,p),id=byte(s,p+1n);if(len<1||len>8||id<1||id>concepts)throw Error('Invalid source lexical record');const text=readBytes(s,p+2n,len).toString();if(!/^[a-z]+$/.test(text))throw Error('Source E009 token is outside its native alphabet');return{slot:i,word:text,old_id:id,new_id:id+ID_OFFSET,support:byte(s,p+10n),bytes:[...readBytes(s,p,16)]};});
 const assertions=Array.from({length:facts},(_,i)=>{const a=[...readBytes(s,PRIMARY+3000n+BigInt(i*8),8)];if(a.slice(0,3).some(id=>id<1||id>concepts))throw Error('Invalid source fact ID');return{slot:i,original:a,remapped:a.map((v,j)=>j<3?v+ID_OFFSET:v)};});
 const entities=Array.from({length:concepts},(_,i)=>{const id=i+1,remapped=id+ID_OFFSET,grounding=byte(s,PRIMARY+600n+BigInt(id)),transitive=byte(s,PRIMARY+2000n+BigInt(id));if(!grounding||transitive>1)throw Error('Invalid source learned concept');return{old_id:id,new_id:remapped,sensor_fingerprint:grounding,transitive,supporting_paths:byte(s,PRIMARY+2100n+BigInt(id)),contradicting_paths:byte(s,PRIMARY+2150n+BigInt(id))};});
 const originalCells=[...s.cells].filter(([a])=>a>=PRIMARY&&a<PRIMARY+10000000000000000n).map(([a,v])=>[a-PRIMARY,v]);
 if(originalCells.some(([offset])=>offset>=4096n))throw Error('Source E009 image exceeds the declared archive layout');
 return{s,vocabulary,assertions,entities,originalCells,words,concepts,facts};
}
export function migrationSource(campaign){
 const lines=['#!reverse-pc-machine-v1'],w=(...x)=>lines.push(...x),L=x=>w('label '+x),p=(a,v)=>w('store8 '+a+' '+v);
 w('load8 r0 '+B,'cmp r0 0','je campaign_install_empty','cmp r0 76','jne campaign_install_refuse','load8 r0 '+(B+1n),'cmp r0 71','jne campaign_install_refuse','load8 r0 '+(B+2n),'cmp r0 '+SCHEMA,'jne campaign_install_refuse');
 const digest=Buffer.from(campaign.s.sha256,'hex');for(const[i,v]of digest.entries())w('load8 r0 '+(B+64n+BigInt(i)),'cmp r0 '+v,'jne campaign_install_refuse');w('set r0 0','print r0','halt');
 L('campaign_install_empty');
 const ranges=[[B,128],[B+600n,128],[B+1000n,1024],[B+2000n,512],[B+3000n,256],[SOURCE_ARCHIVE,4096],[SCRATCH,SCRATCH_BYTES]];
 for(const[i,[start,length]]of ranges.entries()){w('set r0 0');L('campaign_empty_'+i);w('cmp r0 '+length,'jge campaign_empty_done_'+i,'set r7 '+start,'add r7 r0','load8 r1 $r7','cmp r1 0','jne campaign_install_refuse','add r0 1','jmp campaign_empty_'+i);L('campaign_empty_done_'+i);}
 const writes=new Map(),put=(a,v)=>{if(v)writes.set(a,v);};
 put(B+16n,campaign.words);put(B+17n,campaign.concepts+ID_OFFSET);put(B+18n,campaign.facts);put(B+19n,byte(campaign.s,PRIMARY+19n));put(B+24n,campaign.concepts);put(B+25n,ID_OFFSET);put(B+26n,2);put(B+27n,1);
 for(const[i,v]of digest.entries())put(B+64n+BigInt(i),v);
 put(B+96n,campaign.originalCells.length&255);put(B+97n,campaign.originalCells.length>>>8);
 for(const r of campaign.vocabulary){const record=[...r.bytes];record[1]=r.new_id;for(const[i,v]of record.entries())put(B+1000n+BigInt(r.slot*16+i),v);}
 for(const r of campaign.entities){put(B+600n+BigInt(r.new_id),r.sensor_fingerprint);put(B+2000n+BigInt(r.new_id),r.transitive);put(B+2100n+BigInt(r.new_id),r.supporting_paths);put(B+2150n+BigInt(r.new_id),r.contradicting_paths);}
 for(const r of campaign.assertions)for(const[i,v]of r.remapped.entries())put(B+3000n+BigInt(r.slot*8+i),v);
 for(const[offset,v]of campaign.originalCells)put(SOURCE_ARCHIVE+offset,v);
 for(const[a,v]of writes)p(a,v);
 // Publishing magic/version last is an additional ownership guard; the VM transaction is atomic.
 p(B,76);p(B+1n,71);p(B+2n,SCHEMA);w('set r0 0','print r0','halt');L('campaign_install_refuse');w('set r0 0','div r0 0');
 return lines.join('\n')+'\n';
}
export function buildCampaign(runtime,{alternateState,outDir}){
 runtime=path.resolve(runtime);alternateState=path.resolve(alternateState);outDir=path.resolve(outDir);
 fs.mkdirSync(outDir,{recursive:true});if(fs.existsSync(path.join(outDir,'campaign-build.json')))throw Error('Choose a new campaign asset directory');
 const campaign=decodeCampaign(alternateState),query=roleSource(),install=migrationSource(campaign);
 const oldCalibration=fs.readFileSync(path.join(here,'e009-calibrate.xi'),'utf8');
 const calibration=oldCalibration.replace(/\b710\d{16}\b/g,address=>String(B+BigInt(address)-PRIMARY)).replace('load8 r14 '+(B+2n)+'\ncmp r14 1\n','load8 r14 '+(B+2n)+'\ncmp r14 '+SCHEMA+'\n');
 if(calibration===oldCalibration||!calibration.includes('cmp r14 '+SCHEMA+'\n'))throw Error('Calibration source did not match the pinned E009 layout');
 const sources={'campaign-migrate.xi':install,'campaign-role.xi':query,'campaign-calibrate.xi':calibration},roles={};
 for(const[name,source]of Object.entries(sources)){const sourcePath=path.join(outDir,name),binaryPath=sourcePath.replace(/\.xi$/,'.rxe');fs.writeFileSync(sourcePath,source);execFileSync(runtime,['compile',sourcePath,binaryPath,'BBY Q X09 isolated E009 campaign '+name],{encoding:'utf8',timeout:30000,maxBuffer:8*1024*1024});roles[path.basename(binaryPath)]=sha256(fs.readFileSync(binaryPath));}
 const manifest={format:1,version:'X09-E009-Campaign-1',roles,source_sha256:Object.fromEntries(Object.entries(sources).map(([k,v])=>[k,sha256(Buffer.from(v))])),runtime_sha256:sha256(fs.readFileSync(runtime)),region:{start:String(B),end:String(REGION_END)},scratch:{start:String(SCRATCH),end:String(SCRATCH+BigInt(SCRATCH_BYTES))},source_state_sha256:campaign.s.sha256,source_e009_image_sha256:sha256(Buffer.from(JSON.stringify(campaign.originalCells.map(([a,v])=>[String(a),v])))),source_image_archive:{start:String(SOURCE_ARCHIVE),bytes:4096,nonzero_cells:campaign.originalCells.length},remapping:{concept_id_offset:ID_OFFSET,concepts:campaign.entities.map(x=>({source:x.old_id,target:x.new_id}))},learned:{word_records:campaign.words,concept_records:campaign.concepts,fact_records:campaign.facts,concepts:campaign.entities,vocabulary:campaign.vocabulary.map(({bytes,...x})=>x),facts:campaign.assertions},protocol:{handled:String(HANDLED),status:String(STATUS),bank:String(BANK),witness:String(WITNESS),proof:String(PROOF),input:String(C),input_length_low:String(F+8n),input_length_high:String(F+9n),handled_control_pending:String(F+2n),handled_control_result:String(F+3n)},caps:{word_bytes:8,words:32,concept_id:64,facts:24,proof_hops:2,query_input_bytes:64},preserves_primary_E009:true,execution_language:'XI',offline_builder:'Node.js',source_capsule_copied:false};
 fs.writeFileSync(path.join(outDir,'campaign-build.json'),JSON.stringify(manifest,null,2)+'\n');
 return manifest;
}
if(process.argv[1]&&path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){const[runtime,alternateState,outDir]=process.argv.slice(2);if(!outDir)throw Error('Usage: build.mjs RUNTIME ALTERNATE.rvp NEW_ASSET_DIR');const manifest=buildCampaign(runtime,{alternateState,outDir});console.log(JSON.stringify({ok:true,outDir:path.resolve(outDir),version:manifest.version,roles:manifest.roles,learned:manifest.learned,region:manifest.region}));}
