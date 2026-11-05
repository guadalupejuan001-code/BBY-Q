# Exact token frames and sparse learned readout. All inference/SGD runs in XI.
# The prior QChat100 Clifford circuit is reused without changing its state map.
label c1_frame
load64 r1 8150000000000002000
cmp r1 0
jlt c1_bad_frame
set r2 0
set r3 20
label c1_pack_0
mov r0 r2
add r0 8160000000000001000
mov r4 r1
mod r4 2
store8 $r0 r4
div r1 2
add r2 1
sub r3 1
cmp r3 0
jgt c1_pack_0
cmp r1 0
jne c1_bad_frame
load64 r1 8150000000000002008
cmp r1 0
jlt c1_bad_frame
set r2 20
set r3 20
label c1_pack_1
mov r0 r2
add r0 8160000000000001000
mov r4 r1
mod r4 2
store8 $r0 r4
div r1 2
add r2 1
sub r3 1
cmp r3 0
jgt c1_pack_1
cmp r1 0
jne c1_bad_frame
load64 r1 8150000000000002016
cmp r1 0
jlt c1_bad_frame
set r2 40
set r3 16
label c1_pack_2
mov r0 r2
add r0 8160000000000001000
mov r4 r1
mod r4 2
store8 $r0 r4
div r1 2
add r2 1
sub r3 1
cmp r3 0
jgt c1_pack_2
cmp r1 0
jne c1_bad_frame
load64 r1 8150000000000002024
cmp r1 0
jlt c1_bad_frame
set r2 56
set r3 2
label c1_pack_3
mov r0 r2
add r0 8160000000000001000
mov r4 r1
mod r4 2
store8 $r0 r4
div r1 2
add r2 1
sub r3 1
cmp r3 0
jgt c1_pack_3
cmp r1 0
jne c1_bad_frame
load64 r1 8150000000000002032
cmp r1 0
jlt c1_bad_frame
set r2 58
set r3 7
label c1_pack_4
mov r0 r2
add r0 8160000000000001000
mov r4 r1
mod r4 2
store8 $r0 r4
div r1 2
add r2 1
sub r3 1
cmp r3 0
jgt c1_pack_4
cmp r1 0
jne c1_bad_frame
load64 r1 8150000000000002040
cmp r1 0
jlt c1_bad_frame
set r2 65
set r3 7
label c1_pack_5
mov r0 r2
add r0 8160000000000001000
mov r4 r1
mod r4 2
store8 $r0 r4
div r1 2
add r2 1
sub r3 1
cmp r3 0
jgt c1_pack_5
cmp r1 0
jne c1_bad_frame
load64 r1 8150000000000002048
cmp r1 0
jlt c1_bad_frame
set r2 72
set r3 6
label c1_pack_6
mov r0 r2
add r0 8160000000000001000
mov r4 r1
mod r4 2
store8 $r0 r4
div r1 2
add r2 1
sub r3 1
cmp r3 0
jgt c1_pack_6
cmp r1 0
jne c1_bad_frame
load64 r1 8150000000000002056
cmp r1 0
jlt c1_bad_frame
set r2 78
set r3 16
label c1_pack_7
mov r0 r2
add r0 8160000000000001000
mov r4 r1
mod r4 2
store8 $r0 r4
div r1 2
add r2 1
sub r3 1
cmp r3 0
jgt c1_pack_7
cmp r1 0
jne c1_bad_frame
load64 r1 8150000000000002064
cmp r1 0
jlt c1_bad_frame
set r2 94
set r3 6
label c1_pack_8
mov r0 r2
add r0 8160000000000001000
mov r4 r1
mod r4 2
store8 $r0 r4
div r1 2
add r2 1
sub r3 1
cmp r3 0
jgt c1_pack_8
cmp r1 0
jne c1_bad_frame
store64 8160000000000000080 0
call qchat_encode
set r1 0
set r4 1
set r2 0
set r3 20
label c1_unpack_0
mov r0 r2
add r0 8160000000000002000
load8 r5 $r0
cmp r5 0
jlt c1_bad_frame
cmp r5 1
jgt c1_bad_frame
mul r5 r4
add r1 r5
mul r4 2
add r2 1
sub r3 1
cmp r3 0
jgt c1_unpack_0
store64 8150000000000002200 r1
load64 r0 8150000000000002000
cmp r0 r1
jne c1_bad_frame
set r1 0
set r4 1
set r2 20
set r3 20
label c1_unpack_1
mov r0 r2
add r0 8160000000000002000
load8 r5 $r0
cmp r5 0
jlt c1_bad_frame
cmp r5 1
jgt c1_bad_frame
mul r5 r4
add r1 r5
mul r4 2
add r2 1
sub r3 1
cmp r3 0
jgt c1_unpack_1
store64 8150000000000002208 r1
load64 r0 8150000000000002008
cmp r0 r1
jne c1_bad_frame
set r1 0
set r4 1
set r2 40
set r3 16
label c1_unpack_2
mov r0 r2
add r0 8160000000000002000
load8 r5 $r0
cmp r5 0
jlt c1_bad_frame
cmp r5 1
jgt c1_bad_frame
mul r5 r4
add r1 r5
mul r4 2
add r2 1
sub r3 1
cmp r3 0
jgt c1_unpack_2
store64 8150000000000002216 r1
load64 r0 8150000000000002016
cmp r0 r1
jne c1_bad_frame
set r1 0
set r4 1
set r2 56
set r3 2
label c1_unpack_3
mov r0 r2
add r0 8160000000000002000
load8 r5 $r0
cmp r5 0
jlt c1_bad_frame
cmp r5 1
jgt c1_bad_frame
mul r5 r4
add r1 r5
mul r4 2
add r2 1
sub r3 1
cmp r3 0
jgt c1_unpack_3
store64 8150000000000002224 r1
load64 r0 8150000000000002024
cmp r0 r1
jne c1_bad_frame
set r1 0
set r4 1
set r2 58
set r3 7
label c1_unpack_4
mov r0 r2
add r0 8160000000000002000
load8 r5 $r0
cmp r5 0
jlt c1_bad_frame
cmp r5 1
jgt c1_bad_frame
mul r5 r4
add r1 r5
mul r4 2
add r2 1
sub r3 1
cmp r3 0
jgt c1_unpack_4
store64 8150000000000002232 r1
load64 r0 8150000000000002032
cmp r0 r1
jne c1_bad_frame
set r1 0
set r4 1
set r2 65
set r3 7
label c1_unpack_5
mov r0 r2
add r0 8160000000000002000
load8 r5 $r0
cmp r5 0
jlt c1_bad_frame
cmp r5 1
jgt c1_bad_frame
mul r5 r4
add r1 r5
mul r4 2
add r2 1
sub r3 1
cmp r3 0
jgt c1_unpack_5
store64 8150000000000002240 r1
load64 r0 8150000000000002040
cmp r0 r1
jne c1_bad_frame
set r1 0
set r4 1
set r2 72
set r3 6
label c1_unpack_6
mov r0 r2
add r0 8160000000000002000
load8 r5 $r0
cmp r5 0
jlt c1_bad_frame
cmp r5 1
jgt c1_bad_frame
mul r5 r4
add r1 r5
mul r4 2
add r2 1
sub r3 1
cmp r3 0
jgt c1_unpack_6
store64 8150000000000002248 r1
load64 r0 8150000000000002048
cmp r0 r1
jne c1_bad_frame
set r1 0
set r4 1
set r2 78
set r3 16
label c1_unpack_7
mov r0 r2
add r0 8160000000000002000
load8 r5 $r0
cmp r5 0
jlt c1_bad_frame
cmp r5 1
jgt c1_bad_frame
mul r5 r4
add r1 r5
mul r4 2
add r2 1
sub r3 1
cmp r3 0
jgt c1_unpack_7
store64 8150000000000002256 r1
load64 r0 8150000000000002056
cmp r0 r1
jne c1_bad_frame
set r1 0
set r4 1
set r2 94
set r3 6
label c1_unpack_8
mov r0 r2
add r0 8160000000000002000
load8 r5 $r0
cmp r5 0
jlt c1_bad_frame
cmp r5 1
jgt c1_bad_frame
mul r5 r4
add r1 r5
mul r4 2
add r2 1
sub r3 1
cmp r3 0
jgt c1_unpack_8
store64 8150000000000002264 r1
load64 r0 8150000000000002064
cmp r0 r1
jne c1_bad_frame
store64 8150000000000000184 1
load64 r0 8150000000000000256
add r0 1
store64 8150000000000000256 r0
ret
label c1_bad_frame
store64 8150000000000000184 4
ret

