export const Z=9185000000000000000n;
export const ADDR=Object.freeze({Z,T:Z+4096n,NF:Z+8192n,NV:Z+12288n,ARG:Z+16384n,RT:Z+16448n,F:Z+100000n,R:Z+200000n,OUT:Z+300000n,PROOF:Z+304096n,QUEUE:Z+400000n,VS:Z+500000n,OS:Z+501024n,B1:Z+600000n,B2:Z+600032n,C:Z+600064n});
export const WORDS=['$x','$y','$z','<number>','<reserved5>','<reserved6>','<reserved7>','<reserved8>','<reserved9>',
 'recuerda','que','aprende','hecho',':','no','si','entonces','y','regla','corrige','olvida','pregunta','por','quien','es','ruta','plan','planea','desde','hasta','calcula','(',')','+','-','*','/','?','!',';','.',',','ella','el','eso','correcto','incorrecto','conecta','sabes','de','resuelve','supone','recupera','observa','muestra','clase0','clase1','cero','uno','consulta'];
export const ID=Object.freeze(Object.fromEntries(WORDS.map((w,i)=>[w,i+1])));
export const LIMITS=Object.freeze({tokens:128,facts:1024,rules:256,steps:30000,results:64});
export function expand(source){
 return source.replace(/@([A-Z0-9]+)(?:\+(\d+))?/g,(_,name,offset)=>{
  if(!(name in ADDR))throw Error('Unknown XI address '+name);return String(ADDR[name]+BigInt(offset||0));
 }).replace(/%([A-Z0-9_]+)%/g,(_,name)=>{const key=name.toLowerCase();if(!(key in ID))throw Error('Unknown XI word '+key);return String(ID[key]);});
}
