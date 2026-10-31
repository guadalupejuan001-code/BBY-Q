// P01: deterministic intent inference compiled to native XI, no JS text matching at runtime.
// The grammar is a small, auditable supervised curriculum; it is not an LLM or neural weights.
import {B,INPUT,LENGTH,TOTAL} from '../x10/schema.mjs';

export const INTENT_ADDRESS=B+128n;
export const INTENT_NAMES=Object.freeze([
  'unknown','greeting','question','explanation','creation',
  'teaching','correction','statement','instruction'
]);

// Precedence matters. "escribe y ejecuta" must not become a creative-writing request.
// A teach/correct cue is writable only at the beginning of the utterance, and only
// when the utterance is not interrogative. Everything else is read-only by default.
export const CURRICULUM=Object.freeze([
  [5,97,true,'recuerda que'],[5,97,true,'aprende'],[5,96,true,'ensena traduccion'],
  [5,95,true,'ensena que'],[5,95,true,'guarda que'],[5,95,true,'anota que'],
  [6,97,true,'corrige leccion'],[6,97,true,'corrige'],[6,95,true,'correccion'],
  [6,94,true,'quise decir'],[6,93,true,'me equivoque'],[6,90,true,'mejor dicho'],
  [8,99,true,'escribe y ejecuta'],[8,99,true,'genera y ejecuta'],
  [8,98,true,'escribe un programa'],
  [4,97,true,'escribe un poema'],[4,97,true,'escribe un cuento'],
  [4,97,true,'escribe una historia'],[4,96,true,'redacta un cuento'],
  [4,96,true,'crea una historia'],[4,96,true,'crea un cuento'],
  [4,95,true,'inventa un'],[4,95,true,'haz una historia'],[4,93,true,'escribe'],
  [3,97,true,'explicame'],[3,97,true,'explica'],
  [3,96,true,'por que'],[3,95,true,'como funciona'],
  [3,94,true,'cual es la razon'],[3,94,true,'quiero entender'],
  [3,93,true,'hablame de'],[3,93,true,'me explicas'],
  [3,93,true,'puedes explicar'],[3,92,true,'dime por que'],
  [3,96,true,'why'],
  [1,96,true,'que tal'],
  [8,96,true,'calcula'],[8,96,true,'traduce'],[8,95,true,'resume'],
  [8,95,true,'compara'],[8,95,true,'busca'],[8,93,true,'revisa'],
  [8,93,true,'ejecuta'],[8,92,true,'abre'],[8,92,true,'instala'],
  [8,92,true,'analiza'],[8,90,true,'consulta'],[8,90,true,'configura'],
  [8,90,true,'quiero que'],[8,90,true,'dame'],[8,89,true,'muestra'],
  [2,90,true,'que'],[2,90,true,'quien'],[2,90,true,'cuando'],
  [2,90,true,'donde'],[2,90,true,'cuanto'],[2,90,true,'cual'],
  [2,89,true,'como'],[2,89,true,'sabes'],[2,88,true,'es cierto'],
  [2,88,true,'puedes decirme'],[2,88,true,'tiene'],
  [2,89,true,'what'],[2,89,true,'where'],[2,89,true,'when'],
  [2,89,true,'who'],[2,89,true,'how'],
  [1,96,true,'hola'],[1,95,true,'buenas'],[1,94,true,'hello'],
  [1,94,true,'hey'],[1,93,true,'saludos'],
  [7,70,false,'es'],[7,70,false,'tiene'],[7,70,false,'soy'],
  [7,68,false,'estoy'],[7,68,false,'tengo'],[7,65,false,'mi'],
  [7,65,false,'ayer'],[7,65,false,'hoy']
]);

