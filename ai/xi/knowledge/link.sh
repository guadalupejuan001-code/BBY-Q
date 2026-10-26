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
  word)
    link_module "$root/read.xi" m1_entry
    link_module "$root/resolve.xi" m2_entry
    link_module "$root/learn-word.xi" finish
    ;;
  query|combined)
    link_module "$root/read.xi" m1_entry
    link_module "$root/resolve.xi" m2_entry
    link_module "$root/parse-question.xi" dispatch
    echo 'label dispatch'
    if [ "$mode" = combined ]; then
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
      link_module "$root/../dialogue/interpret.xi" "m$((serial+1))_entry"
      link_module "$root/../dialogue/respond.xi" cleanup
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
      link_module "$root/../stories/finish.xi" "m$((serial+1))_entry"
      link_module "$root/../dialogue/respond.xi" "m$((serial+1))_entry"
      link_module "$root/../stories/clean.xi" cleanup
    fi
    echo 'label knowledge'
    link_module "$root/rule-check.xi" "m$((serial+1))_entry"
    link_module "$root/ask.xi" "m$((serial+1))_entry"
    link_module "$root/respond.xi" cleanup
    echo 'label cleanup'
    link_module "$root/clean.xi" finish
    ;;
  *) echo 'unknown link mode' >&2; exit 2;;
esac
echo 'label finish'
echo halt
