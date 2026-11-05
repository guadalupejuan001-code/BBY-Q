import fs from 'node:fs';
import {expand,ID,ADDR,LIMITS} from './schema.mjs';
export function zeroSource(){
 let text=fs.readFileSync(new URL('./core.xi.in',import.meta.url),'utf8');
 text=text.replaceAll('%LP%',String(ID['('])).replaceAll('%RP%',String(ID[')'])).replaceAll('%PLUS%',String(ID['+'])).replaceAll('%MINUS%',String(ID['-'])).replaceAll('%MUL%',String(ID['*'])).replaceAll('%DIV%',String(ID['/'])).replaceAll('%QUESTION%',String(ID['?'])).replaceAll('%BANG%',String(ID['!'])).replaceAll('%DOT%',String(ID['.'])).replaceAll('%COLON%',String(ID[':']));
 return expand(text);
}
export const schema={version:'BBY-Q-0-1',base:String(ADDR.Z),words:ID,limits:LIMITS};
