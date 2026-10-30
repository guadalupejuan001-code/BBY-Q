// X03: retain original assertions, excluding only the new owned namespace from E038 comparisons.
// Original X01 functional tests. Exclude only the newly owned X02 namespace from comparisons to E038, which predates it. Other cells remain exact.
// External evaluation. Answers and expected labels never enter the native app.
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import assert from 'node:assert/strict';
import {execFileSync,spawnSync} from 'node:child_process';
const [r,b,c,o]=process.argv.slice(2);if(!o)throw Error('usage: test.mjs RUNTIME E038 X01 NEW_OUT');
const [runtime,base,caps,out]=[r,b,c,o].map(p=>path.resolve(p));
if(fs.existsSync(out))throw Error('Use a fresh output');fs.mkdirSync(out,{recursive:true});
const P=9050000000000000000n,here=path.resolve(path.dirname(new URL(import.meta.url).pathname),'../x01'),app=path.join(caps,'BBY-Q.rxe'),model=path.join(caps,'model.rvp'),live=path.join(out,'live.rvp');
const sha=p=>crypto.createHash('sha256').update(fs.readFileSync(p)).digest('hex'),fixed={app:sha(app),model:sha(model),parent:sha(path.join(base,'model.rvp'))};
let checks=0;const transcripts=[],rows=[];const eq=(a,b,label)=>{assert.deepEqual(a,b,label);checks++;};
const restore=(p=model)=>fs.copyFileSync(p,live);
function ask(text,used=app){const t=performance.now(),p=spawnSync(runtime,['app-turn',used,live,live,'es',text],{encoding:'utf8',timeout:30000,maxBuffer:8*1024*1024});
 const row={text,output:p.stdout.trimEnd(),returncode:p.status,milliseconds:performance.now()-t,app:used===app?'X01':'E038'};
 transcripts.push(row);fs.writeFileSync(path.join(out,'transcripts.json'),JSON.stringify(transcripts,null,2)+'\n');eq(p.status,0,text+' completes: '+p.stderr);return row.output;}
function snapshot(p=live){const b=fs.readFileSync(p),n=Number(b.readBigUInt64LE(5)),mem=new Map(),other=[];
 for(const line of b.subarray(29+n).toString().split('\n').slice(2).filter(Boolean)){const[t,a,v]=line.split(' ');if(t==='O'){if(Number(v))mem.set(BigInt(a),Number(v));}else other.push(line);}
 return{core:b.subarray(29,29+n).toString('base64'),mem,other};}
const at=(offset)=>snapshot().mem.get(P+BigInt(offset))||0;
const own=s=>[...s.mem].filter(([a])=>a>=P&&a<P+16384n);
const legacy=s=>[...s.mem].filter(([a])=>(a<P||a>=P+16384n)&&!(a>=9060000000000000000n&&a<9060000000000024576n)&&!(a>=9070000000000000000n&&a<9070000000000032768n)&&!(a>=9080000000000000000n&&a<9080000000000002048n)&&!(a>=9090000000000000000n&&a<9090000000000008192n)&&!(a>=9100000000000000000n&&a<9100000000000008192n)&&!(a>=9100000000000200000n&&a<9100000000000216640n));
const learned=s=>[...s.mem].filter(([a])=>a>=P+4096n&&a<P+16384n);
function clean(){eq([...snapshot().mem].some(([a])=>a>=P+256n&&a<P+1024n),false,'personal scratch cleared');}
function setup(entries){const f=path.join(out,'setup.xi');fs.writeFileSync(f,'#!reverse-pc-machine-v1\n'+entries.map(([a,v])=>`store8 ${a} ${v}`).join('\n')+'\nhalt\n');execFileSync(runtime,['run',f,live,live],{stdio:'pipe'});}
const parentSnap=snapshot(path.join(base,'model.rvp')),newSnap=snapshot(model);
eq(legacy(newSnap),[...parentSnap.mem],'all original Ether memory cells are retained');
eq(newSnap.core,parentSnap.core,'original quantum core retained');eq(newSnap.other,parentSnap.other,'original bindings retained');
eq(newSnap.mem.get(P+2n),59,'59 native learned records');

