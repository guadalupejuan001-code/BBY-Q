"""C03: fail-closed cache contracts, isolated from all trained checkpoint files."""
from collections import OrderedDict
from contextvars import ContextVar
from unittest import TestCase
from unittest.mock import patch

from integration.unified.quantum import Quantum as BaseQuantum
from integration.unified.common import A
from .session import (
    C03Quantum, CachedSession, CACHE_CAPACITY,
    _C03_TURN, _ORIGINAL_TURN, fresh_stats,
)


class CacheContractTests(TestCase):
    def make_quantum(self, stats=None):
        q = object.__new__(C03Quantum)
        q.trace = []
        q.meta = {"perception_revision": 3}
        q.readout_magic = 240605
        q._c03_epochs = {"v3": 0, "memory": 0}
        q._c03_caches = {"v3": OrderedDict(), "memory": OrderedDict()}
        q._c03_stats = stats if stats is not None else fresh_stats()
        return q

    def test_original_turn_bytecode_and_immutable_binding(self):
        self.assertIs(_C03_TURN.__code__, _ORIGINAL_TURN.__code__)
        self.assertIsNot(_C03_TURN.__globals__, _ORIGINAL_TURN.__globals__)
        self.assertIs(_C03_TURN.__globals__["Quantum"], C03Quantum)
        self.assertIs(_ORIGINAL_TURN.__globals__["Quantum"], BaseQuantum)
        self.assertTrue(issubclass(CachedSession, type.__mro__[0]) if False else issubclass(CachedSession, __import__("integration.unified.session", fromlist=["Session"]).Session))

    def test_classifier_hit_and_full_native_trace_shape(self):
        stats = fresh_stats()
        q = self.make_quantum(stats)
        n = []
        def simulated_native(self, bank, body, operation, **details):
            n.append((bank, operation))
            self.trace.append({"bank": bank, "operation": operation, "native": True, **details})
            return [{"name": "probability", "value": 0.987}]
        body = (f"store64 {A + 280} 0\ncall select_agent\n"
                "call forward\ncall u2_apply\n")
        kw = {"input_sha256": "a1b2", "readout": "U02", "qubits": 1000}
        with patch.object(BaseQuantum, "stage", new=simulated_native):
            one = q.stage("v3", body, "vqc_forward", **kw)
            two = q.stage("v3", body, "vqc_forward", **kw)
            self.assertEqual(one, two)
            self.assertEqual(n, [("v3", "vqc_forward")])
            self.assertEqual(stats["vqc_hits"], 1)
            self.assertEqual(stats["vqc_misses"], 1)
            self.assertEqual(stats["avoided_native_exec"], 1)
            self.assertEqual(q.trace[0], q.trace[1])
            # A QRL update in the same V3 bank invalidates any old inference.
            q.stage("v3", "call qrl_step", "qrl_step", qubits=1000)
            q.stage("v3", body, "vqc_forward", **kw)
            self.assertEqual(n[-1], ("v3", "vqc_forward"))
            self.assertEqual(stats["vqc_misses"], 2)
            self.assertGreater(stats["invalidations"]["v3"], 0)
            # Changing the requested experiment's readout version also misses.
            q.readout_magic = 12345
            q.stage("v3", body, "vqc_forward", **kw)
            self.assertEqual(stats["vqc_misses"], 3)

    def test_quantum_memory_cache_is_invalidated_by_write(self):
        stats = fresh_stats()
        q = self.make_quantum(stats)
        called = []
        def fake(self, bank, body, operation, **details):
            called.append(operation)
            self.trace.append({"bank": bank, "operation": operation, "native": True, **details})
            return [{"name": "probability", "value": .75}]
        body = "fexpect f0 Z:20000\nfemit probability f0"
        with patch.object(BaseQuantum, "stage", new=fake):
            q.stage("memory", body, "qm_read", slot=0, qubits=4)
            q.stage("memory", body, "qm_read", slot=0, qubits=4)
            self.assertEqual(stats["memory_hits"], 1)
            self.assertEqual(called, ["qm_read"])
            # Do not cache or reuse destructive erasure controls.
            q.stage("memory", "qprepare 20000 4\n"+body, "qm_read", slot=0, qubits=4)
            q.stage("memory", body, "qm_read", slot=0, qubits=4)
            self.assertEqual(called[-2:], ["qm_read", "qm_read"])
            # A user association write invalidates all earlier memory reads.
            q.stage("memory", "call qm_exchange", "qm_exchange", slot=0)
            q.stage("memory", body, "qm_read", slot=0, qubits=4)
            self.assertEqual(called[-1], "qm_read")
            self.assertEqual(stats["memory_misses"], 3)

    def test_input_changed_or_ablated_never_uses_old_prediction(self):
        stats = fresh_stats()
        q = self.make_quantum(stats)
        called = []
        def fake(self, bank, body, operation, **details):
            called.append(body)
            self.trace.append({"bank": bank, "operation": operation, "native": True, **details})
            return [{"value": 1.}]
        body = f"store64 {A + 280} 0\ncall select_agent\ncall forward\ncall u2_apply"
        with patch.object(BaseQuantum, "stage", new=fake):
            q.stage("v3", body, "vqc_forward", input_sha256="X")
            q.stage("v3", body, "vqc_forward", input_sha256="Y")
            self.assertEqual(len(called), 2)
            q.stage("v3", body.replace(f"store64 {A+280} 0", f"store64 {A+280} 1"),
                    "vqc_forward", input_sha256="X")
            self.assertEqual(len(called), 3)

    def test_bounded_lru_cap_no_unbounded_per_turn_growth(self):
        q = self.make_quantum()
        def fake(self, bank, body, operation, **details):
            return []
        with patch.object(BaseQuantum, "stage", new=fake):
            for i in range(CACHE_CAPACITY + 3):
                body = (f"store64 {A + 280} 0\ncall select_agent\n"
                        f"call forward\nstore64 {A+256} {i}\ncall u2_apply")
                q.stage("v3", body, "vqc_forward", input_sha256=str(i))
            self.assertEqual(len(q._c03_caches["v3"]), CACHE_CAPACITY)
            self.assertEqual(q._c03_stats["evictions"], 3)


if __name__ == "__main__":
    import unittest
    unittest.main()
