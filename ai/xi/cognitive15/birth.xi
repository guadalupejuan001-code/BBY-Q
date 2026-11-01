#!reverse-pc-machine-v1
# C15 XI outcome bandit: Q144x4, visits144x4, 16-bit counters.
# Its Q values are feedback-trained; C14 is independent supervised prior.
load8 r0 8280000000000000000
cmp r0 0
jne c15_bad
store8 8280000000000000000 15
store8 8280000000000000008 0
store8 8280000000000000009 0
set r0 15
print r0
halt
label c15_bad
div r0 0
