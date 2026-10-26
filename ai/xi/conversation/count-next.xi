#!reverse-pc-machine-v1
# Follow the learned ordering of actor/assignment verb/quantity/item.
# +35 action: 1 shared name,2 direct bytes,3 decimal via E011,4 done.
load8 r0 7700000000000000032
cmp r0 4
jge done
load8 r1 7400000000000000003
set r7 7700000000000001008
sub r1 1
mul r1 32
add r7 r1
add r7 r0
load8 r2 $r7
add r0 1
store8 7700000000000000032 r0
store8 7700000000000000038 0
cmp r0 1
jne role
store8 7700000000000000038 1
label role
cmp r2 1
je actor
cmp r2 2
je verb
cmp r2 3
je quantity
cmp r2 4
jne invalid
load8 r0 7500000000000000011
set r7 7700000000000100000
mul r0 224
add r7 r0
load8 r1 7400000000000000003
sub r1 1
mul r1 112
add r7 r1
load8 r0 7500000000000000012
load8 r1 7500000000000000013
cmp r1 0
jne plural
cmp r0 1
jne plural
add r7 34
jmp direct
label plural
add r7 68
jmp direct
label actor
load8 r0 7500000000000000010
jmp name
label verb
load8 r0 7700000000000000529
jmp name
label quantity
load8 r0 7500000000000000012
load8 r1 7500000000000000013
cmp r1 0
jne decimal
cmp r0 1
je one
cmp r0 9
jgt decimal
add r0 13
jmp name
label one
load8 r0 7500000000000000011
set r7 7700000000000100000
mul r0 224
add r7 r0
load8 r1 7400000000000000003
sub r1 1
mul r1 112
add r7 r1
label direct
load8 r6 $r7
add r7 1
load8 r13 7700000000000000038
store8 7700000000000000035 2
halt
label name
store8 7700000000000000040 r0
store8 7700000000000000035 1
halt
label decimal
load8 r0 7700000000000000039
cmp r0 0
je decimal_ready
set r14 32
print r14
label decimal_ready
store8 7700000000000000039 1
store8 7700000000000000035 3
halt
label done
set r14 46
print r14
store8 7700000000000000035 4
halt
label invalid
div r0 0
