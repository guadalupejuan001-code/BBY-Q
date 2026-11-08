#!/usr/bin/env python3
"""C13 reproducible, native XI/U02 optimization and stage-aware profiling.

Paired ABBA-like ordering on the SAME frozen U02/C12 trained checkpoints:
- original C12 isolated clone per call
- C13 same isolated clone with authenticated, process-local model byte cache
Never changes native runtime, circuit, model weights, Session.turn, or its SQL.
"""
from __future__ import annotations

import argparse
from contextlib import nullcontext
from hashlib import sha256
import json
from pathlib import Path
import os
import resource
import statistics
import tempfile
import time

from integration.audit_u03_c00.profile import (
    ROOT, apk_files, freeze_assets, stats, usage_cpu_ms, io_counters,
    NativeTrace, summarize_events,
)
from integration.blocks_u03_c12.campaign import _initialize, _training_arm
from integration.blocks_u03_c12.protocol import (
    TRAIN as C12_TRAIN, VALIDATION as C12_VALIDATION,
    TEST as C12_TEST, LOAD as C12_LOAD,
)
from integration.joint_u03_c11.campaign import _clone, _episode, _read_weights
from integration.joint_u03_c11.native import HEADS
from integration.joint_u03_c11.protocol import (
    Heldout, validation as c11_validation, heldout_test as c11_test,
    TRAINED_SEEDS,
)
from integration.memory_u03_c09.view import UnifiedMemoryView
from integration.unified.common import C1
from integration.unified.session import Session

from .cache import authenticated_release_cache

SCHEMA = "BBYQ-U03-C13-authenticated-release-cache-v1"
ARMS = ("u02-frozen", "c12-joint-experimental")
VARIANTS = ("original-c12", "cached-release-c13")
CONTROLS = (None, "memory-erased", "vqc-ablated", "qrl-ablated", "voice-ablated")
CASES = (
    Heldout("c13-perf", "Cedro", "Borde Dorado", 28130101, position=0, bit=0),
    Heldout("c13-perf", "Cobre Fino", "Valle Blanco", 28130102, position=2, bit=1),
    Heldout("c13-perf", "Granito", "Piedra Mansa", 28130103, position=4, bit=0),
    Heldout("c13-perf", "Eslabon", "Puente Limpio", 28130104, position=6, bit=1),
)
DEFAULT_REPEATS = 3


def ensure_separation() -> dict:
    seen = (*c11_validation(), *c11_test(), *C12_TRAIN,
            *C12_VALIDATION, *C12_TEST, *C12_LOAD)
    old_seeds = {c.seed for c in seen} | TRAINED_SEEDS
    old_names = {name.lower() for c in seen for name in (c.name, c.rule)}
    old_names.update(("nara", "faro azul"))
    assert len(CASES) == 4 and {x.bit for x in CASES} == {0, 1}
    assert len({x.seed for x in CASES}) == len(CASES)
    for case in CASES:
        assert case.seed not in old_seeds, "C13 benchmark leaked old sample seed"
        assert case.name.lower() not in old_names
        assert case.rule.lower() not in old_names
    return {
        "independent_of_C11_C12": True,
        "repeats": DEFAULT_REPEATS,
        "unique_cases": len(CASES),
        "immutable_case_sha256": sha256(json.dumps(
            [c.as_dict() for c in CASES], sort_keys=True
        ).encode()).hexdigest(),
    }


def _nonclock(value):
    """Remove only nondeterministic clock fields, not failed outputs."""
    if isinstance(value, dict):
        return {k: _nonclock(v) for k, v in value.items()
                if k not in ("elapsed_ms", "host_wall_ms")}
    if isinstance(value, list):
        return [_nonclock(x) for x in value]
    return value


def _receipt_identity(receipt) -> str:
    return sha256(json.dumps(_nonclock(receipt),sort_keys=True,
                            ensure_ascii=False).encode()).hexdigest()


