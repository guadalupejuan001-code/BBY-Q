# QChat100: exact GHZ-basis text features, native autoregressive binary tree.
# State gates are Clifford; learned readout weights are binary64 numbers.
# A=8160000000000000000; 100 input bits, 868 readout features.
label qchat_encode
load64 r0 8160000000000000080
cmp r0 2
je qchat_analytic
qprepare 10000 100
h 10000
set r0 10000
set r1 10001
label qchat_chain
cx $r0 $r1
add r0 1
add r1 1
cmp r1 10100
jlt qchat_chain
set r4 0
set r5 0
label qchat_input_x
mov r0 r5
add r0 8160000000000001000
load8 r1 $r0
add r4 r1
mod r4 2
cmp r4 0
je qchat_no_x
mov r0 r5
add r0 10001
x $r0
label qchat_no_x
add r5 1
cmp r5 99
jlt qchat_input_x
load8 r0 8160000000000001099
cmp r0 0
je qchat_observe
z 10000
label qchat_observe
set r5 0
label qchat_observe_pair
mov r0 r5
add r0 10000
mov r1 r0
add r1 1
fexpect f0 Z:$r0 Z:$r1
fset f1 1
fsub f1 f0
fdiv f1 2
ftoi r2 f1
mov r0 r5
add r0 8160000000000002000
store8 $r0 r2
add r5 1
cmp r5 99
jlt qchat_observe_pair
# Global coherence: this observable touches all 100 actual qubits.
fexpect f0 X:10000 X:10001 X:10002 X:10003 X:10004 X:10005 X:10006 X:10007 X:10008 X:10009 X:10010 X:10011 X:10012 X:10013 X:10014 X:10015 X:10016 X:10017 X:10018 X:10019 X:10020 X:10021 X:10022 X:10023 X:10024 X:10025 X:10026 X:10027 X:10028 X:10029 X:10030 X:10031 X:10032 X:10033 X:10034 X:10035 X:10036 X:10037 X:10038 X:10039 X:10040 X:10041 X:10042 X:10043 X:10044 X:10045 X:10046 X:10047 X:10048 X:10049 X:10050 X:10051 X:10052 X:10053 X:10054 X:10055 X:10056 X:10057 X:10058 X:10059 X:10060 X:10061 X:10062 X:10063 X:10064 X:10065 X:10066 X:10067 X:10068 X:10069 X:10070 X:10071 X:10072 X:10073 X:10074 X:10075 X:10076 X:10077 X:10078 X:10079 X:10080 X:10081 X:10082 X:10083 X:10084 X:10085 X:10086 X:10087 X:10088 X:10089 X:10090 X:10091 X:10092 X:10093 X:10094 X:10095 X:10096 X:10097 X:10098 X:10099
fset f1 1
fsub f1 f0
fdiv f1 2
ftoi r0 f1
store8 8160000000000002099 r0
jmp qchat_mode
label qchat_analytic
# Explicit control only: the classically equivalent feature map. Never default.
set r5 0
label qchat_analytic_copy
mov r0 r5
add r0 8160000000000001000
load8 r1 $r0
mov r0 r5
add r0 8160000000000002000
store8 $r0 r1
add r5 1
cmp r5 100
jlt qchat_analytic_copy
label qchat_mode
load64 r0 8160000000000000080
cmp r0 1
jne qchat_products
set r5 0
label qchat_ablate
mov r0 r5
add r0 8160000000000002000
store8 $r0 0
add r5 1
cmp r5 100
jlt qchat_ablate
label qchat_products
# Classical products of measured bits, not extra quantum states.
set r5 0
label qchat_product_outer
mov r0 r5
add r0 8160000000000002000
load8 r6 $r0
set r7 0
label qchat_product_inner
mov r0 r7
add r0 8160000000000002088
load8 r1 $r0
mul r1 r6
mov r0 r5
mul r0 12
add r0 r7
add r0 8160000000000002100
store8 $r0 r1
add r7 1
cmp r7 12
jlt qchat_product_inner
add r5 1
cmp r5 64
jlt qchat_product_outer
ret

