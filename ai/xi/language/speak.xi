#!reverse-pc-machine-v1
# E009 first compositional utterances in original XI. ASCII byte stream.
# Decoding these bytes to characters is display I/O, never another language AI.
# S, P, O and (optional) witness ALL come from learned lexical concept IDs.
load8 r12 7100000000000000002
cmp r12 1
je native_language_ready
div r12 0
label native_language_ready
load8 r10 7100000000000000190
cmp r10 0
jne known_response
set r9 63
print r9
halt
label known_response
cmp r10 2
jne affirmative_response
# Prefix denied triple with a syntactic negation, not a learned fact.
set r9 110
print r9
set r9 111
print r9
set r9 58
print r9
set r9 32
print r9
label affirmative_response
set r15 0
label next_utterance_word
cmp r15 3
jne normal_word
# Explanation is selected only if the proof has an actual intermediary.
set r9 32
print r9
set r9 40
print r9
set r9 118
print r9
set r9 105
print r9
set r9 97
print r9
set r9 32
print r9
set r7 7100000000000000194
jmp resolve_word_id
label normal_word
set r7 7100000000000000191
add r7 r15
label resolve_word_id
load8 r8 $r7
cmp r8 1
jge known_concept
set r9 63
print r9
halt
label known_concept
load8 r5 7100000000000000016
set r0 0
label find_spelling
cmp r0 r5
jge missing_spelling
set r4 7100000000000001000
mov r6 r0
mul r6 16
add r4 r6
mov r7 r4
add r7 1
load8 r6 $r7
cmp r6 r8
je spelling_found
add r0 1
jmp find_spelling
label missing_spelling
set r9 63
print r9
halt
label spelling_found
load8 r6 $r4
set r1 0
label emit_ascii
cmp r1 r6
jge word_complete
mov r7 r4
add r7 r1
add r7 2
load8 r9 $r7
print r9
add r1 1
jmp emit_ascii
label word_complete
add r15 1
cmp r15 3
jlt more_words
cmp r15 4
je witness_done
load8 r12 7100000000000000195
cmp r12 2
je next_utterance_word
jmp finish_utterance
label more_words
set r9 32
print r9
jmp next_utterance_word
label witness_done
set r9 41
print r9
label finish_utterance
set r9 46
print r9
halt
