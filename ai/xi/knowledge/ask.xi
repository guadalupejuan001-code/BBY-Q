#!reverse-pc-machine-v1
# Open-world reasoning: missing data is UNKNOWN, not false.
# Negative and conflicted direct evidence block hypothetical composition.
load8 r0 7400000000000000009
cmp r0 0
jne done
load8 r2 7400000000000000010
load8 r3 7400000000000000011
load8 r4 7400000000000000012
load8 r0 7400000000000000013
cmp r0 2
je objects
mov r7 r2
mul r7 256
add r7 r3
mul r7 256
add r7 r4
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
set r10 0
cmp r8 0
je direct_no_positive
set r10 1
label direct_no_positive
cmp r9 0
je direct_done
add r10 2
label direct_done

cmp r10 1
je direct_yes
cmp r10 2
je direct_no
cmp r10 3
je conflict
load8 r0 7400000000000000041
cmp r0 1
jne no_proof
# Sparse keyed edges; bounded native BFS supports multi-hop paths and cycles.
set r7 7400000000000003400
add r7 r2
store8 $r7 1
store8 7400000000000003000 r2
store8 7400000000000000050 1
set r0 0
set r1 1
label breadth_first
cmp r0 r1
jge no_proof
cmp r0 64
jge budget
set r7 7400000000000003000
add r7 r0
load8 r5 $r7
set r6 1
label candidate
cmp r6 255
jgt next_node
mov r7 r5
mul r7 256
add r7 r3
mul r7 256
add r7 r6
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
set r10 0
cmp r8 0
je edge_no_positive
set r10 1
label edge_no_positive
cmp r9 0
je edge_done
add r10 2
label edge_done

cmp r10 1
jne next_candidate
set r7 7400000000000003400
add r7 r6
load8 r8 $r7
cmp r8 0
jne next_candidate
set r7 7400000000000004200
add r7 r5
load8 r8 $r7
add r8 1
cmp r8 31
jgt next_candidate
cmp r1 255
jge budget
set r7 7400000000000003400
add r7 r6
store8 $r7 1
set r7 7400000000000003800
add r7 r6
store8 $r7 r5
set r7 7400000000000004200
add r7 r6
store8 $r7 r8
set r7 7400000000000003000
add r7 r1
store8 $r7 r6
add r1 1
store8 7400000000000000050 r1
cmp r6 r4
je path_found
label next_candidate
add r6 1
jmp candidate
label next_node
add r0 1
jmp breadth_first
label path_found
store8 7400000000000000015 r8
mov r5 r4
set r0 0
label reconstruct
cmp r0 32
jge budget
set r7 7400000000000002200
add r7 r0
store8 $r7 r5
cmp r5 r2
je direct_yes
set r7 7400000000000003800
add r7 r5
load8 r5 $r7
cmp r5 0
je budget
add r0 1
jmp reconstruct
label direct_yes
store8 7400000000000000008 1
store8 7400000000000000014 1
store8 7400000000000002100 r4
load8 r0 7400000000000000015
cmp r0 0
jne done
store8 7400000000000000015 1
halt
label direct_no
store8 7400000000000000008 2
store8 7400000000000000014 1
store8 7400000000000002100 r4
store8 7400000000000000015 1
halt
label conflict
store8 7400000000000000008 0
store8 7400000000000000009 4
halt
label objects
# What-questions list directly taught objects, not every abstract ancestor.
set r4 1
set r0 0
label object_candidate
cmp r4 255
jgt object_done
mov r7 r2
mul r7 256
add r7 r3
mul r7 256
add r7 r4
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
set r10 0
cmp r8 0
je obj_no_positive
set r10 1
label obj_no_positive
cmp r9 0
je obj_done
add r10 2
label obj_done

cmp r10 1
jne next_object
cmp r0 8
jge truncated
set r7 7400000000000002100
add r7 r0
store8 $r7 r4
add r0 1
jmp next_object
label truncated
store8 7400000000000000042 1
label next_object
add r4 1
jmp object_candidate
label object_done
cmp r0 0
je no_proof
store8 7400000000000000008 1
store8 7400000000000000014 r0
halt
label no_proof
store8 7400000000000000009 3
halt
label budget
store8 7400000000000000008 0
store8 7400000000000000009 5
halt
label done
halt
