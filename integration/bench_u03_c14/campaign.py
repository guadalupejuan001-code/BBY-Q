#!/usr/bin/env python3
"""C14 native XI packet attribution, novel ablations and concurrency, no APK.

Each request is handled by the ORIGINAL U02 Session and pinned XI/Ether
runtime on a disposable SQLite backup. Original and C13 cache are benchmark
routes, NOT new models. Native packet wall times are disjoint by source
bank/call; XI gate CPU cannot be measured exclusively by this host tracer.
"""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
from hashlib import sha256
import json
import os
from pathlib import Path
import resource
import sqlite3
import statistics
import tempfile
import time

from integration.audit_u03_c00.profile import (
    ROOT, freeze_assets, apk_files, stats, io_counters, usage_cpu_ms,
)
from integration.blocks_u03_c12.campaign import _initialize, _training_arm
from integration.joint_u03_c11.campaign import _clone, _read_weights
from integration.joint_u03_c11.native import HEADS, native_sample_teacher
from integration.optimize_u03_c13.cache import authenticated_release_cache
from integration.optimize_u03_c13.campaign import (
    _receipt_identity, _measure_one as c13_original_probe, _identical,
)
from integration.memory_u03_c09.view import UnifiedMemoryView
from integration.unified.session import Session

from .native_packets import ExclusivePacketTrace, BANKS
from .protocol import (
    SCHEMA, BENCH, ABLATIONS, INTERFERENCE, CONCURRENT,
    ROUTES, NATIVE_CONTROLS, separation,
)

DEFAULT_REPEATS=2


def snapshot_digest(value):
    return sha256(json.dumps(value,sort_keys=True).encode()).hexdigest()


def _probe(source:Path, case, *, control=None):
    if control not in NATIVE_CONTROLS:
        raise ValueError("C14 cannot invent XI ablation controls")
    started=time.perf_counter_ns()
    cpu0=usage_cpu_ms()
    io0=io_counters(os.getpid())
    with tempfile.TemporaryDirectory(prefix="bbyq-c14-audit-") as tmp:
        location=Path(tmp)/"native.sqlite"
        t=time.perf_counter_ns()
        _clone(source,location)
        backup_ms=(time.perf_counter_ns()-t)/1e6
        sql_statements=[]
        with ExclusivePacketTrace() as profiler:
            t=time.perf_counter_ns()
            session=Session(location)
            open_ms=(time.perf_counter_ns()-t)/1e6
            try:
                before=session.snapshot()
                session.db.set_trace_callback(lambda sql:sql_statements.append(sql.split(None,1)[0].upper())
                                              if sql.strip() else None)
                packet_start=len(profiler.events)
                t=time.perf_counter_ns()
                receipt=session.turn("heldout-inference",case.prompt(),control=control)
                turn_ms=(time.perf_counter_ns()-t)/1e6
                packet_end=len(profiler.events)
                session.db.set_trace_callback(None)
                native=next((r for r in reversed(receipt.get("results",[]))
                             if r.get("kind")=="mission"), {})
                ops=sorted({r.get("operation") for r in receipt.get("trace",[])
                            if isinstance(r.get("operation"),str)})
                if set(ops).intersection({
                    "supervised_update", "u2_adam","qm_train/publish_angles",
                    "qchat_train","entity_qrl_feedback",
                }):
                    raise AssertionError("C14 leaked native training into inference")
                t=time.perf_counter_ns()
                view=UnifiedMemoryView(session).snapshot()
                after=session.snapshot()
                audit_ms=(time.perf_counter_ns()-t)/1e6
                if view["new_memory_authorities"] or len(view["bank_sha256"])!=7:
                    raise AssertionError("C14 untrusted or incomplete original XI banks")
                if not view["C1_synchronized_with_U02"]:
                    raise AssertionError("C14 C1/U02 transaction desynchronized")
                observed={
                    "source_seed":case.seed, "name":case.name,
                    "control":control or "normal",
                    "receipt_ok":bool(receipt.get("ok")),
                    "native_class":native.get("class"),
                    "native_rule":native.get("rule_value"),
                    "native_action":native.get("action"),
                    "native_goal":native.get("goal"),
                    "native_supported":native.get("supported") is True,
                    "native_voice_faithful":native.get("voice",{}).get("faithful") is True,
                    "native_voice_terminated":native.get("voice",{}).get("terminated") is True,
                    "native_trace_ops":ops,
                    "checkpoint_changed_only_in_disposable_test_copy":after!=before,
                    "no_teacher_labels_entered_native_inference":True,
                }
                receipt_sha=_receipt_identity(receipt)
                after_sha=snapshot_digest(after)
            finally:
                session.db.set_trace_callback(None)
                t=time.perf_counter_ns()
                session.close()
                close_ms=(time.perf_counter_ns()-t)/1e6
        # Packet attribution only inside Session.turn, not model authentication.
        only_turn=ExclusivePacketTrace()
        only_turn.events=profiler.events[packet_start:packet_end]
        turn_packets=only_turn.summarize()
        full_packets=profiler.summarize()
        if turn_packets["total_packet_wall_ms"]-turn_ms>0.01:
            # Instrumentation is all synchronous; a packet cannot exceed its
            # enclosing host turn duration except tiny rounding differences.
            raise AssertionError("C14 native packet wall larger than Session.turn")
        io1=io_counters(os.getpid())
        counts=dict(Counter(sql_statements))
        return {
            "seed":case.seed,
            "control":control or "normal",
            "observed":observed,
            "receipt_sha256":receipt_sha,
            "after_snapshot_sha256":after_sha,
            "phase_ms":{
                "sqlite_backup":round(backup_ms,3),
                "session_startup":round(open_ms,3),
                "u02_turn":round(turn_ms,3),
                "post_native_C09_audit":round(audit_ms,3),
                "session_close":round(close_ms,3),
                "end_to_end_without_cache_guard":round((time.perf_counter_ns()-started)/1e6,3),
            },
            "u02_turn_packet_wall_ms":turn_packets["total_packet_wall_ms"],
            "turn_native_packets":turn_packets,
            "full_session_native_packets":full_packets,
            "turn_unattributed_host_ms":round(max(0.,turn_ms-turn_packets["total_packet_wall_ms"]),3),
            "sqlite_trace_statement_counts":counts,
            "sqlite_write_statements_observed":sum(counts.get(x,0)
                                                    for x in ("INSERT","UPDATE","DELETE","REPLACE")),
            "cpu_python_ms":round(usage_cpu_ms()-cpu0,3),
            "process_rss_kib_cumulative":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "process_io_bytes":{
                k:max(0,io1.get(k,0)-io0.get(k,0)) for k in ("read_bytes","write_bytes")
            },
            "all_seven_banks_authenticated":True,
            "c1_u02_synced":True,
        }


