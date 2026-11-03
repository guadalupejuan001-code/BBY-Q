# Caller stages 1000 normalized classical inputs in the feature buffer.
# The feature map itself is implemented in XI, not the transport adapter.
label encode_external_input
set r2 0
label external_features
mov r0 r2
mul r0 8
add r0 8140000000000300000
fload f0 $r0
fmul f0 1.1
fadd f0 1.2
fstore $r0 f0
add r2 1
cmp r2 1000
jlt external_features
ret
