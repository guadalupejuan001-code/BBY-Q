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
  rephrase-teach)
    link_module "$root/read.xi" "m$((serial+1))_entry"
    link_module "$root/resolve.xi" "m$((serial+1))_entry"
    link_module "$root/../open/resolve.xi" "m$((serial+1))_entry"
    link_module "$root/../rephrase/induce.xi" "m$((serial+1))_entry"
    link_module "$root/../rephrase/target.xi" "m$((serial+1))_entry"
    link_module "$root/read.xi" "m$((serial+1))_entry"
    link_module "$root/resolve.xi" "m$((serial+1))_entry"
    link_module "$root/../open/resolve.xi" "m$((serial+1))_entry"
    link_module "$root/../rephrase/induce.xi" "m$((serial+1))_entry"
    link_module "$root/../rephrase/finish-teach.xi" "m$((serial+1))_entry"
    link_module "$root/clean.xi" "m$((serial+1))_entry"
    link_module "$root/../open/clean.xi" "m$((serial+1))_entry"
    link_module "$root/../rephrase/clean.xi" finish
    ;;
  rephrase-seal|rephrase-audit)
    link_module "$root/../rephrase/guard.xi" "m$((serial+1))_entry"
    if [ "$mode" = rephrase-seal ]; then
      link_module "$root/../rephrase/seal.xi" finish
    else
      link_module "$root/../rephrase/audit.xi" finish
    fi
    ;;
  open-word|open-pattern|lingua-pattern|lingua-cue|open-utterance|open-calibrate|open-base|open-style)
    if [ "$mode" = open-word ] || [ "$mode" = open-pattern ] || [ "$mode" = lingua-pattern ] || [ "$mode" = lingua-cue ] || [ "$mode" = open-base ]; then
      link_module "$root/read.xi" "m$((serial+1))_entry"
      link_module "$root/resolve.xi" "m$((serial+1))_entry"
      link_module "$root/../open/resolve.xi" "m$((serial+1))_entry"
    fi
    case "$mode" in
      open-word) link_module "$root/../open/intern.xi" open_learn_cleanup;;
      lingua-cue) link_module "$root/../lingua/learn-cue.xi" open_learn_cleanup;;
      lingua-pattern) link_module "$root/../lingua/learn-pattern.xi" open_learn_cleanup;;
      open-pattern) link_module "$root/../open/learn-pattern.xi" open_learn_cleanup;;
      open-base) link_module "$root/../open/learn-base.xi" open_learn_cleanup;;
      open-style) link_module "$root/../open/learn-style.xi" open_learn_cleanup;;
      open-utterance) link_module "$root/../open/learn-utterance.xi" open_learn_cleanup;;
      open-calibrate)
        link_module "$root/../open/calibrate-start.xi" learn_witness
        echo 'label learn_witness'
        link_module "$root/../open/witness-next.xi" learn_witness_ready
        echo 'label learn_witness_ready'
        echo 'load8 r0 7800000000000000247'
        echo 'cmp r0 1'
        echo 'jne learn_rule'
        link_module "$root/../open/edge.xi" "m$((serial+1))_entry"
        link_module "$root/../open/witness-accept.xi" learn_witness
        echo 'label learn_rule'
        link_module "$root/../open/learn-rule.xi" open_learn_cleanup
        ;;
    esac
    echo 'label open_learn_cleanup'
    link_module "$root/clean.xi" "m$((serial+1))_entry"
    link_module "$root/../open/clean.xi" finish
    ;;
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
    if [ "$mode" != query ]; then
      if [ "$mode" = conversation ]; then echo 'set r13 1'; else echo 'set r13 2'; fi
      link_module "$root/../open/start.xi" "m$((serial+1))_entry"
    fi
    if [ "$mode" = conversation ]; then
      link_module "$root/../conversation/start.xi" "m$((serial+1))_entry"
    fi
    link_module "$root/read.xi" "m$((serial+1))_entry"
    link_module "$root/resolve.xi" "m$((serial+1))_entry"
    if [ "$mode" != query ]; then
      link_module "$root/../open/resolve.xi" "m$((serial+1))_entry"
      rephrase_serial="$serial"
      link_module "$root/../rephrase/normalize.xi" rephrase_apply_check
      echo 'label rephrase_apply_check'
      echo 'load8 r0 8100000000000000003'
      echo 'cmp r0 1'
      echo 'jne rephrase_match'
      echo 'load8 r0 8100000000000000080'
      echo 'cmp r0 0'
      echo 'je rephrase_match'
      link_module "$root/../rephrase/apply.xi" rephrase_loop
      echo 'label rephrase_loop'
      echo 'load8 r0 8100000000000000026'
      echo 'cmp r0 1'
      echo 'je rephrase_match'
      echo "jmp m${rephrase_serial}_choose"
      echo 'label rephrase_match'
      link_module "$root/../open/match.xi" "m$((serial+1))_entry"
      link_module "$root/../lingua/clause.xi" "m$((serial+1))_entry"
      link_module "$root/../rephrase/accept.xi" rephrase_accepted
      echo 'label rephrase_accepted'
      echo 'load8 r0 8100000000000000025'
      echo 'cmp r0 1'
      echo 'jne rephrase_prepared'
      echo 'store8 8100000000000000025 0'
      echo 'jmp rephrase_match'
      echo 'label rephrase_prepared'
      link_module "$root/../open/prepare.xi" open_dispatch
      echo 'label open_dispatch'
      echo 'load8 r0 7800000000000000067'
      echo 'cmp r0 1'
      echo 'je open_teach_check'
      echo 'cmp r0 2'
      echo 'je open_query'
      echo 'cmp r0 3'
      echo 'je open_alias'
      echo 'cmp r0 4'
      echo 'je open_mutate'
      echo 'cmp r0 6'
      echo 'je lingua_resume'
      echo 'cmp r0 5'
      echo 'je open_reply'
      echo 'label open_fallback'
    fi
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
    if [ "$mode" != query ]; then
      echo 'label open_teach_check'
      link_module "$root/../open/teach-check.xi" open_teach_checked
      echo 'label open_teach_checked'
      echo 'load8 r0 7800000000000000087'
      echo 'cmp r0 0'
      echo 'je open_reply'
      echo 'label open_intern'
      link_module "$root/../open/intern-next.xi" open_intern_ready
      echo 'label open_intern_ready'
      echo 'load8 r0 7800000000000000087'
      echo 'cmp r0 0'
      echo 'je open_mutate'
      link_module "$root/../open/intern.xi" "m$((serial+1))_entry"
      link_module "$root/../open/intern-accept.xi" "m$((serial+1))_entry"
      link_module "$root/../open/resolve.xi" open_intern
      echo 'label open_mutate'
      link_module "$root/../open/mutate.xi" open_reply
      echo 'label open_alias'
      link_module "$root/../open/alias-prepare.xi" open_alias_ready
      echo 'label open_alias_ready'
      echo 'load8 r0 7800000000000000087'
      echo 'cmp r0 0'
      echo 'je open_reply'
      link_module "$root/../open/intern.xi" open_alias_done
      echo 'label open_alias_done'
      echo 'store8 7800000000000000080 6'
      echo 'jmp open_reply'
      echo 'label lingua_resume'
      link_module "$root/../lingua/resume.xi" lingua_resumed
      echo 'label lingua_resumed'
      echo 'load8 r0 7800000000000000067'
      echo 'cmp r0 2'
      echo 'je open_query'
      echo 'jmp open_reply'
      echo 'label open_query'
      link_module "$root/../open/query-start.xi" open_query_ready
      echo 'label open_query_ready'
      echo 'load8 r0 7800000000000000067'
      echo 'cmp r0 0'
      echo 'je open_fallback'
      echo 'load8 r0 7800000000000000087'
      echo 'cmp r0 0'
      echo 'je open_reply'
      echo 'cmp r0 1'
      echo 'je open_property'
      link_module "$root/../open/edge.xi" "m$((serial+1))_entry"
      link_module "$root/../open/direct-accept.xi" open_direct_ready
      echo 'label open_direct_ready'
      echo 'load8 r0 7800000000000000087'
      echo 'cmp r0 1'
      echo 'je open_reply'
      link_module "$root/../open/rule-start.xi" open_rule_ready
      echo 'label open_rule_ready'
      echo 'load8 r0 7800000000000000087'
      echo 'cmp r0 0'
      echo 'je open_model_start'
      link_module "$root/rule-check.xi" open_model_start
      echo 'label open_model_start'
      link_module "$root/../open/model-start.xi" open_model_route
      echo 'label open_model_route'
      echo 'load8 r0 7800000000000000255'
      echo 'cmp r0 0'
      echo 'je open_bfs_start'
      echo 'label open_model_next'
      link_module "$root/../open/model-next.xi" open_model_next_ready
      echo 'label open_model_next_ready'
      echo 'load8 r0 7800000000000000255'
      echo 'cmp r0 0'
      echo 'je open_bfs_start'
      echo 'label open_witness'
      link_module "$root/../open/witness-next.xi" open_witness_ready
      echo 'label open_witness_ready'
      echo 'load8 r0 7800000000000000247'
      echo 'cmp r0 0'
      echo 'je open_model_accept'
      link_module "$root/../open/edge.xi" "m$((serial+1))_entry"
      link_module "$root/../open/witness-accept.xi" open_witness
      echo 'label open_model_accept'
      link_module "$root/../open/model-accept.xi" open_model_next
      echo 'label open_bfs_start'
      link_module "$root/../open/bfs-start.xi" open_bfs_ready
      echo 'label open_bfs_ready'
      echo 'load8 r0 7800000000000000087'
      echo 'cmp r0 0'
      echo 'je open_reply'
      echo 'label open_bfs_node'
      link_module "$root/../open/bfs-node.xi" open_bfs_node_ready
      echo 'label open_bfs_node_ready'
      echo 'load8 r0 7800000000000000233'
      echo 'cmp r0 1'
      echo 'je open_bfs_complete'
      echo 'load8 r0 7800000000000000232'
      echo 'cmp r0 0'
      echo 'je open_bfs_scan'
      link_module "$root/../open/edge.xi" "m$((serial+1))_entry"
      link_module "$root/../open/bfs-inherit.xi" open_bfs_check
      echo 'label open_bfs_check'
      echo 'load8 r0 7800000000000000234'
      echo 'cmp r0 4'
      echo 'je open_property_path'
      echo 'cmp r0 1'
      echo 'je open_proof'
      echo 'cmp r0 2'
      echo 'je open_bfs_advance'
      echo 'cmp r0 3'
      echo 'je open_reply'
      echo 'label open_bfs_scan'
      link_module "$root/../open/candidate.xi" open_bfs_candidate
      echo 'label open_bfs_candidate'
      echo 'load8 r0 7800000000000000231'
      echo 'cmp r0 0'
      echo 'je open_bfs_advance'
      link_module "$root/../open/bfs-select.xi" open_bfs_selected
      echo 'label open_bfs_selected'
      echo 'load8 r0 7800000000000000087'
      echo 'cmp r0 0'
      echo 'je open_bfs_scan'
      link_module "$root/../open/edge.xi" open_bfs_edge_ready
      echo 'label open_bfs_edge_ready'
      echo 'load8 r0 7800000000000000087'
      echo 'cmp r0 2'
      echo 'jne open_bfs_traverse'
      echo 'load8 r0 7800000000000000208'
      echo 'cmp r0 1'
      echo 'je open_property_path'
      echo 'cmp r0 3'
      echo 'jne open_bfs_scan'
      echo 'store8 7800000000000000080 4'
      echo 'jmp open_reply'
      echo 'label open_bfs_traverse'
      link_module "$root/../open/bfs-accept.xi" open_bfs_check
      echo 'label open_property_path'
      link_module "$root/../open/property-path-next.xi" "m$((serial+1))_entry"
      link_module "$root/../open/edge.xi" "m$((serial+1))_entry"
      link_module "$root/../open/property-path-accept.xi" open_property_path_ready
      echo 'label open_property_path_ready'
      echo 'load8 r0 7800000000000000137'
      echo 'cmp r0 0'
      echo 'je open_property_path'
      echo 'cmp r0 2'
      echo 'je open_bfs_scan'
      echo 'cmp r0 3'
      echo 'je open_reply'
      link_module "$root/../open/property-derived.xi" open_property_derived_ready
      echo 'label open_property_derived_ready'
      echo 'load8 r0 7800000000000000080'
      echo 'cmp r0 9'
      echo 'je open_reply'
      echo 'jmp open_bfs_scan'
      echo 'label open_bfs_advance'
      echo 'load8 r0 7800000000000000122'
      echo 'add r0 1'
      echo 'store8 7800000000000000122 r0'
      echo 'jmp open_bfs_node'
      echo 'label open_bfs_complete'
      echo 'load8 r0 7800000000000000090'
      echo 'cmp r0 1'
      echo 'jne open_reply'
      echo 'load8 r0 7800000000000000082'
      echo 'cmp r0 1'
      echo 'jne open_reply'
      echo 'load8 r0 7800000000000000136'
      echo 'cmp r0 1'
      echo 'jne open_reply'
      echo 'load8 r0 7800000000000000130'
      echo 'store8 7800000000000000124 r0'
      echo 'load8 r0 7800000000000000131'
      echo 'store8 7800000000000000235 r0'
      echo 'label open_proof'
      link_module "$root/../open/proof.xi" open_reply
      echo 'label open_property'
      link_module "$root/../open/candidate.xi" open_property_candidate
      echo 'label open_property_candidate'
      echo 'load8 r0 7800000000000000231'
      echo 'cmp r0 0'
      echo 'je open_property_reasoning'
      link_module "$root/../open/property-select.xi" open_property_selected
      echo 'label open_property_selected'
      echo 'load8 r0 7800000000000000087'
      echo 'cmp r0 0'
      echo 'je open_property'
      link_module "$root/../open/edge.xi" "m$((serial+1))_entry"
      link_module "$root/../open/property-accept.xi" open_property_accepted
      echo 'label open_property_accepted'
      echo 'load8 r0 7800000000000000080'
      echo 'cmp r0 4'
      echo 'je open_reply'
      echo 'cmp r0 9'
      echo 'je open_reply'
      echo 'jmp open_property'
      echo 'label open_property_reasoning'
      link_module "$root/../open/rule-start.xi" open_rule_ready
      echo 'label open_reply'
      link_module "$root/../open/reply-start.xi" open_reply_route
      echo 'label open_reply_route'
      echo 'load8 r0 7800000000000000302'
      echo 'cmp r0 0'
      echo 'je cleanup'
      echo 'cmp r0 1'
      echo 'je open_body'
      echo 'load8 r0 7800000000000000304'
      link_module "$root/../open/utterance.xi" "m$((serial+1))_entry"
      link_module "$root/../conversation/emit.xi" open_prefix_done
      echo 'label open_prefix_done'
      echo 'load8 r0 7800000000000000080'
      echo 'cmp r0 2'
      echo 'jgt cleanup'
      echo 'load8 r0 7800000000000000138'
      echo 'cmp r0 2'
      echo 'jne open_prefix_body'
      echo 'set r0 14'
      link_module "$root/../open/utterance.xi" "m$((serial+1))_entry"
      link_module "$root/../conversation/emit.xi" open_prefix_body
      echo 'label open_prefix_body'
      echo 'store8 7700000000000000038 1'
      echo 'label open_body'
      link_module "$root/../open/body-next.xi" open_body_dispatch
      echo 'label open_body_dispatch'
      echo 'load8 r0 7800000000000000302'
      echo 'cmp r0 0'
      echo 'je cleanup'
      echo 'cmp r0 1'
      echo 'je open_body_name'
      echo 'cmp r0 2'
      echo 'je open_body_emit'
      echo 'load8 r0 7800000000000000304'
      link_module "$root/../open/utterance.xi" open_body_emit
      echo 'label open_body_name'
      link_module "$root/../open/name.xi" open_name_route
      echo 'label open_name_route'
      echo 'load8 r0 7800000000000000302'
      echo 'cmp r0 2'
      echo 'je open_body_emit'
      link_module "$root/../conversation/name.xi" open_body_emit
      echo 'label open_body_emit'
      link_module "$root/../conversation/emit.xi" open_body
    fi
    echo 'label cleanup'
    if [ "$mode" = conversation ]; then
      link_module "$root/clean.xi" "m$((serial+1))_entry"
      link_module "$root/../conversation/clean.xi" open_final_cleanup
    else
      link_module "$root/clean.xi" open_final_cleanup
    fi
    echo 'label open_final_cleanup'
    if [ "$mode" != query ]; then
      echo 'load8 r0 7800000000000000002'
      echo 'cmp r0 1'
      echo 'jne finish'
      link_module "$root/../conversation/clean.xi" "m$((serial+1))_entry"
      link_module "$root/../open/clean.xi" "m$((serial+1))_entry"
      link_module "$root/../lingua/remember.xi" "m$((serial+1))_entry"
      link_module "$root/../rephrase/clean.xi" finish
    else
      echo 'jmp finish'
    fi
    ;;
  *) echo 'unknown link mode' >&2; exit 2;;
esac
echo 'label finish'
echo halt
