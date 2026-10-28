#!reverse-pc-machine-v1
# Acknowledgement is an observation, not proof on its own. Verify observable
# postconditions; run/arrange/current-window use the host's typed outcome.
store8 8200000000000000064 0
store8 8200000000000000065 0
load8 r0 8300000000000000016
cmp r0 2
jne advance_fail
load8 r0 8300000000000000080
cmp r0 1
jne advance_fail
load8 r0 8200000000000000016
cmp r0 1
jne advance_fail
load8 r12 8300000000000000019
load8 r13 8300000000000000020
cmp r12 1
jlt advance_fail
cmp r12 2
jgt advance_fail
cmp r13 r12
jge advance_fail
mov r7 r13
mul r7 2
add r7 8300000000000000128
load8 r0 $r7
add r7 1
load8 r1 $r7
cmp r0 1
jlt advance_fail
cmp r0 10
jgt advance_fail
cmp r0 7
je advance_passed
cmp r0 8
je advance_desktop
cmp r0 9
je advance_space
cmp r0 10
je advance_passed
cmp r1 15
je advance_passed
cmp r1 1
jlt advance_fail
cmp r1 31
jgt advance_fail
set r7 8200000000000000032
add r7 r1
load8 r2 $r7
cmp r0 6
je advance_closed
cmp r2 1
jlt advance_fail
cmp r0 1
je advance_passed
cmp r0 2
je advance_focused
cmp r0 3
je advance_minimized
set r7 8300000000000000672
add r7 r1
load8 r2 $r7
cmp r0 4
je advance_maximized
cmp r0 5
jne advance_fail
cmp r2 0
jne advance_fail
jmp advance_passed
label advance_closed
cmp r2 0
jne advance_fail
jmp advance_passed
label advance_focused
load8 r2 8200000000000000017
cmp r2 r1
jne advance_fail
jmp advance_passed
label advance_minimized
set r7 8300000000000000640
add r7 r1
load8 r2 $r7
cmp r2 1
jlt advance_fail
jmp advance_passed
label advance_maximized
cmp r2 1
jlt advance_fail
jmp advance_passed
label advance_desktop
load8 r2 8300000000000000711
load8 r3 8200000000000000018
cmp r2 r3
jne advance_fail
jmp advance_passed
label advance_space
load8 r2 8300000000000000710
sub r1 13
cmp r2 r1
jne advance_fail
label advance_passed
add r13 1
store8 8300000000000000020 r13
cmp r13 r12
jge advance_complete
store8 8300000000000000016 1
jmp feedback_verify
label advance_complete
store8 8300000000000000016 3
store8 8200000000000000067 2
jmp feedback_verify
label advance_fail
store8 8300000000000000034 2
store8 8300000000000000016 4
store8 8200000000000000067 3
jmp feedback_verify

label feedback_verify
# Verifier independently validates the complete proposal, its relation to the
# user's goal, the current step and fresh desktop evidence before dispatch.
load8 r0 8300000000000000016
cmp r0 1
jne verify_next_done
store8 8200000000000000064 0
store8 8200000000000000065 0
load8 r0 8200000000000000016
cmp r0 1
jne verify_next_disconnected
load8 r10 8300000000000000017
load8 r11 8300000000000000018
load8 r12 8300000000000000019
load8 r13 8300000000000000020
cmp r12 1
jlt verify_next_reject
cmp r12 2
jgt verify_next_reject
cmp r13 r12
jge verify_next_reject
load8 r0 8300000000000000129
cmp r0 r11
jne verify_next_reject
load8 r0 8300000000000000128
cmp r12 1
jne verify_next_two
cmp r0 r10
jne verify_next_reject
jmp verify_next_step
label verify_next_two
cmp r0 1
jne verify_next_reject
load8 r0 8300000000000000130
cmp r0 r10
jne verify_next_reject
load8 r0 8300000000000000131
cmp r0 r11
jne verify_next_reject
cmp r10 2
je verify_next_step
cmp r10 4
je verify_next_step
cmp r10 5
je verify_next_step
cmp r10 10
jne verify_next_reject
label verify_next_step
mov r7 r13
mul r7 2
add r7 8300000000000000128
load8 r0 $r7
add r7 1
load8 r1 $r7
cmp r0 1
jlt verify_next_reject
cmp r0 10
jgt verify_next_reject
cmp r0 7
jlt verify_next_window
cmp r0 8
jle verify_next_global
cmp r0 9
je verify_next_space
# Running a program requires a catalog capability AND its unique open window.
cmp r1 16
jlt verify_next_reject
cmp r1 31
jgt verify_next_reject
set r7 8300000000000000512
add r7 r1
load8 r2 $r7
cmp r2 2
jne verify_next_reject
jmp verify_next_unique
label verify_next_window
cmp r1 1
jlt verify_next_reject
cmp r1 10
jle verify_next_capability_ok
cmp r1 15
je verify_next_current
cmp r1 16
jlt verify_next_reject
cmp r1 31
jgt verify_next_reject
set r7 8300000000000000512
add r7 r1
load8 r2 $r7
cmp r2 1
jlt verify_next_missing
cmp r2 2
jgt verify_next_reject
label verify_next_capability_ok
cmp r0 1
jne verify_next_unique
set r7 8200000000000000032
add r7 r1
load8 r2 $r7
cmp r2 0
jne verify_next_accept
load8 r2 8200000000000000018
cmp r2 12
jge verify_next_reject
jmp verify_next_accept
label verify_next_unique
set r7 8200000000000000032
add r7 r1
load8 r2 $r7
cmp r2 0
je verify_next_missing
cmp r2 1
jne verify_next_reject
jmp verify_next_accept
label verify_next_current
cmp r0 1
je verify_next_reject
load8 r2 8200000000000000017
cmp r2 0
je verify_next_missing
jmp verify_next_accept
label verify_next_global
cmp r1 0
jne verify_next_reject
jmp verify_next_accept
label verify_next_space
cmp r1 13
je verify_next_accept
cmp r1 14
jne verify_next_reject
label verify_next_accept
store8 8200000000000000064 r0
store8 8200000000000000065 r1
store8 8200000000000000067 1
store8 8300000000000000016 2
store8 8300000000000000034 1
jmp feedback_speak
label verify_next_disconnected
set r0 4
jmp verify_next_fail
label verify_next_missing
set r0 5
jmp verify_next_fail
label verify_next_reject
set r0 6
label verify_next_fail
store8 8300000000000000034 2
store8 8300000000000000016 4
store8 8200000000000000067 r0
label verify_next_done
jmp feedback_speak

label feedback_speak
# Reply fragments are interface data in Ether, selected by native XI outcome.
load8 r0 8200000000000000067
cmp r0 1
jlt feedback_done
cmp r0 6
jgt feedback_done
sub r0 1
mul r0 2
load8 r1 7400000000000000003
sub r1 1
add r0 r1
mul r0 128
set r7 8200000000000030000
add r7 r0
load8 r2 $r7
set r0 0
label feedback_character
cmp r0 r2
jge feedback_done
mov r3 r7
add r3 1
add r3 r0
load8 r14 $r3
print r14
add r0 1
jmp feedback_character
label feedback_done
jmp w4u_feedback_exit

label w4u_feedback_exit
halt
