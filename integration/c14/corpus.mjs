// C14: reproducible human-authored templates + synthetic topic substitutions.
// These are NOT user conversations or externally collected language examples.
// Separation is by BOTH template family and topic identity.
import crypto from 'node:crypto';
const trainTopics=Object.freeze([
 'Aurora','Orion','Nebula','Faro','Cobalto','Jade','Bosque','Cascada','Prisma','Horizonte',
 'Oceano','Luna','Viento','Duna','Jardin','Marfil','Norte','Brisa','Cumbre','Rio',
 'Amapola','Trigo','Crisol','Lirio','Coral'
]);
const testTopics=Object.freeze([
 'Altair','Vega','Sirius','Atlas','Cedro','Arrecife','Valle','Amanecer','Volcan','Granito',
 'Lago','Nieve','Roble','Oasis','Pino','Sendero','Solsticio','Marea','Planeta','Granada',
 'Girasol','Laguna','Otono','Piedra','Estrella'
]);
const templates=Object.freeze({
  memory:[
   '¿Qué dije sobre {tema}?','¿Qué recuerdas que comenté sobre {tema}?',
   'Necesito recordar lo que dije sobre {tema}.','Consulta mi historial sobre {tema}.',
   'Recuérdame nuestra conversación de {tema}.','¿Qué mencioné antes acerca de {tema}?',
   'Recupera nuestra memoria de {tema}.','¿Qué dijimos cuando hablamos de {tema}?',
   'Quiero recordar qué hablamos de {tema}.',
   'Recupera del historial lo que dije sobre {tema}.'
  ],
  reasoning:[
   'Deduce si {tema} implica X.','Analiza las premisas sobre {tema}.',
   'Razona con lógica acerca de {tema}.','Demuestra una conclusión sobre {tema}.',
   'Justifica el argumento relativo a {tema}.','Resuelve un silogismo sobre {tema}.',
   'Explica la inferencia detrás de {tema}.','Evalúa la contradicción en {tema}.',
   'Obtén la conclusión lógica para {tema}.',
   'Justifica por deducción el caso {tema}.'
  ],
  creation:[
   'Escribe un cuento sobre {tema}.','Crea una historia de {tema}.',
   'Inventa un relato con {tema}.','Redacta un poema sobre {tema}.',
   'Escribe cinco versos sobre {tema}.','Imagina una narración de {tema}.',
   'Compone una fábula de {tema}.','Redacta ficción sobre {tema}.',
   'Inventa una historia breve con {tema}.',
   'Compón un poema para {tema}.'
  ],
  general:[
   'Hola, ¿cómo estás con {tema}?','¿Cuánto sabes de {tema}?',
   'Explica el concepto {tema}.','¿Qué significa {tema}?',
   'Quiero información de {tema}.','¿Cuál es el origen de {tema}?',
   'Muestra tres datos sobre {tema}.','Calcula 17 + 25 en el ejemplo {tema}.',
   '¿Cuándo apareció {tema}?',
   'Explícame las propiedades de {tema}.'
  ]
});
const routes=Object.freeze({general:0,memory:1,reasoning:2,creation:3});
export const sha=content=>crypto.createHash('sha256').update(content).digest('hex');
const construct=(topics,first,last,split)=>{
 const result=[];
 for(const [kind,list] of Object.entries(templates)){
  for(let template=first;template<last;template++){
   for(const topic of topics){
    result.push({id:split+'-'+kind+'-'+template+'-'+topic.toLowerCase(),text:list[template].replace('{tema}',topic),
     label:routes[kind],family:kind,template:template,topic:topic});
   }
  }
 }
 return result;
};
export function corpus(){
 const train=construct(trainTopics,0,8,'train'),holdout=construct(testTopics,8,10,'holdout');
 const seen=new Set(train.map(x=>x.text));
 for(const x of holdout)if(seen.has(x.text))throw Error('Holdout leaked into training');
 const uniqueTemplatesTrain=new Set(train.map(x=>x.family+':'+x.template));
 const uniqueTemplatesTest=new Set(holdout.map(x=>x.family+':'+x.template));
 for(const key of uniqueTemplatesTest)if(uniqueTemplatesTrain.has(key))throw Error('Overlapping template families');
 for(const x of holdout)if(trainTopics.includes(x.topic))throw Error('Overlapping holdout topic');
 if(train.length!==800||holdout.length!==200)throw Error('Unexpected sample sizes');
 if(new Set([...train,...holdout].map(x=>x.text)).size!==1000)throw Error('Duplicate messages');
 return {train,holdout,meta:{
  dataset:'C14 synthetic four-way route benchmark',language:'es',real_conversations:false,
  training:train.length,holdout:holdout.length,train_templates:32,holdout_templates:8,
  train_topics:trainTopics.length,holdout_topics:testTopics.length,
  split:'topic-and-template-disjoint',
  train_sha256:sha(JSON.stringify(train)),holdout_sha256:sha(JSON.stringify(holdout))
 }};
}
