#!reverse-pc-machine-v1
# Optional E014 route. Historical checkpoints incur a schema check only.
load8 r0 7500000000000000002
cmp r0 1
jne done
load8 r0 7400000000000000040
cmp r0 0
jne done
load8 r0 7400000000000000032
cmp r0 1
jlt done
load8 r1 7400000000000001600
load8 r2 7500000000000000004
cmp r2 0
je check_verb
cmp r1 r2
je story
label check_verb
load8 r0 7400000000000000032
# Three-token factual/legacy/arithmetic routes retain their existing priority.
cmp r0 4
jlt done
load8 r1 7400000000000001602
cmp r1 0
je check_actor
set r7 7500000000000010001
mul r1 24
add r7 r1
load8 r0 $r7
cmp r0 0
jne story
label check_actor
load8 r0 7400000000000001601
cmp r0 1
jne done
load8 r0 7400000000000001600
cmp r0 13
jlt story
cmp r0 22
jle done
label story
store8 7500000000000000016 1
label done
halt