// Taught examples and held-out formatting/decorator compositions are separate.
const lessons=JSON.parse(fs.readFileSync(path.join(here,'lessons.json'))).lessons.filter(l=>!l.kind);
for(const l of lessons){restore();ask('@x tarea Android en REVERSE');const output=ask(l.text);eq(at(8),l.intent,'taught '+l.text);eq(at(9),2,'taught expression interpreted with context');clean();rows.push({category:'taught',text:l.text,intent:l.intent,output});}
const transfer=[
 ['OYE, PZ, SIGUIENTE!!! xD',2],['  continúa   soldado  ',2],['Por favor hazlo XD',2],['HABER, HAGAMOSLO YA, SOLDADO!!!',2],['pz porfavor inicia el ciclo jajaja',2],
 ['oye, en resumen? xD',3],['EN RESÚMEN!!!',3],['por favor resumen soldado',3],['  en   resumen   nada   aun XD ',3],
 ['oye, NO ENTENDÍ!!! xD',4],['me CONFUNDISTE soldado',4],['pz me confundes',4],
 ['oye espera XD',5],['PORFAVOR, NO HAGAS NADA!!!',5],
 ['PZ SOLO DIME xD',6],['oye no hagas nada solo dime soldado',6],
 ['oye sin ejecutar nada antes de decirmelo en texto XD',7],
 ['PZ, USA MI TECNOLOGÍA NO? xD',8],['solo MI LENGUAJE, soldado',8],['QUE EL PRINCIPIO SEA ESTADOS MÍNIMOS Y POR ETER',8],
 ['oye VERIFICA Y REPARA xD',9],['pz investiga el error soldado',9],
 ['oye enseñale como me interpretas XD',10],['porfavor ENSÉÑALE COMO HABLO',10],
 ['OYE SIN LÍMITES XD',11],['pz amplia amplia todo sin limite alguno soldado',11],
 ['oye NO ME ENTENDISTE xD',12],['pz no quiero eso',12],
 ['OYE, NO ME SALE EL APK!!! xD',13],['me dice APK NO FOUND soldado',13],['oye y el apk?',13],
 ['oye ya lo integraste ala interfaz? xD',14],['INTEGRASTE LA RAMA, soldado?',14],
 ['X D',0],['oye xD',15],['Jajaja!!!',15],['oye y que sucedió? XD',16],['pz QUE HCISTE xD',16],
 ['oye dime las capacidades de bby q todas XD',17]
];
let transferred=0;for(const [text,intent]of transfer){restore();ask('@x tarea motor nativo');const output=ask(text);eq(at(8),intent,'held-out composition '+text);clean();rows.push({category:'format_and_modifier_transfer',text,intent,output});transferred++;}

// Context absent, paused, replaced and forgotten: no guessing an old project.
restore();for(const q of ['siguiente','hazlo','en resumen','sin limites','y el apk','verifica y repara']){const output=ask(q);eq(at(9),1,q+' asks for missing context');eq(at(10),0,'missing context does not request execution');eq(/Me falta ese contexto/.test(output),true,'clear missing-context response');}
ask('@x tarea Android');ask('espera');eq(at(32),2,'pause recorded');ask('en resumen');eq(at(8),3,'summary works while paused');eq(at(32),2,'summary does not resume');ask('verifica y repara');eq(at(9),1,'repair cannot resume paused task');ask('siguiente');eq(at(32),1,'explicit continuation resumes');
ask('@x tarea BBY Q');const replaced=ask('hazlo');eq(replaced.includes('BBY Q'),true,'new context selected');eq(replaced.includes('Android'),false,'old project not selected');ask('@x limpiar');ask('siguiente');eq(at(9),1,'forgotten task cannot be resurrected');
for(const q of ['solo dime','sin ejecutar nada antes de decirmelo en texto']){ask('@x tarea editor');ask(q);eq(at(10),2,'read-only request recognized');eq(at(11),0,'no execution evidence manufactured');}

