// One combined XI agent; the new knowledge bank never occupies personal context.
export const B=9110000000000000000n,K=B+4096n,S=B+500000n,STAGE=S+256n;
export const CAPACITY=512,STRIDE=640,REGION_BYTES=331776;
export const P=S+16n,E=S+18n,RS=S+7936n;
export {C,I,F} from '../x06/schema.mjs';
// B: magic87/schema1; concept count u16+2; revision u32+8; installed+16.
// +32 command/result counters, +512 percent rule, +544 three-way allocation.
// K: 512 records *640. Active+0, key/definition/requirement/source/pages lengths
// +1..5, origin+6, revision u32+8; key64+16, def224+80, requirement224+304,
// source32+528, pages32+560. Stage has the same record layout.
