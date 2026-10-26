#!reverse-pc-machine-v1
# Controlled independent data stream seed, preserved in the SAME RVPC2.
load8 r0 7000000000000000000
cmp r0 66
je identity_ok
div r0 0
label identity_ok
store8 7000000000000000020 42
print r0
