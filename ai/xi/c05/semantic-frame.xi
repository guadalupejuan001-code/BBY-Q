# C05 semantic sidecar boundary verifier, executed by original XI interpreter.
# Only on a disposable native C1 checkpoint; no trained model bank is modified.
# Host transports exact source token byte starts/lengths and scoped negations.
# C05 is a typed representation, NOT a learned semantic inference engine.
# Base: 8150000000000900000
label c05_validate_frame
store64 8150000000000900056 4
load64 r0 8150000000000900000
cmp r0 0
jlt c05_invalid
cmp r0 16384
jgt c05_invalid
load64 r3 8150000000000900008
cmp r3 0
jlt c05_invalid
cmp r3 256
jgt c05_invalid
load64 r8 8150000000000900016
cmp r8 0
jlt c05_invalid
cmp r8 16384
jgt c05_invalid
load64 r9 8150000000000900024
cmp r9 0
jlt c05_invalid
cmp r9 64
jgt c05_invalid
load64 r10 8150000000000900032
cmp r10 0
jlt c05_invalid
cmp r10 256
jgt c05_invalid
set r1 0
set r2 0
label c05_tokens_loop
cmp r1 r3
jge c05_negations
mov r4 r1
mul r4 24
add r4 8150000000000900064
load64 r5 $r4
add r4 8
load64 r6 $r4
add r4 8
load64 r7 $r4
cmp r5 0
jlt c05_invalid
cmp r6 1
jlt c05_invalid
cmp r7 0
jlt c05_invalid
cmp r5 r2
jlt c05_invalid
mov r2 r5
add r2 r6
cmp r2 r0
jgt c05_invalid
add r1 1
jmp c05_tokens_loop
label c05_negations
set r1 0
label c05_negation_loop
cmp r1 r10
jge c05_success
mov r4 r1
mul r4 24
add r4 8150000000000910000
load64 r5 $r4
add r4 8
load64 r6 $r4
add r4 8
load64 r7 $r4
cmp r5 0
jlt c05_invalid
cmp r5 r3
jge c05_invalid
cmp r6 -1
je c05_check_empty_scope
cmp r6 0
jlt c05_invalid
cmp r6 r3
jge c05_invalid
cmp r7 r6
jle c05_invalid
cmp r7 r3
jgt c05_invalid
jmp c05_next_negation
label c05_check_empty_scope
cmp r7 -1
jne c05_invalid
label c05_next_negation
add r1 1
jmp c05_negation_loop
label c05_success
store64 8150000000000900056 1
ret
label c05_invalid
store64 8150000000000900056 4
ret
