"""C05 lossless semantic sidecar for the original C1 native codifier.

The original C1 Codec tokenization, dictionary and XI model remain authoritative.
This module NEVER replaces the C1 training head, predicts intent, changes bank
weights, or expands frozen ABI. It adds conservative, typed, span-grounded
annotations that C06 can later *learn* to consume.
"""
from __future__ import annotations

import base64
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import re
import struct
from typing import Any

from integration.unified.common import C1

SCHEMA = "BBYQ-U03-C05-semantic-v1"
MAGIC = b"C05SEM1\0"
MAX_WIRE = 512 * 1024
CLAUSE_END = {".", ";", "!", "?", "¡", "¿"}
CONNECTORS = {"y", "pero", "aunque", "luego", "después", "despues"}
NEGATION = {"no", "nunca", "jamás", "jamas", "sin"}
ACTION = {
    "define": "define", "definas": "define", "definir": "define",
    "explica": "explain", "expliques": "explain", "explicar": "explain",
    "guarda": "store", "guardar": "store",
    "recuerda": "remember", "recordar": "remember", "recuerdes": "remember",
    "corrige": "correct", "corregir": "correct",
    "lee": "read", "leer": "read", "recupera": "read",
    "observa": "observe", "observar": "observe", "clasifica": "classify",
    "resuelve": "solve", "resuelvas": "solve", "resolver": "solve",
    "decide": "decide", "decidas": "decide", "calcula": "calculate",
    "calcular": "calculate", "aprende": "learn", "aprender": "learn",
    "repite": "repeat", "repítelo": "repeat", "repitelo": "repeat",
    "cuéntalo": "repeat", "cuentalo": "repeat",
    "muestra": "show", "muéstrame": "show", "muestrame": "show",
    "respondas": "respond", "responde": "respond",
}
REFERENCES = {
    "esto", "eso", "aquello", "él", "ella", "ellos", "ellas",
    "este", "ese", "esa", "aquel", "aquella", "lo", "la",
    "repítelo", "repitelo", "cuéntalo", "cuentalo", "dímelo", "dimelo",
}
NUMBER = re.compile(r"[0-9]+(?:[.,][0-9]+)?\Z")
SEPARATORS = {",", ".", ";", "!", "?", "¿", "¡"}
SOFT = {"la", "el", "las", "los", "un", "una", "que", "de", "a"}
OBJECT_BOUNDARY = {"con", "desde", "hasta", "usando", "para", "entonces", "si"}
OWNER = {"mi": "speaker", "mis": "speaker", "tu": "addressee", "tus": "addressee",
         "su": "unspecified", "sus": "unspecified"}


def _json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def _tokens(text: str, codec: C1.Codec, limit: int) -> list[dict[str, Any]]:
    if not isinstance(text, str):
        raise ValueError("C05 accepts only UTF-8 text")
    if len(text.encode("utf-8")) > C1.LIMITS["raw_bytes"]:
        raise ValueError("C05 cannot exceed original C1 byte capacity")
    # The native encoder uses the same regex, byte offsets and dictionary.
    matches = list(C1.TOKEN.finditer(text))
    if len(matches) > limit:
        raise ValueError("C05 cannot exceed native C1 token capacity")
    encoded = codec.text(text)
    raw = encoded["raw"]
    tokens = []
    for index, row in enumerate(encoded["tokens"]):
        piece = raw[row["start"]:row["start"] + row["length"]].decode("utf-8")
        tokens.append({
            "i": index, "id": row["id"], "key": row["key"], "raw": piece,
            "start": row["start"], "length": row["length"],
            "kind": ("number" if NUMBER.fullmatch(row["key"]) else
                     "punctuation" if row["key"] in SEPARATORS else "word"),
        })
    return tokens


def _span(tokens: list[dict], start: int, end: int) -> dict[str, Any] | None:
    if not 0 <= start < end <= len(tokens):
        return None
    return {
        "tokens": [start, end],
        "bytes": [tokens[start]["start"],
                  tokens[end - 1]["start"] + tokens[end - 1]["length"]],
    }


def _clause_end(keys: list[str], start: int) -> int:
    for i in range(start, len(keys)):
        if keys[i] in CLAUSE_END:
            return i
        if i > start and keys[i] in CONNECTORS and i + 1 < len(keys) and (
                keys[i + 1] in ACTION or keys[i + 1] in NEGATION):
            return i
    return len(keys)