label qchat_cache
load64 r6 8160000000000000072
set r5 0
label qchat_cache_loop
mov r0 r5
add r0 8160000000000002000
load8 r1 $r0
mov r0 r6
add r0 r5
store8 $r0 r1
add r5 1
cmp r5 868
jlt qchat_cache_loop
mov r0 r6
add r0 868
load64 r1 8160000000000000048
store8 $r0 r1
ret

label qchat_active
set r5 0
set r6 0
label qchat_active_loop
mov r0 r5
add r0 8160000000000002000
load8 r1 $r0
cmp r1 0
je qchat_active_next
mov r0 r6
mul r0 8
add r0 8160000000000010000
store64 $r0 r5
add r6 1
label qchat_active_next
add r5 1
cmp r5 868
jlt qchat_active_loop
store64 8160000000000000040 r6
ret

label qchat_load_case
load64 r6 8160000000000000072
set r5 0
set r9 0
label qchat_load_case_loop
mov r0 r6
add r0 r5
load8 r1 $r0
cmp r1 0
je qchat_load_case_next
mov r0 r9
mul r0 8
add r0 8160000000000010000
store64 $r0 r5
add r9 1
label qchat_load_case_next
add r5 1
cmp r5 868
jlt qchat_load_case_loop
store64 8160000000000000040 r9
mov r0 r6
add r0 868
load8 r1 $r0
store64 8160000000000000048 r1
ret

# r10 is a binary tree node. Preserve r10..r13, f25 (loss).
label qchat_logit
mov r14 r10
sub r14 1
mul r14 6944
add r14 8160000000000100000
mov r0 r10
sub r0 1
mul r0 8
add r0 8160000000000990000
fload f20 $r0
load64 r8 8160000000000000040
set r7 0
cmp r8 0
je qchat_sigmoid
label qchat_dot
mov r0 r7
mul r0 8
add r0 8160000000000010000
load64 r1 $r0
mul r1 8
add r1 r14
fload f0 $r1
fadd f20 f0
add r7 1
cmp r7 r8
jlt qchat_dot
label qchat_sigmoid
fmax f20 -15
fmin f20 15
fmov f21 f20
fmul f21 -1
fexp f21 f21
fadd f21 1
fset f0 1
fdiv f0 f21
fmov f21 f0
ret

label qchat_train
load64 r12 8160000000000000048
set r10 1
set r13 64
fset f25 0
label qchat_train_node
call qchat_logit
mov r11 r12
div r11 r13
mod r11 2
itof f22 r11
fsub f22 f21
fload f0 8160000000000000032
fmul f22 f0
load64 r8 8160000000000000040
itof f0 r8
fdiv f0 20
fadd f0 1
fdiv f22 f0
set r7 0
cmp r8 0
je qchat_train_bias
label qchat_train_weight
mov r0 r7
mul r0 8
add r0 8160000000000010000
load64 r1 $r0
mul r1 8
add r1 r14
fload f0 $r1
fadd f0 f22
fstore $r1 f0
add r7 1
cmp r7 r8
jlt qchat_train_weight
label qchat_train_bias
mov r0 r10
sub r0 1
mul r0 8
add r0 8160000000000990000
fload f0 $r0
fadd f0 f22
fstore $r0 f0
fmov f0 f21
cmp r11 1
je qchat_train_loss
fset f0 1
fsub f0 f21
label qchat_train_loss
flog f0 f0
fsub f25 f0
mul r10 2
add r10 r11
div r13 2
cmp r13 0
jgt qchat_train_node
load64 r0 8160000000000000024
add r0 1
store64 8160000000000000024 r0
femit nll f25
ret

label qchat_next
call qchat_active
set r10 1
set r13 64
set r12 0
fset f25 0
label qchat_next_node
call qchat_logit
set r11 0
fcmp f21 0.5
jle qchat_next_chosen
# The right subtree must contain at least one vocabulary entry.
mov r0 r12
add r0 r13
load64 r1 8160000000000000008
cmp r0 r1
jge qchat_next_chosen
set r11 1
label qchat_next_chosen
fmov f0 f21
cmp r11 1
je qchat_next_log
fset f0 1
fsub f0 f21
label qchat_next_log
flog f0 f0
fadd f25 f0
mov r0 r11
mul r0 r13
add r12 r0
mul r10 2
add r10 r11
div r13 2
cmp r13 0
jgt qchat_next_node
store64 8160000000000000056 r12
print r12
femit log_probability f25
ret
