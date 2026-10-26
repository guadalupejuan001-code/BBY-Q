#!reverse-pc-machine-v1
# Complete this read-only facade: old working descriptors and query count are
# restored after the original speaker emits its answer. No old learned byte
# changes, and no second model/authority is published.
load8 r8 7100000000000000190
store8 7400000000000000008 r8
# Mode 3 explicitly identifies an original E009 utterance, whose concept IDs
# belong to its existing namespace; never mislabel them as new E012 concepts.
store8 7400000000000000013 3
store8 7400000000000000009 0
store8 7400000000000000010 0
store8 7400000000000000011 0
store8 7400000000000000012 0
store8 7400000000000000014 1
store8 7400000000000000015 0
cmp r8 0
jne begin_restore
store8 7400000000000000009 3
store8 7400000000000000014 0
label begin_restore
set r0 0
label restore
set r7 7400000000000004600
add r7 r0
load8 r8 $r7
store8 $r7 0
set r7 7100000000000000140
add r7 r0
store8 $r7 r8
add r0 1
cmp r0 57
jlt restore
halt
