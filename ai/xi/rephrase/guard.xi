#!reverse-pc-machine-v1
# Structural/model audit shared by promotion and read-only validation.
load8 r0 8100000000000000000
cmp r0 82
jne invalid
load8 r0 8100000000000000001
cmp r0 80
jne invalid
load8 r0 8100000000000000002
cmp r0 1
jne invalid
load8 r10 8100000000000000004
cmp r10 1
jlt invalid
cmp r10 64
jgt invalid
set r0 0
set r11 0
label rule
cmp r0 r10
jge total
set r12 8100000000000010000
mov r7 r0
mul r7 96
add r12 r7
set r13 8100000000000020000
add r13 r7
load8 r9 $r12
cmp r9 1
jlt invalid
cmp r9 15
jgt invalid
load8 r9 $r13
cmp r9 15
jgt invalid
mov r7 r12
add r7 1
load8 r2 $r7
mov r7 r13
add r7 1
load8 r3 $r7
cmp r2 r3
jne invalid
set r7 8100000000000030000
mov r2 r0
mul r2 8
add r7 r2
load8 r2 $r7
cmp r2 1
jlt invalid
cmp r2 4
jgt invalid
add r7 1
load8 r3 $r7
cmp r3 2
jgt invalid
cmp r2 1
je head_scope
cmp r2 4
jne count
label head_scope
cmp r3 1
jlt invalid
label count
add r7 1
load8 r2 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r2 r14
cmp r2 1
jlt invalid
add r11 r2
set r1 0
label bank
mov r8 r12
cmp r1 0
je bank_ready
mov r8 r13
label bank_ready
mov r7 r8
add r7 2
load8 r2 $r7
cmp r2 1
jne invalid
load8 r9 $r8
set r2 0
set r6 0
label slot
cmp r2 r9
jge roles
mov r7 r8
add r7 16
mov r3 r2
mul r3 4
add r7 r3
load8 r3 $r7
cmp r3 16
je literal
cmp r3 1
je variable
cmp r3 2
je variable
cmp r3 4
jne invalid
label variable
mov r14 r7
add r14 3
load8 r14 $r14
cmp r3 2
je predicate_variable
cmp r14 1
jne invalid
jmp typed_variable
label predicate_variable
cmp r14 2
jne invalid
label typed_variable
mov r14 r6
div r14 r3
mod r14 2
cmp r14 0
jne invalid
add r6 r3
jmp next_slot
label literal
add r7 1
load8 r4 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r4 r14
add r7 1
load8 r5 $r7
cmp r5 1
jne literal_kind
# A noun/number may be a metalinguistic scaffold inside an explicitly taught
# literal definition-request prefix or modifier (e.g. information, un poco).
# It can never be injected as a literal entity on the canonical side.
cmp r1 0
jne invalid
mov r7 r12
add r7 1
load8 r14 $r7
cmp r14 5
jne invalid
set r7 8100000000000030000
mov r14 r0
mul r14 8
add r7 r14
load8 r14 $r7
cmp r14 1
je scaffold_scope
cmp r14 3
jne invalid
label scaffold_scope
add r7 1
load8 r14 $r7
cmp r14 1
jne invalid
jmp veto_start
label literal_kind
cmp r5 2
je predicate_count
cmp r5 3
jne invalid
jmp veto_start
label predicate_count
set r3 0
set r5 0
label left_predicate
load8 r14 $r12
cmp r3 r14
jge right_predicate_start
mov r7 r12
add r7 16
mov r14 r3
mul r14 4
add r7 r14
load8 r14 $r7
cmp r14 16
jne left_next
add r7 1
load8 r14 $r7
add r7 1
load8 r15 $r7
mul r15 256
add r14 r15
cmp r14 r4
jne left_next
add r5 1
label left_next
add r3 1
jmp left_predicate
label right_predicate_start
set r3 0
label right_predicate
load8 r14 $r13
cmp r3 r14
jge predicate_balance
mov r7 r13
add r7 16
mov r14 r3
mul r14 4
add r7 r14
load8 r14 $r7
cmp r14 16
jne right_next
add r7 1
load8 r14 $r7
add r7 1
load8 r15 $r7
mul r15 256
add r14 r15
cmp r14 r4
jne right_next
sub r5 1
label right_next
add r3 1
jmp right_predicate
label predicate_balance
cmp r5 0
je veto_start
cmp r5 0
jlt invalid
load8 r14 7800000000000000032
load8 r15 7800000000000000033
mul r15 256
add r14 r15
cmp r4 r14
jne invalid
# Removing a literal classification copula requires a supervised question head.
set r7 8100000000000030000
mov r14 r0
mul r14 8
add r7 r14
load8 r14 $r7
cmp r14 1
je copula_scope
cmp r14 4
jne invalid
label copula_scope
add r7 1
load8 r14 $r7
cmp r14 2
jne invalid
label veto_start
set r3 0
label veto
load8 r14 8000000000000000005
cmp r3 r14
jge raw_spelling
set r7 8000000000000001000
mov r14 r3
mul r14 40
add r7 r14
load8 r14 $r7
cmp r14 2
jne next_veto
add r7 2
load8 r14 $r7
add r7 1
load8 r15 $r7
mul r15 256
add r14 r15
cmp r14 r4
je invalid
label next_veto
add r3 1
jmp veto
label raw_spelling
cmp r1 1
jne next_slot
set r7 8100000000000040000
mov r14 r0
mul r14 512
add r7 r14
mov r14 r2
mul r14 34
add r7 r14
load8 r14 $r7
cmp r14 1
jlt invalid
cmp r14 32
jgt invalid
label next_slot
add r2 1
jmp slot
label roles
mov r7 r8
add r7 1
load8 r3 $r7
set r4 0
cmp r3 5
je required
set r4 1
cmp r3 8
je required
set r4 3
cmp r3 1
je required
set r4 7
cmp r3 2
jne invalid
label required
cmp r6 r4
jne invalid
set r7 8100000000000030000
mov r14 r0
mul r14 8
add r7 r14
load8 r3 $r7
cmp r3 2
je literal_span
cmp r3 3
jne bank_next
label literal_span
cmp r6 0
jne invalid
label bank_next
add r1 1
cmp r1 2
jlt bank
add r0 1
jmp rule
label total
set r7 8100000000000000008
set r0 0
set r1 1
set r2 0
label total_byte
mov r3 r7
add r3 r2
load8 r4 $r3
mul r4 r1
add r0 r4
mul r1 256
add r2 1
cmp r2 4
jlt total_byte
cmp r0 r11
jne invalid
# All transactional scratch must be gone before publication or after a turn.
set r0 16
label controls
set r7 8100000000000000000
add r7 r0
load8 r1 $r7
cmp r1 0
jne invalid
add r0 1
cmp r0 128
jlt controls
set r0 512
label temporary
set r7 8100000000000000000
add r7 r0
load8 r1 $r7
cmp r1 0
jne invalid
add r0 1
cmp r0 768
jlt temporary
set r0 1000
label original
set r7 8100000000000000000
add r7 r0
load8 r1 $r7
cmp r1 0
jne invalid
add r0 1
cmp r0 1602
jlt original
set r0 2000
label output
set r7 8100000000000000000
add r7 r0
load8 r1 $r7
cmp r1 0
jne invalid
add r0 1
cmp r0 2600
jlt output
halt
label invalid
div r0 0
