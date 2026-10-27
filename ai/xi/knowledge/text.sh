#!/usr/bin/env bash
# Byte transport only. All tokenization, grounding and decisions execute in XI.
# Usage: text.sh RUNTIME STATE 'dos mas tres' [es|en] [--compact]
set -euo pipefail
R="$(realpath "$1")"
state="$(realpath "$2")"
text="$3"
lang="${4:-es}"
mode=conversation
if [[ "${5:-}" = --compact ]]; then mode=combined; elif [[ -n "${5:-}" ]]; then exit 2; fi
case "$lang" in es) lang_id=1;; en) lang_id=2;; *) exit 2;; esac
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -e "$state.lock" ]]; then echo 'State has an active writer' >&2; exit 1; fi
# Same stable kernel lock as the resident adapter. Never unlink its inode.
exec 9>>"$state.writer"
flock -n 9 || { echo 'State has an active writer' >&2; exit 1; }
tmp=''
cleanup() {
  if [[ -n "$tmp" ]]; then rm -rf -- "$tmp"; fi
}
trap cleanup EXIT
tmp="$(mktemp -d "$(dirname "$state")/.bbyq-text.XXXXXX")"
# Cache only linked SOURCE, never questions, facts or inferred answers. The key
# covers every module in the native route; source edits invalidate it.
cache="$(dirname "$state")/.bbyq-xi-cache"
mkdir -p -m 700 "$cache"
key="$(sha256sum "$root"/*.xi "$root/link.sh" "$root/../dialogue"/*.xi "$root/../stories"/*.xi "$root/../grammar"/*.xi "$root/../conversation"/*.xi "$root/../open"/*.xi "$root/../language/ask.xi" "$root/../language/speak.xi" | sha256sum)"
key="${key%% *}"
compiled="$cache/$mode-$key.xi"
if [[ ! -s "$compiled" ]]; then
  bash "$root/link.sh" "$mode" > "$tmp/compiled.xi"
  mv "$tmp/compiled.xi" "$compiled"
fi
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
  sed '1d' "$compiled"
} > "$tmp/turn.xi"
"$R" run "$tmp/turn.xi" "$state" "$tmp/result.rvp" > "$tmp/output.jsonl" 2> "$tmp/runtime.log" || { cat "$tmp/runtime.log" >&2; exit 1; }
mv "$tmp/result.rvp" "$state"
while read -r byte; do
  printf -v oct '%03o' "$byte"
  printf '%b' "\\$oct"
done < <(sed -n 's/.*"register":"r\(14\|9\)".*"value":\([0-9][0-9]*\).*/\2/p' "$tmp/output.jsonl")
printf '\n'
