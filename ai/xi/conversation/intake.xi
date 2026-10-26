#!reverse-pc-machine-v1
# Designed conversational grammar over supervised functional concepts.
# Normalize only resolved semantic slots. E014 still owns all account changes.
load8 r0 7700000000000000016
cmp r0 1
jne done
load8 r0 7400000000000000040
cmp r0 0
jne unsupported
load8 r15 7400000000000000032
# Pronouns name the last explicit count referent, never a guessed new entity.
set r0 0
set r10 0
set r12 0
label pronoun_scan
cmp r0 r15
jge pronouns_ready
set r7 7400000000000001600
mov r1 r0
mul r1 2
add r7 r1
load8 r2 $r7
load8 r3 7700000000000000519
cmp r2 r3
je feminine
load8 r3 7700000000000000520
cmp r2 r3
je masculine
set r7 7700000000000010000
mul r2 4
add r7 r2
load8 r3 $r7
cmp r3 1
jne scan_next
add r12 1
jmp scan_next
label feminine
set r11 2
jmp pronoun
label masculine
set r11 1
label pronoun
cmp r10 0
jne clarify
mov r10 r0
add r10 1
label scan_next
add r0 1
jmp pronoun_scan
label pronouns_ready
cmp r10 0
je intents
cmp r12 0
jne clarify
load8 r0 7700000000000000010
cmp r0 1
jne clarify
load8 r0 7700000000000000004
cmp r0 1
jne clarify
load8 r2 7700000000000000005
set r7 7700000000000010001
mov r0 r2
mul r0 4
add r7 r0
load8 r0 $r7
cmp r0 r11
jne clarify
sub r10 1
mul r10 2
set r7 7400000000000001600
add r7 r10
store8 $r7 r2
add r7 1
store8 $r7 1
label intents
load8 r8 7400000000000001600
load8 r9 7400000000000001602
load8 r10 7400000000000001604
load8 r11 7400000000000001606
load8 r12 7400000000000001608
load8 r0 7700000000000000537
cmp r8 r0
jne usual_intents
cmp r15 2
jne usual_intents
load8 r0 7700000000000000538
cmp r9 r0
je status
label usual_intents
load8 r0 7700000000000000513
cmp r8 r0
je greeting
load8 r0 7700000000000000515
cmp r8 r0
je who
load8 r0 7700000000000000530
cmp r8 r0
je what
load8 r0 7700000000000000523
cmp r8 r0
je tell
load8 r0 7700000000000000531
cmp r8 r0
je followup
load8 r0 7700000000000000535
cmp r8 r0
je count_short
load8 r0 7700000000000000532
cmp r8 r0
je english_count_short
jmp action_short
label greeting
cmp r15 1
je greet
cmp r15 2
jne done
load8 r0 7700000000000000526
cmp r9 r0
jne done
label greet
store8 7700000000000000017 1
halt
label who
load8 r0 7700000000000000528
cmp r9 r0
jne done
cmp r15 2
je identity
cmp r15 3
jne done
load8 r0 7700000000000000516
cmp r10 r0
jne done
jmp identity
label what
cmp r15 2
jne what_name
load8 r0 7700000000000000521
cmp r9 r0
je identity
jmp done
label what_name
cmp r15 4
jne done
load8 r0 7700000000000000522
cmp r9 r0
jne check_name
load8 r0 7700000000000000516
cmp r10 r0
jne done
load8 r0 7700000000000000521
cmp r11 r0
je identity
jmp done
label check_name
load8 r0 7700000000000000528
cmp r9 r0
jne factual_article
load8 r0 7700000000000000517
cmp r10 r0
jne factual_article
load8 r0 7700000000000000518
cmp r11 r0
je identity
label factual_article
load8 r0 7400000000000001603
cmp r0 2
jne done
cmp r10 14
je article_ok
load8 r0 7700000000000000514
cmp r10 r0
je article_ok
load8 r0 7700000000000000536
cmp r10 r0
jne done
label article_ok
load8 r0 7400000000000001607
cmp r0 1
jne unsupported
mov r8 r11
jmp fact_query
label tell
cmp r15 3
je tell_three
cmp r15 4
je tell_four
cmp r15 5
jne done
load8 r0 7700000000000000525
cmp r9 r0
jne done
load8 r0 7700000000000000524
cmp r10 r0
jne done
mov r10 r11
mov r11 r12
jmp tell_article
label tell_four
load8 r0 7700000000000000525
cmp r9 r0
jne spanish_tell
load8 r0 7700000000000000524
cmp r10 r0
jne done
mov r8 r11
jmp tell_subject
label spanish_tell
load8 r0 7700000000000000524
cmp r9 r0
jne done
label tell_article
cmp r10 14
je tell_article_ready
load8 r0 7700000000000000514
cmp r10 r0
je tell_article_ready
load8 r0 7700000000000000536
cmp r10 r0
jne done
label tell_article_ready
mov r8 r11
jmp tell_subject
label tell_three
load8 r0 7700000000000000524
cmp r9 r0
jne done
mov r8 r10
label tell_subject
load8 r9 7700000000000000528
jmp fact_query
label followup
cmp r15 2
je followup_two
cmp r15 3
jne done
cmp r9 14
je followup_article
load8 r0 7700000000000000514
cmp r9 r0
je followup_article
load8 r0 7700000000000000536
cmp r9 r0
jne done
label followup_article
mov r8 r10
jmp followup_entity
label followup_two
mov r8 r9
label followup_entity
cmp r8 0
je unsupported
cmp r8 13
jlt followup_topic
cmp r8 22
jle clarify
label followup_topic
load8 r0 7700000000000000010
cmp r0 1
je followup_count
cmp r0 2
jne clarify
load8 r0 7700000000000000007
cmp r0 1
jne clarify
load8 r9 7700000000000000009
jmp fact_query
label followup_count
set r7 7700000000000010000
mov r0 r8
mul r0 4
add r7 r0
load8 r0 $r7
cmp r0 1
je followup_actor
cmp r0 2
jne clarify
mov r10 r8
load8 r8 7700000000000000005
jmp count_query
label followup_actor
load8 r10 7700000000000000006
jmp count_query
label count_short
load8 r0 7700000000000000529
cmp r9 r0
jne done
cmp r15 2
je implicit_count
cmp r15 3
jne done
load8 r0 7400000000000001605
cmp r0 1
jne unsupported
mov r8 r10
jmp explicit_count
label english_count_short
cmp r15 3
jne english_count_five
load8 r0 7700000000000000528
cmp r9 r0
jne done
load8 r0 7700000000000000516
cmp r10 r0
je status
jmp done
label english_count_five
cmp r15 5
jne done
load8 r0 7700000000000000533
cmp r9 r0
jne done
load8 r0 7700000000000000534
cmp r10 r0
jne done
load8 r0 7700000000000000529
cmp r12 r0
jne done
load8 r0 7400000000000001607
cmp r0 1
jne unsupported
mov r8 r11
jmp explicit_count
label implicit_count
load8 r8 7700000000000000005
label explicit_count
load8 r0 7700000000000000010
cmp r0 1
jne clarify
load8 r0 7700000000000000004
cmp r0 1
jne clarify
load8 r10 7700000000000000006
jmp count_query
label action_short
cmp r15 4
je actor_more
cmp r15 3
jne verb_first
load8 r0 7400000000000001601
cmp r0 1
jne verb_first
# Explicit actor with omitted object: A V NUMBER.
load8 r0 7400000000000001603
cmp r0 2
jne done
cmp r10 0
je actor_number
cmp r10 13
jlt done
cmp r10 22
jgt done
label actor_number
set r12 0
jmp actor_effect
label actor_more
load8 r0 7400000000000001601
cmp r0 1
jne done
load8 r0 7700000000000000527
cmp r11 r0
jne done
load8 r0 7400000000000001603
cmp r0 2
jne done
set r12 1
label actor_effect
set r7 7500000000000010002
mov r0 r9
mul r0 24
add r7 r0
load8 r0 $r7
cmp r0 1
jlt done
cmp r0 3
jgt done
cmp r12 1
jne actor_context
cmp r0 1
je unsupported
label actor_context
load8 r0 7700000000000000010
cmp r0 1
jne clarify
load8 r0 7700000000000000004
cmp r0 1
jne clarify
load8 r0 7700000000000000006
store8 7400000000000001606 r0
store8 7400000000000001607 1
store8 7400000000000000032 4
halt
label verb_first
cmp r15 2
jlt done
cmp r15 3
jgt done
load8 r0 7400000000000001601
cmp r0 2
jne done
set r7 7500000000000010002
mov r0 r8
mul r0 24
add r7 r0
load8 r0 $r7
cmp r0 1
jlt done
cmp r0 3
jgt done
cmp r15 3
jne verb_question
load8 r1 7700000000000000527
cmp r10 r1
jne verb_question
cmp r0 1
je unsupported
label verb_question
load8 r0 7400000000000000047
cmp r0 0
jne unsupported
load8 r0 7700000000000000010
cmp r0 1
jne clarify
load8 r0 7700000000000000004
cmp r0 1
jne clarify
mov r11 r8
load8 r8 7700000000000000005
cmp r15 2
je action_implicit_item
load8 r0 7700000000000000527
cmp r10 r0
je action_implicit_item
load8 r0 7400000000000001605
cmp r0 1
jne unsupported
jmp action_item
label action_implicit_item
load8 r10 7700000000000000006
label action_item
# Copy only the numeric token to its canonical E014 position. XI resolves it.
set r0 0
label number_copy
set r7 7400000000000000546
add r7 r0
load8 r1 $r7
set r7 7400000000000000580
add r7 r0
store8 $r7 r1
add r0 1
cmp r0 34
jlt number_copy
load8 r0 7400000000000001603
store8 7400000000000001605 r0
store8 7400000000000001604 r9
store8 7400000000000001600 r8
store8 7400000000000001601 1
store8 7400000000000001602 r11
store8 7400000000000001603 2
store8 7400000000000001606 r10
store8 7400000000000001607 1
store8 7400000000000000032 4
halt
label count_query
cmp r8 0
je clarify
cmp r10 0
je clarify
load8 r0 7700000000000000535
store8 7400000000000001600 r0
store8 7400000000000001601 3
store8 7400000000000001602 r10
store8 7400000000000001603 1
load8 r0 7700000000000000529
store8 7400000000000001604 r0
store8 7400000000000001605 2
store8 7400000000000001606 r8
store8 7400000000000001607 1
store8 7400000000000000032 4
halt
label fact_query
cmp r8 0
je unsupported
cmp r8 13
jlt fact_entity
cmp r8 22
jle unsupported
label fact_entity
cmp r8 12
jle fact_ready
set r7 7400000000000006000
add r7 r8
load8 r0 $r7
cmp r0 1
jne unsupported
label fact_ready
load8 r0 7700000000000000530
store8 7400000000000001600 r0
store8 7400000000000001601 3
store8 7400000000000001602 r9
store8 7400000000000001603 2
store8 7400000000000001604 r8
store8 7400000000000001605 1
store8 7400000000000000032 3
halt
label identity
store8 7700000000000000017 2
halt
label status
store8 7700000000000000017 8
halt
label unsupported
store8 7700000000000000017 3
halt
label clarify
store8 7700000000000000017 4
label done
halt
