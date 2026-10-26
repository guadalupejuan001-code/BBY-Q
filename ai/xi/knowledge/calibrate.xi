#!reverse-pc-machine-v1
load8 r0 7400000000000000002
cmp r0 1
jne invalid
# Register a witnessed A-R-B, B-R-C, A-R-C comparison, not a rule by name.
# event=3; predicate +25, A/B/C +26/27/28. Distinct witnesses only, max 8.
load8 r0 7400000000000000024
cmp r0 3
jne invalid
load8 r5 7400000000000000025
load8 r2 7400000000000000026
load8 r3 7400000000000000027
load8 r4 7400000000000000028
cmp r2 r3
je invalid
cmp r3 r4
je invalid
cmp r2 r4
je invalid
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
jne invalid
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
jne invalid
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
je valid_witness
cmp r10 2
jne invalid
label valid_witness
set r11 7400000000000050000
mov r0 r5
mul r0 40
add r11 r0
load8 r6 $r11
set r0 0
label scan
cmp r0 r6
jge append
mov r7 r11
add r7 1
mov r1 r0
mul r1 3
add r7 r1
load8 r8 $r7
cmp r8 r2
jne next
add r7 1
load8 r8 $r7
cmp r8 r3
jne next
add r7 1
load8 r8 $r7
cmp r8 r4
je clean_start
label next
add r0 1
jmp scan
label append
cmp r6 8
jge invalid
mov r7 r11
add r7 1
mov r0 r6
mul r0 3
add r7 r0
store8 $r7 r2
add r7 1
store8 $r7 r3
add r7 1
store8 $r7 r4
add r6 1
store8 $r11 r6
label clean_start
set r0 16
label clean
set r7 7400000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 2048
jlt clean
halt
label invalid
div r0 0
