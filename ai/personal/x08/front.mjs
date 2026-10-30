import {generate} from './generate.mjs';import {transport} from '../x06/transport.xi.mjs';import {assembler} from '../x06/asm.mjs';import {B,F} from './schema.mjs';
const strip=s=>s.split('\n').filter(l=>!l.startsWith('#!')).join('\n');
export function frontSource(parent,knowledgeGuard){
 const a=assembler();transport(a);const done=parent.slice(parent.indexOf('label x6_done\n'),parent.indexOf('label x6_corrupt\n')),cancel=parent.slice(parent.indexOf('label x6_routes\n')+'label x6_routes\n'.length,parent.indexOf('label x6_match_routes\n'));
 const guard=strip(knowledgeGuard).replace('halt\nlabel refuse','jmp x08_entry\nlabel refuse');
 return `#!reverse-pc-machine-v1\n${guard}\nlabel x08_entry\nload8 r0 ${B}\ncmp r0 88\njne x8_corrupt\nload8 r0 ${B+1n}\ncmp r0 1\njne x8_corrupt\nstore8 ${B+2n} 1\njmp x6_text_v2\nlabel x6_routes\n${cancel}\nlabel x6_match_routes\njmp x8_routes\n${strip(generate())}\nlabel x7_routes\nstore8 ${B+2n} 0\nstore8 ${F+2n} 1\nhalt\nlabel x6_parent\njmp x8_corrupt\nlabel x6_format\njmp x8_format\n${a.lines.join('\n')}\n${done}\n`;
}
