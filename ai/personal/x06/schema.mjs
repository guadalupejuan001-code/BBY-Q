export const B=9100000000000000000n,S=B+100000n,T=B+120000n,F=B+200000n,C=F+256n,I=7400000000000000128n;
export const TASKS=16,STRIDE=320,PLAN_BYTES=8192,SCRATCH_BYTES=4096,INPUT_BYTES=16384,OUTPUT_BYTES=65536;
export const P=S+16n,E=S+18n,LINE=S+20n,RS=S+3900n;
// Plan: magic86/schema1, has-plan+2, count+3, goal length+4, status+5,
// generation u32+8, budget u24+12, remaining u24+16, completed+20,
// scheduled+21, unplaced+22; goal160+64; records16*320+256.
// Record: active+0, done+1, blocked+2, priority+3, minutes u16+4,
// label length+6, criterion length+7, dependency flags16+8,
// label96+24, criterion160+120, rank+280, start u24+281, end u24+284.
// Text v2: F{magic86,version2,pending,result,language}, input u16+8,
// error+10; raw bytes16384 at F+256. Native validation precedes dispatch.
