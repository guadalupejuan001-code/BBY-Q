#!reverse-pc-machine-v1
# Native XI endurance harness: vary the observable world's independent seed.
# This is a TEST INPUT, not information identifying the regime to the learner.
load8 r0 7000000000000000610
cmp r0 4
je have_four_models
div r0 0
label have_four_models
load8 r0 7000000000000000041
cmp r0 0
je no_incomplete_exam
div r0 0
label no_incomplete_exam
load8 r0 7000000000000000020
add r0 17
mod r0 251
store8 7000000000000000020 r0
print r0
