#!/usr/bin/env bash
set -euo pipefail
if (( $# != 3 )); then
  printf '%s\n' 'Uso: check.sh RUNTIME X07_NATIVE NUEVO_DIRECTORIO' >&2
  exit 2
fi
BBYQ_RUNTIME="$(realpath -- "$1")"
BBYQ_PARENT="$(realpath -- "$2")"
BBYQ_OUTPUT="$(realpath -m -- "$3")"
BBYQ_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
test ! -e "$BBYQ_OUTPUT" || { printf '%s\n' 'El destino ya existe.' >&2; exit 2; }
mkdir -p -- "$BBYQ_OUTPUT"
cd -- "$BBYQ_ROOT"
node ai/personal/x08/build.mjs "$BBYQ_RUNTIME" "$BBYQ_PARENT" integration/x08/data "$BBYQ_OUTPUT/native"
node integration/x08/tests/test.mjs "$BBYQ_RUNTIME" "$BBYQ_OUTPUT/native" "$BBYQ_OUTPUT/core"
node integration/x08/tests/codec.test.mjs "$BBYQ_RUNTIME" "$BBYQ_OUTPUT/native" "$BBYQ_OUTPUT/codec"
node integration/x08/tests/capacity.test.mjs "$BBYQ_RUNTIME" "$BBYQ_OUTPUT/native" "$BBYQ_OUTPUT/capacity"
node integration/x08/tests/session.test.mjs "$BBYQ_RUNTIME" "$BBYQ_OUTPUT/native" "$BBYQ_OUTPUT/sessions"
node integration/x08/tests/migration.test.mjs "$BBYQ_RUNTIME" "$BBYQ_OUTPUT/native" "$BBYQ_PARENT" "$BBYQ_OUTPUT/migration"
node integration/x08/tests/regression.test.mjs "$BBYQ_RUNTIME" "$BBYQ_OUTPUT/native" "$BBYQ_OUTPUT/regressions"
