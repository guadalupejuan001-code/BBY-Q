#!reverse-pc-machine-v1
# An explicit negative at an ancestor is an exception barrier. Contradictory
# ancestor evidence blocks a confident inherited answer.
store8 7800000000000000234 0
load8 r0 7800000000000000208
cmp r0 0
je done
cmp r0 1
je found
cmp r0 3
je conflict
store8 7800000000000000234 2
halt
label found
load8 r0 7800000000000000123
cmp r0 31
jge depth_limit
store8 7800000000000000234 1
store8 7800000000000000235 1
load8 r0 7800000000000000122
store8 7800000000000000124 r0
load8 r0 7800000000000000209
cmp r0 2
jlt done
store8 7800000000000000089 1
halt
label conflict
store8 7800000000000000080 4
store8 7800000000000000234 3
halt
label depth_limit
store8 7800000000000000080 9
store8 7800000000000000234 3
label done
halt