def _measure_one(source: Path, case: Heldout, *, control=None) -> dict:
    """Same original C11/C12 native XI task with phase timing added.

    File backup → fresh U02 Session → original XI turn → independent C09
    bank/sync audit. Every measured case has a NEW database and no teacher.
    """
    if control not in CONTROLS:
        raise ValueError("C13 cannot invent a native ablation")
    total_start = time.perf_counter_ns()
    cpu_start = usage_cpu_ms()
    io_start = io_counters(os.getpid())
    with tempfile.TemporaryDirectory(prefix="bbyq-c13-isolated-") as tmp:
        db = Path(tmp) / "one-native-task.sqlite"
        t0 = time.perf_counter_ns()
        _clone(source, db)
        clone_ms = (time.perf_counter_ns() - t0) / 1e6

        t0 = time.perf_counter_ns()
        model = Session(db)
        startup_ms = (time.perf_counter_ns() - t0) / 1e6
        try:
            initial = model.snapshot()
            t0 = time.perf_counter_ns()
            receipt = model.turn("heldout-inference", case.prompt(),control=control)
            turn_ms = (time.perf_counter_ns() - t0) / 1e6
            native = next((x for x in reversed(receipt.get("results", []))
                           if x.get("kind") == "mission"), {})
            trace_ops = sorted({
                event.get("operation")
                for event in receipt.get("trace", [])
                if isinstance(event.get("operation"), str)
            })
            forbidden = {"supervised_update", "u2_adam", "qm_train/publish_angles",
                         "qchat_train", "entity_qrl_feedback"}
            if forbidden.intersection(trace_ops):
                raise AssertionError("C13 inference ran native supervised learning")
            t0 = time.perf_counter_ns()
            view = UnifiedMemoryView(model).snapshot()
            after_snapshot = model.snapshot()
            audit_ms = (time.perf_counter_ns() - t0) / 1e6
            if view["new_memory_authorities"] or len(view["bank_sha256"]) != 7:
                raise AssertionError("C13 created a second memory or corrupt XI bank")
            if not view["C1_synchronized_with_U02"]:
                raise AssertionError("C13 desynchronized native C1/U02 memory")

            observed = {
                "source_seed": case.seed, "name": case.name,
                "control": control or "normal",
                "receipt_ok": bool(receipt.get("ok")),
                "native_class": native.get("class"),
                "native_rule": native.get("rule_value"),
                "native_action": native.get("action"),
                "native_goal": native.get("goal"),
                "native_supported": native.get("supported") is True,
                "native_voice_faithful": native.get("voice", {}).get("faithful") is True,
                "native_voice_terminated": native.get("voice", {}).get("terminated") is True,
                "native_trace_ops": trace_ops,
                "checkpoint_changed_only_in_disposable_test_copy":
                    after_snapshot != initial,
                "no_teacher_labels_entered_native_inference": True,
            }
            receipt_sha = _receipt_identity(receipt)
            after_sha = sha256(json.dumps(after_snapshot,sort_keys=True).encode()).hexdigest()
        finally:
            t0 = time.perf_counter_ns()
            model.close()
            close_ms = (time.perf_counter_ns() - t0) / 1e6
    end_io = io_counters(os.getpid())
    return {
        "observed": observed,
        "receipt_sha256": receipt_sha,
        "after_snapshot_sha256": after_sha,
        "phase_ms": {
            "sqlite_backup": round(clone_ms, 3),
            "session_startup_authentication": round(startup_ms, 3),
            "original_u02_xi_turn": round(turn_ms, 3),
            "c09_post_inference_audit": round(audit_ms, 3),
            "session_close": round(close_ms, 3),
            "total_including_new_db": round((time.perf_counter_ns()-total_start)/1e6, 3),
        },
        "python_cpu_ms": round(usage_cpu_ms()-cpu_start, 3),
        "python_rss_peak_kib_cumulative": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "process_io_bytes": {
            name: max(0, end_io.get(name, 0)-io_start.get(name, 0))
            for name in ("read_bytes", "write_bytes")
        },
        "source_seed": case.seed,
        "control": control or "normal",
        "authenticated_banks": 7,
        "c1_u02_synchronized": True,
    }


def _identical(first: dict, second: dict) -> bool:
    return (first["observed"] == second["observed"] and
            first["receipt_sha256"] == second["receipt_sha256"] and
            first["after_snapshot_sha256"] == second["after_snapshot_sha256"])


