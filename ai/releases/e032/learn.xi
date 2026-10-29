#!reverse-pc-machine-v1
# Native supervised induction of two-role temporal frames.
# Teacher supplies raw text, two role strings, language, intent, time, polarity.
# No template, offsets, expected answer or factual event is supplied.
load8 r0 8650000000000000000
cmp r0 1
jgt tt_invalid
load8 r0 8650000000000000016
cmp r0 1
jlt tt_invalid
cmp r0 64
jgt tt_invalid
sub r0 1
mul r0 256
set r15 8650000000000004096
add r15 r0
load8 r0 8650000000000000017
cmp r0 1
jlt tt_invalid
cmp r0 2
jgt tt_invalid
load8 r0 8650000000000000018
cmp r0 1
jlt tt_invalid
cmp r0 2
jgt tt_invalid
load8 r0 8650000000000000019
cmp r0 1
jlt tt_invalid
cmp r0 3
jgt tt_invalid
load8 r0 8650000000000000020
cmp r0 1
jlt tt_invalid
cmp r0 2
jgt tt_invalid
load8 r0 8650000000000000021
cmp r0 3
jlt tt_invalid
cmp r0 255
jgt tt_invalid
load8 r0 8650000000000000022
cmp r0 1
jlt tt_invalid
cmp r0 31
jgt tt_invalid
load8 r0 8650000000000000023
cmp r0 1
jlt tt_invalid
cmp r0 31
jgt tt_invalid
load8 r9 8650000000000000021
load8 r10 8650000000000000022
load8 r11 8650000000000000023
set r0 0
label tt_validate_s
cmp r0 r10
jge tt_start_s
set r7 8650000000000000512
add r7 r0
load8 r3 $r7
cmp r3 48
jlt tt_invalid
cmp r3 57
jle tt_valid_s
cmp r3 97
jlt tt_invalid
cmp r3 122
jgt tt_invalid
label tt_valid_s
add r0 1
jmp tt_validate_s
label tt_start_s
set r0 0
set r2 0
label tt_scan_s
mov r1 r0
add r1 r10
cmp r1 r9
jgt tt_done_s
set r1 0
label tt_char_s
cmp r1 r10
jge tt_bound_s
set r7 8650000000000000128
add r7 r0
add r7 r1
load8 r3 $r7
set r7 8650000000000000512
add r7 r1
load8 r4 $r7
cmp r3 r4
jne tt_next_s
add r1 1
jmp tt_char_s
label tt_bound_s
cmp r0 0
je tt_right_s
set r7 8650000000000000127
add r7 r0
load8 r3 $r7
cmp r3 32
je tt_right_s
cmp r3 191
jne tt_next_s
label tt_right_s
mov r7 r0
add r7 r10
cmp r7 r9
je tt_hit_s
add r7 8650000000000000128
load8 r3 $r7
cmp r3 32
je tt_hit_s
cmp r3 63
je tt_hit_s
cmp r3 46
jne tt_next_s
label tt_hit_s
add r2 1
mov r12 r0
label tt_next_s
add r0 1
jmp tt_scan_s
label tt_done_s
cmp r2 1
jne tt_invalid
set r0 0
label tt_validate_o
cmp r0 r11
jge tt_start_o
set r7 8650000000000000544
add r7 r0
load8 r3 $r7
cmp r3 48
jlt tt_invalid
cmp r3 57
jle tt_valid_o
cmp r3 97
jlt tt_invalid
cmp r3 122
jgt tt_invalid
label tt_valid_o
add r0 1
jmp tt_validate_o
label tt_start_o
set r0 0
set r2 0
label tt_scan_o
mov r1 r0
add r1 r11
cmp r1 r9
jgt tt_done_o
set r1 0
label tt_char_o
cmp r1 r11
jge tt_bound_o
set r7 8650000000000000128
add r7 r0
add r7 r1
load8 r3 $r7
set r7 8650000000000000544
add r7 r1
load8 r4 $r7
cmp r3 r4
jne tt_next_o
add r1 1
jmp tt_char_o
label tt_bound_o
cmp r0 0
je tt_right_o
set r7 8650000000000000127
add r7 r0
load8 r3 $r7
cmp r3 32
je tt_right_o
cmp r3 191
jne tt_next_o
label tt_right_o
mov r7 r0
add r7 r11
cmp r7 r9
je tt_hit_o
add r7 8650000000000000128
load8 r3 $r7
cmp r3 32
je tt_hit_o
cmp r3 63
je tt_hit_o
cmp r3 46
jne tt_next_o
label tt_hit_o
add r2 1
mov r13 r0
label tt_next_o
add r0 1
jmp tt_scan_o
label tt_done_o
cmp r2 1
jne tt_invalid
cmp r12 32
jgt tt_invalid
mov r0 r13
sub r0 r12
sub r0 r10
cmp r0 1
jlt tt_invalid
cmp r0 48
jgt tt_invalid
store8 8650000000000000033 r0
store8 8650000000000000032 r12
mov r0 r9
sub r0 r13
sub r0 r11
cmp r0 0
jlt tt_invalid
cmp r0 32
jgt tt_invalid
store8 8650000000000000034 r0
load8 r0 $r15
cmp r0 0
je tt_allocate
cmp r0 1
jne tt_invalid
mov r7 r15
add r7 1
load8 r3 $r7
load8 r4 8650000000000000018
cmp r3 r4
jne tt_invalid
mov r7 r15
add r7 2
load8 r3 $r7
load8 r4 8650000000000000019
cmp r3 r4
jne tt_invalid
mov r7 r15
add r7 3
load8 r3 $r7
load8 r4 8650000000000000020
cmp r3 r4
jne tt_invalid
mov r7 r15
add r7 4
load8 r3 $r7
load8 r4 8650000000000000017
cmp r3 r4
jne tt_invalid
mov r7 r15
add r7 5
load8 r3 $r7
load8 r4 8650000000000000032
cmp r3 r4
jne tt_invalid
mov r7 r15
add r7 6
load8 r3 $r7
load8 r4 8650000000000000033
cmp r3 r4
jne tt_invalid
mov r7 r15
add r7 7
load8 r3 $r7
load8 r4 8650000000000000034
cmp r3 r4
jne tt_invalid
set r0 0
load8 r8 8650000000000000032
label tt_cmp_pre
cmp r0 r8
jge tt_cmp_pre_done
mov r7 r15
add r7 80
add r7 r0
load8 r3 $r7
set r7 8650000000000000128
add r7 r0
load8 r4 $r7
cmp r3 r4
jne tt_invalid
add r0 1
jmp tt_cmp_pre
label tt_cmp_pre_done
set r0 0
load8 r8 8650000000000000033
label tt_cmp_mid
cmp r0 r8
jge tt_cmp_mid_done
mov r7 r15
add r7 112
add r7 r0
load8 r3 $r7
set r7 8650000000000000128
add r7 r12
add r7 r10
add r7 r0
load8 r4 $r7
cmp r3 r4
jne tt_invalid
add r0 1
jmp tt_cmp_mid
label tt_cmp_mid_done
set r0 0
load8 r8 8650000000000000034
label tt_cmp_suf
cmp r0 r8
jge tt_cmp_suf_done
mov r7 r15
add r7 160
add r7 r0
load8 r3 $r7
set r7 8650000000000000128
add r7 r13
add r7 r11
add r7 r0
load8 r4 $r7
cmp r3 r4
jne tt_invalid
add r0 1
jmp tt_cmp_suf
label tt_cmp_suf_done
mov r7 r15
add r7 8
load8 r3 $r7
cmp r3 r10
jne tt_s_distinct
set r0 0
label tt_s_same
cmp r0 r10
jge tt_clean
mov r7 r15
add r7 16
add r7 r0
load8 r3 $r7
set r7 8650000000000000512
add r7 r0
load8 r4 $r7
cmp r3 r4
jne tt_s_distinct
add r0 1
jmp tt_s_same
label tt_s_distinct
mov r7 r15
add r7 9
load8 r3 $r7
cmp r3 r11
jne tt_promote
set r0 0
label tt_o_same
cmp r0 r11
jge tt_clean
mov r7 r15
add r7 48
add r7 r0
load8 r3 $r7
set r7 8650000000000000544
add r7 r0
load8 r4 $r7
cmp r3 r4
jne tt_promote
add r0 1
jmp tt_o_same
label tt_promote
store8 $r15 2
jmp tt_clean
label tt_allocate
store8 8650000000000000000 1
store8 $r15 1
load8 r3 8650000000000000018
mov r7 r15
add r7 1
store8 $r7 r3
load8 r3 8650000000000000019
mov r7 r15
add r7 2
store8 $r7 r3
load8 r3 8650000000000000020
mov r7 r15
add r7 3
store8 $r7 r3
load8 r3 8650000000000000017
mov r7 r15
add r7 4
store8 $r7 r3
load8 r3 8650000000000000032
mov r7 r15
add r7 5
store8 $r7 r3
load8 r3 8650000000000000033
mov r7 r15
add r7 6
store8 $r7 r3
load8 r3 8650000000000000034
mov r7 r15
add r7 7
store8 $r7 r3
load8 r3 8650000000000000022
mov r7 r15
add r7 8
store8 $r7 r3
load8 r3 8650000000000000023
mov r7 r15
add r7 9
store8 $r7 r3
set r0 0
label tt_copy_s
cmp r0 r10
jge tt_copy_s_done
set r7 8650000000000000512
add r7 r0
load8 r3 $r7
mov r7 r15
add r7 16
add r7 r0
store8 $r7 r3
add r0 1
jmp tt_copy_s
label tt_copy_s_done
set r0 0
label tt_copy_o
cmp r0 r11
jge tt_copy_o_done
set r7 8650000000000000544
add r7 r0
load8 r3 $r7
mov r7 r15
add r7 48
add r7 r0
store8 $r7 r3
add r0 1
jmp tt_copy_o
label tt_copy_o_done
set r0 0
load8 r8 8650000000000000032
label tt_cp_pre
cmp r0 r8
jge tt_cp_pre_done
set r7 8650000000000000128
add r7 r0
load8 r3 $r7
mov r7 r15
add r7 80
add r7 r0
store8 $r7 r3
add r0 1
jmp tt_cp_pre
label tt_cp_pre_done
set r0 0
load8 r8 8650000000000000033
label tt_cp_mid
cmp r0 r8
jge tt_cp_mid_done
set r7 8650000000000000128
add r7 r12
add r7 r10
add r7 r0
load8 r3 $r7
mov r7 r15
add r7 112
add r7 r0
store8 $r7 r3
add r0 1
jmp tt_cp_mid
label tt_cp_mid_done
set r0 0
load8 r8 8650000000000000034
label tt_cp_suf
cmp r0 r8
jge tt_cp_suf_done
set r7 8650000000000000128
add r7 r13
add r7 r11
add r7 r0
load8 r3 $r7
mov r7 r15
add r7 160
add r7 r0
store8 $r7 r3
add r0 1
jmp tt_cp_suf
label tt_cp_suf_done
label tt_clean
set r0 16
label tt_clean_byte
set r7 8650000000000000000
add r7 r0
store8 $r7 0
add r0 1
cmp r0 4096
jlt tt_clean_byte
halt
label tt_invalid
div r0 0