def _same(a,b):
    return (a["observed"]==b["observed"]
            and a["receipt_sha256"]==b["receipt_sha256"]
            and a["after_snapshot_sha256"]==b["after_snapshot_sha256"])


def _report_route(rows):
    fields=("sqlite_backup","session_startup","u02_turn",
            "post_native_C09_audit","session_close","end_to_end_including_guard")
    return {
        "n":len(rows),
        "end_to_end_ms":stats([x["phase_ms"]["end_to_end_including_guard"] for x in rows]),
        "phases_ms":{k:stats([x["phase_ms"][k] for x in rows]) for k in fields},
        "python_cpu_ms":stats([x["cpu_python_ms"] for x in rows]),
        "python_cumulative_rss_kib_max":max(x["process_rss_kib_cumulative"] for x in rows),
        "process_io_bytes_observed":{k:sum(x["process_io_bytes"][k] for x in rows)
                                     for k in ("read_bytes","write_bytes")},
        "sqlite_write_statements_observed":sum(x["sqlite_write_statements_observed"] for x in rows),
        "sqlite_statement_counts":dict(Counter({
            kind:sum(r["sqlite_trace_statement_counts"].get(kind,0) for r in rows)
            for kind in {key for r in rows for key in r["sqlite_trace_statement_counts"]}
        })),
        "packet_wall_ms_disjoint_by_engine":{
            bank:stats([r["turn_native_packets"]["disjoint_packet_host_wall_ms_by_owner"][bank]
                        for r in rows]) for bank in BANKS
        },
        "native_cpu_ms_approx":stats([r["turn_native_packets"]["approx_child_process_cpu_ms"] or 0
                                       for r in rows]),
        "source_bytes_to_xi":stats([r["turn_native_packets"]["source_bytes_to_XI"] for r in rows]),
        "xi_execute_packets":stats([r["turn_native_packets"]["packets"] for r in rows]),
        "host_turn_minus_packet_wall_ms":stats([r["turn_unattributed_host_ms"] for r in rows]),
        "outputs_valid":all(r["observed"]["receipt_ok"] for r in rows),
        "all_seven_banks_authenticated":all(r["all_seven_banks_authenticated"] for r in rows),
        "all_c1_u02_synced":all(r["c1_u02_synced"] for r in rows),
        "native_packet_spans_never_overlap":all(
            r["turn_native_packets"]["nonoverlapping_host_packet_spans"] for r in rows
        ),
        "exclusive_engine_wall_is_not_exclusive_gate_cpu":True,
    }


