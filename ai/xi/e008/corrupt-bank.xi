#!reverse-pc-machine-v1
# Adversarial test only: damage one archived byte. Integrity audit MUST reject.
load8 r0 7000000000000000610
cmp r0 4
je all_banks
div r0 0
label all_banks
load8 r1 7000000000000000766
add r1 1
mod r1 255
store8 7000000000000000766 r1
print r1
