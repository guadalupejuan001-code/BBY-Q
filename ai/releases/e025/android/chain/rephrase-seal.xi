#!reverse-pc-machine-v1
label m0_entry
# Structural/model audit shared by promotion and read-only validation.
load8 r0 8100000000000000000
cmp r0 82
jne m0_invalid
load8 r0 8100000000000000001
cmp r0 80
jne m0_invalid
load8 r0 8100000000000000002
cmp r0 1
jne m0_invalid
load8 r10 8100000000000000004
cmp r10 1
jlt m0_invalid
cmp r10 64
jgt m0_invalid
set r0 0
set r11 0
label m0_rule
cmp r0 r10
jge m0_total
set r12 8100000000000010000
mov r7 r0
mul r7 96
add r12 r7
set r13 8100000000000020000
add r13 r7
load8 r9 $r12
cmp r9 1
jlt m0_invalid
cmp r9 15
jgt m0_invalid
load8 r9 $r13
cmp r9 15
jgt m0_invalid
mov r7 r12
add r7 1
load8 r2 $r7
mov r7 r13
add r7 1
load8 r3 $r7
cmp r2 r3
jne m0_invalid
set r7 8100000000000030000
mov r2 r0
mul r2 8
add r7 r2
load8 r2 $r7
cmp r2 1
jlt m0_invalid
cmp r2 4
jgt m0_invalid
add r7 1
load8 r3 $r7
cmp r3 2
jgt m0_invalid
cmp r2 1
je m0_head_scope
cmp r2 4
jne m0_count
label m0_head_scope
cmp r3 1
jlt m0_invalid
label m0_count
add r7 1
load8 r2 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r2 r14
cmp r2 1
jlt m0_invalid
add r11 r2
set r1 0
label m0_bank
mov r8 r12
cmp r1 0
je m0_bank_ready
mov r8 r13
label m0_bank_ready
mov r7 r8
add r7 2
load8 r2 $r7
cmp r2 1
jne m0_invalid
load8 r9 $r8
set r2 0
set r6 0
label m0_slot
cmp r2 r9
jge m0_roles
mov r7 r8
add r7 16
mov r3 r2
mul r3 4
add r7 r3
load8 r3 $r7
cmp r3 16
je m0_literal
cmp r3 1
je m0_variable
cmp r3 2
je m0_variable
cmp r3 4
jne m0_invalid
label m0_variable
mov r14 r7
add r14 3
load8 r14 $r14
cmp r3 2
je m0_predicate_variable
cmp r14 1
jne m0_invalid
jmp m0_typed_variable
label m0_predicate_variable
cmp r14 2
jne m0_invalid
label m0_typed_variable
mov r14 r6
div r14 r3
mod r14 2
cmp r14 0
jne m0_invalid
add r6 r3
jmp m0_next_slot
label m0_literal
add r7 1
load8 r4 $r7
add r7 1
load8 r14 $r7
mul r14 256
add r4 r14
add r7 1
load8 r5 $r7
cmp r5 1
jne m0_literal_kind
# A noun/number may be a metalinguistic scaffold inside an explicitly taught
# literal definition-request prefix or modifier (e.g. information, un poco).
# It can never be injected as a literal entity on the canonical side.
cmp r1 0
jne m0_invalid
mov r7 r12
add r7 1
load8 r14 $r7
cmp r14 5
jne m0_invalid
set r7 8100000000000030000
mov r14 r0
mul r14 8
add r7 r14
load8 r14 $r7
cmp r14 1
je m0_scaffold_scope
cmp r14 3
jne m0_invalid
label m0_scaffold_scope
add r7 1
load8 r14 $r7
cmp r14 1
jne m0_invalid
jmp m0_veto_start
label m0_literal_kind
cmp r5 2
je m0_predicate_count
cmp r5 3
jne m0_invalid
jmp m0_veto_start
label m0_predicate_count
set r3 0
set r5 0
label m0_left_predicate
load8 r14 $r12
cmp r3 r14
jge m0_right_predicate_start
mov r7 r12
add r7 16
mov r14 r3
mul r14 4
add r7 r14
load8 r14 $r7
cmp r14 16
jne m0_left_next
add r7 1
load8 r14 $r7
add r7 1
load8 r15 $r7
mul r15 256
add r14 r15
cmp r14 r4
jne m0_left_next
add r5 1
label m0_left_next
add r3 1
jmp m0_left_predicate
label m0_right_predicate_start
set r3 0
label m0_right_predicate
load8 r14 $r13
cmp r3 r14
jge m0_predicate_balance
mov r7 r13
add r7 16
mov r14 r3
mul r14 4
add r7 r14
load8 r14 $r7
cmp r14 16
jne m0_right_next
add r7 1
load8 r14 $r7
add r7 1
load8 r15 $r7
mul r15 256
add r14 r15
cmp r14 r4
jne m0_right_next
sub r5 1
label m0_right_next
add r3 1
jmp m0_right_predicate
label m0_predicate_balance
cmp r5 0
je m0_veto_start
cmp r5 0
jlt m0_invalid
load8 r14 7800000000000000032
load8 r15 7800000000000000033
mul r15 256
add r14 r15
cmp r4 r14
jne m0_invalid
# Removing a literal classification copula requires a supervised question head.
set r7 8100000000000030000
mov r14 r0
mul r14 8
add r7 r14
load8 r14 $r7
cmp r14 1
je m0_copula_scope
cmp r14 4
jne m0_invalid
label m0_copula_scope
add r7 1
load8 r14 $r7
cmp r14 2
jne m0_invalid
label m0_veto_start
set r3 0
label m0_veto
load8 r14 8000000000000000005
cmp r3 r14
jge m0_raw_spelling
set r7 8000000000000001000
mov r14 r3
mul r14 40
add r7 r14
load8 r14 $r7
cmp r14 2
jne m0_next_veto
add r7 2
load8 r14 $r7
add r7 1
load8 r15 $r7
mul r15 256
add r14 r15
cmp r14 r4
je m0_invalid
label m0_next_veto
add r3 1
jmp m0_veto
label m0_raw_spelling
cmp r1 1
jne m0_next_slot
set r7 8100000000000040000
mov r14 r0
mul r14 512
add r7 r14
mov r14 r2
mul r14 34
add r7 r14
load8 r14 $r7
cmp r14 1
jlt m0_invalid
cmp r14 32
jgt m0_invalid
label m0_next_slot
add r2 1
jmp m0_slot
label m0_roles
mov r7 r8
add r7 1
load8 r3 $r7
set r4 0
cmp r3 5
je m0_required
set r4 1
cmp r3 8
je m0_required
set r4 3
cmp r3 1
je m0_required
set r4 7
cmp r3 2
jne m0_invalid
label m0_required
cmp r6 r4
jne m0_invalid
set r7 8100000000000030000
mov r14 r0
mul r14 8
add r7 r14
load8 r3 $r7
cmp r3 2
je m0_literal_span
cmp r3 3
jne m0_bank_next
label m0_literal_span
cmp r6 0
jne m0_invalid
label m0_bank_next
add r1 1
cmp r1 2
jlt m0_bank
add r0 1
jmp m0_rule
label m0_total
set r7 8100000000000000008
set r0 0
set r1 1
set r2 0
label m0_total_byte
mov r3 r7
add r3 r2
load8 r4 $r3
mul r4 r1
add r0 r4
mul r1 256
add r2 1
cmp r2 4
jlt m0_total_byte
cmp r0 r11
jne m0_invalid
# All transactional scratch must be gone before publication or after a turn.
set r0 16
label m0_controls
set r7 8100000000000000000
add r7 r0
load8 r1 $r7
cmp r1 0
jne m0_invalid
add r0 1
cmp r0 128
jlt m0_controls
set r0 512
label m0_temporary
set r7 8100000000000000000
add r7 r0
load8 r1 $r7
cmp r1 0
jne m0_invalid
add r0 1
cmp r0 768
jlt m0_temporary
set r0 1000
label m0_original
set r7 8100000000000000000
add r7 r0
load8 r1 $r7
cmp r1 0
jne m0_invalid
add r0 1
cmp r0 1602
jlt m0_original
set r0 2000
label m0_output
set r7 8100000000000000000
add r7 r0
load8 r1 $r7
cmp r1 0
jne m0_invalid
add r0 1
cmp r0 2600
jlt m0_output
jmp m1_entry
label m0_invalid
div r0 0
label m1_entry
load8 r0 8100000000000000003
cmp r0 0
jne m1_invalid
store8 8100000000000000003 1
jmp finish
label m1_invalid
div r0 0
label finish
halt
