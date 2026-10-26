#!reverse-pc-machine-v1
# Route canonical bytes to the EXISTING E011 arithmetic learner, not a host
# classifier. No knowledge content or replacement arithmetic model here.
store8 7300000000000000016 1
load8 r0 7400000000000000003
store8 7300000000000000003 r0
load8 r15 7400000000000000032
set r0 0
set r1 0
label token
cmp r0 r15
jge complete
# Conversational aliases of a grounded numeral reuse its original E010 name.
load8 r4 7700000000000000016
cmp r4 1
jne raw_token
set r7 7400000000000001600
mov r2 r0
mul r2 2
add r7 r2
load8 r4 $r7
cmp r4 13
jlt raw_token
cmp r4 22
jgt raw_token
sub r4 1
mul r4 32
set r7 7200000000000001005
add r7 r4
jmp token_ready
label raw_token
set r7 7400000000000000512
mov r2 r0
mul r2 34
add r7 r2
label token_ready
load8 r3 $r7
set r2 0
label character
cmp r2 r3
jge separator
mov r8 r7
add r8 1
add r8 r2
load8 r9 $r8
set r8 7300000000000000128
add r8 r1
store8 $r8 r9
add r1 1
add r2 1
jmp character
label separator
add r0 1
cmp r0 r15
jge complete
set r8 7300000000000000128
add r8 r1
store8 $r8 32
add r1 1
jmp token
label complete
store8 7300000000000000017 r1
halt