def _benchmark(sources, *, repeats, original_v3):
    traces={route:{} for route in ROUTES}
    originals={"u02-frozen", "c12-joint-unpromoted"}
    # Two repetitions with rotated route order, plus candidate scoped cache.
    for repetition in range(repeats):
        order=list(ROUTES)
        if repetition%2:
            order.reverse()
        for route in order:
            arm,cache=ROUTES[route]
            scope=authenticated_release_cache() if cache else nullcontext(None)
            batch_started=time.perf_counter_ns()
            batch=[]
            with scope:
                for case in BENCH:
                    row=_probe(sources[arm],case)
                    batch.append(row)
                    traces[route][(repetition,case.seed)]=row
            # Cache-authentication costs must not disappear from the speed
            # comparison. Add measured scope overhead equally per sample.
            overhead=max(0.,((time.perf_counter_ns()-batch_started)/1e6-
                             sum(r["phase_ms"]["end_to_end_without_cache_guard"]
                                 for r in batch))/len(batch))
            for row in batch:
                row["phase_ms"]["cache_guard_amortized"]=round(overhead,3)
                row["phase_ms"]["end_to_end_including_guard"]=round(
                    row["phase_ms"]["end_to_end_without_cache_guard"]+overhead,3
                )
    for key in sorted(traces["u02-frozen"]):
        if not _same(traces["u02-frozen"][key],
                     traces["c13-cache-frozen-experimental"][key]):
            raise AssertionError("C14 caching changed U02 receipts or native snapshots")
    # The C14 profiler is observational; cross-check against original C13
    # instrument-free implementation on an entirely fresh disposable clone.
    reference=c13_original_probe(sources["frozen"],BENCH[0])
    if (reference["observed"]!=traces["u02-frozen"][(0,BENCH[0].seed)]["observed"]
        or reference["receipt_sha256"]!=traces["u02-frozen"][(0,BENCH[0].seed)]["receipt_sha256"]
        or reference["after_snapshot_sha256"]!=traces["u02-frozen"][(0,BENCH[0].seed)]["after_snapshot_sha256"]):
        raise AssertionError("C14 disjoint XI instrumentation changed actual U02 behavior")
    result={route:_report_route([traces[route][key] for key in sorted(traces[route])])
            for route in ROUTES}
    paired=[]
    for key in sorted(traces["u02-frozen"]):
        a=traces["u02-frozen"][key]["phase_ms"]["end_to_end_including_guard"]
        b=traces["c13-cache-frozen-experimental"][key]["phase_ms"]["end_to_end_including_guard"]
        paired.append({"seed":key[1],"repeat":key[0],"reference_ms":a,"cached_ms":b,
                       "percent_change":round((a-b)/a*100,3)})
    a=statistics.median([r["reference_ms"] for r in paired])
    b=statistics.median([r["cached_ms"] for r in paired])
    # Only now, after ALL three routes produced predictions, reveal the
    # original synthetic XI labels in a separate native interpreter session.
    labels={case.seed:native_sample_teacher(original_v3,case.seed) for case in BENCH}
    rules={case.seed:case.bit for case in BENCH}
    heldout={route:{
        "total":len(rows),
        "class_correct":sum(record["observed"]["native_class"]==labels[key[1]]
                            for key,record in rows.items()),
        "rule_correct":sum(record["observed"]["native_rule"]==rules[key[1]]
                           for key,record in rows.items()),
        "voice_faithful_and_terminated":sum(
            record["observed"]["native_voice_faithful"] and
            record["observed"]["native_voice_terminated"] for record in rows.values()
        ),
        "receipts_ok":sum(record["observed"]["receipt_ok"] for record in rows.values()),
        "teacher_revealed_only_after_all_native_inference":True,
    } for route,rows in traces.items()}
    return {
        "routes":result,
        "heldout_synthetic_XI":heldout,
        "cache_paired":{
            "pairs":len(paired),
            "median_reference_ms":round(a,3),
            "median_cached_ms":round(b,3),
            "observed_median_speedup_pct":round((a-b)/a*100,2),
            "cache_fastest_pairs":sum(row["reference_ms"]>row["cached_ms"] for row in paired),
            "source_output_and_checkpoint_identity":True,
            "raw_pairs":paired,
        },
        "raw_native_samples":{route:[
            {"seed":k[1], "repeat":k[0], "phase_ms":v["phase_ms"],
             "native_packets":v["turn_native_packets"],"sql":v["sqlite_trace_statement_counts"],
             "cpu_python_ms":v["cpu_python_ms"],
             "process_io_bytes":v["process_io_bytes"]}
            for k,v in sorted(rows.items())
        ] for route,rows in traces.items()},
    }


