#!/usr/bin/env python3
"""Independent native XI check for C05 using original exact C1 tokenizer.

The only writable model is an ephemeral bank created by the original
REVERSE-PC CLI. Frozen C1/U02/U03 checkpoint bytes are SHA-256 compared
before/after. This adds no trained head or new Android artifact.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import random
import tempfile

from integration.audit_u03_c00.profile import ROOT, apk_files, freeze_assets
from integration.unified.common import C1
from integration.sequence2 import build as C1Build
from .native import native_check
from .semantic import analyze, raw_roundtrip, wire_decode, wire_encode


FIXTURES = [
    ("no definas memoria", ""),
    ("define memoria no interferencia", ""),
    ("no quiero que definas memoria, explica interferencia", ""),
    ("Guarda la regla Faro Azul con valor 1 observa Nara con muestra 88113 y resuelve desde 3", ""),
    ("recuerda que mi nave se llama Niña Ámbar", ""),
    ("resuelve Brisa Nueva usando la regla Faro Azul desde 3", ""),
    ("observa Nara con muestra 88114", ""),
    ("lee la regla Faro Azul", ""),
    ("repítelo", "define memoria"),
    ("repítelo", "define memoria y explica interferencia"),
    ("sí, exactamente.", "si alguien es clase cero entonces es alerta"),
    ("si alguien es clase cero entonces es alerta", ""),
    ("repite lo anterior, pero no definas universo", "define energía"),
    ("sin datos no hay respuesta", ""),
    ("pago 000123,4500 y recibo 123.45", ""),
    ("no resuelvas Nara", ""),
    ("  Ámbar 🧠, año 2026. \n", ""),
    ("nunca expliques memoria", ""),
    ("define café y no interferencia", ""),
]


def main():
    protected, old_apks = freeze_assets(), apk_files()
    C1Build.main()  # Original native C1 build, no checkpoint modification.
    cases = []
    rng = random.Random(2026110705)
    names = ("Ñandú", "Ámbar", "Prisma", "Nara", "Brisa", "XI", "Ether", "Oaxaca")
    for topic, previous in FIXTURES:
        cases.append((topic, previous))
    for index in range(48):
        first = names[rng.randrange(len(names))] + " " + str(index + 340)
        second = names[rng.randrange(len(names))] + " " + str(index + 740)
        cases.extend([
            (f"no definas {first}", ""),
            (f"define {first} no {second}", ""),
            (f"observa {first} con muestra {rng.randrange(100000, 999999)}", ""),
            ("repítelo", f"define {first}"),
        ])
    successes = []
    with tempfile.TemporaryDirectory(prefix="bbyq-c05-original-xi-") as temporary:
        path = Path(temporary) / "native-c1.rvp"
        C1.birth(path, 4096)
        with C1.Model(path, ["<pad>"], ["<eos>"]) as native:
            for i, (prompt, previous) in enumerate(cases):
                proof = native_check(native, prompt, previous)
                analysis = analyze(prompt, previous)
                check = wire_decode(wire_encode(analysis))
                if check != analysis or raw_roundtrip(check) != (
                    prompt.encode("utf-8"), previous.encode("utf-8")
                ):
                    raise AssertionError("C05 wire failed exact roundtrip")
                successes.append({
                    "index": i, "tokens": proof["tokens"],
                    "negations": proof["negations"],
                    "native_xi_validated": proof["native_XI_validated"],
                })
            # Verify malformed semantic spans are rejected *inside XI*.
            bad = native.run(
                f"store64 8150000000000900008 257\n"
                "call c05_validate_frame"
            )
            if native.memory(8150000000000900056, 8) != (
                    (4).to_bytes(8, "little", signed=True)):
                raise AssertionError("XI did not reject oversized C05 token span")
    if freeze_assets() != protected or apk_files() != old_apks:
        raise AssertionError("C05 altered an immutable release checkpoint or generated APK")
    report = {
        "passed": True, "native_C1_and_XI_c05_validation": True,
        "count": len(successes),
        "new_native_c05_semantic_probes": len(successes),
        "original_UTF8_and_token_ids_identical": True,
        "invalid_semantic_XI_frame_rejected": True,
        "model_parameters_updated": False,
        "frozen_asset_count": len(protected),
        "frozen_sources_unchanged": True, "apk_built": False,
        "cases": successes,
        "scope": "Native boundaries/transport only. Semantic roles are candidates, not learned parsing accuracy.",
    }
    outfile = ROOT / "build/c05/native-checks.json"
    outfile.parent.mkdir(parents=True, exist_ok=True)
    outfile.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "cases"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
