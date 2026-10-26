#!reverse-pc-machine-v1
# Recheck current facts at inference time. Stale/contradicted witnesses cannot
# preserve a rule. At least TWO different positive closures and zero negatives.
load8 r5 7400000000000000011
set r11 7400000000000050000
mov r0 r5
mul r0 40
add r11 r0
load8 r15 $r11
cmp r15 8
jgt invalid
set r0 0
set r6 0
set r12 0
label witness
cmp r0 r15
jge finish
mov r7 r11
add r7 1
mov r1 r0
mul r1 3
add r7 r1
load8 r2 $r7
add r7 1
load8 r3 $r7
add r7 1
load8 r4 $r7
mov r7 r2
mul r7 256
add r7 r5
mul r7 256
add r7 r3
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
set r10 0
cmp r8 0
je ab_no_positive
set r10 1
label ab_no_positive
cmp r9 0
je ab_done
add r10 2
label ab_done

cmp r10 1
jne next
mov r7 r3
mul r7 256
add r7 r5
mul r7 256
add r7 r4
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
set r10 0
cmp r8 0
je bc_no_positive
set r10 1
label bc_no_positive
cmp r9 0
je bc_done
add r10 2
label bc_done

cmp r10 1
jne next
mov r7 r2
mul r7 256
add r7 r5
mul r7 256
add r7 r4
mul r7 4
add r7 7400000000001000000
load8 r8 $r7
add r7 1
load8 r9 $r7
set r10 0
cmp r8 0
je ac_no_positive
set r10 1
label ac_no_positive
cmp r9 0
je ac_done
add r10 2
label ac_done

cmp r10 1
je positive
cmp r10 0
je next
# Negative or conflicted closure blocks this empirical generalization.
set r12 1
jmp next
label positive
add r6 1
label next
add r0 1
jmp witness
label finish
store8 7400000000000000041 0
cmp r12 0
jne done
cmp r6 2
jlt done
store8 7400000000000000041 1
label done
halt
label invalid
div r0 0
