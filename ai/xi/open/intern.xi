#!reverse-pc-machine-v1
# Explicit teacher only: 7800000000000000160 requested u16 ID (0 allocate),+162 kind,
# +163 language,+164 raw token index. Return +166 u16 ID. All failures throw
# so the original native transaction rolls back vocabulary and facts together.
load8 r0 7800000000000000002
cmp r0 1
jne invalid
load8 r0 7400000000000000040
cmp r0 0
jne invalid
load8 r0 7800000000000000164
load8 r1 7400000000000000032
cmp r0 r1
jge invalid
load8 r11 7800000000000000162
cmp r11 1
jlt invalid
cmp r11 3
jgt invalid
load8 r12 7800000000000000163
cmp r12 1
jlt invalid
cmp r12 2
jgt invalid
set r8 7400000000000000512
mov r1 r0
mul r1 34
add r8 r1
load8 r9 $r8
cmp r9 1
jlt invalid
cmp r9 32
jgt invalid
set r7 7800000000000001024
mul r0 4
add r7 r0
mov r15 r7
load8 r2 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r2 r14
add r7 2
load8 r3 $r7
load8 r10 7800000000000000160
load8 r14 7800000000000000161
mul r14 256
add r10 r14
cmp r2 0
je unknown
cmp r3 r11
jne invalid
cmp r10 0
je reuse
cmp r10 r2
jne invalid
label reuse
mov r14 r2
mod r14 256
store8 7800000000000000166 r14
mov r14 r2
div r14 256
store8 7800000000000000167 r14
halt
label unknown
load8 r6 7800000000000000006
load8 r14 7800000000000000007
mul r14 256
add r6 r14
cmp r6 2048
jge invalid
cmp r10 0
jne requested
load8 r10 7800000000000000004
load8 r14 7800000000000000005
mul r14 256
add r10 r14
cmp r10 65535
jge invalid
mov r0 r10
add r0 1
mov r14 r0
mod r14 256
store8 7800000000000000004 r14
mov r14 r0
div r14 256
store8 7800000000000000005 r14
jmp new_kind
label requested
cmp r10 255
jgt extended_kind
cmp r10 22
jle old_entity
set r7 7400000000000006000
add r7 r10
load8 r0 $r7
cmp r0 r11
jne invalid
jmp new_entry
label old_entity
cmp r11 1
jne invalid
jmp new_entry
label extended_kind
set r7 7800000000000020000
add r7 r10
load8 r0 $r7
cmp r0 0
je update_next
cmp r0 r11
jne invalid
jmp new_entry
label update_next
load8 r0 7800000000000000004
load8 r14 7800000000000000005
mul r14 256
add r0 r14
cmp r10 r0
jlt new_kind
cmp r10 65535
jge invalid
mov r0 r10
add r0 1
mov r14 r0
mod r14 256
store8 7800000000000000004 r14
mov r14 r0
div r14 256
store8 7800000000000000005 r14
label new_kind
set r7 7800000000000020000
add r7 r10
store8 $r7 r11
label new_entry
set r7 7800000000000100000
mov r0 r6
mul r0 40
add r7 r0
mov r15 r7
mov r14 r10
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r10
div r14 256
store8 $r15 r14
add r7 2
store8 $r7 r11
add r7 1
store8 $r7 r12
add r7 1
store8 $r7 r9
add r7 1
set r0 0
label copy
cmp r0 r9
jge publish
mov r1 r8
add r1 1
add r1 r0
load8 r2 $r1
mov r1 r7
add r1 r0
store8 $r1 r2
add r0 1
jmp copy
label publish
add r6 1
mov r14 r6
mod r14 256
store8 7800000000000000006 r14
mov r14 r6
div r14 256
store8 7800000000000000007 r14
mov r14 r10
mod r14 256
store8 7800000000000000166 r14
mov r14 r10
div r14 256
store8 7800000000000000167 r14
halt
label invalid
div r0 0
