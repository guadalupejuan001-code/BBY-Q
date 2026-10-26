#!reverse-pc-machine-v1
# E008 long-lived provenance and counter-overflow regression, read only.
load8 r0 7000000000000000610
cmp r0 4
je full_archive
div r0 0
label full_archive
load8 r0 7000000000000000612
load8 r1 7000000000000000625
load8 r2 7000000000000000614
load8 r3 7000000000000000626
print r0
print r1
print r2
print r3
mem_stats
stats
