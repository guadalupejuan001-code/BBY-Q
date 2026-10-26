#!reverse-pc-machine-v1
# E009 native XI metacognition: decide what to study from the semantic proof.
# 0=use proven knowledge, 1=collect relation evidence, 2=ground a new word.
# Never pretend an absent observation is a fact. No external AI/controller.
load8 r0 7100000000000000002
cmp r0 1
je schema_ok
div r0 0
label schema_ok
load8 r1 7100000000000000190
cmp r1 0
jne known_proof
load8 r2 7100000000000000191
cmp r2 0
jne grounded_but_unresolved
store8 7100000000000000240 2
store8 7100000000000000241 0
store8 7100000000000000242 0
store8 7100000000000000243 0
jmp explanation_ready
label grounded_but_unresolved
store8 7100000000000000240 1
store8 7100000000000000241 r2
load8 r3 7100000000000000192
store8 7100000000000000242 r3
load8 r4 7100000000000000193
store8 7100000000000000243 r4
jmp explanation_ready
label known_proof
store8 7100000000000000240 0
store8 7100000000000000241 0
store8 7100000000000000242 0
store8 7100000000000000243 0
label explanation_ready
load8 r14 7100000000000000240
print r14
load8 r14 7100000000000000241
print r14
load8 r14 7100000000000000242
print r14
load8 r14 7100000000000000243
print r14
mem_stats
stats
