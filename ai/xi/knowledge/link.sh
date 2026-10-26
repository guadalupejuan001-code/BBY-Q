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
      echo 'load8 r0 7400000000000000013'
      echo 'cmp r0 0'
      echo 'jne knowledge'
      echo 'load8 r0 7400000000000000040'
      echo 'cmp r0 0'
      echo 'jne knowledge'
      link_module "$root/arithmetic-intake.xi" m4_entry
      link_module "$root/../dialogue/read.xi" m5_entry
      link_module "$root/../dialogue/resolve.xi" m6_entry
      link_module "$root/../dialogue/interpret.xi" m7_entry
      link_module "$root/../dialogue/respond.xi" cleanup
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
