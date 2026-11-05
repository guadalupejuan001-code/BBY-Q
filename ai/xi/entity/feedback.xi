# Native supervised language target: describe the proposal actually made.
# The host only encodes the resulting prefix bytes for the existing text codec.
label entity_voice_teacher
load64 r0 8184000000000000080
cmp r0 -1
je entity_teacher_refusal
cmp r0 2
je entity_teacher_terminal
store64 8184000000000000512 5
store8 8184000000000000520 75
store8 8184000000000000521 4
store8 8184000000000000522 43
add r0 76
store8 8184000000000000523 r0
store8 8184000000000000524 3
ret
label entity_teacher_terminal
store64 8184000000000000512 3
store8 8184000000000000520 78
store8 8184000000000000521 79
store8 8184000000000000522 3
ret
label entity_teacher_refusal
store64 8184000000000000512 4
store8 8184000000000000520 52
store8 8184000000000000521 50
store8 8184000000000000522 40
store8 8184000000000000523 3
ret