export function intentSource(){
  const P=INTENT_ADDRESS,N=B+1024n,D=B+32768n,lines=['#!reverse-pc-machine-v1'];
  const w=(...xs)=>lines.push(...xs),L=name=>w('label '+name);
  const st=(a,v)=>w('store8 '+a+' '+v);
  // P+0=kind; P+1=confidence; P+2=read-only; P+3=question punctuation;
  // P+4=matched cue (1-based); P+8=normalized length.
  st(P,0);st(P+1n,0);st(P+2n,1);st(P+3n,0);st(P+4n,0);st(P+8n,0);
  w('load8 r9 '+LENGTH,'load8 r4 '+(LENGTH+1n),'mul r4 256','add r9 r4',
    'cmp r9 0','jle p01_unknown',
    'cmp r9 190','jle p01_setup','set r9 190');
  L('p01_setup');st(N,32);w('set r0 0','set r1 1');
  L('p01_norm');
  w('cmp r0 r9','jge p01_finish','set r7 '+INPUT,'add r7 r0',
    'load8 r3 $r7','add r0 1',
    'cmp r3 63','je p01_question',
    'cmp r3 194','je p01_c2','cmp r3 195','je p01_c3',
    'cmp r3 65','jlt p01_ascii','cmp r3 90','jgt p01_ascii','add r3 32');
  L('p01_ascii');
  w('cmp r3 97','jlt p01_digit','cmp r3 122','jle p01_put');
  L('p01_digit');
  w('cmp r3 48','jlt p01_space','cmp r3 57','jle p01_put');
  L('p01_space');w('set r3 32','jmp p01_put');
  L('p01_question');st(P+3n,1);w('set r3 32','jmp p01_put');
  L('p01_c2');
  w('cmp r0 r9','jge p01_space','set r7 '+INPUT,'add r7 r0','load8 r6 $r7',
    'cmp r6 191','jne p01_c2_end');st(P+3n,1);
  L('p01_c2_end');w('add r0 1','set r3 32','jmp p01_put');
  L('p01_c3');
  w('cmp r0 r9','jge p01_space','set r7 '+INPUT,'add r7 r0','load8 r6 $r7');
  const accents=[
    [97,[161,129]],[101,[169,137]],[105,[173,141]],
    [111,[179,147]],[117,[186,154,188,156]],[110,[177,145]]
  ];
  for(const [letter,bytes] of accents)for(const byte of bytes)w('cmp r6 '+byte,'je p01_accent_'+letter);
  w('add r0 1','jmp p01_space');
  for(const [letter] of accents){L('p01_accent_'+letter);w('add r0 1','set r3 '+letter,'jmp p01_put');}
  L('p01_put');
  w('cmp r3 32','jne p01_write','set r7 '+N,'add r7 r1','sub r7 1',
    'load8 r6 $r7','cmp r6 32','je p01_norm');
  L('p01_write');
  w('cmp r1 190','jge p01_finish','set r7 '+N,'add r7 r1',
    'store8 $r7 r3','add r1 1','jmp p01_norm');
  L('p01_finish');
  w('cmp r1 1','jle p01_unknown','set r7 '+N,'add r7 r1',
    'store8 $r7 32','add r1 1');st(P+8n,'r1');
  const entries=[];let offset=0;
  for(const [kind,confidence,anchored,cue] of CURRICULUM){
    const bytes=Buffer.from(' '+cue+' ','utf8');
    if(bytes.length>80)throw Error('Invalid P01 cue length');
    const addr=D+BigInt(offset);
    entries.push({kind,confidence,anchored,bytes,addr});
    offset+=bytes.length;
  }
  if(offset>3072||entries.length>255)throw Error('P01 curriculum is outside its bounded layout');
  for(const entry of entries)for(const[i,byte]of entry.bytes.entries())st(entry.addr+BigInt(i),byte);
  for(const [i,entry] of entries.entries()){
    const tag='p01_rule_'+i, n=entry.bytes.length;
    L(tag);w('load8 r8 '+(P+8n),'sub r8 '+n,'set r0 0');
    L(tag+'_seek');
    w('cmp r0 r8','jgt '+tag+'_done');
    if(entry.anchored)w('cmp r0 20','jgt '+tag+'_done');
    w('set r5 0');
    L(tag+'_compare');
    w('cmp r5 '+n,'jge '+tag+'_found',
      'set r7 '+N,'add r7 r0','add r7 r5','load8 r2 $r7',
      'set r7 '+entry.addr,'add r7 r5','load8 r3 $r7',
      'cmp r2 r3','jne '+tag+'_next','add r5 1','jmp '+tag+'_compare');
    L(tag+'_next');w('add r0 1','jmp '+tag+'_seek');
    L(tag+'_found');
    if(entry.kind===5||entry.kind===6){
      // Explicit teaching/correction cannot be inferred from an interrogative.
      w('load8 r6 '+(P+3n),'cmp r6 0','jne '+tag+'_next');
    }
    st(P,entry.kind);st(P+1n,entry.confidence);
    st(P+2n,(entry.kind===5||entry.kind===6)?0:1);
    st(P+4n,i+1);w('halt');
    L(tag+'_done');
  }
  // No keyword match: a question mark is sufficient for a question, but never
  // for permission to write memory. Otherwise abstain instead of hallucinating.
  w('load8 r6 '+(P+3n),'cmp r6 1','jne p01_unknown');
  st(P,2);st(P+1n,62);w('halt');
  L('p01_unknown');w('halt');
  return lines.join('\n')+'\n';
}
