#!reverse-pc-machine-v1
# Read the old lexicon in place, then the append-only u16 extension. Unknown
# questions never allocate. For old IDs, aliases also normalize old K slots.
load8 r0 7800000000000000002
cmp r0 1
jne done
load8 r0 7400000000000000040
cmp r0 0
jne done
load8 r13 7400000000000000032
load8 r12 7800000000000000006
load8 r14 7800000000000000007
mul r14 256
add r12 r14
cmp r12 2048
jgt invalid
set r0 0
label token
cmp r0 r13
jge done
set r7 7400000000000001600
mov r1 r0
mul r1 2
add r7 r1
load8 r10 $r7
add r7 1
load8 r11 $r7
cmp r10 0
jne save
set r1 7400000000000000512
mov r2 r0
mul r2 34
add r1 r2
load8 r2 $r1
set r3 0
label word
cmp r3 r12
jge save
set r4 7800000000000100000
mov r5 r3
mul r5 40
add r4 r5
mov r7 r4
add r7 4
load8 r5 $r7
cmp r5 r2
jne next_word
set r6 0
label letters
cmp r6 r2
jge found
mov r7 r1
add r7 1
add r7 r6
load8 r8 $r7
mov r7 r4
add r7 5
add r7 r6
load8 r9 $r7
cmp r8 r9
jne next_word
add r6 1
jmp letters
label found
mov r15 r4
load8 r10 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r10 r14
mov r7 r4
add r7 2
load8 r11 $r7
jmp save
label next_word
add r3 1
jmp word
label save
set r7 7800000000000001024
mov r1 r0
mul r1 4
add r7 r1
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
cmp r10 255
jgt next_token
set r7 7400000000000001600
mov r1 r0
mul r1 2
add r7 r1
store8 $r7 r10
add r7 1
store8 $r7 r11
label next_token
add r0 1
jmp token
label done
halt
label invalid
div r0 0
