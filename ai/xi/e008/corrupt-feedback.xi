#!reverse-pc-machine-v1
# Invalid consequence while a new evaluation batch is staged.
load8 r0 7000000000000000041
cmp r0 0
jne batch_present
div r0 0
label batch_present
store8 7000000000000012000 3
