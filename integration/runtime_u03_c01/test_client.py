"""Fast transport and scope tests, independent of runtime compilation."""
import unittest

from integration.runtime_u03_c01 import client
from integration.unified import common, quantum


class CachedXIClientTests(unittest.TestCase):
    def setUp(self):
        client.CachedXiSession.reset_counters()

    def test_register_library_once_and_preserve_exact_prelude(self):
        session = object.__new__(client.CachedXiSession)
        session._libraries = {}
        seen = []

        def fake_request(name, payload):
            seen.append((name, payload))
            if name == "CODELIB":
                return "1", 0
            return '{"type":"register","register":"r12","value":9}\n', 0.5

        session._cached_request = fake_request
        source = "#!reverse-pc-machine-v1\nbudget 1000\nset r12 9\nhalt\n" + "label library\nret\n"*60
        first = session.execute(source)
        second = session.execute(source)
        self.assertEqual(first, second)
        self.assertEqual([x[0] for x in seen], ["CODELIB", "EXECREF", "EXECREF"])
        self.assertEqual(seen[1][1], "1\n#!reverse-pc-machine-v1\nbudget 1000\nset r12 9\nhalt\n")
        self.assertEqual(session.stats["libraries_registered"], 1)
        self.assertEqual(session.stats["library_cache_hits"], 1)
        self.assertEqual(session.stats["exec_ref"], 2)
        self.assertTrue(session.stats["xi_wire_payload_bytes"] <
                        session.stats["logical_execute_source_bytes"])

    def test_small_source_has_exact_fallback(self):
        session = object.__new__(client.CachedXiSession)
        session._libraries = {}
        seen = []

        def fake_request(name, payload):
            seen.append((name, payload))
            return '{}\n', 1.0

        session._cached_request = fake_request
        value = "#!reverse-pc-machine-v1\nhalt\n"
        self.assertEqual(session.execute(value), ([{}], 1.0))
        self.assertEqual(seen, [("EXEC", value)])
        self.assertEqual(session.stats["exec_fallback"], 1)

    def test_context_always_restores_original_session(self):
        base = common.C1.XiSession
        alias = quantum.XiSession
        with self.assertRaisesRegex(RuntimeError, "injected"):
            with client.activate():
                self.assertIs(common.C1.XiSession, client.CachedXiSession)
                self.assertIs(quantum.XiSession, client.CachedXiSession)
                raise RuntimeError("injected")
        self.assertIs(common.C1.XiSession, base)
        self.assertIs(quantum.XiSession, alias)

    def test_bounded_pool_restores_before_reusing_state(self):
        class FakeProcess:
            def poll(self):
                return None

        class FakeWorker:
            def __init__(self):
                self.process = FakeProcess()
                self.commands = []
                self.closed = False

            def _request(self, command, payload):
                self.commands.append((command, payload))
                return "{}", 0.0

            def close(self):
                self.closed = True

        pool = client.ScopedXiPool(max_idle=1)
        worker = FakeWorker()
        pool.idle.append(worker)
        self.assertIs(pool.borrow("ignored", "/tmp/example.rvp"), worker)
        self.assertEqual(worker.commands[0][0], "RESTORE")
        self.assertEqual(client.CachedXiSession.stats["restores"], 1)
        pool.release(worker)
        self.assertEqual(len(pool.idle), 1)
        pool.shutdown()
        self.assertTrue(worker.closed)
        self.assertEqual(pool.idle, [])

    def test_failed_restore_is_fail_closed(self):
        class FakeProcess:
            def poll(self):
                return None

        class BrokenWorker:
            process = FakeProcess()
            closed = False

            def _request(self, command, payload):
                raise RuntimeError("corrupt RVPC2")

            def close(self):
                self.closed = True

        pool = client.ScopedXiPool()
        worker = BrokenWorker()
        pool.idle.append(worker)
        with self.assertRaisesRegex(RuntimeError, "corrupt"):
            pool.borrow("ignored", "/tmp/corrupt.rvp")
        self.assertTrue(worker.closed)
        self.assertEqual(pool.idle, [])
        pool.shutdown()

    def test_exact_saved_state_reuse_requires_matching_hash_and_clean_worker(self):
        import hashlib
        import tempfile
        from pathlib import Path

        class FakeProcess:
            def poll(self):
                return None

        class FakeWorker:
            process = FakeProcess()
            closed = False

            def __init__(self, content):
                self._c01_exact_hash = hashlib.sha256(content).hexdigest()
                self._c01_dirty = False
                self.commands = []

            def _request(self, name, payload):
                self.commands.append(name)
                return "{}", 0.0

            def close(self):
                self.closed = True

        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "state.rvp"
            path.write_bytes(b"exact immutable state")
            pool = client.ScopedXiPool()
            w = FakeWorker(path.read_bytes())
            pool.idle.append(w)
            self.assertIs(pool.borrow("unused", path), w)
            self.assertEqual(w.commands, [])
            self.assertEqual(client.CachedXiSession.stats["exact_snapshot_reuses"], 1)
            pool.release(w)
            w._c01_dirty = True  # A new unsaved EXEC makes the cache unsafe.
            self.assertIs(pool.borrow("unused", path), w)
            self.assertEqual(w.commands, ["RESTORE"])
            pool.release(w)
            w._c01_exact_hash = hashlib.sha256(b"another checkpoint").hexdigest()
            w._c01_dirty = False
            self.assertIs(pool.borrow("unused", path), w)
            self.assertEqual(w.commands, ["RESTORE", "RESTORE"])
            pool.release(w)
            pool.shutdown()
            self.assertTrue(w.closed)

    def test_c01_is_opt_in(self):
        self.assertIsNot(common.C1.XiSession, client.CachedXiSession)


if __name__ == "__main__":
    unittest.main()