def _ablations(sources, original_v3):
    """Native teacher is obtained in separate XI only after all predictions."""
    rows={arm:[] for arm in ("frozen","joint")}
    for arm in rows:
        for case in ABLATIONS:
            for control in NATIVE_CONTROLS:
                x=_probe(sources[arm],case,control=control)
                rows[arm].append({
                    "seed":case.seed, "control":control or "normal",
                    "class":x["observed"]["native_class"],
                    "rule":x["observed"]["native_rule"],
                    "action":x["observed"]["native_action"],
                    "goal":x["observed"]["native_goal"],
                    "supported":x["observed"]["native_supported"],
                    "voice_faithful":x["observed"]["native_voice_faithful"],
                    "voice_terminated":x["observed"]["native_voice_terminated"],
                    "receipt_ok":x["observed"]["receipt_ok"],
                    "native_packet_ops":x["turn_native_packets"]["commands_pre_halt"],
                    "host_ms":x["phase_ms"]["end_to_end_without_cache_guard"],
                })
    teachers={case.seed:native_sample_teacher(original_v3,case.seed) for case in ABLATIONS}
    gold={c.seed:c for c in ABLATIONS}
    report={}
    for arm,records in rows.items():
        by_control={}
        for control in NATIVE_CONTROLS:
            name=control or "normal"
            matched=[r for r in records if r["control"]==name]
            assert len(matched)==len(ABLATIONS)
            by_control[name]={
                "total":len(matched),
                "class_correct":sum(r["class"]==teachers[r["seed"]] for r in matched),
                "rule_correct":sum(r["rule"]==gold[r["seed"]].bit for r in matched),
                "voice_faithful_and_terminated":sum(
                    r["voice_faithful"] and r["voice_terminated"] for r in matched
                ),
                "native_receipts_ok":sum(r["receipt_ok"] for r in matched),
                "mean_host_ms":round(statistics.mean(r["host_ms"] for r in matched),3),
            }
        deltas=[]
        normal={r["seed"]:r for r in records if r["control"]=="normal"}
        for row in records:
            if row["control"]=="normal":
                continue
            reference=normal[row["seed"]]
            deltas.append({
                "seed":row["seed"],"control":row["control"],
                "changed_class":row["class"]!=reference["class"],
                "changed_rule":row["rule"]!=reference["rule"],
                "changed_action":row["action"]!=reference["action"],
                "changed_voice":(row["voice_faithful"],row["voice_terminated"])!=
                                (reference["voice_faithful"],reference["voice_terminated"]),
            })
        report[arm]={
            "by_control":by_control,
            "counterfactual_differences":deltas,
            "all_failed_cases_retained":len(records)==20,
            "teacher_from_original_XI_after_prediction":True,
            "raw":records,
        }
    return report


def _interference(sources):
    result={}
    for arm in ("frozen","joint"):
        src=sources[arm]
        with tempfile.TemporaryDirectory(prefix="bbyq-c14-revisit-") as tmp:
            db=Path(tmp)/"revisit.sqlite"
            _clone(src,db)
            with Session(db) as model:
                rows=[]
                for index,case in enumerate(INTERFERENCE):
                    receipt=model.turn(f"c14-revisit-{index}",case.prompt())
                    mission=next((r for r in reversed(receipt.get("results",[]))
                                  if r.get("kind")=="mission"),{})
                    view=UnifiedMemoryView(model).snapshot()
                    rows.append({
                        "seed":case.seed, "ok":bool(receipt.get("ok")),
                        "class":mission.get("class"),"rule":mission.get("rule_value"),
                        "goal":mission.get("goal"),"action":mission.get("action"),
                        "voice":mission.get("voice",{}).get("faithful"),
                        "C1_synced":view["C1_synchronized_with_U02"],
                        "banks":len(view["bank_sha256"]),
                    })
            fields=("class","rule","goal","action","voice")
            result[arm]={
                "steps":rows,
                "a_output_changed_after_b":any(rows[0][k]!=rows[2][k] for k in fields),
                "all_c1_u02_synced":all(x["C1_synced"] for x in rows),
                "all_banks_authenticated":all(x["banks"]==7 for x in rows),
                "all_receipts_ok":all(x["ok"] for x in rows),
            }
    return result


