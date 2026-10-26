#!reverse-pc-machine-v1
# BBY Q / XI birth. The agent owns one RVPC2 / Inverse Ether Memory.
# No pre-trained model, Python learning loop or C++ learner.
load8 r0 7000000000000000000
cmp r0 0
je bbyq_empty
div r0 0
label bbyq_empty
store8 7000000000000000000 66
store8 7000000000000000001 81
store8 7000000000000000002 4
# Four signed relation weights encoded as signed value + 128.
store8 7000000000000000064 128
store8 7000000000000000065 128
store8 7000000000000000066 128
store8 7000000000000000067 128
# Epoch counter starts as background-zero, not a separate database.
load8 r0 7000000000000000016
print r0
mem_stats
stats
