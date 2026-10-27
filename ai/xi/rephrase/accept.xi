#!reverse-pc-machine-v1
# A rewrite is accepted only for a unique read-only query interpretation.
# Otherwise restore every original token vector, reset the matcher and retry
# the original route. No transformed input can teach, retract, alias or act.
load8 r0 8100000000000000003
cmp r0 1
jne done
load8 r0 8100000000000000026
cmp r0 1
je restore
load8 r0 8100000000000000024
cmp r0 1
jne done
load8 r0 7800000000000000065
cmp r0 0
jne restore
load8 r0 7800000000000000064
cmp r0 1
je done
cmp r0 2
je done
cmp r0 5
je done
cmp r0 8
je done
cmp r0 9
jlt restore
cmp r0 12
jle done
label restore
load8 r0 8100000000000001600
store8 7400000000000000032 r0
set r0 0
label raw
set r7 8100000000000001000
add r7 r0
load8 r1 $r7
set r7 7400000000000000512
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 510
jlt raw
set r0 0
label legacy
set r7 8100000000000001510
add r7 r0
load8 r1 $r7
set r7 7400000000000001600
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 30
jlt legacy
set r0 0
label open
set r7 8100000000000001540
add r7 r0
load8 r1 $r7
set r7 7800000000000001024
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 60
jlt open
set r0 64
label selection
set r7 7800000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 80
jlt selection
set r0 187
label matching
set r7 7800000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 191
jlt matching
store8 8100000000000000024 0
store8 8100000000000000026 0
store8 8100000000000000025 1
label done
halt
