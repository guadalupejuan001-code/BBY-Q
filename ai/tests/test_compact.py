import copy
import random
import unittest

from bbyq.compact import decode, encode
from bbyq.context_experiment import context_campaign
from bbyq.model import new_entity
from bbyq.store import COMPACT_FLAG, MAX_PAYLOAD, NativeStore


class CompactTests(unittest.TestCase):
    def test_exact_roundtrip_on_learned_context_state(self):
        _, entity = context_campaign(42, 2, 150, 80, 24)
        packed = NativeStore._encode(entity)
        size = int.from_bytes(packed[:4], 'little')
        self.assertTrue(size & COMPACT_FLAG)
        self.assertLess(len(packed), 0.6 * len(__import__('json').dumps(
            entity, separators=(',', ':'), sort_keys=True).encode()))
        raw = decode(packed[4:], MAX_PAYLOAD)
        self.assertEqual(__import__('json').loads(raw), entity)

    def test_legacy_uncompressed_bytes_can_be_decoded_by_store(self):
        entity = new_entity('original-v1')
        for name in ('active_context', 'next_context', 'active_updates',
                     'archived', 'switches', 'surprise_streak'):
            entity['model'].pop(name)
        raw = __import__('json').dumps(entity, separators=(',', ':'), sort_keys=True,
                                       allow_nan=False, ensure_ascii=True).encode()
        legacy = len(raw).to_bytes(4, 'little') + raw
        self.assertFalse(int.from_bytes(legacy[:4], 'little') & COMPACT_FLAG)
        self.assertEqual(__import__('json').loads(legacy[4:]), entity)

    def test_overlapping_backreferences_and_random_inputs(self):
        rng = random.Random(123)
        for raw in [b'aaaaa' * 500, b'abcdef' * 600,
                    bytes(rng.randrange(0, 128) for _ in range(300)),
                    b'{}', b'', b'abc' * 2000]:
            self.assertEqual(decode(encode(raw), len(raw)), raw)

    def test_reject_bad_reference_and_decompression_bomb(self):
        for input_bytes, limit in [(b'BQL2\x80\x01', 300),
                                   (b'BQL2\x80\x01\x00\x07', 300),
                                   (b'BQL2aaaaaaaa\x80\x00\x00\x05', 300),
                                   (encode(b'xyz'*100), 8)]:
            with self.assertRaises(ValueError):
                decode(input_bytes, limit)

    def test_compact_preserves_full_unicode_json_as_ascii(self):
        entity = new_entity('á — X')
        packed = NativeStore._encode(entity)
        self.assertTrue(packed[4:].startswith(b'BQL2'))
        payload = decode(packed[4:], MAX_PAYLOAD)
        self.assertIn(b'\\u00e1', payload)


if __name__ == '__main__':
    unittest.main()
