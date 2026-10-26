#!/usr/bin/env bash
# Byte transport only. All tokenization, grounding and decisions execute in XI.
# Usage: text.sh RUNTIME STATE 'dos mas tres' [es|en]
set -euo pipefail
R="$(realpath "$1")"
state="$(realpath "$2")"
text="$3"
lang="${4:-es}"
case "$lang" in es) lang_id=1;; en) lang_id=2;; *) exit 2;; esac
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir "$state.lock" 2>/dev/null || { echo 'State has an active writer' >&2; exit 1; }
tmp="$(mktemp -d "$(dirname "$state")/.bbyq-text.XXXXXX")"
trap 'rm -rf "$tmp"; rmdir "$state.lock"' EXIT
length="$(printf %s "$text" | wc -c)"
if ((length>255)); then echo 'Input exceeds 255 bytes' >&2; exit 2; fi
B=7400000000000000000
{
  echo '#!reverse-pc-machine-v1'
  printf 'store8 %s 1\nstore8 %s %s\nstore8 %s %s\n' "$((B+16))" "$((B+17))" "$length" "$((B+3))" "$lang_id"
  i=0
  for byte in $(printf %s "$text" | od -An -tu1); do
    printf 'store8 %s %s\n' "$((B+128+i))" "$byte"
    i=$((i+1))
  done
  bash "$root/link.sh" combined | sed '1d'
} > "$tmp/turn.xi"
"$R" run "$tmp/turn.xi" "$state" "$tmp/result.rvp" > "$tmp/output.jsonl" 2> "$tmp/runtime.log" || { cat "$tmp/runtime.log" >&2; exit 1; }
mv "$tmp/result.rvp" "$state"
while read -r byte; do
  printf -v oct '%03o' "$byte"
  printf '%b' "\\$oct"
done < <(sed -n 's/.*"register":"r\(14\|9\)".*"value":\([0-9][0-9]*\).*/\2/p' "$tmp/output.jsonl")
printf '\n'
