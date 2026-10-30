// Owned X08 logical ranges. The low book addresses reduce textual RVPC2 overhead.
export const B=9120000000000000000n,S=B+100000n,P=S+16n,E=S+18n,RS=S+3900n;
export const OUT=S+12000n,INPUT_BYTES=16384,OUTPUT_BYTES=32768;
export const BOOK=600000000n,PAGES=BOOK+4096n,TEXT=BOOK+8192n;
export const DICT=601000000n,WORDS=DICT+4096n,ROW=256,CAPACITY=2048;
export const INDEX=602000000n,INDEX_ROWS=INDEX+4096n,INDEX_STRIDE=112;
export {C,I,F} from '../x06/schema.mjs';