def _condensed(rows: list[dict]) -> dict:
    phases = (
        "sqlite_backup", "session_startup_authentication",
        "original_u02_xi_turn", "c09_post_inference_audit", "session_close",
        "total_including_new_db", "scope_guard_overhead_amortized",
        "total_including_guard",
    )
    return {
        "n": len(rows),
        "wall_ms": {phase: stats([r["phase_ms"][phase] for r in rows])
                    for phase in phases},
        "python_cpu_ms": stats([r["python_cpu_ms"] for r in rows]),
        "python_rss_peak_kib_max_cumulative": max(r["python_rss_peak_kib_cumulative"]
                                                   for r in rows),
        "process_io_bytes_observed": {
            name: sum(r["process_io_bytes"][name] for r in rows)
            for name in ("read_bytes", "write_bytes")
        },
        "authentic_seven_banks": all(r["authenticated_banks"] == 7 for r in rows),
        "c1_u02_synchronized": all(r["c1_u02_synchronized"] for r in rows),
        "no_teacher_in_inference": all(
            r["observed"]["no_teacher_labels_entered_native_inference"] for r in rows
        ),
    }


def _paired_report(original: list, cached: list) -> dict:
    assert len(original) == len(cached) and len(original) >= 8
    assert all(a["source_seed"]==b["source_seed"] for a,b in zip(original,cached))
    assert all(_identical(a,b) for a,b in zip(original,cached))
    base = [row["phase_ms"]["total_including_guard"] for row in original]
    newer = [row["phase_ms"]["total_including_guard"] for row in cached]
    paired_pct = [(a-b)/a*100 for a,b in zip(base,newer)]
    baseline=statistics.median(base)
    candidate=statistics.median(newer)
    return {
        "all_native_outputs_and_receipts_byte_equivalent": True,
        "all_post_inference_native_snapshots_equal": True,
        "pairs": len(base),
        "baseline_median_ms": round(baseline,3),
        "cached_median_ms": round(candidate,3),
        "median_delta_ms": round(baseline-candidate,3),
        "observed_median_speedup_percent": round(100*(baseline-candidate)/baseline,2),
        "paired_speedup_percent": stats(paired_pct),
        "cached_faster_pairs": sum(a>b for a,b in zip(base,newer)),
        "candidate_is_faster_at_median": candidate < baseline,
        "runtime_model_still_frozen": True,
    }


def _trace_one(source: Path, case: Heldout, cache: bool):
    tracer=NativeTrace()
    tracer.attach(C1.XiSession)
    try:
        tracer.reset()
        tracer.enabled=True
        with authenticated_release_cache() if cache else nullcontext():
            outcome=_measure_one(source,case)
        tracer.enabled=False
        return {
            "outcome": outcome["observed"],
            "native_profile": summarize_events(tracer.events),
            "native_vm_hwm_kib_observed": tracer.native_peak_kib,
            "python_peak_rss_kib_cumulative": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "note": "XI execute enclosing packet durations overlap; no exclusive per-gate CPU time",
        }
    finally:
        tracer.enabled=False
        tracer.detach()