def _concurrency(sources):
    """Two real SQLite WAL writers on ONE sandbox DB; no tracing monkeypatch.

    The native XI sessions are independent per thread, and only SQLite is
    authoritative; this does not assert parallel CPU speedup.
    """
    result={}
    for arm in ("frozen","joint"):
        with tempfile.TemporaryDirectory(prefix="bbyq-c14-concurrent-") as tmp:
            db=Path(tmp)/"shared.sqlite"
            _clone(sources[arm],db)
            def worker(index,case):
                with Session(db) as model:
                    r=model.turn(f"c14-concurrent-{index}",case.prompt())
                    mission=next((row for row in reversed(r.get("results",[]))
                                  if row.get("kind")=="mission"),{})
                    return {
                        "index":index, "receipt_ok":bool(r.get("ok")),
                        "class":mission.get("class"),
                        "rule":mission.get("rule_value"),
                        "action":mission.get("action"),
                        "receipt_sha256":_receipt_identity(r),
                    }
            t0=time.perf_counter_ns()
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures=[pool.submit(worker,i,case)
                         for i,case in enumerate(CONCURRENT)]
                received=[future.result(timeout=90) for future in futures]
            elapsed_ms=(time.perf_counter_ns()-t0)/1e6
            with Session(db) as model:
                view=UnifiedMemoryView(model).snapshot()
                snapshot=model.snapshot()
                stored=[model.db.execute(
                    "SELECT result FROM unified_requests WHERE id=?", (f"c14-concurrent-{i}",)
                ).fetchone() for i in range(2)]
                tasks=model.db.execute(
                    "SELECT COUNT(*) FROM unified_tasks WHERE id LIKE 'c14-concurrent-%'"
                ).fetchone()[0]
                if tasks!=2 or not all(stored):
                    raise AssertionError("C14 concurrent original XI lost a committed mission")
                if not view["C1_synchronized_with_U02"] or len(view["bank_sha256"])!=7:
                    raise AssertionError("C14 concurrent SQLite/XI state not synchronized")
                replays=[model.turn(f"c14-concurrent-{i}",case.prompt())
                         for i,case in enumerate(CONCURRENT)]
                if model.snapshot()!=snapshot:
                    raise AssertionError("C14 concurrent retry advanced training or revision")
                for receipt,original in zip(replays,received):
                    if _receipt_identity(receipt)!=original["receipt_sha256"]:
                        raise AssertionError("C14 replay failed across concurrent writers")
            if not all(row["receipt_ok"] for row in received):
                raise AssertionError("C14 concurrent native mission rejected")
            result[arm]={
                "parallel_writers":2, "committed_distinct_tasks":tasks,
                "all_receipts_ok":True, "replays_exact_without_new_revision":True,
                "C1_U02_synced":True, "seven_banks_authenticated":True,
                "wall_ms":round(elapsed_ms,3),
                "raw":received,
                "not_claimed_parallel_speedup":True,
            }
    return result