# Append an exact feature (family r0, integer value r1) to F or G.
label c1_append
mul r0 1099511627776
add r0 r1
load64 r2 8150000000000000280
load64 r3 8150000000000000288
cmp r3 1024
jge c1_feature_overflow
mov r4 r3
mul r4 8
add r4 r2
store64 $r4 r0
add r3 1
store64 8150000000000000288 r3
ret
label c1_feature_overflow
store64 8150000000000000184 3
ret

label c1_encode_input
store64 8150000000000000184 1
load64 r0 8150000000000000008
cmp r0 0
jlt c1_input_bad
cmp r0 256
jgt c1_input_bad
load64 r0 8150000000000000016
cmp r0 0
jlt c1_input_bad
cmp r0 64
jgt c1_input_bad
store64 8150000000000000024 0
store64 8150000000000000032 0
store64 8150000000000000288 0
store64 8150000000000000280 8150000000000100000
label c1_input_loop
load64 r0 8150000000000000024
cmp r0 2
jge c1_input_done
cmp r0 0
jne c1_history_count
load64 r1 8150000000000000008
set r2 8150000000000010000
set r3 8150000000000015000
jmp c1_input_counted
label c1_history_count
load64 r1 8150000000000000016
set r2 8150000000000020000
set r3 8150000000000021000
label c1_input_counted
load64 r4 8150000000000000032
cmp r4 r1
jge c1_next_section
mov r5 r4
mul r5 8
add r2 r5
load64 r6 $r2
cmp r6 1
jlt c1_input_bad
cmp r6 1048576
jge c1_input_bad
store64 8150000000000002000 r6
set r6 0
cmp r4 0
je c1_previous_ready
sub r2 8
load64 r6 $r2
label c1_previous_ready
store64 8150000000000002008 r6
store64 8150000000000002016 r4
store64 8150000000000002024 r0
store64 8150000000000002032 0
store64 8150000000000002040 0
store64 8150000000000002048 0
add r3 r5
load64 r6 $r3
store64 8150000000000002056 r6
store64 8150000000000002064 0
call c1_frame
load64 r0 8150000000000000184
cmp r0 1
jne c1_input_done
load64 r0 8150000000000002224
mul r0 3
load64 r1 8150000000000002200
call c1_append
load64 r1 8150000000000002208
cmp r1 0
je c1_no_pair
mul r1 1048576
load64 r2 8150000000000002200
add r1 r2
load64 r0 8150000000000002224
mul r0 3
add r0 1
call c1_append
label c1_no_pair
load64 r1 8150000000000002216
mul r1 1048576
load64 r2 8150000000000002200
add r1 r2
load64 r0 8150000000000002224
mul r0 3
add r0 2
call c1_append
load64 r0 8150000000000000032
add r0 1
store64 8150000000000000032 r0
jmp c1_input_loop
label c1_next_section
load64 r0 8150000000000000024
add r0 1
store64 8150000000000000024 r0
store64 8150000000000000032 0
jmp c1_input_loop
label c1_input_bad
store64 8150000000000000184 4
label c1_input_done
load64 r0 8150000000000000184
cmp r0 1
jne c2_focus_done
call c2_scope_features
label c2_focus_done
load64 r0 8150000000000000288
store64 8150000000000000040 r0
call c2_add_role
ret