def campaign(output: Path, *, repeats=DEFAULT_REPEATS) -> dict:
    if repeats < 3 or repeats > 8:
        raise ValueError("C13 paired benchmark requires 3..8 repetitions")
    protected_before=freeze_assets()
    apk_before=apk_files()
    assert len(protected_before)==159, "C13 must preserve 159 frozen sources/checkpoints"
    splits=ensure_separation()
    output=Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    start=time.perf_counter_ns()

    with tempfile.TemporaryDirectory(prefix="bbyq-c13-native-performance-") as tmp:
        root=Path(tmp)
        initial=root/"common-original-u02.sqlite"
        _initialize(initial)
        initial_sha=sha256(initial.read_bytes()).hexdigest()
        arms={}
        training={}
        before_banks={}
        for arm in ARMS:
            db=root/(arm+".sqlite")
            _clone(initial,db)
            arms[arm]=db
            training[arm]=_training_arm(db,train=(arm=="c12-joint-experimental"))
            hashes,snapshot=_read_weights(db)
            before_banks[arm]={"hashes":hashes,"snapshot":snapshot,"sqlite_sha":sha256(db.read_bytes()).hexdigest()}
        if training["c12-joint-experimental"]["native_feedback_count"]!=2:
            raise AssertionError("C13 lost two original C12 XI feedback checks")
        if not all(training["c12-joint-experimental"]["native_parameter_changed"].values()):
            raise AssertionError("C13 original XI trained parameter audit invalid")
        if any(training["u02-frozen"]["native_parameter_changed"].values()):
            raise AssertionError("C13 frozen U02 incorrectly trained")

        per_arm={}
        for arm,source in arms.items():
            store={v:{} for v in VARIANTS}
            series={v:[] for v in VARIANTS}
            cache_counter={"cold_authentications":0,"cache_hits":0}
            # Deterministic alternation avoids always giving one variant the
            # colder page cache or more thermal throttling of the runner.
            for repetition in range(repeats):
                order=VARIANTS if repetition % 2 == 0 else tuple(reversed(VARIANTS))
                for variant in order:
                    scope=authenticated_release_cache() if variant=="cached-release-c13" else nullcontext(None)
                    batch_t0=time.perf_counter_ns()
                    batch_rows=[]
                    with scope as counter:
                        for case in CASES:
                            row=_measure_one(source,case)
                            key=(repetition,case.seed)
                            store[variant][key]=row
                            batch_rows.append(row)
                        if counter is not None:
                            for key in cache_counter:
                                cache_counter[key]+=counter[key]
                    # Include the amortized immutable-manifest gate at BOTH
                    # boundaries: hiding this cost would bias the speed claim.
                    batch_total_ms=(time.perf_counter_ns()-batch_t0)/1e6
                    raw_ms=sum(r["phase_ms"]["total_including_new_db"] for r in batch_rows)
                    scope_overhead_ms=max(0.0,(batch_total_ms-raw_ms)/len(batch_rows))
                    for row in batch_rows:
                        phases=row["phase_ms"]
                        phases["scope_guard_overhead_amortized"]=round(scope_overhead_ms,3)
                        phases["total_including_guard"]=round(
                            phases["total_including_new_db"]+scope_overhead_ms,3)

            # Paired per-case comparison with identical native receipts.
            for variant in VARIANTS:
                series[variant]=[store[variant][key]
                                 for key in sorted(store[variant])]
            source_baseline=series["original-c12"]
            candidate=series["cached-release-c13"]
            pair=_paired_report(source_baseline,candidate)
            # Cross-check the original C11/C12 actual episode, not merely our
            # instrumented wrapper; both execute the native U02 Session.
            golden=_episode(source,CASES[0])
            assert golden==source_baseline[0]["observed"]
            assert golden==candidate[0]["observed"]

            # Original U02 ablation controls on 2 cases with exact path parity.
            ablations=[]
            for control in CONTROLS:
                for case in CASES[:2]:
                    a=_measure_one(source,case,control=control)
                    with authenticated_release_cache():
                        b=_measure_one(source,case,control=control)
                    if not _identical(a,b):
                        raise AssertionError("C13 altered XI ablation semantic output")
                    ablations.append({
                        "case_seed":case.seed,
                        "control":control or "normal",
                        "identical_original_vs_cached":True,
                        "class":a["observed"]["native_class"],
                        "rule":a["observed"]["native_rule"],
                        "voice_faithful":a["observed"]["native_voice_faithful"],
                        "action_simulated":a["observed"]["native_action"],
                    })

            after_hashes,after_snapshot=_read_weights(source)
            if before_banks[arm]["hashes"]!=after_hashes:
                raise AssertionError("C13 cached inference changed ORIGINAL XI weights")
            if before_banks[arm]["snapshot"]!=after_snapshot:
                raise AssertionError("C13 cached inference wrote source U02 checkpoint")
            if before_banks[arm]["sqlite_sha"]!=sha256(source.read_bytes()).hexdigest():
                raise AssertionError("C13 cached inference changed SQLite source file")
            per_arm[arm]={
                "reference":_condensed(source_baseline),
                "cached":_condensed(candidate),
                "paired":pair,
                "native_ablations":ablations,
                "cache_stats":cache_counter,
                "source_checkpoint_unchanged":True,
                "all_six_native_parameter_regions_unchanged_during_inference":True,
            }

        profile_original=_trace_one(arms["u02-frozen"],CASES[-1],False)
        profile_cached=_trace_one(arms["u02-frozen"],CASES[-1],True)
        if profile_original["outcome"] != profile_cached["outcome"]:
            raise AssertionError("C13 instrumented original XI trace changed behavior")
        if sha256(initial.read_bytes()).hexdigest()!=initial_sha:
            raise AssertionError("C13 initial U02 checkpoint mutated")
        if freeze_assets()!=protected_before or apk_files()!=apk_before:
            raise AssertionError("C13 changed protected sources or built APK")
        # C13 is an opt-in performance candidate; not a promoted user model.
        accepted = all(row["paired"]["candidate_is_faster_at_median"] and
                       row["paired"]["observed_median_speedup_percent"]>=3.0
                       for row in per_arm.values())
        report={
            "schema":SCHEMA, "passed":True,
            "branch_base":"C12 PR #98 exact commit d31d60bb0ee356b004e9e1e2d819aa361ef3a9db",
            "architecture":"BBY Q -> w4U -> QdU",
            "original_runtime":"REVERSE-PC XI/Ether U02 original",
            "source_protected_count":159,
            "frozen_assets_unchanged":True,
            "all_checkpoint_sources_unmodified":True,
            "original_u02_sqlite_unchanged":True,
            "new_primary_memory_authorities":0,
            "apk_built":False, "new_apks":[],
            "model_promoted":False,
            "trained_c12_candidate_still_not_promoted":True,
            "optimizations": {
                "candidate":"scoped authenticated release model bytes cache",
                "native_xi_algorithm_modified":False,
                "inference_results_cached":False,
                "sqlite_transactions_modified":False,
                "cache_scope":"only disposable isolated U02 sessions, no production",
                "recommend_enable_opt_in_if_verified_gain":accepted,
                "minimum_speedup_to_recommend_percent":3.0,
            },
            "benchmark_protocol": {
                **splits,
                "repeats_per_case":repeats,
                "samples_per_arm_variant":repeats*len(CASES),
                "runner_order":"even original then cached; odd cached then original",
                "teacher_unsealed_for_inference":False,
                "source_from_common_u02_checkpoint":True,
                "identical_case_control_pairs":True,
            },
            "training_reference": {
                arm: {"original_native_feedback":training[arm]["native_feedback_count"],
                      "six_weight_changes_before_inference":training[arm]["native_parameter_changed"]}
                for arm in ARMS
            },
            "arms":per_arm,
            "instrumented_profile": {
                "original":profile_original,
                "cached":profile_cached,
                "comparison":"Instrumentation adds overhead: compare paired noninstrumented workload for speed claims.",
            },
            "runner_python_rss_kib_max":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "total_wall_ms":round((time.perf_counter_ns()-start)/1e6,3),
            "c14_next":True,
            "limits":[
                "Only host Linux, original XI software simulator and synthetic tasks; no Android or hardware quantum advantage.",
                "Timing is end-to-end isolated request; includes new SQLite copy, source authentication and C09 audit.",
                "Native trace enclosing execution packets may contain multiple XI calls; no false exclusive timings.",
                "Native peak RSS and /proc I/O are host observations; page cache may make read_bytes zero.",
                "Measured paired end-to-end timing includes amortized SHA-256 manifest checks for cached scope; those checks cannot be hidden.",
                "Median speedup from small runner samples is descriptive, not a guaranteed production acceleration.",
                "No model improvement: C12 joint candidate was never promoted, even if host initialization is faster.",
            ],
        }
        output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
        return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--repeats",type=int,default=DEFAULT_REPEATS)
    parser.add_argument("--out",type=Path,default=ROOT/"build/c13/benchmark.json")
    options=parser.parse_args()
    report=campaign(options.out,repeats=options.repeats)
    print(json.dumps({
        "passed":report["passed"],
        "samples":report["benchmark_protocol"]["samples_per_arm_variant"],
        "paired":{arm:round(data["paired"]["observed_median_speedup_percent"],2)
                  for arm,data in report["arms"].items()},
        "candidate_recommended":report["optimizations"]["recommend_enable_opt_in_if_verified_gain"],
        "protected":report["source_protected_count"],
        "apk_built":False,
    },ensure_ascii=False))


if __name__=="__main__":
    main()
