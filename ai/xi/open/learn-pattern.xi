#!reverse-pc-machine-v1
# Supervised construction ID/intent plus semantic labels; no slot ordering is
# supplied. Infer masks from two differently labeled examples, retaining a
# literal possibility until varying examples distinguish it from a variable.
# +176 construction(1..64),+177 intent(1..8),+178 alias token+1,
# +180/182/184 S/P/O u16. This teaches syntax, never answers or facts.
load8 r0 7800000000000000002
cmp r0 1
jne invalid
load8 r0 7400000000000000040
cmp r0 0
jne invalid
load8 r13 7400000000000000032
cmp r13 1
jlt invalid
load8 r0 7800000000000000176
cmp r0 1
jlt invalid
cmp r0 64
jgt invalid
load8 r1 7800000000000000010
cmp r0 r1
jle count_ok
store8 7800000000000000010 r0
label count_ok
sub r0 1
mul r0 96
set r12 7800000000000010000
add r12 r0
load8 r11 7800000000000000177
cmp r11 1
jlt invalid
cmp r11 8
jgt invalid
set r0 7
cmp r11 8
jne generic_required
set r0 1
label generic_required
cmp r11 1
jne not_property
set r0 3
label not_property
cmp r11 6
jne not_alias
set r0 9
label not_alias
cmp r11 5
jne required_ready
load8 r1 7800000000000000180
load8 r14 7800000000000000181
mul r14 256
add r1 r14
load8 r2 7800000000000000182
load8 r14 7800000000000000183
mul r14 256
add r2 r14
add r1 r2
load8 r2 7800000000000000184
load8 r14 7800000000000000185
mul r14 256
add r2 r14
add r1 r2
cmp r1 0
jne required_ready
set r0 0
label required_ready
store8 7800000000000000186 r0
set r0 0
label token
cmp r0 r13
jge compare_header
set r7 7800000000000001024
mov r1 r0
mul r1 4
add r7 r1
mov r15 r7
load8 r8 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r8 r14
add r7 2
load8 r9 $r7
load8 r1 7800000000000000178
mov r2 r0
add r2 1
cmp r1 r2
je alias
cmp r8 0
je invalid
set r10 16
load8 r1 7800000000000000180
load8 r14 7800000000000000181
mul r14 256
add r1 r14
cmp r1 0
je predicate
cmp r8 r1
jne predicate
add r10 1
label predicate
load8 r1 7800000000000000182
load8 r14 7800000000000000183
mul r14 256
add r1 r14
cmp r1 0
je object
cmp r8 r1
jne object
add r10 2
label object
load8 r1 7800000000000000184
load8 r14 7800000000000000185
mul r14 256
add r1 r14
cmp r1 0
je descriptor
cmp r8 r1
jne descriptor
add r10 4
jmp descriptor
label alias
set r10 8
label descriptor
set r7 7800000000000002048
mov r1 r0
mul r1 4
add r7 r1
store8 $r7 r10
add r7 1
mov r15 r7
mov r14 r8
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r8
div r14 256
store8 $r15 r14
add r7 2
store8 $r7 r9
add r0 1
jmp token
label compare_header
load8 r0 $r12
cmp r0 0
je allocate
cmp r0 r13
jne invalid
mov r7 r12
add r7 1
load8 r0 $r7
cmp r0 r11
jne invalid
set r0 0
label intersect_slot
cmp r0 r13
jge second_witness
mov r7 r12
add r7 16
mov r1 r0
mul r1 4
add r7 r1
load8 r2 $r7
set r8 7800000000000002048
add r8 r1
load8 r3 $r8
mov r9 r7
add r9 1
mov r15 r9
load8 r4 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r4 r14
mov r9 r8
add r9 1
mov r15 r9
load8 r5 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r5 r14
set r6 1
set r10 0
label bit
cmp r6 32
jge mask_ready
mov r1 r2
div r1 r6
mod r1 2
cmp r1 0
je next_bit
mov r1 r3
div r1 r6
mod r1 2
cmp r1 0
je next_bit
cmp r6 16
jne keep_bit
cmp r4 r5
jne next_bit
mov r9 r7
add r9 3
load8 r1 $r9
mov r9 r8
add r9 3
load8 r11 $r9
cmp r1 r11
jne next_bit
label keep_bit
add r10 r6
label next_bit
mul r6 2
jmp bit
label mask_ready
cmp r10 0
je invalid
store8 $r7 r10
add r0 1
jmp intersect_slot
label allocate
store8 $r12 r13
mov r7 r12
add r7 1
store8 $r7 r11
add r7 2
store8 $r7 1
add r7 1
load8 r0 7800000000000000180
load8 r14 7800000000000000181
mul r14 256
add r0 r14
mov r15 r7
mov r14 r0
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r0
div r14 256
store8 $r15 r14
add r7 2
load8 r0 7800000000000000182
load8 r14 7800000000000000183
mul r14 256
add r0 r14
mov r15 r7
mov r14 r0
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r0
div r14 256
store8 $r15 r14
add r7 2
load8 r0 7800000000000000184
load8 r14 7800000000000000185
mul r14 256
add r0 r14
mov r15 r7
mov r14 r0
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r0
div r14 256
store8 $r15 r14
mov r1 r13
mul r1 4
set r0 0
label copy_slots
cmp r0 r1
jge promote
set r7 7800000000000002048
add r7 r0
load8 r2 $r7
mov r7 r12
add r7 16
add r7 r0
store8 $r7 r2
add r0 1
jmp copy_slots
label second_witness
load8 r0 7800000000000000186
cmp r0 0
je promote
set r1 0
set r3 1
label distinct_role
cmp r1 3
jge witness_ready
# A supervised predicate role may remain the same across examples. A single
# occurrence can still be distinguished from literal positions below.
cmp r1 1
je next_role
mov r2 r0
div r2 r3
mod r2 2
cmp r2 0
je next_role
set r7 7800000000000000180
mov r2 r1
mul r2 2
add r7 r2
mov r15 r7
load8 r4 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r4 r14
mov r7 r12
add r7 4
add r7 r2
mov r15 r7
load8 r5 $r15
add r15 1
load8 r14 $r15
mul r14 256
add r5 r14
cmp r4 r5
je promote
label next_role
add r1 1
mul r3 2
jmp distinct_role
label witness_ready
mov r7 r12
add r7 3
store8 $r7 2
add r7 7
load8 r0 7800000000000000180
load8 r14 7800000000000000181
mul r14 256
add r0 r14
mov r15 r7
mov r14 r0
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r0
div r14 256
store8 $r15 r14
add r7 2
load8 r0 7800000000000000182
load8 r14 7800000000000000183
mul r14 256
add r0 r14
mov r15 r7
mov r14 r0
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r0
div r14 256
store8 $r15 r14
add r7 2
load8 r0 7800000000000000184
load8 r14 7800000000000000185
mul r14 256
add r0 r14
mov r15 r7
mov r14 r0
mod r14 256
store8 $r15 r14
add r15 1
mov r14 r0
div r14 256
store8 $r15 r14
label promote
mov r7 r12
add r7 2
store8 $r7 0
load8 r0 7800000000000000186
cmp r0 0
je check_slots
add r7 1
load8 r1 $r7
cmp r1 2
jne done
label check_slots
# Force a supervised variable when it has exactly one compatible position.
# Multiple occurrences (e.g. two copies of "is") remain ambiguous until
# varying examples distinguish the literal prefix from the predicate slot.
set r3 1
label force_role
cmp r3 16
jge forced_ready
load8 r4 7800000000000000186
div r4 r3
mod r4 2
cmp r4 0
je force_next
set r0 0
set r4 0
set r6 0
label force_scan
cmp r0 r13
jge force_found
mov r7 r12
add r7 16
mov r1 r0
mul r1 4
add r7 r1
load8 r2 $r7
div r2 r3
mod r2 2
cmp r2 0
je force_scan_next
add r4 1
mov r6 r7
label force_scan_next
add r0 1
jmp force_scan
label force_found
cmp r4 1
jne force_next
store8 $r6 r3
label force_next
mul r3 2
jmp force_role
label forced_ready
set r0 0
set r8 0
label unique
cmp r0 r13
jge unique_done
mov r7 r12
add r7 16
mov r1 r0
mul r1 4
add r7 r1
load8 r2 $r7
cmp r2 16
je next_slot
cmp r2 1
je variable
cmp r2 2
je variable
cmp r2 4
je variable
cmp r2 8
jne done
label variable
mov r1 r8
div r1 r2
mod r1 2
cmp r1 0
jne invalid
add r8 r2
label next_slot
add r0 1
jmp unique
label unique_done
load8 r0 7800000000000000186
cmp r8 r0
jne done
mov r7 r12
add r7 2
store8 $r7 1
label done
halt
label invalid
div r0 0
