#!reverse-pc-machine-v1
# E005: blank relation grammar. Nothing from XOR is preloaded.
load8 r0 7000000000000000000
cmp r0 0
je empty
div r0 0
label empty
store8 7000000000000000000 66
store8 7000000000000000001 81
store8 7000000000000000002 6
store8 7000000000000000003 1
# A linear model is the starting point for structural growth.
store8 7000000000000000064 128
store8 7000000000000000065 128
store8 7000000000000000066 128
# No feature descriptors at birth. Addresses +200..+203 stay zero.
# Active count, epoch, slot evidence and stream version default to zero.
mem_stats
stats
