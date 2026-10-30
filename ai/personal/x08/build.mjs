// Deterministic offline assembly and curriculum reconciliation. Live cognition is XI.
import fs from 'node:fs';import path from 'node:path';import crypto from 'node:crypto';import zlib from 'node:zlib';import {execFileSync} from 'node:child_process';
import {frontSource} from './front.mjs';import {assembler} from './asm.mjs';import {lexicon} from './lexicon.mjs';
import {B,S,BOOK,PAGES,TEXT,DICT,WORDS,INDEX,ROW,CAPACITY,INDEX_STRIDE,I,F} from './schema.mjs';
import {encode,makeDictionary} from './book-codec.mjs';import {bankRole} from '../x07/bank.mjs';import {B as X7,K,S as S7,STAGE} from '../x07/schema.mjs';
const [r,b,d,o]=process.argv.slice(2);if(!o)throw Error('Usage: build.mjs RUNTIME X07_BUILD DATA NEW_OUT');
const [rt,base,data,out]=[r,b,d,o].map(x=>path.resolve(x));if(fs.existsSync(out))throw Error('Choose a fresh build');fs.mkdirSync(out,{recursive:true});
let phaseNumber=0;
const sha=b=>crypto.createHash('sha256').update(b).digest('hex'),read=n=>fs.readFileSync(path.join(base,n)),write=(n,v)=>fs.writeFileSync(path.join(out,n),v),strip=s=>s.split('\n').filter(l=>!l.startsWith('#!')).join('\n');
// Every native phase consumes an immutable input and publishes a distinct output.
// A success event alone is not used as proof that a lesson survived publication.
function run(...args){
 const same=args[0]==='run'&&args[2]===args[3],destination=same?args[3]:null,next=same?path.join(out,'.phase-'+phaseNumber+++'.rvp'):null;
 if(same)args[3]=next;
 try{const output=execFileSync(rt,args,{encoding:'utf8',timeout:60000,maxBuffer:16*1024*1024});if(same)fs.renameSync(next,destination);return output;}
 finally{if(next&&fs.existsSync(next))fs.unlinkSync(next);}
}
const OLD_S7=9110000000000500000n,NEW_S7=9110000000004000000n;
function relocate(text){return text.replace(/\b\d{19}\b/g,n=>{const p=BigInt(n);return p>=OLD_S7&&p<OLD_S7+8192n?String(NEW_S7+p-OLD_S7):n;});}
function widen(text){return relocate(text).replaceAll('load8 r0 9110000000000000001\ncmp r0 1\n','load8 r0 9110000000000000001\ncmp r0 2\n').replaceAll('cmp r0 512\n','cmp r0 4096\n').replaceAll('cmp r10 512\n','cmp r10 4096\n');}
for(const [file,expected] of Object.entries({'BBY-Q.rxe':'0e76be1dd41adedbce86e7467a56c0291af777aac0e9a3639972e710ce97c03e','conversation.xi':'f2932bcb09ed7eaa013b0882f4cf9a9f72c15d0649059241d0d3d4665d5a9432','model.rvp':'d9800e677553c8f0abb909821c9a0845329a41da229da415ebbd082ac1afb40e'}))if(sha(read(file))!==expected)throw Error('Pinned X07 parent required: '+file);
const catalog=JSON.parse(fs.readFileSync(path.join(data,'curriculum.json'))),pages=fs.readFileSync(path.join(data,'pages.jsonl'),'utf8').trim().split('\n').map(JSON.parse),dict=lexicon();
if(catalog.concepts.length>512||pages.length!==122||dict.length>CAPACITY)throw Error('Dataset capacity');
write('curriculum.json',JSON.stringify(catalog,null,2)+'\n');write('pages.jsonl',pages.map(p=>JSON.stringify(p)).join('\n')+'\n');
for(const n of ['guard.xi','guard-x07.xi','text-finish.xi','dispatch.xi','review.xi','result.xi','qdu-plan.xi','qdu-dispatch.xi','learn.xi','learn-bank.xi',...fs.readdirSync(base).filter(x=>/^upgrade-parent-.*\.xi$/.test(x))])if(fs.existsSync(path.join(base,n)))write(n,n==='guard-x07.xi'||n==='learn-bank.xi'?widen(read(n).toString()):read(n));
write('text-finish.xi',read('text-finish.xi').toString().replace('halt\nlabel x6finish_refuse','store8 '+(B+2n)+' 0\nhalt\nlabel x6finish_refuse'));
let parent=read('conversation.xi').toString();const moduleEnd=parent.indexOf('label x7_parent\n');if(moduleEnd<0)throw Error('Pinned X07 shape');parent=widen(parent.slice(0,moduleEnd))+relocate(parent.slice(moduleEnd));if(parent.split('label x6_match_routes\njmp x7_routes\n').length!==2||parent.split('label e29_rewrite_start\n').length!==2)throw Error('Parent dispatch shape');
parent=parent.replace('label x6_match_routes\njmp x7_routes\n','label x6_match_routes\njmp x8_routes\n').replace('label e29_rewrite_start\n','label e29_rewrite_start\ncmp r2 1\njne x8_no_consent\n');

