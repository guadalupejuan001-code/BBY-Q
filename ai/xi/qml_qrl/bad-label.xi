#!reverse-pc-machine-v1
# Fixture malformada: el trainer debe rechazar label=2 y hacer rollback.
load8 r0 8100000000000001000
cmp r0 86
jne invalid
store8 8100000000000001201 2
halt
label invalid
div r0 0
