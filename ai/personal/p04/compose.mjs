// P04 - bounded composition of original verse, fictional stories and grounded
// explanations. JavaScript generates XI bytecode at BUILD time only.
// All request parsing, phrase selection, word insertion and output run in XI.
import {B,INPUT,LENGTH} from '../x10/schema.mjs';
export const COMPOSE_BASE=B+98304n;
export const COMPOSE_LIMIT=768;
export const COMPOSE_MODES=Object.freeze({unsupported:0,poem:1,story:2,grounded_explanation:3});
const P=COMPOSE_BASE,N=P+1024n,MAX_TOPIC=80,VARIANTS=4;

const poem=[
 [
  ['Al borde del silencio, ',' aprende a cantar.'],
  ['Bajo un cielo sin relojes, ',' vuelve a brillar.'],
  ['En la respiración del viento, ',' se deja escuchar.'],
  ['Donde comienza la noche, ',' se atreve a soñar.']
 ],
 [
  ['Sobre la lluvia tranquila, ',' inventa otro lugar.'],
  ['Entre las luces dormidas, ',' elige despertar.'],
  ['En un jardín de preguntas, ',' se dispone a volar.'],
  ['Más allá de las montañas, ',' no deja de buscar.']
 ],
 [
  ['A la orilla del recuerdo, ',' conserva una señal.'],
  ['Cuando el ruido se retira, ',' encuentra algo especial.'],
  ['Sin conocer el destino, ',' sigue un pulso natural.'],
  ['En las manos de la tarde, ',' guarda un sueño mineral.']
 ],
 [
  ['De repente, entre las sombras, ',' dibuja claridad.'],
  ['Sin pedirle nada al tiempo, ',' sostiene su verdad.'],
  ['Cuando el miedo se hace pequeño, ',' recupera libertad.'],
  ['Con la calma de los astros, ',' celebra la realidad.']
 ],
 [
  ['Y en el centro de la bruma, ',' aprende a resistir.'],
  ['Bajo el último lucero, ',' no se cansa de existir.'],
  ['Junto al río de los nombres, ',' descubre cómo seguir.'],
  ['Al escuchar el horizonte, ',' encuentra qué decir.']
 ],
 [
  ['Hasta que llega la aurora, ',' vuelve a comenzar.'],
  ['Y al abrirse las ventanas, ',' tiene algo que contar.'],
  ['Cuando termina el camino, ',' se transforma en mar.'],
  ['Y después del largo invierno, ',' decide florecer y cantar.']
 ]
];
const story=[
 [
  ['En una ciudad sin mapas, ',' encontró una puerta cerrada.'],
  ['Una mañana inesperada, ',' recibió una carta sin remitente.'],
  ['En el borde del bosque, ',' descubrió un sendero nuevo.'],
  ['Al caer la primera lluvia, ',' escuchó un mensaje lejano.']
 ],
 [
  ['Al principio, ',' no supo por dónde empezar.'],
  ['Antes de decidir, ',' examinó cada pista.'],
  ['Durante el viaje, ',' tuvo que elegir entre dos caminos.'],
  ['Con muchas preguntas, ',' buscó a alguien que pudiera ayudar.']
 ],
 [
  ['A mitad del camino, ',' encontró una señal olvidada.'],
  ['Cuando todo parecía perdido, ',' reconoció una ruta distinta.'],
  ['Tras un silencio largo, ',' consiguió unir las pistas.'],
  ['Entre los árboles, ',' halló una respuesta inesperada.']
 ],
 [
  ['Con paciencia, ',' convirtió el miedo en curiosidad.'],
  ['Sin rendirse, ',' decidió seguir una nueva dirección.'],
  ['Después de pensarlo, ',' compartió su descubrimiento.'],
  ['Al escuchar al viento, ',' cambió su manera de mirar.']
 ],
 [
  ['Al amanecer, ',' comprendió por qué había empezado el viaje.'],
  ['Antes de regresar, ',' dejó una señal para otros viajeros.'],
  ['Cuando salió el sol, ',' pudo ver el paisaje completo.'],
  ['Al final de la tarde, ',' recuperó la calma.']
 ],
 [
  ['Desde aquel día, ',' contó la aventura a quien quiso escuchar.'],
  ['Y así, ',' transformó aquella duda en una historia.'],
  ['A partir de entonces, ',' supo que siempre podía explorar otra ruta.'],
  ['Finalmente, ',' regresó con una pregunta todavía más grande.']
 ]
];
const numberNames=[['dos',2],['tres',3],['cuatro',4],['cinco',5],['seis',6]];
const options=[];
for(const [type,middle,number] of [[1,'poema','versos'],[2,'cuento','frases'],[2,'historia','frases']]){
 for(const name of ['escribe un','crea un','haz un']){
  // "una historia" rather than "un historia"; remove un for this pattern.
  const verb=type===2&&middle==='historia'?name.replace(/ un$/,' una'):name;
  for(const [label,n] of numberNames)options.push([verb+' '+middle+' de '+label+' '+number+' sobre ',type,n]);
  for(let n=2;n<=6;n++)options.push([verb+' '+middle+' de '+n+' '+number+' sobre ',type,n]);
  options.push([verb+' '+middle+' sobre ',type,type===1?4:3]);
 }
}
options.push(['inventa una historia sobre ',2,3],['inventa un cuento sobre ',2,3]);
options.push(['poema sobre ',1,4],['cuento sobre ',2,3]);
const explanationHeaders=['explica con datos:\nhecho: ','explica con estos datos:\nhecho: ','explica:\nhecho: '];

