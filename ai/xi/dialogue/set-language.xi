#!reverse-pc-machine-v1
# Own output preference; previous E010/E009 memory remains bytewise unchanged.
load8 r0 7300000000000000002
cmp r0 1
jne invalid
load8 r0 7300000000000000080
cmp r0 1
je valid
cmp r0 2
jne invalid
label valid
store8 7300000000000000003 r0
store8 7300000000000000080 0
halt
label invalid
div r0 0
