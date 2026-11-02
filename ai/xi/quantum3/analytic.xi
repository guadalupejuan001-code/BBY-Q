# Exact classical equivalent of this particular local quantum feature map.
# For a RY-encoded product, CNOT prefix chain, and local RY(theta),
# <Z_i> = cos(theta_i)*product(j<=i,cos(x_j))
#          - sin(theta_i)*sin(x_i)*sin(x_(i+1)); last site omits the next sin.
# This is NOT the quantum agent backend. It is an independent XI baseline
# proving that any advantage on these tasks need not be computational quantum
# advantage. The common optimizer and parameter count stay identical.
label analytic_block
fset f4 1
mov r2 r1
label analytic_loop
mov r7 r2
mul r7 8
add r7 8140000000000300000
fload f0 $r7
fcos f2 f0
fmul f4 f2
fsin f3 f0
mov r0 r2
add r0 1
cmp r0 r3
jge analytic_last
add r7 8
fload f5 $r7
fsin f5 f5
fmul f3 f5
label analytic_last
mov r5 r2
mul r5 8
add r5 r13
fload f1 $r5
cmp r2 r10
jne analytic_unshifted
fadd f1 f31
label analytic_unshifted
fcos f0 f1
fmul f0 f4
fsin f1 f1
fmul f1 f3
fsub f0 f1
call consume_observation
add r2 1
cmp r2 r3
jlt analytic_loop
ret
