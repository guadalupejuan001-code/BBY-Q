#!reverse-pc-machine-v1
# BBY Q E009 / original XI. One persistent organism, not another engine.
# This protocol is a narrow experimental grounded-symbol language.
load8 r0 7000000000000000002
cmp r0 6
je prior_schema_ok
div r0 0
label prior_schema_ok
load8 r0 7000000000000000610
cmp r0 4
je four_original_memories_intact
div r0 0
label four_original_memories_intact
load8 r0 7100000000000000000
cmp r0 0
je free_namespace
div r0 0
label free_namespace
store8 7100000000000000000 76
store8 7100000000000000001 71
store8 7100000000000000002 1
# No words, concepts, predicates, facts, or prelearned answers at birth.
# All counters and dictionaries inherit Ether's zero background.
print r0
mem_stats
stats