# Explicit bounded syntax supplies role features without destroying the full
# measured sequence. A contrast selects its positive target; a negative
# request elsewhere supplies a separate feature. The output remains learned.
label c2_scope_features
load64 r8 8150000000000000008
cmp r8 4
jne c2_negative_scan_begin
load64 r0 8150000000000010000
load64 r1 8150000000000000360
cmp r0 r1
jne c2_negative_scan_begin
load64 r0 8150000000000010016
load64 r1 8150000000000000368
cmp r0 r1
jne c2_negative_scan_begin
set r0 10
load64 r1 8150000000000010008
call c1_append
ret
label c2_negative_scan_begin
set r9 0
label c2_negative_scan
cmp r9 r8
jge c2_scope_done
mov r0 r9
mul r0 8
add r0 8150000000000010000
load64 r0 $r0
load64 r1 8150000000000000368
cmp r0 r1
jne c2_negative_scan_next
set r0 11
set r1 1
call c1_append
ret
label c2_negative_scan_next
add r9 1
jmp c2_negative_scan
label c2_scope_done
ret

# A cache is opaque exact measured features, shared by a prompt's token labels.
label c1_cache_input
load64 r0 8150000000000000128
load64 r1 8150000000000000040
store64 $r0 r1
mov r3 r0
add r3 8
load64 r4 8150000000000000008
store64 $r3 r4
add r3 8
load64 r4 8150000000000000016
store64 $r3 r4
set r2 0
label c1_cache_loop
cmp r2 r1
jge c1_cache_done
mov r3 r2
mul r3 8
add r3 8150000000000100000
load64 r4 $r3
mov r3 r2
mul r3 8
add r3 24
add r3 r0
store64 $r3 r4
add r2 1
jmp c1_cache_loop
label c1_cache_done
ret
label c1_load_input
load64 r0 8150000000000000128
load64 r1 $r0
store64 8150000000000000040 r1
mov r3 r0
add r3 8
load64 r4 $r3
store64 8150000000000000008 r4
add r3 8
load64 r4 $r3
store64 8150000000000000016 r4
set r2 0
label c1_load_loop
cmp r2 r1
jge c1_load_done
mov r3 r2
mul r3 8
add r3 24
add r3 r0
load64 r4 $r3
mov r3 r2
mul r3 8
add r3 8150000000000100000
store64 $r3 r4
add r2 1
jmp c1_load_loop
label c1_load_done
call c2_add_role
ret

