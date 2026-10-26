#!/usr/bin/env bash
# Source linkage only. The native program decides whether input is a factual
# question or a continuation of the preexisting E011 arithmetic conversation.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mode="${1:-query}"
echo '#!reverse-pc-machine-v1'
serial=0
link_module() {
  local file="$1" exit_label="$2" prefix="m${serial}_"
  echo "label ${prefix}entry"
  awk -v prefix="$prefix" -v exit_label="$exit_label" '
    /^#!/ {next}
    $1=="label" {$2=prefix $2; print; next}
    $1 ~ /^j(mp|e|ne|ge|le|gt|lt)$/ {$2=prefix $2; print; next}
    $1=="halt" {print "jmp " exit_label; next}
    {print}
  ' "$file"
  serial=$((serial+1))
}
case "$mode" in
  utterance|order|nominal|config|role)
    case "$mode" in
      utterance) learner=learn-utterance;; order) learner=learn-order;;
      nominal) learner=learn-nominal;; config) learner=learn-config;;
      role) learner=learn-role;;
    esac
    if [ "$mode" = order ] || [ "$mode" = nominal ]; then
      link_module "$root/read.xi" "m$((serial+1))_entry"
      link_module "$root/resolve.xi" "m$((serial+1))_entry"
    fi
    link_module "$root/../conversation/$learner.xi" "m$((serial+1))_entry"
    link_module "$root/../conversation/learn-clean.xi" finish
    ;;
  pattern)
    link_module "$root/read.xi" m1_entry
    link_module "$root/resolve.xi" m2_entry
    link_module "$root/../grammar/learn-pattern.xi" finish
    ;;
  word)
    link_module "$root/read.xi" m1_entry
    link_module "$root/resolve.xi" m2_entry
    link_module "$root/learn-word.xi" finish
    ;;
  query|combined|conversation)
    if [ "$mode" = conversation ]; then
      link_module "$root/../conversation/start.xi" "m$((serial+1))_entry"
    fi
    link_module "$root/read.xi" "m$((serial+1))_entry"
    link_module "$root/resolve.xi" "m$((serial+1))_entry"
    if [ "$mode" = conversation ]; then
      link_module "$root/../conversation/intake.xi" conversation_intake
      echo 'label conversation_intake'
      echo 'load8 r0 7700000000000000017'
      echo 'cmp r0 0'
      echo 'jne conversation_shortcut'
    fi
    if [ "$mode" != query ]; then
      link_module "$root/../grammar/match.xi" "m$((serial+1))_entry"
    fi
    link_module "$root/parse-question.xi" dispatch
    echo 'label dispatch'
    if [ "$mode" != query ]; then
      link_module "$root/../stories/detect.xi" choose_story
      echo 'label choose_story'
      echo 'load8 r0 7500000000000000016'
      echo 'cmp r0 1'
      echo 'je story'
      link_module "$root/legacy-check.xi" choose_route
      echo 'label choose_route'
      echo 'load8 r0 7400000000000000013'
      echo 'cmp r0 0'
      echo 'je check_legacy'
      echo 'load8 r0 7400000000000000009'
      echo 'cmp r0 0'
      echo 'je knowledge'
      echo 'label check_legacy'
      echo 'load8 r0 7400000000000000046'
      echo 'cmp r0 1'
      echo 'je legacy'
      echo 'load8 r0 7400000000000000013'
      echo 'cmp r0 0'
      echo 'jne knowledge'
      echo 'load8 r0 7400000000000000040'
      echo 'cmp r0 0'
      echo 'jne knowledge'
      link_module "$root/arithmetic-intake.xi" "m$((serial+1))_entry"
      link_module "$root/../dialogue/read.xi" "m$((serial+1))_entry"
      link_module "$root/../dialogue/resolve.xi" "m$((serial+1))_entry"
      link_module "$root/../dialogue/interpret.xi" arithmetic_reply
      echo 'label arithmetic_reply'
      if [ "$mode" = conversation ]; then
        echo 'load8 r0 7700000000000000016'
        echo 'cmp r0 1'
        echo 'je conversation_arithmetic'
      fi
      link_module "$root/../dialogue/respond.xi" cleanup
      if [ "$mode" = conversation ]; then
        echo 'label conversation_arithmetic'
        echo 'store8 7700000000000000025 3'
        link_module "$root/../conversation/prepare.xi" conversation_render
      fi
      echo 'label legacy'
      link_module "$root/legacy-intake.xi" "m$((serial+1))_entry"
      link_module "$root/../language/ask.xi" "m$((serial+1))_entry"
      link_module "$root/../language/speak.xi" "m$((serial+1))_entry"
      link_module "$root/legacy-restore.xi" cleanup
      echo 'label story'
      link_module "$root/../stories/begin.xi" story_parse
      echo 'label story_parse'
      link_module "$root/../stories/parse.xi" story_parsed
      echo 'label story_parsed'
      echo 'load8 r0 7500000000000000017'
      echo 'cmp r0 1'
      echo 'jne story_finish'
      link_module "$root/../stories/number-intake.xi" "m$((serial+1))_entry"
      link_module "$root/../dialogue/resolve.xi" "m$((serial+1))_entry"
      link_module "$root/../stories/arithmetic-intake.xi" story_number_ready
      echo 'label story_number_ready'
      echo 'load8 r0 7500000000000000017'
      echo 'cmp r0 1'
      echo 'jne story_finish'
      link_module "$root/../dialogue/interpret.xi" "m$((serial+1))_entry"
      link_module "$root/../stories/apply.xi" story_parse
      echo 'label story_finish'
      link_module "$root/../stories/finish.xi" story_reply
      echo 'label story_reply'
      if [ "$mode" = conversation ]; then
        echo 'load8 r0 7700000000000000016'
        echo 'cmp r0 1'
        echo 'je conversation_story'
      fi
      link_module "$root/../dialogue/respond.xi" story_clean
      echo 'label story_clean'
      link_module "$root/../stories/clean.xi" cleanup
      if [ "$mode" = conversation ]; then
        echo 'label conversation_story'
        echo 'store8 7700000000000000025 1'
        link_module "$root/../conversation/prepare.xi" conversation_render
      fi
    fi
    echo 'label knowledge'
    link_module "$root/rule-check.xi" "m$((serial+1))_entry"
    link_module "$root/ask.xi" knowledge_reply
    echo 'label knowledge_reply'
    if [ "$mode" = conversation ]; then
      echo 'load8 r0 7700000000000000016'
      echo 'cmp r0 1'
      echo 'je conversation_fact'
    fi
    link_module "$root/respond.xi" cleanup
    if [ "$mode" = conversation ]; then
      echo 'label conversation_fact'
      echo 'store8 7700000000000000025 2'
      link_module "$root/../conversation/prepare.xi" conversation_render
      echo 'label conversation_shortcut'
      echo 'store8 7700000000000000025 0'
      link_module "$root/../conversation/prepare.xi" conversation_render
      echo 'label conversation_render'
      echo 'load8 r0 7700000000000000018'
      echo 'cmp r0 2'
      echo 'je conversation_count'
      echo 'cmp r0 3'
      echo 'je conversation_number'
      echo 'cmp r0 4'
      echo 'je conversation_fact_start'
      link_module "$root/../conversation/utterance.xi" "m$((serial+1))_entry"
      link_module "$root/../conversation/emit.xi" conversation_done
      echo 'label conversation_count'
      link_module "$root/../conversation/count-next.xi" conversation_count_dispatch
      echo 'label conversation_count_dispatch'
      echo 'load8 r0 7700000000000000035'
      echo 'cmp r0 1'
      echo 'je conversation_count_name'
      echo 'cmp r0 2'
      echo 'je conversation_count_direct'
      echo 'cmp r0 3'
      echo 'je conversation_count_decimal'
      echo 'jmp conversation_done'
      echo 'label conversation_count_name'
      link_module "$root/../conversation/name.xi" conversation_count_direct
      echo 'label conversation_count_direct'
      link_module "$root/../conversation/emit.xi" conversation_count
      echo 'label conversation_count_decimal'
      link_module "$root/../dialogue/respond.xi" conversation_count
      echo 'label conversation_number'
      link_module "$root/../conversation/utterance.xi" "m$((serial+1))_entry"
      link_module "$root/../conversation/emit.xi" conversation_number_space
      echo 'label conversation_number_space'
      echo 'set r14 32'
      echo 'print r14'
      link_module "$root/../dialogue/respond.xi" conversation_number_done
      echo 'label conversation_number_done'
      echo 'set r14 46'
      echo 'print r14'
      echo 'jmp conversation_done'
      echo 'label conversation_fact_start'
      echo 'load8 r0 7400000000000000008'
      echo 'cmp r0 2'
      echo 'jne conversation_fact_next'
      echo 'store8 7700000000000000019 7'
      link_module "$root/../conversation/utterance.xi" "m$((serial+1))_entry"
      link_module "$root/../conversation/emit.xi" conversation_fact_prefix_done
      echo 'label conversation_fact_prefix_done'
      echo 'set r14 32'
      echo 'print r14'
      echo 'store8 7700000000000000039 0'
      echo 'store8 7700000000000000038 0'
      echo 'label conversation_fact_next'
      link_module "$root/../conversation/fact-next.xi" conversation_fact_dispatch
      echo 'label conversation_fact_dispatch'
      echo 'load8 r0 7700000000000000035'
      echo 'cmp r0 1'
      echo 'je conversation_fact_name'
      echo 'cmp r0 2'
      echo 'je conversation_fact_direct'
      echo 'jmp conversation_done'
      echo 'label conversation_fact_name'
      link_module "$root/../conversation/name.xi" conversation_fact_direct
      echo 'label conversation_fact_direct'
      link_module "$root/../conversation/emit.xi" conversation_fact_next
      echo 'label conversation_done'
      echo 'load8 r0 7700000000000000025'
      echo 'cmp r0 1'
      echo 'je story_clean'
      echo 'jmp cleanup'
    fi
    echo 'label cleanup'
    if [ "$mode" = conversation ]; then
      link_module "$root/clean.xi" "m$((serial+1))_entry"
      link_module "$root/../conversation/clean.xi" finish
    else
      link_module "$root/clean.xi" finish
    fi
    ;;
  *) echo 'unknown link mode' >&2; exit 2;;
esac
echo 'label finish'
echo halt
