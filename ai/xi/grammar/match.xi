#!reverse-pc-machine-v1
# Read learned structural records only; no Spanish/English spelling in code.
# Match all enabled patterns. Conflicting semantic roles cause abstention.
# On one semantic interpretation, normalize RESOLVED slots to E014's query.
# Raw input and numeric expressions are never rewritten.
load8 r0 7600000000000000002
cmp r0 0
je done
cmp r0 1
jne invalid
load8 r0 7400000000000000040
cmp r0 0
jne done
load8 r15 7400000000000000032
cmp r15 4
jlt done
load8 r13 7600000000000000003
cmp r13 16
jgt invalid
set r0 0
label pattern
cmp r0 r13
jge matched
set r1 7600000000000001000
mov r2 r0
mul r2 64
add r1 r2
load8 r2 $r1
cmp r2 r15
jne next_pattern
mov r7 r1
add r7 1
load8 r2 $r7
cmp r2 1
jne next_pattern
set r2 0
set r9 0
set r10 0
set r11 0
label token
cmp r2 r15
jge full_match
mov r3 r1
add r3 8
mov r4 r2
mul r4 3
add r3 r4
load8 r4 $r3
set r5 7400000000000001600
mov r6 r2
mul r6 2
add r5 r6
load8 r6 $r5
add r5 1
load8 r7 $r5
cmp r6 0
je next_pattern
cmp r4 0
je literal
cmp r4 3
je verb
cmp r4 2
jgt invalid
cmp r7 1
jne next_pattern
cmp r6 13
jlt entity
cmp r6 22
jle next_pattern
label entity
cmp r4 1
jne item
mov r9 r6
jmp next_token
label item
mov r10 r6
jmp next_token
label verb
cmp r7 2
jne next_pattern
set r5 7500000000000010002
mov r8 r6
mul r8 24
add r5 r8
load8 r8 $r5
cmp r8 1
jne next_pattern
mov r11 r6
jmp next_token
label literal
add r3 1
load8 r8 $r3
cmp r8 r6
jne next_pattern
add r3 1
load8 r8 $r3
cmp r8 r7
jne next_pattern
label next_token
add r2 1
jmp token
label full_match
cmp r9 0
je invalid
cmp r10 0
je invalid
cmp r11 0
je invalid
load8 r4 7600000000000000008
cmp r4 0
je first_match
load8 r4 7600000000000000009
cmp r4 r9
jne ambiguous
load8 r4 7600000000000000010
cmp r4 r10
jne ambiguous
load8 r4 7600000000000000011
cmp r4 r11
jne ambiguous
jmp next_pattern
label first_match
store8 7600000000000000008 1
store8 7600000000000000009 r9
store8 7600000000000000010 r10
store8 7600000000000000011 r11
jmp next_pattern
label ambiguous
store8 7600000000000000008 2
label next_pattern
add r0 1
jmp pattern
label matched
load8 r0 7600000000000000008
cmp r0 0
je clean
cmp r0 1
jne conflict
load8 r0 7500000000000000004
cmp r0 0
je invalid
store8 7400000000000001600 r0
store8 7400000000000001601 3
load8 r0 7600000000000000010
store8 7400000000000001602 r0
store8 7400000000000001603 1
load8 r0 7600000000000000011
store8 7400000000000001604 r0
store8 7400000000000001605 2
load8 r0 7600000000000000009
store8 7400000000000001606 r0
store8 7400000000000001607 1
store8 7400000000000000032 4
jmp clean
label conflict
store8 7400000000000000040 1
label clean
store8 7600000000000000008 0
store8 7600000000000000009 0
store8 7600000000000000010 0
store8 7600000000000000011 0
label done
halt
label invalid
div r0 0
