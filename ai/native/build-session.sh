#!/usr/bin/env bash
set -euo pipefail
runtime="$(realpath "$1")"
build="$2"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
test "$(git -C "$runtime" rev-parse HEAD)" = 6d4de14a2dfbce4b8a7f1cb50e29d11b9073fe98
test "$(git -C "$runtime/deps/mundo-x" rev-parse HEAD)" = e2778d962af22f6f1a0794058dd4685fc2573966
mkdir -p "$build"
build="$(realpath "$build")"
python3 "$runtime/scripts/prepare-ether-compat.py" "$runtime/deps/mundo-x" "$build/ether-compat"
g++ -std=c++17 -O2 -pthread -DREVERSE_PC_HAVE_BOUNDED_PRODUCT_IMPORT=1 \
  -I"$build/ether-compat" -I"$runtime/src" -I"$runtime/deps/mundo-x/native/include" \
  "$root/session.cpp" -o "$build/bbyq_session"