def campaign(out:Path, *, repeats=DEFAULT_REPEATS):
    if not 2<=repeats<=4:
        raise ValueError("C14 requires 2..4 repetitions, not one")
    protected=freeze_assets()
    apks=apk_files()
    if len(protected)!=159:
        raise AssertionError("C14 original protected inventory count differs from 159")
    split=separation()
    out=Path(out)
    out.parent.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter_ns()
    with tempfile.TemporaryDirectory(prefix="bbyq-c14-run-") as tmp:
        root=Path(tmp)
        common=root/"original-u02.sqlite"
        init=_initialize(common)
        original_common_sha=sha256(common.read_bytes()).hexdigest()
        sources={}
        training={}
        original_ids={}
        for arm in ("frozen","joint"):
            src=root/(arm+".sqlite")
            _clone(common,src)
            sources[arm]=src
            training[arm]=_training_arm(src,train=(arm=="joint"))
            hashes,snapshot=_read_weights(src)
            original_ids[arm]={
                "weights":hashes,"snapshot":snapshot,
                "sqlite_sha256":sha256(src.read_bytes()).hexdigest(),
            }
        if training["joint"]["native_feedback_count"]!=2 or not all(
                training["joint"]["native_parameter_changed"].values()):
            raise AssertionError("C14 did not reproduce native trained C12 control")
        if any(training["frozen"]["native_parameter_changed"].values()):
            raise AssertionError("C14 original U02 frozen control changed weights")

        benchmark=_benchmark(sources,repeats=repeats,original_v3=init["original_v3"])
        ablations=_ablations(sources,init["original_v3"])
        interference=_interference(sources)
        concurrent=_concurrency(sources)

        for arm,src in sources.items():
            hashes,snapshot=_read_weights(src)
            if hashes!=original_ids[arm]["weights"] or snapshot!=original_ids[arm]["snapshot"]:
                raise AssertionError("C14 original source checkpoint was mutated")
            if sha256(src.read_bytes()).hexdigest()!=original_ids[arm]["sqlite_sha256"]:
                raise AssertionError("C14 source SQLite changed outside disposable clones")
        if sha256(common.read_bytes()).hexdigest()!=original_common_sha:
            raise AssertionError("C14 changed original common U02 SQLite")
        if protected!=freeze_assets() or apks!=apk_files():
            raise AssertionError("C14 changed 159 historical assets or created APK")
        # C13 did not pass 3% across multiple campaigns. This cycle DOES NOT
        # override that frozen decision based on profiling/ablation results.
        report={
            "schema":SCHEMA,
            "passed":True,
            "base_C13_PR":99,
            "base_C13_sha":"5e88433895218ad90ee18f7380c49a69a51bc07e",
            "architecture":"BBY Q -> w4U -> QdU",
            "native_XI_original_unchanged":True,
            "protected_asset_count":len(protected),
            "historical_sha256_unchanged":True,
            "checkpoints_unchanged":True,
            "new_primary_memory_authorities":0,
            "apk_built":False,
            "model_promoted":False,
            "cache_promoted":False,
            "frozen_kept_as_reference":True,
            "protocol":{**split,"repeats":repeats,
                        "samples_per_route":repeats*len(BENCH),
                        "heldout_labels_generated_after_native_predictions":True,
                        "not_quantum_hardware":True},
            "training":{
                arm:{"original_verified_feedback":training[arm]["native_feedback_count"],
                     "six_native_parameter_regions_changed":training[arm]["native_parameter_changed"]}
                for arm in training
            },
            "benchmark":benchmark,
            "ablations":ablations,
            "interference":interference,
            "concurrency":concurrent,
            "total_wall_ms":round((time.perf_counter_ns()-started)/1e6,3),
            "limitations":[
                "All benchmarks use synthetic original XI contracts and simulated qubits; not quantum physics hardware or general intelligence.",
                "Disjoint packet wall is attributable to one bank/call, but cannot infer exclusive gates or native CPU per function.",
                "Native CPU from /proc is coarse; Python process peak RSS includes other tasks and is not component-specific.",
                "Linux /proc I/O may show cache effects; zero read_bytes is not zero actual reads.",
                "SQLite trace counts SQL statements, not per-statement exclusive wall or SSD durability.",
                "C13 cache was not deployed; effects are runner-dependent, no speedup or promotion without predeclared evidence.",
                "Concurrent SQLite correctness for two writers does not prove large-scale concurrency, fault tolerance or throughput gains.",
                "Four ablation seeds are descriptive only; no causal claim from small synthetic samples.",
            ],
        }
        out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
        return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--out",type=Path,default=ROOT/"build/c14/benchmark.json")
    p.add_argument("--repeats",type=int,default=DEFAULT_REPEATS)
    arg=p.parse_args()
    report=campaign(arg.out,repeats=arg.repeats)
    print(json.dumps({
        "passed":report["passed"], "cases":report["protocol"]["case_count"],
        "samples_per_route":report["protocol"]["samples_per_route"],
        "engine_packet_medians_ms":{
            route:{bank:round(values["median"],2)
                   for bank,values in data["packet_wall_ms_disjoint_by_engine"].items()}
            for route,data in report["benchmark"]["routes"].items()},
        "ablation_per_arm":{arm:len(result["raw"]) for arm,result in report["ablations"].items()},
        "concurrent_cases":{arm:r["committed_distinct_tasks"] for arm,r in report["concurrency"].items()},
        "cache_promoted":False,"model_promoted":False,
        "historical_files":159,"apk_built":False,
    },ensure_ascii=False))


if __name__=="__main__":
    main()