# Output IDs and positions have exact fields; no hash and no clipping below 64.
label c1_copy_input
load64 r1 8150000000000000040
set r2 0
label c1_active_copy
cmp r2 r1
jge c1_active_ready
mov r0 r2
mul r0 8
add r0 8150000000000100000
load64 r3 $r0
mov r0 r2
mul r0 8
add r0 8150000000000110000
store64 $r0 r3
add r2 1
jmp c1_active_copy
label c1_active_ready
store64 8150000000000000288 r1
store64 8150000000000000280 8150000000000110000
ret
label c1_prefix
call c1_copy_input
store64 8150000000000002000 0
store64 8150000000000002008 0
store64 8150000000000002016 0
store64 8150000000000002024 2
load64 r0 8150000000000000088
store64 8150000000000002032 r0
load64 r0 8150000000000000096
store64 8150000000000002040 r0
load64 r0 8150000000000000104
store64 8150000000000002048 r0
store64 8150000000000002056 0
store64 8150000000000002064 0
call c1_frame
load64 r0 8150000000000000184
cmp r0 1
jne c1_prefix_done
set r0 6
load64 r1 8150000000000002232
call c1_append
set r0 7
load64 r1 8150000000000002240
call c1_append
set r0 8
load64 r1 8150000000000002248
call c1_append
set r0 9
load64 r1 8150000000000002240
mul r1 128
load64 r2 8150000000000002232
add r1 r2
call c1_append
load64 r0 8150000000000000288
store64 8150000000000000048 r0
load64 r1 8150000000000000192
cmp r1 2
jne c1_prefix_done
store64 8150000000000000048 0
label c1_prefix_done
ret

