"""Compact representation of repeated logical relations in BBY Q snapshots.

BBY Q owns this tiny bounded back-reference format. No third-party codec or
pretrained model. It is only a transport projection; Inverse Ether Memory is
still the sole persistent state authority, and original logical JSON is exact.
"""
from __future__ import annotations

MAGIC = b'BQL2'
REFERENCE = 0x80
WINDOW = 4096
MATCH_LIMIT = 255
MIN_MATCH = 5
CANDIDATES = 12


def encode(raw: bytes) -> bytes:
    """Encode ASCII canonical JSON using finite local previously-seen fragments."""
    if any(b >= 128 for b in raw):
        raise ValueError('Compact codec input must be ASCII canonical JSON')
    index: dict[bytes, list[int]] = {}
    output = bytearray(MAGIC)
    size = len(raw)
    pos = 0
    while pos < size:
        match_length = 0
        distance = 0
        if pos + 3 <= size:
            key = raw[pos:pos+3]
            for candidate in reversed(index.get(key, [])):
                behind = pos - candidate
                if behind > WINDOW or behind <= 0:
                    continue
                length = 3
                limit = min(MATCH_LIMIT, size - pos)
                while length < limit and raw[pos+length] == raw[candidate+length]:
                    length += 1
                if length > match_length:
                    match_length, distance = length, behind
                    if length == MATCH_LIMIT:
                        break
        consumed = match_length if match_length >= MIN_MATCH else 1
        if consumed != 1:
            output.append(REFERENCE)
            output.extend(distance.to_bytes(2, 'little'))
            output.append(match_length)
        else:
            output.append(raw[pos])
        for i in range(pos, min(pos+consumed, size-2)):
            key = raw[i:i+3]
            slots = index.setdefault(key, [])
            slots.append(i)
            if len(slots) > CANDIDATES:
                del slots[0]
        pos += consumed
    return bytes(output)


def decode(payload: bytes, maximum: int) -> bytes:
    """Strict restoration; bounded expansion; reject invalid address references."""
    if not payload.startswith(MAGIC):
        raise ValueError('Unknown BBY Q compact snapshot')
    out = bytearray()
    pos = len(MAGIC)
    while pos < len(payload):
        op = payload[pos]
        if op < REFERENCE:
            if len(out) >= maximum:
                raise ValueError('Compact state expansion exceeds budget')
            out.append(op)
            pos += 1
            continue
        if op != REFERENCE or pos + 4 > len(payload):
            raise ValueError('Corrupt BBY Q compact reference')
        distance = int.from_bytes(payload[pos+1:pos+3], 'little')
        length = payload[pos+3]
        if (not 1 <= distance <= WINDOW or distance > len(out) or
                length < MIN_MATCH or len(out) + length > maximum):
            raise ValueError('Out-of-range BBY Q compact reference')
        for _ in range(length):
            out.append(out[-distance])
        pos += 4
    return bytes(out)
