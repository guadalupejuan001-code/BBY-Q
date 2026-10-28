#!reverse-pc-machine-v1
label m0_entry
# Social-only reader. Never used by the desktop command interpreter. Normalize
# case and punctuation into private tokens; preserve the original input bytes.
# S=8500000000000000000; +16 error, +17 count; +512 tokens, stride 34.
store8 8500000000000000016 0
store8 8500000000000000017 0
store8 8500000000000000018 0
load8 r9 7400000000000000017
cmp r9 1
jlt m0_bad
set r0 0
set r1 0
set r2 0
label m0_character
cmp r0 r9
jge m0_end
set r7 7400000000000000128
add r7 r0
load8 r3 $r7
cmp r3 32
je m0_separator
cmp r3 9
je m0_separator
cmp r3 33
je m0_separator
cmp r3 63
je m0_separator
cmp r3 44
je m0_separator
cmp r3 46
je m0_separator
cmp r3 194
je m0_opening_mark
cmp r3 195
je m0_latin
cmp r3 45
je m0_write
cmp r3 65
jlt m0_digit
cmp r3 90
jgt m0_lowercase
add r3 32
label m0_lowercase
cmp r3 97
jlt m0_bad
cmp r3 122
jgt m0_bad
jmp m0_write
label m0_digit
cmp r3 48
jlt m0_bad
cmp r3 57
jgt m0_bad
label m0_write
cmp r1 15
jge m0_bad
cmp r2 32
jge m0_bad
set r7 8500000000000000513
mov r8 r1
mul r8 34
add r7 r8
add r7 r2
store8 $r7 r3
add r2 1
jmp m0_next
label m0_opening_mark
cmp r2 0
jne m0_bad
add r0 1
cmp r0 r9
jge m0_bad
set r7 7400000000000000128
add r7 r0
load8 r3 $r7
cmp r3 161
je m0_next
cmp r3 191
jne m0_bad
jmp m0_next
label m0_latin
cmp r1 15
jge m0_bad
cmp r2 30
jgt m0_bad
set r7 8500000000000000513
mov r8 r1
mul r8 34
add r7 r8
add r7 r2
store8 $r7 195
add r2 1
add r0 1
cmp r0 r9
jge m0_bad
set r7 7400000000000000128
add r7 r0
load8 r3 $r7
cmp r3 128
jlt m0_bad
cmp r3 191
jgt m0_bad
cmp r3 159
jgt m0_write
cmp r3 151
je m0_bad
add r3 32
jmp m0_write
label m0_separator
cmp r2 0
je m0_next
set r7 8500000000000000512
mov r8 r1
mul r8 34
add r7 r8
store8 $r7 r2
add r1 1
set r2 0
label m0_next
add r0 1
jmp m0_character
label m0_end
cmp r2 0
je m0_count
set r7 8500000000000000512
mov r8 r1
mul r8 34
add r7 r8
store8 $r7 r2
add r1 1
label m0_count
cmp r1 0
je m0_bad
store8 8500000000000000017 r1
jmp m1_entry
label m0_bad
store8 8500000000000000016 1
jmp m1_entry
label m1_entry
# Explicit supervised fragment/category or response lesson. No host-side
# intent classifier. +32 mode (1 phrase, 2 reply), +33 category (1..10).
load8 r0 8500000000000000000
cmp r0 85
jne m1_invalid
load8 r0 8500000000000000002
cmp r0 0
jne m1_invalid
load8 r11 8500000000000000033
cmp r11 1
jlt m1_invalid
cmp r11 10
jgt m1_invalid
load8 r0 8500000000000000032
cmp r0 2
je m1_reply
cmp r0 1
jne m1_invalid
cmp r11 9
jgt m1_invalid
load8 r0 8500000000000000016
cmp r0 0
jne m1_invalid
load8 r13 8500000000000000017
load8 r12 8500000000000000003
set r0 0
label m1_existing
cmp r0 r12
jge m1_allocate
set r7 8600000000000100000
mov r1 r0
mul r1 516
add r7 r1
load8 r1 $r7
cmp r1 r13
jne m1_next_record
mov r10 r7
add r10 2
set r1 0
label m1_compare_word
cmp r1 r13
jge m1_same
set r8 8500000000000000512
mov r2 r1
mul r2 34
add r8 r2
mov r9 r10
add r9 r2
load8 r3 $r8
load8 r4 $r9
cmp r3 r4
jne m1_next_record
set r5 0
label m1_compare_byte
cmp r5 r3
jge m1_compared_word
add r8 1
add r9 1
load8 r4 $r8
load8 r6 $r9
cmp r4 r6
jne m1_next_record
add r5 1
jmp m1_compare_byte
label m1_compared_word
add r1 1
jmp m1_compare_word
label m1_same
add r7 1
load8 r1 $r7
cmp r1 r11
jne m1_invalid
jmp m1_done
label m1_next_record
add r0 1
jmp m1_existing
label m1_allocate
cmp r12 255
jge m1_invalid
set r7 8600000000000100000
mul r12 516
add r7 r12
store8 $r7 r13
add r7 1
store8 $r7 r11
add r7 1
set r0 0
label m1_copy_word
cmp r0 r13
jge m1_allocated
set r8 8500000000000000512
mov r1 r0
mul r1 34
add r8 r1
load8 r2 $r8
store8 $r7 r2
set r3 0
label m1_copy_byte
cmp r3 r2
jge m1_word_done
add r8 1
add r7 1
load8 r4 $r8
store8 $r7 r4
add r3 1
jmp m1_copy_byte
label m1_word_done
set r7 8600000000000100002
load8 r1 8500000000000000003
mul r1 516
add r7 r1
add r0 1
mov r1 r0
mul r1 34
add r7 r1
jmp m1_copy_word
label m1_allocated
load8 r0 8500000000000000003
add r0 1
store8 8500000000000000003 r0
jmp m1_done
label m1_reply
load8 r0 7400000000000000003
cmp r0 1
jlt m1_invalid
cmp r0 2
jgt m1_invalid
sub r11 1
mul r11 512
set r7 8500000000000100000
add r7 r11
sub r0 1
mul r0 256
add r7 r0
load8 r6 7400000000000000017
cmp r6 1
jlt m1_invalid
load8 r0 $r7
cmp r0 0
jne m1_invalid
store8 $r7 r6
set r0 0
label m1_copy_reply
cmp r0 r6
jge m1_done
set r8 7400000000000000128
add r8 r0
load8 r1 $r8
add r7 1
store8 $r7 r1
add r0 1
jmp m1_copy_reply
label m1_done
jmp m2_entry
label m1_invalid
div r0 0
label m2_entry
# Keep only the sealed teaching table. Queries leave no private scratch bytes.
set r0 16
label m2_controls
set r7 8500000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 128
jlt m2_controls
set r0 512
label m2_tokens
set r7 8500000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 1024
jlt m2_tokens
jmp m3_entry
label m3_entry
# E013: clear bounded actual intake and the visited-node queue, preserving the
# same E012 clean-state invariant. Token slots are cleared even after bad input.
load8 r2 7400000000000000017
load8 r3 7400000000000000050
set r0 0
label m3_visited
cmp r0 r3
jge m3_raw_start
set r7 7400000000000003000
add r7 r0
load8 r1 $r7
cmp r1 1
jlt m3_invalid
store8 $r7 0
set r7 7400000000000003400
add r7 r1
store8 $r7 0
set r7 7400000000000003800
add r7 r1
store8 $r7 0
set r7 7400000000000004200
add r7 r1
store8 $r7 0
add r0 1
jmp m3_visited
label m3_raw_start
set r0 0
label m3_raw
cmp r0 r2
jge m3_token_start
set r7 7400000000000000128
add r7 r0
store8 $r7 0
add r0 1
jmp m3_raw
label m3_token_start
set r0 0
label m3_tokens
set r7 7400000000000000512
add r7 r0
store8 $r7 0
add r0 1
cmp r0 510
jlt m3_tokens
set r0 0
label m3_resolved
set r7 7400000000000001600
add r7 r0
store8 $r7 0
add r0 1
cmp r0 30
jlt m3_resolved
set r0 16
label m3_control
set r7 7400000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 64
jlt m3_control
jmp finish
label m3_invalid
div r0 0
label finish
halt
