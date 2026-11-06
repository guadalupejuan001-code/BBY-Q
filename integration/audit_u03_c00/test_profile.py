"""Fast, dependency-free C00 instrumentation contract tests."""
import tempfile
import unittest
from pathlib import Path

from integration.audit_u03_c00.profile import (
    FROZEN_PATHS, apk_files, difference, freeze_assets,
    invoked_calls, stats, summarize_events,
)


class C00ProfileTests(unittest.TestCase):
    def test_exec_calls_exclude_library_definitions(self):
        source = (
            "#!reverse-pc-machine-v1\n"
            "call vqc_sample\ncall select_agent\ncall forward\nhalt\n"
            "label irrelevant\ncall qrl_step\ncall qm_exchange\n"
        )
        self.assertEqual(invoked_calls(source), ["vqc_sample", "select_agent", "forward"])

    def test_statistics_have_explicit_small_sample_p95(self):
        self.assertEqual(stats([4, 1, 9, 2])["median"], 3.0)
        self.assertEqual(stats([4, 1, 9, 2])["p95_nearest_rank"], 9)
        self.assertEqual(stats([]), {})

    def test_io_deltas_never_invent_negative_io(self):
        self.assertEqual(difference({"read_bytes": 0, "write_bytes": 40},
                                    {"read_bytes": 20, "write_bytes": 10}),
                         {"read_bytes": 0, "write_bytes": 30})

    def test_events_are_per_packet_not_false_exclusive_calls(self):
        events = [{
            "type": "execute", "wall_ms": 15.0, "source_bytes": 600,
            "calls": ["forward", "u2_apply"], "native_cpu_ms": 10.0,
            "native_io_bytes": {"read_bytes": 0, "write_bytes": 4096},
        }, {"type": "save", "wall_ms": 8.0}]
        report = summarize_events(events)
        self.assertEqual(report["source_bytes_sent_to_xi"], 600)
        self.assertEqual(report["native_api"]["execute"]["count"], 1)
        self.assertEqual(report["call_invocations"]["forward"]["enclosing_exec_wall_ms"], 15.0)
        self.assertEqual(report["call_invocations"]["u2_apply"]["enclosing_exec_wall_ms"], 15.0)
        self.assertEqual(report["native_io_bytes_observed"]["write_bytes"], 4096)

    def test_frozen_assets_are_read_only_fingerprinted(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for relative in FROZEN_PATHS:
                directory = root / relative
                directory.mkdir(parents=True)
                (directory / "checkpoint.json").write_text("original")
            baseline = freeze_assets(root)
            self.assertEqual(len(baseline), len(FROZEN_PATHS))
            (root / FROZEN_PATHS[0] / "checkpoint.json").write_text("changed")
            changed = freeze_assets(root)
            self.assertNotEqual(changed, baseline)

    def test_apk_detection_is_limited_to_build_outputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "build").mkdir()
            (root / "build/fake.apk").write_bytes(b"")
            (root / "android-personal/app/build").mkdir(parents=True)
            (root / "android-personal/app/build/another.apk").write_bytes(b"")
            self.assertEqual(len(apk_files(root)), 2)


if __name__ == "__main__":
    unittest.main()
