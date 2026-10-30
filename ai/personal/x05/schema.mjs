export const B=9090000000000000000n,S=B+100000n,C=S+512n,I=7400000000000000128n,P=S+110n,E=S+111n,TS=S+1024n,CODE=B+1024n,OLD=B+6144n,OUT=B+512n,DS=S+3000n;
export const Q=8460000000000000000n,M=8300000000000000000n,A=8200000000000000000n;
// B: magic85/schema1, +2 status, +3 kind, +4 op, +5 count, +6 repair,
// +8 source u16, +10 generation u32, +14 attempt u32, +20 receipt count.
// +32 full SHA256 (host byte transport), +64 16 signed32 parameters (5 bytes),
// +180 original-source u16; +256 receipt{gen,attempt,sha32,status,count}.
// +512 16 observed signed64 values (9 bytes); +1024 source4096; +6144 old512.