parent=parent.replace('label x6_match_routes\njmp x8_routes\n','label x6_match_routes\njmp x7_routes\n').replace('jne x8_no_consent','jne x08_consent');
const consent=assembler();consent.L('x08_consent');consent.ld(0,F+3n);consent.w('cmp r0 1','jne x08_consent_ready');consent.st(9100000000000100200n,1);consent.L('x08_consent_ready');consent.say('No guardé esa afirmación. Para conservarla, escribe «recuerda que …» o usa una enseñanza explícita.');consent.w('jmp x6_done');
const code='#!reverse-pc-machine-v1\n'+strip(parent)+'\n'+consent.lines.join('\n')+'\n';write('conversation.xi',code);run('compile',path.join(out,'conversation.xi'),path.join(out,'code.rxe'),'BBY Q X08 preserved X07 and explicit archive consent');
const front=frontSource(parent,fs.readFileSync(path.join(out,'guard-x07.xi'),'utf8'));write('front.xi',front);run('compile',path.join(out,'front.xi'),path.join(out,'front.rxe'),'BBY Q X08 native language and curriculum dispatch');
const model=path.join(out,'model.rvp');write('model.rvp',read('model.rvp'));
const upgrade='#!reverse-pc-machine-v1\nload8 r0 9110000000000000001\ncmp r0 1\nje apply\ncmp r0 2\njne refuse\nhalt\nlabel apply\nstore8 9110000000000000001 2\nhalt\nlabel refuse\nset r0 0\nmod r0 0\n';write('upgrade-knowledge-bank.xi',upgrade);run('run',path.join(out,'upgrade-knowledge-bank.xi'),model,model);
const learned=[],migration=['upgrade-knowledge-bank.xi'];const learner=widen(strip(bankRole()));
for(const [i,record]of catalog.concepts.entries()){
 if(i<224)continue;
 let s='#!reverse-pc-machine-v1\nstore8 '+S7+' 1\n';const p=(p,v)=>{s+=`store8 ${p} ${v}\n`;};p(STAGE,1);p(STAGE+6n,3);
 for(const[k,offset,start,max]of [['key',1,16,64],['definition',2,80,224],['requirement',3,304,224],['source',4,528,32],['pages',5,560,32]]){const v=Buffer.from(record[k]);if(v.length<1||v.length>max)throw Error('Training field: '+record.key+' '+k);p(STAGE+BigInt(offset),v.length);for(const[j,c]of v.entries())p(STAGE+BigInt(start+j),c);}
 s=relocate(s)+learner;const n='install-lesson-'+String(i).padStart(3,'0')+'.xi';write(n,s);const events=run('run',path.join(out,n),model,model).split('\n').filter(l=>l.startsWith('{')).map(JSON.parse).filter(x=>x.type==='register');if(events.length!==1||events[0].value!==0)throw Error('Native teaching refused '+record.key);learned.push({index:i,key:record.key,status:0});migration.push(n);
 if((i-223)%32===0)console.log('X08 native training '+(i+1)+'/'+catalog.concepts.length);
}
// Native data installation checks unowned ranges; a partly installed state is never published.
let stores='';const p=(p,v)=>{if(v)stores+=`store8 ${p} ${v}\n`;},bytes=(addr,b)=>{for(const[i,v]of Buffer.from(b).entries())p(addr+BigInt(i),v);},u=(addr,v,n)=>{for(let i=0;i<n;i++){p(addr+BigInt(i),v&255);v=Math.floor(v/256);}};
const bookDictionary=makeDictionary(pages);write('book-dictionary.bin',bookDictionary);p(BOOK,88);p(BOOK+1n,1);u(BOOK+14n,bookDictionary.length,2);bytes(BOOK+128n,bookDictionary);u(BOOK+2n,122,2);let offset=0,compressedOffset=0;const encoded=[];for(const page of pages){const b=Buffer.from(page.text),packed=encode(b,bookDictionary),entry=PAGES+BigInt((page.page-1)*8);if(sha(b)!==page.sha256)throw Error('Page hash');u(entry,compressedOffset,4);u(entry+4n,b.length,2);u(entry+6n,packed.length,2);bytes(TEXT+BigInt(compressedOffset),packed);encoded.push(packed);offset+=b.length;compressedOffset+=packed.length;}u(BOOK+4n,offset,4);u(BOOK+8n,compressedOffset,4);p(BOOK+12n,1);
p(DICT,88);p(DICT+1n,1);u(DICT+2n,dict.length,2);for(const[i,row]of dict.entries()){const a=WORDS+BigInt(i*ROW);p(a,row.kind);p(a+1n,Buffer.byteLength(row.es));p(a+2n,Buffer.byteLength(row.en));bytes(a+8n,row.es.toLowerCase());bytes(a+132n,row.en);}
const normalize=t=>t.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9]+/g,' ').trim().split(/ +/).filter(x=>x.length>=2&&x.length<=32),stop=new Set('de la el en que con sin los las un una unos unas es son del por para como y o a the and of in to is are was were for from with that this as be it on at an or not no al se su sus lo'.split(' ')),terms=new Map();
function index(text,id){for(const term of new Set(normalize(text))){if(stop.has(term))continue;if(!terms.has(term))terms.set(term,new Set());terms.get(term).add(id);}}
for(const[i,c]of catalog.concepts.entries())index(c.key+' '+c.definition+' '+c.requirement,i);for(const page of pages)index(page.text,512+page.page-1);
// Cross-language aliases expose existing source evidence, never invented answers.
for(const row of dict.filter(x=>x.kind===1)){const es=normalize(row.es),en=normalize(row.en);if(es.length!==1||en.length!==1||stop.has(es[0])||stop.has(en[0]))continue;const ids=new Set([...(terms.get(es[0])||[]),...(terms.get(en[0])||[])]);if(ids.size){terms.set(es[0],new Set(ids));terms.set(en[0],new Set(ids));}}
const buckets=Array(4093).fill(0),entries=[];for(const [term,set]of [...terms].sort((a,b)=>a[0].localeCompare(b[0],'en'))){const ids=[...set].sort((a,b)=>a-b);if(ids.length>64)continue;let h=0;for(const b of Buffer.from(term))h=(h*33+b)%4093;for(let i=0;i<ids.length;i+=32){entries.push({term,ids:ids.slice(i,i+32),next:buckets[h]});buckets[h]=entries.length;}}
if(entries.length>65535)throw Error('Index capacity');p(INDEX,88);p(INDEX+1n,1);u(INDEX+2n,entries.length,2);for(const[i,v]of buckets.entries())u(INDEX+256n+BigInt(i*2),v,2);for(const[i,c]of catalog.concepts.entries()){const a=INDEX+10000n+BigInt(i*66);p(a,Buffer.byteLength(c.key));bytes(a+1n,c.key);}
for(const[i,x]of entries.entries()){const a=INDEX+65536n+BigInt(i*INDEX_STRIDE);p(a,Buffer.byteLength(x.term));p(a+1n,x.ids.length);u(a+2n,x.next,2);bytes(a+8n,x.term);for(const[j,v]of x.ids.entries())u(a+40n+BigInt(j*2),v,2);}
// Split installation so every phase fits the unchanged VM instruction budget.
const lines=stores.trimEnd().split('\n'),parts=[];for(let i=0;i<lines.length;i+=24000){const n='install-data-'+String(parts.length).padStart(2,'0')+'.xi';write(n,'#!reverse-pc-machine-v1\n'+lines.slice(i,i+24000).join('\n')+'\nhalt\n');run('run',path.join(out,n),model,model);parts.push(n);}migration.push(...parts);
write('activate-x08.xi',`#!reverse-pc-machine-v1\nstore8 ${B} 88\nstore8 ${B+1n} 1\nhalt\n`);run('run',path.join(out,'activate-x08.xi'),model,model);migration.push('activate-x08.xi');
const {snapshot}=await import('../x05/io.mjs');const cells=snapshot(model),encodedBook=Buffer.concat(encoded);for(let i=0;i<compressedOffset;i++)if((cells.get(TEXT+BigInt(i))||0)!==encodedBook[i])throw Error('Book reconstruction');
const bankBase=9110000000000000000n,bankRows=bankBase+4096n;
const field=(p,n)=>Buffer.from(Array.from({length:n},(_,i)=>cells.get(p+BigInt(i))||0)).toString('utf8'),records=new Map();
for(let i=0;i<4096;i++){const p=bankRows+BigInt(i*640);if(cells.get(p)!==1)continue;records.set(field(p+16n,cells.get(p+1n)||0),{definition:field(p+80n,cells.get(p+2n)||0),requirement:field(p+304n,cells.get(p+3n)||0)});}
if((cells.get(bankBase+2n)||0)+256*(cells.get(bankBase+3n)||0)!==catalog.concepts.length||records.size!==catalog.concepts.length)throw Error('Native training count differs from the declared curriculum; no release was published');
for(const record of catalog.concepts){const saved=records.get(record.key.toLowerCase());if(!saved||saved.definition!==record.definition||saved.requirement!==record.requirement)throw Error('Native training retention failed: '+record.key);}
const app=false,packError='X08 uses two native XI roles sharing one state. Use run.mjs/session.mjs with code.rxe + front.rxe + model; no incomplete capsule is published.';
// The transport always uses code+state. A capsule fallback is explicitly disabled.
const roles={};for(const n of ['guard.xi','guard-x07.xi','text-finish.xi','dispatch.xi','review.xi','result.xi','qdu-plan.xi','qdu-dispatch.xi','learn.xi','learn-bank.xi'])if(fs.existsSync(path.join(out,n)))roles[n]=sha(fs.readFileSync(path.join(out,n)));
write('model.rvp.gz',zlib.gzipSync(fs.readFileSync(model),{level:9}));const m={version:'X08-Training-Language-1',runtime_sha256:sha(fs.readFileSync(rt)),parent:'X07-Knowledge-Android-1',parent_app_sha256:sha(read('BBY-Q.rxe')),front_sha256:sha(fs.readFileSync(path.join(out,'front.rxe'))),parent_source_sha256:sha(read('conversation.xi')),knowledge_schema:2,knowledge_bank_capacity:4096,knowledge_scratch:String(NEW_S7),concepts:catalog.concepts.length,relations:catalog.concepts.length*2,book_codec:'X08-LZ-page-v1',book_dictionary_bytes:bookDictionary.length,book_dictionary_sha256:sha(bookDictionary),book_compressed_bytes:compressedOffset,book_pages:122,book_bytes:offset,book_normalized_sha256:sha(Buffer.concat(pages.map(p=>Buffer.from(p.text)))),dictionary_entries:dict.length,index_entries:entries.length,model_bytes:fs.statSync(model).size,model_sha256:sha(fs.readFileSync(model)),code_sha256:sha(fs.readFileSync(path.join(out,'code.rxe'))),app_sha256:app?sha(fs.readFileSync(path.join(out,'BBY-Q.rxe'))):null,standalone_capsule:app,capsule_error:packError,roles_sha256:roles,migration:migration.map(file=>({file,sha256:sha(fs.readFileSync(path.join(out,file)))})),scope_excluded:['P13','P14'],intelligence:'XI/Ether; JS is offline assembly and transport only'};write('build.json',JSON.stringify(m,null,2)+'\n');write('native-training.json',JSON.stringify({records:learned,total:learned.length},null,2)+'\n');console.log(JSON.stringify(m));
