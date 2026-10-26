#!/usr/bin/env bash
# Source linker only. No parsing of user text, prediction or model in the host.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
case "${1:-}" in
  query) modules=(read resolve interpret respond) ;;
  teach) modules=(read resolve learn) ;;
  *) echo 'usage: link.sh query|teach' >&2; exit 2 ;;
esac
echo '#!reverse-pc-machine-v1'
for ((i=0; i<${#modules[@]}; i++)); do
  prefix="s${i}_"
  successor=''
  if ((i+1<${#modules[@]})); then successor="s$((i+1))_entry"; fi
  echo "label ${prefix}entry"
  awk -v prefix="$prefix" -v successor="$successor" '
    /^#!/ {next}
    $1=="label" {$2=prefix $2; print; next}
    $1 ~ /^j(mp|e|ne|ge|le|gt|lt)$/ {$2=prefix $2; print; next}
    $1=="halt" {if(successor!="") print "jmp " successor; else print; next}
    {print}
  ' "$root/${modules[$i]}.xi"
done