def _negations(tokens: list[dict]) -> list[dict]:
    keys = [t["key"] for t in tokens]
    result = []
    for i, key in enumerate(keys):
        if key not in NEGATION:
            continue
        end = _clause_end(keys, i + 1)
        next_actions = [j for j in range(i + 1, min(end, i + 6))
                        if keys[j] in ACTION]
        if key == "sin":
            kind = "absence"
            scope = _span(tokens, i + 1, end)
            target = None
        elif next_actions:
            target = next_actions[0]
            kind = "prohibition" if key in {"no", "nunca", "jamás", "jamas"} else "negated_action"
            scope = _span(tokens, target, end)
        elif i > 0 and any(k in ACTION for k in keys[max(0, i - 9):i]):
            kind = "contrast_exclusion"
            scope = _span(tokens, i + 1, end)
            target = None
        else:
            kind = "unresolved"
            scope = _span(tokens, i + 1, end)
            target = None
        result.append({
            "operator": key, "token": i, "kind": kind,
            "scope": scope, "action_token": target,
        })
    return result


def _role(tokens: list[dict], name: str, start: int, end: int) -> dict | None:
    span = _span(tokens, start, end)
    return {"role": name, "span": span} if span else None


def _events(tokens: list[dict], negations: list[dict]) -> list[dict]:
    keys = [t["key"] for t in tokens]
    action_indices = [i for i, k in enumerate(keys) if k in ACTION]
    events = []
    for number, i in enumerate(action_indices):
        end = action_indices[number + 1] if number + 1 < len(action_indices) else len(keys)
        for j in range(i + 1, end):
            if keys[j] in CLAUSE_END or (
                    keys[j] in CONNECTORS and j + 1 < end and
                    keys[j + 1] in ACTION):
                end = j
                break
        verb = ACTION[keys[i]]
        roles: list[dict] = []
        # The C05 scope is conservative. A role is added only with an
        # explicit anchor, never inferred from outside the current clause.
        def append(role, a, b):
            item = _role(tokens, role, a, b)
            if item:
                roles.append(item)

        if verb in {"store", "remember", "correct", "read", "solve", "observe",
                    "classify", "define", "explain", "calculate", "show"}:
            if "regla" in keys[i+1:end]:
                r = keys.index("regla", i+1, end)
                stop = next((j for j in range(r + 1, end)
                             if keys[j] in OBJECT_BOUNDARY or keys[j] in NEGATION),
                            end)
                append("rule_name", r + 1, stop)
            if verb in {"observe", "classify", "solve"}:
                a = i + 1
                while a < end and keys[a] in SOFT:
                    a += 1
                b = next((j for j in range(a, end)
                          if keys[j] in {"con", "usando", "desde", "hasta"}),
                         end)
                append("observation_name", a, b)
            if verb in {"define", "explain"}:
                a = i + 1
                while a < end and keys[a] in SOFT:
                    a += 1
                b = next((j for j in range(a, end) if keys[j] in NEGATION), end)
                append("topic", a, b)
            if verb in {"remember", "store"} and "llama" in keys[i+1:end]:
                j = keys.index("llama", i + 1, end)
                append("name_value", j + 1, end)
            if verb == "read" and "regla" not in keys[i+1:end]:
                append("explicit_target", i + 1, end)
        for j in range(i + 1, end - 1):
            if keys[j] in OWNER:
                append("owner_" + OWNER[keys[j]], j, j + 1)
            if keys[j] == "valor" and tokens[j + 1]["kind"] == "number":
                append("value", j + 1, j + 2)
            if keys[j] == "muestra" and tokens[j + 1]["kind"] == "number":
                append("sample", j + 1, j + 2)
            if keys[j] == "desde" and tokens[j + 1]["kind"] == "number":
                append("position_from", j + 1, j + 2)
        forbidden = any(n["kind"] == "prohibition" and n["action_token"] == i
                        for n in negations)
        # Excluding a topic is different from prohibiting the command.
        excluded = [n["scope"] for n in negations if n["kind"] == "contrast_exclusion"
                    and i < n["token"] < end and n["scope"] is not None]
        events.append({
            "verb_token": i, "verb": verb, "token_range": [i, end],
            "polarity": "prohibited" if forbidden else "not-negated-by-c05",
            "roles": roles, "excluded_topics": excluded,
            "interpretation": "candidate-structure-not-executed",
        })
    return events


def _quantities(tokens: list[dict]) -> list[dict]:
    amounts = []
    for t in tokens:
        if t["kind"] != "number":
            continue
        lexeme = t["raw"]
        try:
            exact = Decimal(lexeme.replace(",", "."))
        except InvalidOperation as exc:
            raise ValueError("Invalid exact C05 decimal") from exc
        amounts.append({
            "token": t["i"], "lexeme": lexeme,
            "decimal": format(exact, "f"),
            "separator": "," if "," in lexeme else "." if "." in lexeme else None,
            "bytes": [t["start"], t["start"] + t["length"]],
            "negative": False,
        })
    for amount in amounts:
        i = amount["token"]
        if i and tokens[i - 1]["raw"] == "-" and (
            tokens[i - 1]["start"] + tokens[i - 1]["length"] == tokens[i]["start"]):
            amount["negative"] = True
    return amounts


