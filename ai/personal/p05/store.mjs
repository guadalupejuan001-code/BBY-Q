// P05 durable short-term conversation index. SQLite provides storage only;
// native XI decides whether a user request is history recall and which turn.
import crypto from 'node:crypto';
import {CONTEXT_MAX_ENTRY_BYTES,CONTEXT_MAX_CANDIDATES,CONTEXT_MODES} from './context.mjs';
const MAX_INDEXED_TURNS=32,MAX_REPLY_BYTES=512;
const sha=b=>crypto.createHash('sha256').update(b).digest('hex');
export function ensureContext(db){
 db.exec('CREATE TABLE IF NOT EXISTS conversation_turns ('+
 'generation INTEGER PRIMARY KEY CHECK(generation>=1),'+
 'request_id TEXT NOT NULL UNIQUE,'+
 'utterance TEXT NOT NULL,reply TEXT NOT NULL,'+
 'digest TEXT NOT NULL CHECK(length(digest)=64)) STRICT;');
}
export function history(db){
 ensureContext(db);
 const rows=db.prepare('SELECT generation,request_id,utterance,reply,digest FROM conversation_turns ORDER BY generation DESC LIMIT ?').all(CONTEXT_MAX_CANDIDATES);
 for(const row of rows)
  if(sha(Buffer.from(row.utterance))!==row.digest)throw Object.assign(new Error('Índice conversacional alterado.'),{code:'E_CONTEXT_INTEGRITY'});
 return rows;
}
export function contextCount(db){
 ensureContext(db);
 return db.prepare('SELECT COUNT(*) AS n FROM conversation_turns').get().n;
}
export function saveConversation(db,raw,result,requestId,generation){
 if(result?.context_skip_record===true)return;
 ensureContext(db);
 // Oversize messages become an empty barrier: a pronoun cannot silently
 // resolve to an older topic after a new topic was not indexed.
 const user=raw.length<=CONTEXT_MAX_ENTRY_BYTES?raw.toString('utf8'):'';
 const reply=typeof result.response==='string'&&Buffer.byteLength(result.response)<=MAX_REPLY_BYTES?result.response:'';
 db.prepare('INSERT INTO conversation_turns VALUES(?,?,?,?,?)').run(generation,requestId,user,reply,sha(Buffer.from(user)));
 db.prepare('DELETE FROM conversation_turns WHERE generation NOT IN '+
  '(SELECT generation FROM conversation_turns ORDER BY generation DESC LIMIT ?)').run(MAX_INDEXED_TURNS);
}
function evidence(row){
 if(!row||!row.utterance)return 'No tengo un mensaje anterior verificable dentro de la ventana conversacional disponible.';
 return 'En el turno '+row.generation+' escribiste: «'+row.utterance+'».';
}
function replyEvidence(row){
 if(!row||!row.reply)return 'No tengo una respuesta anterior completa dentro de la ventana conversacional disponible.';
 return 'En el turno '+row.generation+' respondí: «'+row.reply+'».';
}
export function contextTurn(db,decision,rows,{explicit=false}={}){
 const mode=decision.mode;
 if(mode===CONTEXT_MODES.unsupported){
  if(!explicit)return null;
  return {ok:true,response:'Mensaje incorporado al historial breve de esta sesión, no al banco de entrenamiento.',
   extension:'P05-context-XI',context_skip_record:false,knowledge_read_only:true,context_mode:mode};
 }
 if(mode===CONTEXT_MODES.clear){
  ensureContext(db);
  const previous=contextCount(db);db.exec('DELETE FROM conversation_turns');
  return {ok:true,response:'Vacié '+previous+' entradas del índice conversacional breve. Los comprobantes históricos de la sesión y las lecciones aprendidas siguen conservados.',
   extension:'P05-context-XI',context_skip_record:true,knowledge_read_only:true,context_mode:mode,context_cleared:previous};
 }
 if(mode===CONTEXT_MODES.status){
  return {ok:true,response:'El índice conversacional breve conserva '+contextCount(db)+' turnos (máximo '+MAX_INDEXED_TURNS+'). Las búsquedas nativas examinan hasta '+CONTEXT_MAX_CANDIDATES+' turnos recientes. No son lecciones aprendidas.',
   extension:'P05-context-XI',context_skip_record:true,knowledge_read_only:true,context_mode:mode};
 }
 if(mode===CONTEXT_MODES.recent){
  const entries=rows.slice(0,5).filter(r=>r.utterance);
  return {ok:true,response:entries.length?'Últimos mensajes que registré:\n'+entries.map(r=>'Turno '+r.generation+': «'+r.utterance+'»').join('\n'):'No tengo mensajes anteriores verificables en el índice conversacional.',
   extension:'P05-context-XI',context_skip_record:true,knowledge_read_only:true,context_mode:mode};
 }
 if(mode===CONTEXT_MODES.not_found)
  return {ok:true,response:'No encontré una mención verificable de ese tema en los turnos recientes. No voy a inventar un recuerdo.',
   extension:'P05-context-XI',context_skip_record:true,knowledge_read_only:true,context_mode:mode,context_resolved:false};
 if(mode===CONTEXT_MODES.ambiguous)
  return {ok:true,response:'No puedo identificar un antecedente único y reciente para esa referencia. Menciona el tema por su nombre.',
   extension:'P05-context-XI',context_skip_record:true,knowledge_read_only:true,context_mode:mode,context_resolved:false};
 if(mode===CONTEXT_MODES.named||mode===CONTEXT_MODES.pronoun||mode===CONTEXT_MODES.last||mode===CONTEXT_MODES.answer){
  const row=rows[decision.slot-1],found=!!row;
  return {ok:true,response:mode===CONTEXT_MODES.answer?replyEvidence(row):evidence(row),
   extension:'P05-context-XI',context_skip_record:true,knowledge_read_only:true,
   context_mode:mode,context_resolved:found&&!!(mode===CONTEXT_MODES.answer?row.reply:row.utterance),
   context_source_generation:found?row.generation:null};
 }
 throw Object.assign(new Error('Modo de memoria XI desconocido.'),{code:'E_CONTEXT_MODE'});
}
