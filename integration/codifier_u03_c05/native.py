"""Native XI verification of the C05 semantic frame on a disposable C1 bank.

The code runs against the *original* REVERSE-PC XI interpreter and C1 encoder.
No trained release snapshot is touched. Feature scope and byte bounds are
independently checked in XI, while deeper linguistic claims stay host-side
candidates until the C06 learning/evaluation campaign.
"""
from __future__ import annotations

from pathlib import Path
import struct

from integration.unified.common import C1, ROOT
from .semantic import analyze, raw_roundtrip, wire_encode

NATIVE_BASE = 8150000000000900000
PROGRAM = ROOT / "ai/xi/c05/semantic-frame.xi"


def native_check(model: C1.Model, prompt: str, previous: str = "") -> dict:
    frame = analyze(prompt, previous)
    raw, history = raw_roundtrip(frame)
    original = model.prepare(prompt, previous)
    if original["raw"] != raw:
        raise AssertionError("C05 altered original C1 UTF-8 input")
    if model.memory(C1.S["RAW"], len(raw)) != raw:
        raise AssertionError("Native C1 lost original current UTF-8")
    if history and model.memory(C1.S["HRAW"], len(history)) != history:
        raise AssertionError("Native C1 lost original context UTF-8")

    tokens = frame["tokens"]
    if tokens:
        lengths = struct.unpack("<" + "q" * len(tokens),
                                model.memory(C1.S["TL"], 8 * len(tokens)))
        if list(lengths) != [token["length"] for token in tokens]:
            raise AssertionError("C05 native tokenizer byte lengths differ")

    if "label c05_validate_frame" not in model.library:
        model.library += "\n" + PROGRAM.read_text()
    n = frame["negations"]
    wire = wire_encode(frame)
    body = C1.stage64(NATIVE_BASE, [
        len(raw), len(tokens), len(history),
        len(frame["history_tokens"]), len(n),
        len(frame["events"]), len(wire), 0,
    ])
    for i, token in enumerate(tokens):
        body += C1.stage64(NATIVE_BASE + 64 + 24 * i,
                           [token["start"], token["length"], token["id"]])
    for i, marker in enumerate(n):
        scope = marker["scope"]
        bounds = scope["tokens"] if scope else [-1, -1]
        body += C1.stage64(NATIVE_BASE + 10000 + i * 24,
                           [marker["token"], *bounds])
    model.run(body + "call c05_validate_frame")
    result = struct.unpack("<q", model.memory(NATIVE_BASE + 56, 8))[0]
    if result != 1:
        raise AssertionError("XI native C05 semantic boundary rejected the input")
    return {
        "passed": True,
        "native_XI_validated": True,
        "original_C1_native_codec_preserved": True,
        "utf8_bytes": len(raw),
        "history_bytes": len(history),
        "tokens": len(tokens),
        "negations": len(n),
        "frame_bytes": len(wire),
        "checkpoint_saved": False,
    }
