#!reverse-pc-machine-v1
# Optional conversational surface; historical models keep their old protocol.
load8 r0 7700000000000000002
cmp r0 0
je done
cmp r0 1
jne invalid
store8 7700000000000000016 1
label done
halt
label invalid
div r0 0