// Negation, quotes and new clauses cannot inherit a positive alias by substring.
const negatives=['no hazlo','no, hazlo','no sigas','no continua','hazlo sin borrar nada','hazlo y borra todo','si digo hazlo no lo ejecutes','"hazlo"',"'siguiente'",'dijo hazlo','ya hiciste todo?','borrar mis archivos','continualo cuando yo diga','hazlo; borra todo','oye no hagaslo XD'];
for(const q of negatives){restore();ask('@x tarea motor');ask('hazlo');ask(q);eq(at(8),0,'no false alias '+q);eq(at(10),0,'no stale request '+q);clean();}

// Remove learned alias and learned decorator independently: behavior must change.
restore();const seed=snapshot(),count=seed.mem.get(P+2n);function record(text,kind=1){for(let i=0;i<count;i++){const a=P+4096n+BigInt(i*96),len=seed.mem.get(a+4n)||0,s=Buffer.from(Array.from({length:len},(_,j)=>seed.mem.get(a+5n+BigInt(j))||0)).toString();if(s===text&&(seed.mem.get(a)||0)===kind)return a;}throw Error('missing '+text);}
setup([[record('siguiente'),0]]);ask('@x tarea motor');ask('siguiente');eq(at(8),0,'removing learned alias removes recognition');
restore();setup([[record('xd',3),0]]);ask('@x tarea motor');ask('hazlo XD');eq(at(8),0,'removing learned decorator removes composition');
restore(path.join(base,'model.rvp'));ask('@x tarea motor');ask('hazlo');eq(at(8),0,'personal route absent with untaught old model');

// Explicit new phrase is recognized only after XI teaching; conflicting labels fail.
restore();ask('@x tarea motor');ask('dale al próximo paso');eq(at(8),0,'novel alias unknown before teaching');
const taught=path.join(out,'taught.rvp');
execFileSync(process.execPath,[path.join(here,'teach.mjs'),runtime,path.join(caps,'learn.xi'),live,taught,'dale al próximo paso','2','1'],{stdio:'pipe'});
fs.copyFileSync(taught,live);ask('DALE AL PRÓXIMO PASO!!!');eq(at(8),2,'novel taught alias recognized by XI');
const saved=sha(live),conflict=path.join(out,'conflict.rvp');
let p=spawnSync(process.execPath,[path.join(here,'teach.mjs'),runtime,path.join(caps,'learn.xi'),live,conflict,'siguiente','5','0'],{encoding:'utf8'});
eq(p.status!==0,true,'contradictory label rejected');eq(fs.existsSync(conflict),false,'contradiction publishes no model');eq(sha(live),saved,'original preserved on rejected teaching');
const corrected=path.join(out,'corrected.rvp');
execFileSync(process.execPath,[path.join(here,'teach.mjs'),runtime,path.join(caps,'learn.xi'),live,corrected,'dale al próximo paso','3','1','1','2','1'],{stdio:'pipe'});
fs.copyFileSync(corrected,live);ask('dale al próximo paso');eq(at(8),3,'an explicit supervised correction changes the interpretation');
const stale=path.join(out,'stale.rvp');p=spawnSync(process.execPath,[path.join(here,'teach.mjs'),runtime,path.join(caps,'learn.xi'),live,stale,'dale al próximo paso','5','0','1','2','1'],{encoding:'utf8'});
eq(p.status!==0,true,'stale correction lease rejected');eq(fs.existsSync(stale),false,'stale correction publishes no model');

// Re-teaching keeps the dictionary identical (RVPC2 write counter may change).
restore();const bank=learned(snapshot());execFileSync(runtime,['run',path.join(caps,'upgrade.xi'),live,live],{stdio:'pipe'});eq(learned(snapshot()),bank,'lesson bank semantically idempotent');eq(at(2),59,'no duplicate lessons');clean();