label c1_cache_prefix
load64 r0 8150000000000000320
load64 r1 8150000000000000048
load64 r2 8150000000000000040
sub r1 r2
store64 $r0 r1
set r3 0
label c1_cache_prefix_loop
cmp r3 r1
jge c1_cache_prefix_done
mov r4 r3
add r4 r2
mul r4 8
add r4 8150000000000110000
load64 r5 $r4
mov r4 r3
mul r4 8
add r4 8
add r4 r0
store64 $r4 r5
add r3 1
jmp c1_cache_prefix_loop
label c1_cache_prefix_done
ret
label c1_load_prefix
call c1_copy_input
load64 r0 8150000000000000320
load64 r1 $r0
load64 r2 8150000000000000040
set r3 0
label c1_load_prefix_loop
cmp r3 r1
jge c1_load_prefix_done
mov r4 r3
mul r4 8
add r4 8
add r4 r0
load64 r5 $r4
mov r4 r3
add r4 r2
mul r4 8
add r4 8150000000000110000
store64 $r4 r5
add r3 1
jmp c1_load_prefix_loop
label c1_load_prefix_done
add r2 r1
store64 8150000000000000048 r2
ret

# Preserve r10..r13 and f25, as in the original native binary-tree learner.
# All exact features remain available. Weakly share pair/position evidence so
# one training wording cannot dominate a familiar word in a new wording.
# r6 receives the exact feature family; f23 returns its fixed coefficient.
label c1_feature_scale
fset f23 1
load64 r0 8150000000000000056
cmp r0 1
jne c2_nonfiller_scale
cmp r6 6
jge c2_nonfiller_scale
mov r0 r1
mod r0 1048576
add r0 8150000000500000000
load8 r0 $r0
cmp r0 1
jne c2_nonfiller_scale
fset f23 0
ret
label c2_nonfiller_scale
cmp r6 6
jge c1_scale_output
mod r6 3
cmp r6 0
je c1_scale_done
fset f23 .4
load64 r0 8150000000000000056
cmp r0 1
jne c1_scale_done
fset f23 .05
cmp r6 2
jne c1_scale_done
mov r0 r1
mod r0 1099511627776
div r0 1048576
cmp r0 0
jne c1_scale_done
fset f23 2
ret
label c1_scale_output
fset f23 2
cmp r6 8
jne c1_scale_done
fset f23 .5
label c1_scale_done
ret

label c1_logit
load64 r14 8150000000000000056
cmp r14 1
jne c2_weight_bank_ready
set r14 2
label c2_weight_bank_ready
mul r14 36028797018963968
add r14 8150001000000000000
mov r0 r10
sub r0 1
mul r0 140737488355328
add r14 r0
mov r0 r10
sub r0 1
mul r0 8
load64 r1 8150000000000000056
cmp r1 1
jne c2_logit_bias_bank_ready
set r1 2
label c2_logit_bias_bank_ready
mul r1 1024
add r0 r1
add r0 8150000000005000000
fload f20 $r0
load64 r8 8150000000000000048
set r7 0
label c1_dot
cmp r7 r8
jge c1_sigmoid
mov r0 r7
mul r0 8
add r0 8150000000000110000
load64 r1 $r0
mov r6 r1
div r6 1099511627776
call c1_feature_scale
mul r1 8
add r1 r14
fload f0 $r1
fmul f0 f23
fadd f20 f0
add r7 1
jmp c1_dot
label c1_sigmoid
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