def _references(current: list[dict], previous: list[dict]) -> list[dict]:
    candidates = []
    previous_keys = [t["key"] for t in previous]
    # This is a *candidate antecedent*, not a claim of resolved identity.
    # A previous instruction with one explicit "define X" is unambiguous
    # in this small supported grammar. Otherwise no coreference is invented.
    for i, key in enumerate(previous_keys):
        if key in {"define", "explica", "definir"} and i + 1 < len(previous):
            j = i + 1
            while j < len(previous) and previous_keys[j] in SOFT:
                j += 1
            if j < len(previous) and previous_keys[j] not in SEPARATORS:
                candidates.append(_span(previous, j, j + 1))
    distinct = [x for x in candidates if x is not None]
    result = []
    for token in current:
        if token["key"] not in REFERENCES:
            continue
        result.append({
            "token": token["i"], "form": token["key"],
            "candidate_in_previous": distinct[0] if len(distinct) == 1 else None,
            "status": "unverified-candidate" if len(distinct) == 1 else "unresolved",
        })
    return result


def _logic(tokens: list[dict]) -> list[dict]:
    keys = [t["key"] for t in tokens]
    result = []
    for i, key in enumerate(keys):
        if key == "si":
            later = next((j for j in range(i + 1, len(keys)) if keys[j] == "entonces"), None)
            if later is not None:
                result.append({
                    "kind": "conditional-marker",
                    "if": i, "then": later,
                    "antecedent": _span(tokens, i + 1, later),
                    "consequent": _span(tokens, later + 1, len(tokens)),
                    "status": "surface-only",
                })
        if key == "sí":
            result.append({"kind": "affirmative-marker", "token": i})
    return result


def analyze(prompt: str, previous: str = "") -> dict:
    """Lossless C1-compatible UTF-8 record with conservative semantic spans."""
    codec = C1.Codec(["<pad>"])
    current = _tokens(prompt, codec, C1.LIMITS["tokens"])
    history = _tokens(previous, codec, C1.LIMITS["history_tokens"])
    neg = _negations(current)
    data = {
        "schema": SCHEMA,
        "current_raw_b64": base64.b64encode(prompt.encode("utf-8")).decode("ascii"),
        "previous_raw_b64": base64.b64encode(previous.encode("utf-8")).decode("ascii"),
        "current_sha256": sha256(prompt.encode("utf-8")).hexdigest(),
        "previous_sha256": sha256(previous.encode("utf-8")).hexdigest(),
        "tokens": current, "history_tokens": history,
        "negations": neg, "events": _events(current, neg),
        "quantities": _quantities(current),
        "references": _references(current, history),
        "logic_markers": _logic(current),
        "model_claim": "none; host span annotation, original XI C1 remains authoritative",
    }
    return data


def wire_encode(analysis: dict) -> bytes:
    if analysis.get("schema") != SCHEMA:
        raise ValueError("Unknown C05 semantic schema")
    payload = _json(analysis)
    if len(payload) > MAX_WIRE:
        raise ValueError("C05 semantic packet too large")
    return MAGIC + struct.pack("<I", len(payload)) + sha256(payload).digest() + payload


def wire_decode(packet: bytes) -> dict:
    head = len(MAGIC) + 4 + 32
    if not isinstance(packet, bytes) or len(packet) < head or packet[:len(MAGIC)] != MAGIC:
        raise ValueError("C05 invalid magic or truncated header")
    size = struct.unpack("<I", packet[len(MAGIC):len(MAGIC) + 4])[0]
    if size > MAX_WIRE or len(packet) != head + size:
        raise ValueError("C05 truncated or oversized payload")
    payload = packet[head:]
    if sha256(payload).digest() != packet[len(MAGIC) + 4:head]:
        raise ValueError("C05 semantic packet SHA-256 mismatch")
    try:
        document = json.loads(payload.decode("utf-8"))
        source = base64.b64decode(document["current_raw_b64"], validate=True).decode("utf-8")
        prior = base64.b64decode(document["previous_raw_b64"], validate=True).decode("utf-8")
    except (UnicodeError, ValueError, KeyError, TypeError) as exc:
        raise ValueError("C05 non-canonical semantic packet") from exc
    if document != analyze(source, prior) or _json(document) != payload:
        raise ValueError("C05 untrusted semantic annotations do not match source")
    return document


def raw_roundtrip(document: dict) -> tuple[bytes, bytes]:
    """Recover the *exact* original UTF-8 including whitespace and casing."""
    wire = wire_decode(wire_encode(document))
    return (
        base64.b64decode(wire["current_raw_b64"]),
        base64.b64decode(wire["previous_raw_b64"]),
    )
