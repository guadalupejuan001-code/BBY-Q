#!reverse-pc-machine-v1
# Read-only bounded structural audit. The examiner also checks every learned
# byte against the authentic parent and independently evaluates all ledgers.
load8 r0 7500000000000000000
cmp r0 83
jne invalid
load8 r0 7500000000000000001
cmp r0 84
jne invalid
load8 r0 7500000000000000002
cmp r0 1
jne invalid
load8 r0 7500000000000000006
cmp r0 16
jgt invalid
mov r15 r0
set r0 0
label ledger
cmp r0 16
jge ledger_done
set r7 7500000000000001000
mov r1 r0
mul r1 8
add r7 r1
set r1 0
label ledger_field
cmp r1 8
jge next_row
mov r8 r7
add r8 r1
load8 r2 $r8
cmp r0 r15
jge must_be_zero
cmp r1 4
jge must_be_zero
cmp r1 2
jge next_field
cmp r2 0
je invalid
cmp r2 13
jlt entity_role
cmp r2 22
jle invalid
label entity_role
set r8 7400000000000006000
add r8 r2
load8 r3 $r8
cmp r3 1
je next_field
# Old E010 color/animal/shape identities need no copied kind-table row.
cmp r2 12
jgt invalid
jmp next_field
label must_be_zero
cmp r2 0
jne invalid
label next_field
add r1 1
jmp ledger_field
label next_row
add r0 1
jmp ledger
label ledger_done
set r0 16
label controls
set r7 7500000000000000000
add r7 r0
load8 r1 $r7
cmp r1 0
jne invalid
add r0 1
cmp r0 64
jlt controls
set r0 2000
label staging
set r7 7500000000000000000
add r7 r0
load8 r1 $r7
cmp r1 0
jne invalid
add r0 1
cmp r0 2216
jlt staging
set r0 0
label verbs
set r7 7500000000000010000
mov r1 r0
mul r1 24
add r7 r1
load8 r2 $r7
cmp r2 7
jgt invalid
add r7 1
load8 r3 $r7
cmp r3 2
jgt invalid
add r7 1
load8 r4 $r7
cmp r4 3
jgt invalid
cmp r4 0
je next_verb
cmp r3 2
jne invalid
set r5 1
cmp r4 1
je expected_mask
set r5 2
cmp r4 2
je expected_mask
set r5 4
label expected_mask
cmp r2 r5
jne invalid
label next_verb
add r0 1
cmp r0 256
jlt verbs
mem_stats
stats
halt
label invalid
div r0 0