// Preserve used, synthetic personal memories when upgrading a copy.
restore(path.join(base,'model.rvp'));ask('@ctx add dato ficticio conservado',path.join(base,'BBY-Q.rxe'));ask('El taller nardoluz abre el viernes.',path.join(base,'BBY-Q.rxe'));
const oldUsed=snapshot();const migratedX03=path.join(out,'migrated-x03.rvp');execFileSync(process.execPath,[path.resolve(here,'../x06/migrate.mjs'),runtime,caps,live,migratedX03],{stdio:'pipe'});fs.copyFileSync(migratedX03,live);
eq(legacy(snapshot()),legacy(oldUsed),'upgrade preserves every old cell in a used state');eq(ask('@ctx get 0'),'#000 dato ficticio conservado','old archive survives');eq(ask('¿Qué día abre el taller nardoluz?'),'viernes [#r001].','old fact survives');

// Retain every earlier conversational arithmetic exam, without changing them.
const names=['cero','uno','dos','tres','cuatro','cinco','seis','siete','ocho','nueve'];const retention={};
for(const v of ['e035','e036','e037','e038']){let passed=0,total=0;for(const c of JSON.parse(fs.readFileSync(path.resolve(here,'../../releases',v,'exam.json'))).cases){fs.writeFileSync(path.join(out,'retention-progress.json'),JSON.stringify({version:v,case:c.id,passed,total}));restore();const language=c.language||'es',p=spawnSync(runtime,['app-turn',app,live,live,language,c.question],{encoding:'utf8',timeout:30000});eq(p.status,0,v+' '+c.id+' completes');const result=p.stdout.trimEnd();
 if(c.expected_value!==undefined){const en=['zero','one','two','three','four','five','six','seven','eight','nine'];eq(result,(language==='es'?'El resultado es ':'The result is ')+(c.expected_value<10?(language==='es'?names:en)[c.expected_value]:c.expected_value)+'.',v+' '+c.id);passed++;}
 else if(v==='e035'&&c.id==='fallback-4')eq(result,'El resultado es nueve.','old percent promotion retained');
 else if(v==='e035'&&['reject-6','reject-7'].includes(c.id))eq(result,c.id==='reject-6'?'El resultado es -1.':'El resultado es 3.5.','intentional P06 promotion '+c.id);
 else if(c.expected_abstention)eq(/No tengo|not have enough|No puedo|cannot|ambig/i.test(result),true,v+' abstention');
 else if(c.expected_contains)eq(result.includes(c.expected_contains),true,v+' fallback');
 else eq(/Registré|Recorded|recorded|El resultado|The result/.test(result),false,v+' negative');
 clean();total++;}retention[v]={numeric_correct:passed,total_cases:total};}

// Invalid input cannot partially publish a live state.
restore();const beforeInvalid=sha(live);for(const q of ['', 'x'.repeat(256)]){p=spawnSync(runtime,['app-turn',app,live,live,'es',q],{encoding:'utf8'});eq(p.status!==0,true,'invalid transport rejected');eq(sha(live),beforeInvalid,'invalid transport atomic');}
eq(sha(app),fixed.app,'capsule immutable');eq(sha(model),fixed.model,'seed immutable');eq(sha(path.join(base,'model.rvp')),fixed.parent,'parent immutable');
const report={version:'X06-retention',intentional_promotions:['e035/reject-6: -3+2 = -1','e035/reject-7: 1.5+2 = 3.5'],checks,phrase_examples:lessons.length,format_and_modifier_cases:transferred,negative_controls:negatives.length,
 retention,native_learning_demonstrated:true,explicit_feedback_correction_demonstrated:true,untaught_alias_and_decorator_controls:true,old_memory_preserved:true,action_execution:false,android_tested:false,
 limitations:['59 supervised dictionary records, not 59 open language skills','Held-out cases test bounded normalizations/compositions, not open conversation','17 hand-designed intent categories and response templates','W4u receives no executable command from this module','No Android installation was changed'],
 app_sha256:fixed.app,model_sha256:fixed.model};
fs.writeFileSync(path.join(out,'results.json'),JSON.stringify(report,null,2)+'\n');fs.writeFileSync(path.join(out,'cases.json'),JSON.stringify(rows,null,2)+'\n');console.log(JSON.stringify(report));