label c1_train
load64 r12 8150000000000000064
set r10 1
load64 r0 8150000000000000056
set r13 64
cmp r0 0
je c1_train_node
set r13 8
label c1_train_node
call c1_logit
mov r11 r12
div r11 r13
mod r11 2
itof f22 r11
fsub f22 f21
fload f0 8150000000000000112
fmul f22 f0
load64 r8 8150000000000000048
itof f0 r8
fdiv f0 20
fadd f0 1
fdiv f22 f0
set r7 0
label c1_train_weight
cmp r7 r8
jge c1_train_bias
mov r0 r7
mul r0 8
add r0 8150000000000110000
load64 r1 $r0
mov r6 r1
div r6 1099511627776
call c1_feature_scale
mul r1 8
add r1 r14
fload f0 $r1
fmov f24 f22
fmul f24 f23
fadd f0 f24
fstore $r1 f0
add r7 1
jmp c1_train_weight
label c1_train_bias
mov r0 r10
sub r0 1
mul r0 8
load64 r1 8150000000000000056
cmp r1 1
jne c2_train_bias_bank_ready
set r1 2
label c2_train_bias_bank_ready
mul r1 1024
add r0 r1
add r0 8150000000005000000
fload f0 $r0
fadd f0 f22
fstore $r0 f0
mul r10 2
add r10 r11
div r13 2
cmp r13 0
jgt c1_train_node
load64 r0 8150000000000000056
mul r0 8
add r0 8150000000000000224
load64 r1 $r0
add r1 1
store64 $r0 r1
ret

label c1_next
set r10 1
set r13 64
set r12 0
load64 r0 8150000000000000056
cmp r0 0
je c1_next_begin
set r13 8
label c1_next_begin
fset f25 0
label c1_next_node
call c1_logit
set r11 0
fcmp f21 0.5
jle c1_next_chosen
mov r0 r12
add r0 r13
load64 r1 8150000000000000056
mul r1 8
add r1 8150000000000000208
load64 r1 $r1
cmp r0 r1
jge c1_next_chosen
set r11 1
label c1_next_chosen
fmov f0 f21
cmp r11 1
je c1_next_log
fset f0 1
fsub f0 f21
label c1_next_log
fmax f0 0.000000000001
flog f0 f0
fadd f25 f0
mov r0 r11
mul r0 r13
add r12 r0
mul r10 2
add r10 r11
div r13 2
cmp r13 0
jgt c1_next_node
store64 8150000000000000072 r12
print r12
femit log_probability f25
ret

# Derive routing features from the exact measured token rows. The first
# meaningful token is invariant to a leading question mark or courtesy word.
# Semantic support is learned with examples of unknown inputs, not a supplied
# tool label. Legacy measured caches are upgraded without changing their rows.
label c2_add_role
load64 r8 8150000000000000040
cmp r8 0
jle c2_role_start
mov r0 r8
sub r0 1
mul r0 8
add r0 8150000000000100000
load64 r0 $r0
div r0 1099511627776
cmp r0 12
jge c2_role_done
label c2_role_start
store64 8150000000000000720 0
store64 8150000000000000728 0
set r9 0
label c2_role_scan
cmp r9 r8
jge c2_role_append
mov r0 r9
mul r0 8
add r0 8150000000000100000
load64 r10 $r0
mov r0 r10
div r0 1099511627776
cmp r0 0
jne c2_role_next
mod r10 1048576
mov r0 r10
add r0 8150000000500000000
load8 r0 $r0
cmp r0 1
je c2_role_next
load64 r0 8150000000000000720
cmp r0 0
jne c2_role_known
store64 8150000000000000720 r10
label c2_role_known
mov r0 r10
add r0 8150000000502000000
load8 r0 $r0
cmp r0 1
jne c2_role_next
store64 8150000000000000728 1
label c2_role_next
add r9 1
jmp c2_role_scan
label c2_role_append
store64 8150000000000000288 r8
store64 8150000000000000280 8150000000000100000
set r0 12
load64 r1 8150000000000000720
call c1_append
load64 r0 8150000000000000704
cmp r0 1
jne c2_role_count
set r0 13
load64 r1 8150000000000000728
call c1_append
label c2_role_count
load64 r0 8150000000000000288
store64 8150000000000000040 r0
label c2_role_done
ret

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
