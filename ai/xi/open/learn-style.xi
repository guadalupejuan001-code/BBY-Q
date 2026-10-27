#!reverse-pc-machine-v1
# Explicit user preference; not a learned language capability or inference rule.
# +316 request: 0 historical evidence display, 1 concise with proof on request.
load8 r0 7800000000000000002
cmp r0 1
jne invalid
load8 r0 7800000000000000316
cmp r0 1
jgt invalid
cmp r0 0
je commit
load8 r1 7800000000000507168
cmp r1 0
je invalid
load8 r1 7800000000000507424
cmp r1 0
je invalid
label commit
store8 7800000000000000003 r0
halt
label invalid
div r0 0
