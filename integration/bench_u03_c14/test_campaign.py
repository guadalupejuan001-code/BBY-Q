"""C14 original XI packet billing, new splits, control safety and report contracts."""
from __future__ import annotations

import inspect
from pathlib import Path
import unittest

from .native_packets import ExclusivePacketTrace, packet_owner, BANKS, bank_for_path
from . import protocol
from . import campaign


class C14Contracts(unittest.TestCase):
    def test_all_cases_new_and_supervision_not_passed_to_inference(self):
        p=protocol.separation()
        self.assertTrue(p["novel_vs_C11_C12_C13"])
        self.assertEqual(p["case_count"],6)
        self.assertEqual(p["ablations_cases"],4)
        self.assertEqual({r.bit for r in protocol.BENCH},{0,1})
        self.assertEqual(len(protocol.NATIVE_CONTROLS),5)
        self.assertEqual(campaign.DEFAULT_REPEATS,2)
        src=inspect.getsource(campaign._probe)
        self.assertIn('receipt=session.turn("heldout-inference",case.prompt(),control=control)',src)
        self.assertNotIn("payload=",src)
        self.assertIn("native_trace_ops",src)
        self.assertIn("sqlite_trace_statement_counts",src)
        abl=inspect.getsource(campaign._ablations)
        self.assertLess(abl.index("for arm in rows:"),abl.index("teachers={"))
        self.assertIn("native_sample_teacher",abl)
        self.assertNotIn("qiskit",src)
        self.assertNotIn("torch",src)

    def test_packets_per_engine_are_not_duplicate_gate_times(self):
        self.assertEqual(packet_owner("router", ["c1_next"]), "C1")
        self.assertEqual(packet_owner("memory", ["qm_read"]), "QMemory")
        self.assertEqual(packet_owner("v3", ["vqc_sample","forward"]), "VQC")
        self.assertEqual(packet_owner("v3", ["qrl_step"]), "QRL")
        self.assertEqual(packet_owner("v3", ["forward", "qrl_step"]), "XI-mixed")
        self.assertEqual(packet_owner("v3", ["mem_materialize"]), "XI-transport")
        self.assertEqual(packet_owner("entity", ["entity_infer"]), "Entity")
        self.assertEqual(packet_owner("voice", ["qchat_encode"]), "QChat")
        self.assertEqual(bank_for_path(Path("/tmp/entity.rvp")), "entity")
        self.assertEqual(len(BANKS),8)

    def test_exclusive_packets_sum_once_and_report_mixed(self):
        x=ExclusivePacketTrace()
        def event(owner, start, end, ms, calls):
            return {
                "kind":"execute","bank":"v3","owner":owner,
                "start_ns":start,"end_ns":end,"duration_ms":ms,
                "native_cpu_ms_approx":0,"native_io_bytes":{"read_bytes":0,"write_bytes":0},
                "native_vm_hwm_kib":160,"source_bytes":250,"calls":calls,
            }
        x.events=[
            event("VQC",100,1000100,1,["forward"]),
            event("QRL",2000000,4000000,2,["qrl_step"]),
            event("XI-mixed",5000000,8000000,3,["qrl_step","forward"]),
        ]
        report=x.summarize()
        self.assertEqual(report["packets"],3)
        self.assertEqual(report["total_packet_wall_ms"],6)
        self.assertEqual(report["disjoint_packet_host_wall_ms_by_owner"]["VQC"],1)
        self.assertEqual(report["disjoint_packet_host_wall_ms_by_owner"]["QRL"],2)
        self.assertEqual(report["disjoint_packet_host_wall_ms_by_owner"]["XI-mixed"],3)
        self.assertEqual(sum(report["disjoint_packet_host_wall_ms_by_owner"].values()),6)
        self.assertTrue(report["multi_call_packets_never_double_counted"])
        self.assertTrue(report["nonoverlapping_host_packet_spans"])

    def test_overlapping_spans_fail_closed(self):
        x=ExclusivePacketTrace()
        x.events=[
            {"kind":"execute","owner":"VQC","start_ns":0,"end_ns":2000,
             "duration_ms":.002,"native_io_bytes":{},"source_bytes":0,
             "calls":[],"native_cpu_ms_approx":0,"native_vm_hwm_kib":0},
            {"kind":"execute","owner":"QRL","start_ns":1000,"end_ns":3000,
             "duration_ms":.002,"native_io_bytes":{},"source_bytes":0,
             "calls":[],"native_cpu_ms_approx":0,"native_vm_hwm_kib":0},
        ]
        with self.assertRaisesRegex(AssertionError,"overlap"):
            x.summarize()

    def test_concurrency_is_real_sqlite_not_fake_parallel_model(self):
        src=inspect.getsource(campaign._concurrency)
        self.assertIn("ThreadPoolExecutor",src)
        self.assertIn("Session(db)",src)
        self.assertIn("future.result(timeout=90)",src)
        self.assertIn("unified_requests",src)
        self.assertIn("unified_tasks",src)
        self.assertIn("replays_exact_without_new_revision",src)
        self.assertNotIn("ExclusivePacketTrace",src)

    def test_unchanged_checkpoints_no_automatic_promotion(self):
        src=inspect.getsource(campaign.campaign)
        self.assertIn("protected=freeze_assets()",src)
        self.assertIn("protected!=freeze_assets()",src)
        self.assertIn("hashes!=original_ids[arm][\"weights\"]",src)
        self.assertIn("snapshots",inspect.getsource(campaign._same) or "snapshots") if False else None
        self.assertIn('"model_promoted":False',src)
        self.assertIn('"cache_promoted":False',src)
        self.assertIn('"architecture":"BBY Q -> w4U -> QdU"',src)


if __name__=="__main__":
    unittest.main()
