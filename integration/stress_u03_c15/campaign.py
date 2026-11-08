#!/usr/bin/env python3
"""C15 actual U02 XI/Ether SQLite-WAL stress, recovery and idempotency.

All experiments run on disposable SQLite backups from two native bank states.
Never mutates the original release, the C12 training source, historical 159
assets or any personal database. No physical quantum hardware/Android/APK.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
from contextlib import nullcontext
from hashlib import sha256
import json
import os
from pathlib import Path
import resource
import sqlite3
import subprocess
import sys
import tempfile
import threading
import time

from integration.audit_u03_c00.profile import (
    ROOT, apk_files, freeze_assets, io_counters, stats, usage_cpu_ms,
)
from integration.blocks_u03_c12.campaign import _initialize, _training_arm
from integration.joint_u03_c11.campaign import _clone, _read_weights
from integration.joint_u03_c11.native import HEADS
from integration.optimize_u03_c13.cache import authenticated_release_cache
from integration.optimize_u03_c13.campaign import _measure_one, _identical, _receipt_identity
from integration.memory_u03_c09.view import UnifiedMemoryView
from integration.unified.common import digest
from integration.unified.session import Session

from .protocol import (
    SCHEMA, LEVELS, READERS, READER_SNAPSHOTS, CASES, COLLISION,
    COLLISION_DIFFERENT_PROMPT, FAULT, CACHE_CASES, EXPECTED_NATIVE_OPERATIONS,
    ARMS, C13_ROUTE, separation,
)


def _sha(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _child_cpu_ms() -> float:
    r = resource.getrusage(resource.RUSAGE_CHILDREN)
    return (r.ru_utime + r.ru_stime) * 1000.


def _mission(receipt):
    return next((r for r in reversed(receipt.get("results", []))
                 if r.get("kind") == "mission"), {})


def _original_bank_view(db: Path):
    """Read a WAL snapshot with a raw *read-only* SQLite connection.

    C09/U02 are authoritative; this diagnostic only authenticates a single
    snapshot and never opens a writer, stages models or caches native state.
    """
    url = "file:" + db.resolve().as_posix() + "?mode=ro"
    with sqlite3.connect(url, uri=True, timeout=40, isolation_level=None) as con:
        con.execute("PRAGMA query_only=ON")
        con.execute("BEGIN")
        try:
            state = con.execute(
                "SELECT metadata,sha,revision FROM unified_state WHERE id=1"
            ).fetchone()
            if state is None or digest(state[0]) != state[1]:
                raise AssertionError("C15 WAL reader detected invalid U02 metadata hash")
            meta = json.loads(state[0])
            language = con.execute(
                "SELECT sha,metadata_sha FROM state WHERE id=1"
            ).fetchone()
            if not language or meta.get("language_sync") != list(language):
                raise AssertionError("C15 WAL reader observed torn U02/C1 sync")
            banks = con.execute(
                "SELECT name,snapshot,sha FROM unified_banks ORDER BY name"
            ).fetchall()
            if len(banks) != 7:
                raise AssertionError("C15 WAL reader missed original seven banks")
            for name,raw,hash_expected in banks:
                if digest(raw) != hash_expected:
                    raise AssertionError("C15 WAL reader observed torn bank: "+name)
            count = con.execute(
                "SELECT COUNT(*) FROM unified_requests WHERE id LIKE 'c15-level-%'"
            ).fetchone()[0]
            return {"revision":int(state[2]),"requests":count,
                    "seven_banks_authenticated":True,
                    "C1_U02_synchronized":True}
        finally:
            con.execute("ROLLBACK")


def _reader(db, start, first_commit, initial_revision, index, snapshots):
    start.wait(timeout=30)
    values = []
    began = time.perf_counter_ns()
    # Read WAL snapshots while first native writer is calculating, then
    # REQUIRE one last snapshot after a real U02/SQLite commit. This avoids
    # a false claim that early readers witnessed any state transition.
    for _ in range(snapshots-1):
        values.append(_original_bank_view(db))
        time.sleep(.05)
    if not first_commit.wait(timeout=95):
        raise AssertionError("C15 WAL reader never observed a committed XI request")
    values.append(_original_bank_view(db))
    revisions = [x["revision"] for x in values]
    if revisions != sorted(revisions):
        raise AssertionError("C15 WAL reader revision went backward")
    if revisions[-1] <= initial_revision:
        raise AssertionError("C15 WAL reader did not observe a post-commit revision")
    return {"reader":index,"snapshots":len(values),"revisions":revisions,
            "initial_revision":initial_revision,
            "after_commit_revision_seen":True,
            "saw_coherent_banks":all(x["seven_banks_authenticated"] for x in values),
            "C1_U02_synchronized":all(x["C1_U02_synchronized"] for x in values),
            "wall_ms":round((time.perf_counter_ns()-began)/1e6,3)}


def _writer(db, start, first_commit, index, case, level):
    start.wait(timeout=30)
    began = time.perf_counter_ns()
    t0 = time.perf_counter_ns()
    with Session(db) as model:
        open_ms = (time.perf_counter_ns()-t0)/1e6
        t1 = time.perf_counter_ns()
        receipt = model.turn(f"c15-level-{level}-{index}", case.prompt())
        turn_ms = (time.perf_counter_ns()-t1)/1e6
        mission = _mission(receipt)
        ops = {r.get("operation") for r in receipt.get("trace", [])
               if isinstance(r.get("operation"),str)}
        if not all(op in ops for op in EXPECTED_NATIVE_OPERATIONS):
            raise AssertionError("C15 native mission skipped one of six XI engines")
        if not receipt.get("ok") or mission.get("status") != 1:
            raise AssertionError("C15 native mission failed in load campaign")
        # model.turn has committed to WAL before this event is signaled.
        first_commit.set()
        return {
            "worker":index, "seed":case.seed, "request_id":receipt["request_id"],
            "native_receipt_sha256":_receipt_identity(receipt),
            "native_class":mission.get("class"),
            "native_rule":mission.get("rule_value"),
            "action_simulated":mission.get("action"),
            "voice_faithful":mission.get("voice",{}).get("faithful") is True,
            "all_six_XI_engines_executed":True,
            "session_startup_ms":round(open_ms,3),
            "native_turn_ms":round(turn_ms,3),
            "total_wall_ms":round((time.perf_counter_ns()-began)/1e6,3),
        }


def _load_level(source: Path, arm: str, level: int, scratch:Path):
    db = scratch / f"{arm}-level-{level}.sqlite"
    _clone(source, db)
    initial_revision = _original_bank_view(db)["revision"]
    readers = READERS[level]
    start = threading.Barrier(level+readers)
    first_commit = threading.Event()
    before_io = io_counters(os.getpid())
    before_python_cpu = usage_cpu_ms()
    before_child_cpu = _child_cpu_ms()
    began = time.perf_counter_ns()
    with ThreadPoolExecutor(max_workers=level+readers) as pool:
        futures = [pool.submit(_writer, db, start, first_commit, i, CASES[i], level)
                   for i in range(level)]
        watching = [pool.submit(_reader, db, start, first_commit, initial_revision,
                                i, READER_SNAPSHOTS)
                    for i in range(readers)]
        writers = [f.result(timeout=180) for f in futures]
        observers = [f.result(timeout=180) for f in watching]
    wall = (time.perf_counter_ns()-began)/1e6
    after_io = io_counters(os.getpid())
    after_python_cpu = usage_cpu_ms()
    after_child_cpu = _child_cpu_ms()

    # Reopen original native U02 and verify every committed receipt and task.
    with Session(db) as model:
        view = UnifiedMemoryView(model).snapshot()
        assert len(view["bank_sha256"])==7 and view["C1_synchronized_with_U02"]
        assert view["new_memory_authorities"]==0
        snap = model.snapshot()
        task_count = model.db.execute(
            "SELECT COUNT(*) FROM unified_tasks WHERE id LIKE ?", (f"c15-level-{level}-%",)
        ).fetchone()[0]
        if task_count != level:
            raise AssertionError("C15 SQLite lost a concurrently committed XI task")
        persisted=[]
        for i,case in enumerate(CASES[:level]):
            row=model.db.execute(
                "SELECT result FROM unified_requests WHERE id=?",
                (f"c15-level-{level}-{i}",)
            ).fetchone()
            if row is None:
                raise AssertionError("C15 WAL missing native request receipt")
            persisted.append(json.loads(row[0]))
        replay = [model.turn(f"c15-level-{level}-{i}",case.prompt())
                  for i,case in enumerate(CASES[:level])]
        if model.snapshot() != snap:
            raise AssertionError("C15 replay re-executed native XI or changed revision")
        for i,(old,again) in enumerate(zip(persisted,replay)):
            if old != again or _receipt_identity(again) != writers[i]["native_receipt_sha256"]:
                raise AssertionError("C15 concurrent replay returned different original receipt")
        integrity=model.db.execute("PRAGMA integrity_check").fetchone()[0]
        journal=model.db.execute("PRAGMA journal_mode").fetchone()[0]
    if integrity!="ok" or journal.lower()!="wal":
        raise AssertionError("C15 concurrent SQLite-WAL integrity check failed")
    if not all(v["C1_U02_synchronized"] and v["saw_coherent_banks"]
               and v["after_commit_revision_seen"] for v in observers):
        raise AssertionError("C15 readers missed a post-commit WAL snapshot or saw torn state")
    return {
        "arm":arm, "writer_count":level, "reader_count":readers,
        "wal_snapshots_total":sum(v["snapshots"] for v in observers),
        "tasks_committed":task_count, "replays_exact":True,
        "sqlite_integrity_check":integrity, "journal_mode":journal,
        "source_checkpoint_read_only":True,
        "all_XI_six_engines_executed":all(r["all_six_XI_engines_executed"] for r in writers),
        "all_reader_snapshots_authenticated":True,
        "readers_observed_post_commit_revision":True,
        "C1_U02_synced":True, "seven_banks_authenticated":True,
        "wall_ms":round(wall,3),
        "throughput_native_tasks_per_second":round(level*1000/wall,4),
        "writer_total_wall_ms":stats([r["total_wall_ms"] for r in writers]),
        "writer_startup_ms":stats([r["session_startup_ms"] for r in writers]),
        "writer_native_turn_ms":stats([r["native_turn_ms"] for r in writers]),
        "python_cpu_ms_total_level":round(after_python_cpu-before_python_cpu,3),
        "native_child_cpu_ms_approx_total_level":round(max(0,after_child_cpu-before_child_cpu),3),
        "python_process_rss_peak_kib_cumulative":resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "python_process_io_bytes_level":{
            k:max(0,after_io.get(k,0)-before_io.get(k,0))
            for k in ("read_bytes","write_bytes")
        },
        "readers":observers, "writers":writers,
        "scope_limits":"Only %d writers and %d read-only observers on disposable Linux WAL; not a hardware limit"%(level,readers),
    }


def _failure_rollback(source:Path, arm:str, work:Path):
    errors=[]
    for cutoff in (1,2,3):
        db=work/f"{arm}-rollback-{cutoff}.sqlite"
        _clone(source,db)
        with Session(db) as model:
            before=model.snapshot()
            history=model.history()
            try:
                model.turn(f"c15-fail-{cutoff}", FAULT.prompt(), fail_after=cutoff)
            except RuntimeError:
                pass
            else:
                raise AssertionError("C15 native failure injection did not trigger")
            if model.snapshot()!=before or model.history()!=history:
                raise AssertionError("C15 original XI transaction leaked partial checkpoint")
        with Session(db) as restored:
            view=UnifiedMemoryView(restored).snapshot()
            if restored.snapshot()!=before or not view["C1_synchronized_with_U02"]:
                raise AssertionError("C15 rollback did not survive U02 restart")
            if restored.db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
                raise AssertionError("C15 rollback corrupted SQLite")
        errors.append({"cutoff":cutoff,"rollback_exact":True,"restart_exact":True})
    return {"injected_failures":len(errors),"all_atomic_rollback":True,"results":errors}


def _abrupt_crash(mode:str, db:Path):
    """Subprocess only, explicitly exits with an unclean status."""
    if mode=="before-commit":
        connection=sqlite3.connect(str(db),timeout=30,isolation_level=None)
        connection.execute("BEGIN IMMEDIATE")
        count=connection.execute(
            "UPDATE unified_banks SET sha=? WHERE name='v3'", ("c15-uncommitted-injected-corruption",)
        ).rowcount
        if count!=1:
            os._exit(75)
        os._exit(73)
    if mode=="after-commit":
        model=Session(db)
        result=model.turn("c15-crash-committed", FAULT.prompt())
        if not result.get("ok"):
            os._exit(75)
        # This exits without calling model.close or normal Python cleanup.
        os._exit(74)
    raise ValueError("Unsupported C15 crash mode")


def _crash_recovery(source:Path,arm:str,work:Path):
    results={}
    for mode,expected_return in (("before-commit",73),("after-commit",74)):
        db=work/f"{arm}-{mode}.sqlite"
        _clone(source,db)
        with Session(db) as original:
            baseline=original.snapshot()
        process=subprocess.run([
            sys.executable,"-m","integration.stress_u03_c15.campaign",
            "--crash-mode",mode,"--crash-db",str(db)
        ],cwd=ROOT,timeout=90,capture_output=True,text=True)
        if process.returncode!=expected_return:
            raise AssertionError("C15 crash worker unexpected exit: "
                                 +str(process.returncode)+" "+process.stderr[-500:])
        with Session(db) as restored:
            view=UnifiedMemoryView(restored).snapshot()
            if not view["C1_synchronized_with_U02"] or len(view["bank_sha256"])!=7:
                raise AssertionError("C15 WAL crash recovery returned corrupt banks")
            if restored.db.execute("PRAGMA integrity_check").fetchone()[0]!="ok":
                raise AssertionError("C15 WAL crash recovery failed integrity_check")
            before_replay=restored.snapshot()
            if mode=="before-commit":
                if before_replay!=baseline:
                    raise AssertionError("C15 process death leaked uncommitted bank SHA")
                row=restored.db.execute(
                    "SELECT id FROM unified_requests WHERE id='c15-crash-committed'"
                ).fetchone()
                if row:
                    raise AssertionError("C15 aborted transaction unexpectedly committed")
            else:
                saved=restored.db.execute(
                    "SELECT result FROM unified_requests WHERE id='c15-crash-committed'"
                ).fetchone()
                if saved is None:
                    raise AssertionError("C15 crash-after-commit lost committed native receipt")
                returned=restored.turn("c15-crash-committed",FAULT.prompt())
                if json.loads(saved[0])!=returned or restored.snapshot()!=before_replay:
                    raise AssertionError("C15 native committed receipt not idempotent after crash")
            results[mode]={
                "abrupt_process_exit_code":expected_return,
                "SQLite_WAL_recovered":True,"seven_native_banks_authenticated":True,
                "C1_U02_synchronized":True,
                "uncommitted_state_restored":mode=="before-commit",
                "committed_XI_receipt_survived_restart":mode=="after-commit",
                "replay_idempotent":mode=="after-commit",
            }
    return results


def _colliding_requests(source:Path,arm:str,work:Path):
    db=work/f"{arm}-collision.sqlite"
    _clone(source,db)
    start=threading.Barrier(2)
    def worker(index):
        start.wait(timeout=30)
        with Session(db) as model:
            result=model.turn("c15-collision",COLLISION.prompt())
            return {"id":index,"receipt":_receipt_identity(result),
                    "ok":bool(result.get("ok"))}
    with ThreadPoolExecutor(max_workers=2) as pool:
        futures=[pool.submit(worker,i) for i in range(2)]
        answers=[f.result(timeout=120) for f in futures]
    if not all(x["ok"] for x in answers) or answers[0]["receipt"]!=answers[1]["receipt"]:
        raise AssertionError("C15 racing same request ID returned inconsistent receipts")
    with Session(db) as model:
        previous=model.snapshot()
        count=model.db.execute(
            "SELECT COUNT(*) FROM unified_requests WHERE id='c15-collision'"
        ).fetchone()[0]
        task_count=model.db.execute(
            "SELECT COUNT(*) FROM unified_tasks WHERE id LIKE 'c15-collision:%'"
        ).fetchone()[0]
        if count!=1 or task_count!=1:
            raise AssertionError("C15 racing same request double-committed a task")
        try:
            model.turn("c15-collision",COLLISION_DIFFERENT_PROMPT.prompt())
        except ValueError:
            rejected=True
        else:
            rejected=False
        if not rejected or model.snapshot()!=previous:
            raise AssertionError("C15 conflicting request ID overwrote original receipt")
        view=UnifiedMemoryView(model).snapshot()
        if not view["C1_synchronized_with_U02"]:
            raise AssertionError("C15 collision desynchronized C1/U02")
    return {
        "simultaneous_same_id_requests":2,
        "unique_persisted_request":count,
        "unique_persisted_native_task":task_count,
        "both_receipts_identical":True,"different_payload_same_id_rejected":True,
        "no_revision_change_on_collision_replay":True,
    }


def _cache_control(source:Path):
    """C13 global monkeypatch is NOT thread-safe: only sequential opt-in runs."""
    records=[]
    for case in CACHE_CASES:
        reference=_measure_one(source,case)
        with authenticated_release_cache():
            cached=_measure_one(source,case)
        if not _identical(reference,cached):
            raise AssertionError("C15 C13 cache changed original native XI receipt/snapshot")
        records.append({
            "seed":case.seed,"native_outputs_identical":True,
            "original_end_to_end_ms":reference["phase_ms"]["total_including_new_db"],
            "cache_end_to_end_ms_excludes_scope_auth":cached["phase_ms"]["total_including_new_db"],
        })
    return {
        "route":C13_ROUTE, "single_threaded_only":True,
        "cache_not_promoted":True,
        "note":"C13 cache is not safe for concurrent use; scope excluded from stress. Cost excluding authentication is not a fair speedup comparison.",
        "identical_receipts_and_snapshots":True,
        "samples":records,
    }


def campaign(output:Path, *,levels=LEVELS):
    if tuple(levels)!=LEVELS:
        raise ValueError("C15 levels must match predeclared matrix")
    protected=freeze_assets()
    apks=apk_files()
    if len(protected)!=159:
        raise AssertionError("C15 changed protected historical file count")
    split=separation()
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter_ns()
    with tempfile.TemporaryDirectory(prefix="bbyq-c15-native-WAL-") as tmp:
        folder=Path(tmp)
        common=folder/"U02-original.sqlite"
        _initialize(common)
        common_sha=_sha(common)
        sources={}
        training={}
        saved={}
        for arm in ARMS:
            db=folder/(arm+".sqlite")
            _clone(common,db)
            sources[arm]=db
            training[arm]=_training_arm(db,train=(arm=="c12-joint-unpromoted"))
            weights,snapshot=_read_weights(db)
            saved[arm]={
                "weights":weights,"snapshot":snapshot,"sqlite_sha":_sha(db),
            }
        if training["c12-joint-unpromoted"]["native_feedback_count"]!=2:
            raise AssertionError("C15 did not reproduce original native C12 learning")
        if not all(training["c12-joint-unpromoted"]["native_parameter_changed"].values()):
            raise AssertionError("C15 C12 native parameter hashes did not change")
        if any(training["u02-frozen"]["native_parameter_changed"].values()):
            raise AssertionError("C15 frozen U02 changed original weights")

        stress={arm:[] for arm in ARMS}
        for arm in ARMS:
            for level in LEVELS:
                stress[arm].append(_load_level(sources[arm],arm,level,folder))
        failures={arm:_failure_rollback(sources[arm],arm,folder) for arm in ARMS}
        crashes={arm:_crash_recovery(sources[arm],arm,folder) for arm in ARMS}
        collisions={arm:_colliding_requests(sources[arm],arm,folder) for arm in ARMS}
        cached=_cache_control(sources["u02-frozen"])

        for arm,src in sources.items():
            weights,snapshot=_read_weights(src)
            if weights!=saved[arm]["weights"] or snapshot!=saved[arm]["snapshot"]:
                raise AssertionError("C15 source XI model changed during stress")
            if _sha(src)!=saved[arm]["sqlite_sha"]:
                raise AssertionError("C15 original source SQLite changed")
        if _sha(common)!=common_sha:
            raise AssertionError("C15 original initial SQLite mutated")
        if freeze_assets()!=protected or apk_files()!=apks:
            raise AssertionError("C15 touched 159 protected assets or created APK")

        observed_limits={}
        for arm,rows in stress.items():
            observed_limits[arm]={
                "largest_concurrent_writers_tested":max(r["writer_count"] for r in rows),
                "largest_simultaneous_readers_tested":max(r["reader_count"] for r in rows),
                "peak_throughput_tasks_per_second_observed":max(
                    r["throughput_native_tasks_per_second"] for r in rows),
                "writer_count_at_observed_peak_throughput":max(
                    rows,key=lambda r:r["throughput_native_tasks_per_second"]
                )["writer_count"],
                "throughput_by_level":{str(r["writer_count"]):
                    r["throughput_native_tasks_per_second"] for r in rows},
                "strict_capacity_maximum_claimed":False,
            }
        report={
            "schema":SCHEMA,"passed":True,
            "source_PR":100,
            "exact_base_commit":"e774b1b3694a1a2dfaa505b054888b80db495db1",
            "architecture":"BBY Q -> w4U -> QdU",
            "original_XI_U02_unchanged":True,
            "protected_files":159,"historical_hashes_unchanged":True,
            "original_SQLite_sources_unchanged":True,
            "new_primary_memory_authorities":0,
            "model_promoted":False,"cache_promoted":False,
            "no_merge_in_campaign":True,"apk_built":False,
            "source_models":{
                arm:{"verified_native_training_feedback":training[arm]["native_feedback_count"],
                     "native_weight_changes":training[arm]["native_parameter_changed"],
                     "original_checkpoint_snapshot_sha256":
                         sha256(json.dumps(saved[arm]["snapshot"],sort_keys=True).encode()).hexdigest()}
                for arm in ARMS},
            "protocol":split,
            "stress_levels":stress,
            "fault_rollback":failures,
            "abrupt_process_restarts":crashes,
            "request_id_collisions":collisions,
            "C13_opt_in_cache_serial_comparator":cached,
            "observed_limits":observed_limits,
            "total_campaign_wall_ms":round((time.perf_counter_ns()-started)/1e6,3),
            "limitations":[
                "Real native XI software simulator and SQLite-WAL on Linux only; no physical qubits, Android or quantum speedup measured.",
                "Concurrent writers use SQLite BEGIN IMMEDIATE and may serialize; correctness does not imply parallel throughput.",
                "All stress levels are predeclared finite synthetic fixtures; a maximum system capacity is NOT established.",
                "Reader audit uses read-only SQLite WAL snapshots and hashes; post-level original C09 view independently verifies semantics.",
                "Crash-before-commit models abrupt death inside a raw SQLite WAL transaction, not a crash inside the XI interpreter.",
                "Crash-after-commit kills host after completed original XI receipt; it does not test partial native execution on power failure.",
                "CPU and /proc I/O in concurrent steps are process aggregate, not attributable to any one writer; RSS is cumulative peak.",
                "Native child CPU from resource usage is approximate and includes interpreter/process startup.",
                "C13 cache is a process-global experimental monkeypatch and is intentionally NOT stress-tested concurrently, and is not promoted.",
                "No new knowledge, no generative open-domain validation and no claims of quantum hardware advantage.",
            ],
        }
        output.write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
        return report


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--out",type=Path,default=ROOT/"build/c15/stress.json")
    parser.add_argument("--crash-mode",choices=("before-commit","after-commit"))
    parser.add_argument("--crash-db",type=Path)
    args=parser.parse_args()
    if args.crash_mode:
        if args.crash_db is None:
            parser.error("--crash-db required for crash worker")
        _abrupt_crash(args.crash_mode,args.crash_db)
        return
    report=campaign(args.out)
    print(json.dumps({
        "passed":report["passed"],
        "levels":report["protocol"]["levels"],
        "throughput":{
            arm:{str(x["writer_count"]):x["throughput_native_tasks_per_second"]
                 for x in report["stress_levels"][arm]} for arm in ARMS},
        "rollbacks":{arm:d["injected_failures"] for arm,d in report["fault_rollback"].items()},
        "crash_recoveries":{arm:list(d) for arm,d in report["abrupt_process_restarts"].items()},
        "same_id_collisions":{arm:d["unique_persisted_native_task"] for arm,d in report["request_id_collisions"].items()},
        "cache_promoted":False,"model_promoted":False,
        "protected":159,"apk_built":False,
    },ensure_ascii=False))


if __name__=="__main__":
    main()
