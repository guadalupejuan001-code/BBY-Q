#!reverse-pc-machine-v1
# Reuse E011's number resolver. A shared E010 number alias is canonicalized
# to its original taught Spanish name, then resolved by the original code.
# Other text (including decimals) is copied unchanged, never host-parsed.
store8 7300000000000000016 1
store8 7300000000000000024 0
store8 7300000000000000032 1
store8 7300000000000000040 0
load8 r0 7500000000000000037
set r7 7400000000000001600
mov r1 r0
mul r1 2
add r7 r1
load8 r2 $r7
cmp r2 1
jlt raw
cmp r2 22
jgt raw
sub r2 1
mul r2 32
set r7 7200000000000001000
add r7 r2
load8 r1 $r7
cmp r1 4
jne raw
add r7 4
load8 r1 $r7
cmp r1 2
jlt raw
add r7 1
jmp copy_start
label raw
set r7 7400000000000000512
mul r0 34
add r7 r0
label copy_start
load8 r2 $r7
cmp r2 1
jlt invalid
cmp r2 17
jgt too_long
store8 7300000000000000512 r2
set r0 0
label copy
cmp r0 r2
jge done
mov r8 r7
add r8 1
add r8 r0
load8 r1 $r8
set r8 7300000000000000513
add r8 r0
store8 $r8 r1
add r0 1
jmp copy
label too_long
store8 7300000000000000040 1
label done
halt
label invalid
div r0 0
