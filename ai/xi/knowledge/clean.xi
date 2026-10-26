#!reverse-pc-machine-v1
# Erase raw text, resolved tokens, teacher labels, BFS queue/visits/parents.
# Keep only bounded answer/proof descriptors, never an expected test answer.
set r0 16
label intake
set r7 7400000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 2048
jlt intake
set r0 3000
label search_work
set r7 7400000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 4500
jlt search_work
halt
