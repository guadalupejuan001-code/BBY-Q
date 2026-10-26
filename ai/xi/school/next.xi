#!reverse-pc-machine-v1
# Competence-based curriculum (not age/grade school).
# Four domains: 1 color 2 animal 3 shape 4 quantity.
# Mastery is a guarded, reproducible promotion on independent test evidence.
load8 r12 7200000000000000000
cmp r12 83
je school_ready
div r12 0
label school_ready
set r0 0
set r14 0
label review_domains
set r11 7200000000000000040
add r11 r0
load8 r7 $r11
set r11 7200000000000000050
add r11 r0
load8 r8 $r11
set r9 0
cmp r7 4
jlt incomplete_domain
mov r10 r8
mul r10 10
mov r11 r7
mul r11 9
cmp r10 r11
jlt incomplete_domain
set r9 1
jmp save_mastery
label incomplete_domain
cmp r14 0
jne save_mastery
mov r14 r0
add r14 1
label save_mastery
set r11 7200000000000000060
add r11 r0
store8 $r11 r9
add r0 1
cmp r0 4
jlt review_domains
cmp r14 0
jne still_learning
# Counted-object competence unlocks learned operations; a separate blind
# arithmetic exam determines whether this competence merits a higher stage.
store8 7200000000000000003 1
load8 r11 7200000000000000072
cmp r11 4
jlt arithmetic_pending
load8 r12 7200000000000000073
mul r12 10
mov r13 r11
mul r13 9
cmp r12 r13
jlt arithmetic_pending
store8 7200000000000000003 2
label arithmetic_pending
store8 7200000000000000070 0
store8 7200000000000000071 1
jmp plan_ready
label still_learning
store8 7200000000000000003 0
store8 7200000000000000070 r14
store8 7200000000000000071 0
label plan_ready
load8 r12 7200000000000000003
print r12
load8 r12 7200000000000000070
print r12
load8 r12 7200000000000000071
print r12
mem_stats
