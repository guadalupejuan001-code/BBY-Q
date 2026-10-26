#!reverse-pc-machine-v1
# 7700000000000000025 is set by native source linkage: 0 act,1 story,2 fact,3 arithmetic.
# Successful semantic results update small persistent discourse descriptors.
store8 7700000000000000032 0
store8 7700000000000000033 0
store8 7700000000000000034 0
store8 7700000000000000039 0
store8 7700000000000000038 1
load8 r0 7700000000000000017
cmp r0 0
jne act
load8 r0 7700000000000000025
cmp r0 1
je story
cmp r0 2
je factual
cmp r0 3
jne invalid
load8 r0 7300000000000000008
cmp r0 1
jne unknown
store8 7700000000000000010 0
store8 7700000000000000018 3
store8 7700000000000000019 5
halt
label story
load8 r0 7500000000000000008
cmp r0 1
jne unknown
store8 7700000000000000004 1
load8 r0 7500000000000000010
store8 7700000000000000005 r0
load8 r0 7500000000000000011
store8 7700000000000000006 r0
store8 7700000000000000010 1
# A grammatical count sentence requires a learned order and noun inflection.
load8 r1 7400000000000000003
set r7 7700000000000001001
sub r1 1
mul r1 32
add r7 r1
load8 r0 $r7
cmp r0 2
jne count_fallback
load8 r0 7500000000000000011
mul r0 224
set r7 7700000000000100000
add r7 r0
load8 r1 7400000000000000003
sub r1 1
mul r1 112
add r7 r1
load8 r0 7500000000000000012
load8 r1 7500000000000000013
cmp r1 0
jne plural
cmp r0 1
jne plural
load8 r0 $r7
cmp r0 0
je count_fallback
add r7 34
load8 r0 $r7
cmp r0 0
je count_fallback
jmp count_ready
label plural
add r7 101
load8 r0 $r7
cmp r0 3
jne count_fallback
sub r7 33
load8 r0 $r7
cmp r0 0
je count_fallback
label count_ready
store8 7700000000000000018 2
halt
label count_fallback
store8 7700000000000000018 3
store8 7700000000000000019 6
halt
label factual
load8 r0 7400000000000000008
cmp r0 1
je fact_ready
cmp r0 2
jne unknown
label fact_ready
store8 7700000000000000007 1
load8 r0 7400000000000000010
store8 7700000000000000008 r0
load8 r0 7400000000000000011
store8 7700000000000000009 r0
store8 7700000000000000010 2
store8 7700000000000000018 4
halt
label unknown
set r0 3
label act
store8 7700000000000000018 1
store8 7700000000000000019 r0
cmp r0 3
jlt done
cmp r0 8
je done
store8 7700000000000000010 0
label done
halt
label invalid
div r0 0
