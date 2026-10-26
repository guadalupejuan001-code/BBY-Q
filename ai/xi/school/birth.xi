#!reverse-pc-machine-v1
# E010 classroom belongs to existing BBY Q, not a new AI/model.
load8 r0 7000000000000000002
cmp r0 6
je original_xi_valid
div r0 0
label original_xi_valid
load8 r0 7000000000000000610
cmp r0 4
je original_knowledge_complete
div r0 0
label original_knowledge_complete
load8 r0 7100000000000000000
cmp r0 76
je original_language_valid
div r0 0
label original_language_valid
load8 r0 7200000000000000000
cmp r0 0
je new_preschool
div r0 0
label new_preschool
store8 7200000000000000000 83
store8 7200000000000000001 67
store8 7200000000000000002 1
store8 7200000000000000003 1
store8 7200000000000000004 1
# 1=preescolar, 2=primaria, 3=secundaria; language 1=es 2=en.
# The learner is born with ZERO color, animal, shape and numeral concepts.
print r0
mem_stats
stats
