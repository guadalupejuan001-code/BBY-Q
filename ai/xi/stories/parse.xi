#!reverse-pc-machine-v1
# Designed microgrammar over shared learned IDs, never literal word spellings.
# A V NUMBER ITEM (LINK [A] V NUMBER ITEM)*, <=15 tokens.
# QUESTION ITEM ASSIGN_VERB A asks about an existing pair.
# +33 cursor,+34 previous actor,+35 ledger slot,+36 effect,+37 quantity token,
# +38 next cursor,+39 actor,+40 item,+17 pending arithmetic flag.
store8 7500000000000000017 0
load8 r0 7500000000000000008
cmp r0 1
jne done
load8 r0 7500000000000000033
load8 r15 7400000000000000032
cmp r0 r15
jge done
cmp r0 0
jne require_link
load8 r1 7400000000000001600
load8 r2 7500000000000000004
cmp r2 0
je explicit
cmp r1 r2
je question
jmp explicit
label require_link
set r7 7400000000000001600
mov r1 r0
mul r1 2
add r7 r1
load8 r1 $r7
load8 r2 7500000000000000005
cmp r2 0
je syntax
cmp r1 r2
jne syntax
add r0 1
cmp r0 r15
jge syntax
set r7 7400000000000001601
mov r1 r0
mul r1 2
add r7 r1
load8 r1 $r7
cmp r1 2
jne explicit
load8 r2 7500000000000000034
cmp r2 0
je syntax
mov r1 r0
add r0 3
jmp clause_slots
label explicit
load8 r1 7400000000000000047
cmp r1 0
jne syntax
set r7 7400000000000001600
mov r1 r0
mul r1 2
add r7 r1
load8 r2 $r7
add r7 1
load8 r3 $r7
cmp r3 1
jne unknown
cmp r2 13
jlt actor_ok
cmp r2 22
jle syntax
label actor_ok
mov r1 r0
add r1 1
add r0 4
label clause_slots
cmp r0 r15
jgt syntax
store8 7500000000000000038 r0
store8 7500000000000000039 r2
set r7 7400000000000001600
mov r3 r1
mul r3 2
add r7 r3
load8 r3 $r7
add r7 1
load8 r4 $r7
cmp r4 2
jne unknown
set r7 7500000000000010002
mul r3 24
add r7 r3
load8 r3 $r7
cmp r3 1
jlt unknown
cmp r3 3
jgt invalid
store8 7500000000000000036 r3
add r1 1
store8 7500000000000000037 r1
add r1 1
set r7 7400000000000001600
mul r1 2
add r7 r1
load8 r4 $r7
add r7 1
load8 r5 $r7
cmp r5 1
jne unknown
cmp r4 13
jlt item_ok
cmp r4 22
jle syntax
label item_ok
store8 7500000000000000040 r4
store8 7500000000000000015 2
jmp lookup
label question
cmp r15 4
jne syntax
load8 r2 7400000000000001606
load8 r3 7400000000000001607
cmp r3 1
jne unknown
cmp r2 13
jlt question_actor_ok
cmp r2 22
jle syntax
label question_actor_ok
load8 r4 7400000000000001602
load8 r3 7400000000000001603
cmp r3 1
jne unknown
cmp r4 13
jlt question_item_ok
cmp r4 22
jle syntax
label question_item_ok
load8 r3 7400000000000001604
load8 r5 7400000000000001605
cmp r5 2
jne unknown
set r7 7500000000000010002
mul r3 24
add r7 r3
load8 r3 $r7
cmp r3 1
jne syntax
store8 7500000000000000039 r2
store8 7500000000000000040 r4
store8 7500000000000000015 1
store8 7500000000000000033 r15
label lookup
load8 r5 7500000000000000032
set r0 0
label pair
cmp r0 r5
jge missing
set r7 7500000000000002000
mov r1 r0
mul r1 8
add r7 r1
load8 r1 $r7
cmp r1 r2
jne next_pair
add r7 1
load8 r1 $r7
cmp r1 r4
je found
label next_pair
add r0 1
jmp pair
label missing
load8 r1 7500000000000000015
cmp r1 1
je no_memory
load8 r1 7500000000000000036
cmp r1 1
jne no_memory
cmp r0 16
jge capacity
label found
store8 7500000000000000035 r0
load8 r1 7500000000000000015
cmp r1 1
jne ready
set r7 7500000000000002002
mul r0 8
add r7 r0
load8 r0 $r7
store8 7500000000000000012 r0
add r7 1
load8 r0 $r7
store8 7500000000000000013 r0
store8 7500000000000000010 r2
store8 7500000000000000011 r4
halt
label ready
store8 7500000000000000017 1
halt
label unknown
set r0 1
jmp failure
label syntax
set r0 2
jmp failure
label no_memory
set r0 3
jmp failure
label capacity
set r0 5
label failure
store8 7500000000000000008 0
store8 7500000000000000009 r0
store8 7500000000000000017 0
label done
halt
label invalid
div r0 0
