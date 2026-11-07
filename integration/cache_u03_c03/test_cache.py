"""C03 cache invariants: immutable archives, SHA invalidation, bounded capacity."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from integration.unified import session as original
from integration.sequence2 import workspace as c1_workspace
from .session import (
    ArchiveMemo, CachedSession, _C03_INIT, _C1_INIT,
    archive_cache_scope,
)


class ArchiveCacheTests(unittest.TestCase):
    def fixture(self, root):
        release = Path(root) / "release"
        release.mkdir()
        (release / "v3.rvp.gz").write_bytes(b"compressed-checkpoint-1")
        (release / "manifest.json").write_text(
            json.dumps({"perception": {"file": "v3.rvp.gz"}})
        )
        return release

    def test_same_bytes_reuse_only_authenticated_checkpoint(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = self.fixture(tmp)
            memo = ArchiveMemo(max_bytes=512, max_entries=3)
            loads = []
            def loader():
                loads.append(1)
                return b"original-uncompressed-model"
            self.assertEqual(memo.get("perception", folder, loader), loader())
            self.assertEqual(memo.get("perception", folder, loader), b"original-uncompressed-model")
            self.assertEqual(len(loads), 2)  # manual loader() above + cache miss
            self.assertEqual(memo.stats["hits"], 1)
            self.assertEqual(memo.stats["misses"], 1)
            self.assertEqual(memo.stats["bypassed_native_executions"], 0)

    def test_tampering_detected_even_if_file_size_does_not_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = self.fixture(tmp)
            memo = ArchiveMemo()
            calls = []
            def verified_loader():
                calls.append("verified")
                return hashlib.sha256((folder / "v3.rvp.gz").read_bytes()).digest()
            first = memo.get("perception", folder, verified_loader)
            data = (folder / "v3.rvp.gz")
            data.write_bytes(b"tampered--checkpoint-1")
            self.assertEqual(len(data.read_bytes()), len(b"compressed-checkpoint-1"))
            self.assertNotEqual(memo.get("perception", folder, verified_loader), first)
            self.assertEqual(calls, ["verified", "verified"])
            self.assertEqual(memo.stats["hits"], 0)
            self.assertEqual(memo.stats["misses"], 2)

    def test_binding_and_manifest_edit_invalidate_cached_bytes(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = self.fixture(tmp)
            memo = ArchiveMemo()
            memo.get("perception", folder, lambda: b"frozen")
            manifest = folder / "manifest.json"
            manifest.write_text(json.dumps({"perception": {"file": "v3.rvp.gz"},
                                            "version": 2}))
            again = []
            memo.get("perception", folder, lambda: again.append(True) or b"replacement")
            self.assertEqual(again, [True])

    def test_lru_memory_cap_and_no_mutable_result_sharing(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = self.fixture(tmp)
            memo = ArchiveMemo(max_bytes=8, max_entries=2)
            first = memo.get("perception", folder, lambda: {"a": b"1234"})
            first["a"] = b"invalid"
            second = memo.get("perception", folder, lambda: self.fail("Cache hit missing"))
            self.assertEqual(second, {"a": b"1234"})
            self.assertEqual(memo.snapshot()["resident_bytes"], 4)
            other = folder / "v3.rvp.gz"
            other.write_bytes(b"different-image")
            memo.get("perception", folder, lambda: b"12345678")
            self.assertLessEqual(memo.snapshot()["resident_bytes"], 8)
            self.assertLessEqual(memo.snapshot()["entries"], 2)

    def test_loader_failure_is_not_cached(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = self.fixture(tmp)
            memo = ArchiveMemo()
            with self.assertRaisesRegex(ValueError, "Corrupt"):
                memo.get("perception", folder, lambda: (_ for _ in ()).throw(ValueError("Corrupt")))
            self.assertEqual(memo.snapshot()["entries"], 0)
            self.assertEqual(memo.stats["hits"], 0)

    def test_missing_release_manifest_bypasses_cache(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp)
            memo = ArchiveMemo()
            n = []
            self.assertEqual(memo.get("perception", folder, lambda: n.append(1) or b"a"), b"a")
            self.assertEqual(memo.get("perception", folder, lambda: n.append(1) or b"b"), b"b")
            self.assertEqual(len(n), 2)
            self.assertEqual(memo.stats["hits"], 0)

    def test_scope_does_not_leak_or_patch_native_u02(self):
        init = original.Session.__init__
        turn = original.Session.turn
        self.assertIs(_C03_INIT.__code__, init.__code__)
        self.assertIs(_C1_INIT.__code__, c1_workspace.Workspace.__init__.__code__)
        self.assertIs(CachedSession.turn, turn)
        with archive_cache_scope(max_bytes=64) as memo:
            self.assertEqual(memo.snapshot()["entries"], 0)
        self.assertEqual(memo.snapshot()["entries"], 0)
        self.assertIs(original.Session.__init__, init)
        self.assertIs(original.Session.turn, turn)


if __name__ == "__main__":
    unittest.main()