export function composeSource(){
 const code=['#!reverse-pc-machine-v1'];let sequence=0;
 const w=(...v)=>code.push(...v),L=x=>w('label '+x),u=x=>x+'_'+sequence++;
 const st=(a,v)=>w('store8 '+a+' '+v),ld=(r,a)=>w('load8 r'+r+' '+a);
 function say(s){for(const b of Buffer.from(s,'utf8'))w('set r14 '+b,'print r14');}
 function save16(a,r){
  w('mov r12 r'+r,'mod r12 256');st(a,'r12');
  w('mov r12 r'+r,'div r12 256');st(a+1n,'r12');
 }
 function read16(r,a){ld(r,a);ld(12,a+1n);w('mul r12 256','add r'+r+' r12');}
 function emitSpan(a){
  read16(10,a);read16(11,a+2n);
  const loop=u('p04_span'),end=u('p04_span_done');
  L(loop);w('cmp r11 0','jle '+end,'set r7 '+INPUT,'add r7 r10','load8 r14 $r7','print r14','add r10 1','sub r11 1','jmp '+loop);L(end);
 }
 // Result P+0 handled, +1 mode, +2 count, +3 rejection reason,
 // +4 topic hash, +8..11 topic span, +100..111 grounded field spans.
 for(let i=0;i<=12;i++)st(P+BigInt(i),0);
 w('load8 r9 '+LENGTH,'load8 r8 '+(LENGTH+1n),'mul r8 256','add r9 r8',
   'cmp r9 1','jlt p04_unhandled','cmp r9 '+COMPOSE_LIMIT,'jgt p04_unhandled');
 // Keep a byte-for-byte normalized shadow. No semantic work is done on host.
 w('set r0 0');L('p04_norm');
 w('cmp r0 r9','jge p04_dispatch','set r7 '+INPUT,'add r7 r0','load8 r3 $r7',
   'cmp r3 65','jlt p04_store','cmp r3 90','jgt p04_store','add r3 32');
 L('p04_store');w('set r7 '+N,'add r7 r0','store8 $r7 r3','add r0 1','jmp p04_norm');
 L('p04_dispatch');
 function prefix(text,to,type,count){
  const miss=u('p04_miss'),found=u('p04_match');
  const bytes=Buffer.from(text,'utf8');
  w('cmp r9 '+bytes.length,'jle '+miss);
  for(const [i,b]of bytes.entries()){ld(3,N+BigInt(i));w('cmp r3 '+b,'jne '+miss);}
  w('set r4 '+bytes.length,'set r6 '+count,'set r8 '+type,'jmp '+to);
  L(miss);
 }
 for(const [head,mode,n]of options)prefix(head,'p04_creative',mode,n);
 for(const head of explanationHeaders)prefix(head,'p04_explain_parse',3,3);
 w('jmp p04_unhandled');

 L('p04_creative');st(P+1n,'r8');st(P+2n,'r6');
 w('mov r5 r9');
 L('p04_trim_right');
 w('cmp r5 r4','jle p04_unhandled','mov r7 r5','sub r7 1','add r7 '+N,'load8 r3 $r7',
  'cmp r3 32','je p04_dec_end','cmp r3 46','je p04_dec_end','cmp r3 63','je p04_dec_end','cmp r3 33','je p04_dec_end','jmp p04_trim_left');
 L('p04_dec_end');w('sub r5 1','jmp p04_trim_right');
 L('p04_trim_left');w('cmp r4 r5','jge p04_unhandled','set r7 '+N,'add r7 r4','load8 r3 $r7','cmp r3 32','jne p04_topic_size','add r4 1','jmp p04_trim_left');
 L('p04_topic_size');
 w('mov r3 r5','sub r3 r4','cmp r3 2','jlt p04_unhandled','cmp r3 '+MAX_TOPIC,'jgt p04_unhandled');
 save16(P+8n,4);save16(P+10n,3);
 w('set r0 r4','set r8 0');
 L('p04_topic_validate');
 w('cmp r0 r5','jge p04_topic_ready','set r7 '+INPUT,'add r7 r0','load8 r3 $r7',
 'cmp r3 32','jlt p04_unhandled','cmp r3 127','je p04_unhandled','cmp r3 59','je p04_unhandled',
 'add r8 r3','add r0 1','jmp p04_topic_validate');
 L('p04_topic_ready');w('mod r8 '+VARIANTS);st(P+4n,'r8');st(P,1);
 // Stanza / fiction steps. The index is kept in r0, choice in r1.
 w('set r0 0');L('p04_creative_loop');ld(7,P+2n);w('cmp r0 r7','jge p04_done');
 ld(1,P+4n);w('mov r2 r0','mul r2 5','add r1 r2','mod r1 '+VARIANTS);
 ld(3,P+1n);w('cmp r3 1','je p04_poem_route','jmp p04_story_route');
 const after='p04_after_creative_line';
 function banks(prefix,items){
  for(let index=0;index<items.length;index++){
   const tag=prefix+'_'+index,openDone=tag+'_open_done';
   L(tag);
   // Two independent native selections permit 4x4 combinations per line:
   // one choice selects the syntactic opening, another the ending.
   for(let n=0;n<VARIANTS;n++){
    const miss=u('p04_open_next');
    w('cmp r1 '+n,'jne '+miss);
    say(items[index][n][0]);w('jmp '+openDone);L(miss);
   }
   w('jmp p04_unhandled');
   L(openDone);
   // Spanish subject ellipsis: fiction can keep the protagonist from the
   // opening sentence without needlessly repeating the noun in every line.
   if(prefix!=='p04_story'||index===0)emitSpan(P+8n);
   ld(1,P+4n);
   w('mul r1 3','mov r2 r0','mul r2 7','add r1 r2','mod r1 '+VARIANTS);
   for(let n=0;n<VARIANTS;n++){
    const miss=u('p04_end_next');
    w('cmp r1 '+n,'jne '+miss);
    say(prefix==='p04_story'&&index>0?items[index][n][1].trimStart():items[index][n][1]);
    w('jmp '+after);L(miss);
   }
   w('jmp p04_unhandled');
  }
 }
 L('p04_poem_route');
 ld(7,P+2n);w('mov r3 r7','sub r3 1','cmp r0 r3','je p04_poem_5');
 for(let i=0;i<5;i++)w('cmp r0 '+i,'je p04_poem_'+i);
 w('jmp p04_unhandled');
 L('p04_story_route');
 ld(7,P+2n);w('mov r3 r7','sub r3 1','cmp r0 r3','je p04_story_5');
 for(let i=0;i<5;i++)w('cmp r0 '+i,'je p04_story_'+i);
 w('jmp p04_unhandled');
 banks('p04_poem',poem);banks('p04_story',story);
 L(after);w('add r0 1');ld(7,P+2n);w('cmp r0 r7','jge p04_done');
 ld(3,P+1n);w('cmp r3 1','jne p04_story_separator');say('\n');w('jmp p04_creative_loop');
 L('p04_story_separator');say(' ');w('jmp p04_creative_loop');

 // Explanations are derived only from explicit user supplied fields, never
 // from unsupported general-domain premises.
 L('p04_explain_parse');st(P+1n,3);st(P+2n,3);
 // Each field is one line. Parse original spans; compare cue bytes in shadow.
 function parseField(addr,terminating){
  save16(addr,4);
  w('mov r5 r4');
  const scan=u('p04_field_scan'),ready=u('p04_field_ready');
  L(scan);w('cmp r4 r9','jge '+ready,'set r7 '+N,'add r7 r4','load8 r3 $r7',
     'cmp r3 10','je '+ready,'cmp r3 13','je '+ready,
     'cmp r3 32','jlt p04_unhandled','add r4 1','jmp '+scan);
  L(ready);
  w('mov r3 r4','sub r3 r5','cmp r3 1','jlt p04_unhandled','cmp r3 180','jgt p04_unhandled');
  save16(addr+2n,3);
  if(!terminating){
   w('cmp r4 r9','jge p04_unhandled','set r7 '+N,'add r7 r4','load8 r3 $r7',
     'cmp r3 13','jne p04_field_lf_'+sequence,'add r4 1');
   const lf='p04_field_lf_'+sequence++;
   L(lf);w('cmp r4 r9','jge p04_unhandled','set r7 '+N,'add r7 r4','load8 r3 $r7',
      'cmp r3 10','jne p04_unhandled','add r4 1');
  }else{
   w('cmp r4 r9','je p04_fields_done','set r7 '+N,'add r7 r4','load8 r3 $r7',
    'cmp r3 13','je p04_last_cr','cmp r3 10','je p04_last_lf','jmp p04_unhandled');
   L('p04_last_cr');w('add r4 1','cmp r4 r9','jge p04_fields_done','set r7 '+N,'add r7 r4','load8 r3 $r7','cmp r3 10','jne p04_unhandled');
   L('p04_last_lf');w('add r4 1','cmp r4 r9','jne p04_unhandled','jmp p04_fields_done');
  }
 }
 function matchCue(cue){
  const b=Buffer.from(cue),miss=u('p04_cue_invalid'),end=u('p04_cue_ok');
  w('mov r3 r4','add r3 '+b.length,'cmp r3 r9','jgt p04_unhandled');
  for(const [i,c]of b.entries()){
   w('set r7 '+(N+BigInt(i)),'add r7 r4','load8 r3 $r7','cmp r3 '+c,'jne p04_unhandled');
  }
  w('add r4 '+b.length);
 }
 parseField(P+100n,false);
 matchCue('causa: ');
 parseField(P+104n,false);
 matchCue('efecto: ');
 parseField(P+108n,true);
 L('p04_fields_done');st(P,1);say('Según los datos aportados, ');
 emitSpan(P+100n);say('. Esto se atribuye a que ');emitSpan(P+104n);
 say('. En consecuencia, ');emitSpan(P+108n);
 say('. No he verificado estas premisas fuera del texto recibido.');
 w('jmp p04_done');
 L('p04_done');w('halt');
 L('p04_unhandled');st(P,0);st(P+1n,0);st(P+2n,0);w('halt');
 return code.join('\n')+'\n';
}
