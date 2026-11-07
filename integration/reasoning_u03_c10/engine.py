"""C10: provenance-gated native XI/Zero reasoning in an isolated SQLite clone.

No inference is implemented here. A typed goal is planned as an ordered DAG,
using C09's single trustworthy U02-SQLite index. The native U02/REVERSE-PC
runtime is then invoked in a disposable restored *copy* to produce an actual
native proof or supported QMemory/VQC/Entity/QRL/QChat mission.

Refuse stale VQC projections, legacy C1 desynchronization, unknown user rules,
contradictory unverified overlays, missing XI proofs or concurrent source changes.
Never treat a VQC-derived class as a real-world fact, issue real actions, mutate
a live checkpoint, or proclaim a new quantum advantage.
"""
from __future__ import annotations

from hashlib import sha256
import sqlite3
from pathlib import Path
import tempfile

from integration.unified.common import encoded, key
from integration.unified.session import Session
from integration.memory_u03_c09.view import UnifiedMemoryView, verified_overlay
from .planner import SCHEMA, Goal, steps, ordered, original_native_prompt


def _present(case:dict) -> str:
    """Explicit, deterministic prompt to resolve a blocked prerequisite."""
    codes={
        "blocked_legacy_desynchronization":
            "El banco C1 y la memoria U02 no coinciden; sincroniza los datos antes de razonar.",
        "blocked_missing_VQC_observation":
            "Falta una observación VQC; proporciona una muestra para esta entidad.",
        "blocked_stale_VQC_projection":
            "La clasificación VQC está obsoleta; revalídala con el runtime original.",
        "blocked_missing_QMemory":
            "Falta una asociación QMemory supervisada; no se puede planificar esa misión.",
        "blocked_unverified_disagreement":
            "Se recibió una afirmación contradictoria sin verificación externa; solicita procedencia confiable.",
        "blocked_concurrent_change":
            "La memoria cambió durante la comprobación; vuelve a verificar la revisión.",
        "native_unproven":
            "El motor XI no produjo una prueba nativa de esta conclusión.",
    }
    return codes.get(case["status"],"No hay evidencia suficiente para concluir.")


def _report(goal, graph, *, status, memory=None, reason=None,
            native=None, source_unchanged=True, overlay_count=0,
            blocked_at=None, sandbox_executed=False):
    entry={
        "schema":SCHEMA,
        "goal":{"kind":goal.kind,"observation":goal.observation,
                "association":goal.association,"position":goal.position},
        "status":status,
        "plan":graph,
        "execution_order":ordered(graph),
        "blocked_at":blocked_at,
        "native":native,
        "memory_view_sha256":memory["view_sha256"] if memory else None,
        "original_revision":memory["revision"] if memory else None,
        "bank_identities":memory["bank_sha256"] if memory else None,
        "unverified_overlay_count":overlay_count,
        "source_unchanged_at_last_check":source_unchanged,
        "original_database_writes":0,
        "new_authoritative_memories":0,
        "native_goal_executed_in_disposable_copy":bool(native is not None or sandbox_executed),
        "user_actions_executed":False,
        "conclusions_are_real_world_truth":False,
        "checkpoint_or_model_training_performed":False,
    }
    if status.startswith("blocked_") or status=="native_unproven":
        entry["reason"]=reason or _present(entry)
        entry["clarification"]=_present(entry)
    if status in ("native_proof","native_plan"):
        entry["evidence_scope"]="U02 native XI proof/mission under synthetic original checkpoint, NOT real-world truth"
    return entry


def _record(memory:dict, kind:str, subject:str, predicate:str):
    options=[
        row for row in memory["facts"]
        if row["kind"]==kind and row["subject"]==key(subject)
        and row["predicate"]==predicate
    ]
    if len(options)>1:
        raise ValueError("C10 duplicate authoritative memory entries")
    return options[0] if options else None


def check_plan(goal:Goal, memory:dict, overlay=()):
    """Fail-closed preflight, with no native processes or source writes."""
    graph=steps(goal)
    ordered(graph)
    if memory.get("schema")!="BBYQ-U03-C09-read-only-memory-v1":
        raise ValueError("C10 requires verified original C09 memory view")
    if memory["new_memory_authorities"]!=0 or not memory["read_only"]:
        raise ValueError("C10 may not plan over additional memory authorities")
    if not memory["C1_synchronized_with_U02"]:
        return _report(goal,graph,status="blocked_legacy_desynchronization",
                       memory=memory,blocked_at="require_C1_sync")

    subject="observación "+goal.observation
    observation=_record(memory,"vqc_observation",subject,"input_sha256")
    projection=_record(memory,"vqc_projection",subject,"clase")
    if observation is None:
        return _report(goal,graph,status="blocked_missing_VQC_observation",
                       memory=memory,blocked_at="require_current_VQC_input")
    if projection is None or projection["status"]!="current" or (
            key(subject) in memory["stale_projections"]):
        return _report(goal,graph,status="blocked_stale_VQC_projection",
                       memory=memory,blocked_at="require_current_VQC_input")
    if projection.get("input_sha256")!=observation["value"] or (
            projection.get("bank_sha256")!=memory["bank_sha256"]["v3"]):
        raise ValueError("C10 inconsistent native VQC projection identity")
    # The projection is a *model-derived class*, not world truth.
    facts=[projection]
    if goal.kind=="plan_mission":
        rule=_record(memory,"qmemory_association",goal.association,"valor")
        if rule is None or rule["status"]!="recorded" or (
                rule["provenance"]!="explicit-user-supervision") or (
                type(rule["value"]) is not int or rule["value"] not in (0,1)):
            return _report(goal,graph,status="blocked_missing_QMemory",
                           memory=memory,blocked_at="require_QMemory_supervision")
        facts.append(rule)

    if not isinstance(overlay,(list,tuple)) or len(overlay)>12:
        raise ValueError("C10 requires <=12 typed untrusted overlay claims")
    verified=[verified_overlay(item) for item in overlay]
    for item in verified:
        for original in facts:
            if item["subject"]==original["subject"] and (
                    item["predicate"]==original["predicate"]):
                if item["value"]!=original["value"]:
                    return _report(
                        goal,graph,status="blocked_unverified_disagreement",
                        memory=memory,overlay_count=len(overlay),
                        blocked_at="check_untrusted_conflicts",
                    )
    return _report(goal,graph,status="ready_for_native",
                   memory=memory,overlay_count=len(overlay))


class Reasoner:
    def __init__(self, session):
        self.session=session
        self.view=UnifiedMemoryView(session)

    def plan(self, goal:Goal, *, overlay=()):
        """Request one native proof in a sandbox and return a provenance trace.

        After preflighting a coherent C09 view, make a coherent SQLite backup
        and reopen it using frozen U02. Revalidate the backup identity BEFORE
        executing any XI operation on it. Verify original source afterwards.
        No speculative execution can be committed to the caller database.
        """
        goal.validate()
        if self.session.db.in_transaction:
            raise RuntimeError("C10 cannot create a plan inside a writer transaction")
        original=self.view.snapshot()
        pre=check_plan(goal,original,overlay=overlay)
        if pre["status"]!="ready_for_native":
            return pre
        graph=pre["plan"]
        prompt=original_native_prompt(goal)
        with tempfile.TemporaryDirectory(prefix="bbyq-c10-isolated-xi-") as td:
            path=Path(td)/"disposable.sqlite"
            destination=sqlite3.connect(str(path),timeout=60,isolation_level=None)
            try:
                # SQLite backup captures one consistent WAL state and never
                # writes into the source U02 database.
                self.session.db.backup(destination)
            finally:
                destination.close()

            with Session(path) as replay:
                copied=UnifiedMemoryView(replay).snapshot()
                if copied["view_sha256"]!=original["view_sha256"]:
                    return _report(
                        goal,graph,status="blocked_concurrent_change",
                        memory=original,blocked_at="verify_C09_copy_is_same_revision",
                        overlay_count=pre["unverified_overlay_count"],
                        source_unchanged=False)
                # Treat the request ID namespace as untrusted as well; do
                # not accept an old receipt planted under our own ID.
                request_id="c10-disposable-"+sha256(
                    encoded({"goal":prompt,"revision":original["revision"],
                             "view":original["view_sha256"]})
                ).hexdigest()[:24]
                if replay.db.execute(
                    "SELECT 1 FROM unified_requests WHERE id=?",(request_id,)
                ).fetchone():
                    raise ValueError("C10 synthetic request ID collision in native copy")
                native_result=replay.turn(request_id,prompt)
                if not isinstance(native_result,dict):
                    raise AssertionError("Original XI must return a typed receipt")
                actions={row.get("operation") for row in native_result.get("trace",[])}
                result=next(
                    (row for row in reversed(native_result.get("results",[]))
                     if row.get("kind") in ("query","mission")),None
                )
                native={
                    "original_engine":"U02 frozen native XI/Zero",
                    "request_sha256":sha256(prompt.encode("utf-8")).hexdigest(),
                    "receipt_sha256":sha256(encoded(native_result)).hexdigest(),
                    "XI_operations":sorted(x for x in actions if isinstance(x,str)),
                    "copy_checkpoint_modified_only_in_disposable_sandbox":True,
                    "original_state_authoritative":False,
                }
                if goal.kind=="prove_alert":
                    good=bool(native_result.get("ok") and result
                              and result.get("kind")=="query"
                              and result.get("status")==1
                              and result.get("proof")
                              and "c1_encode_input/c1_next" in actions)
                    native["symbolic_proof_ids"]=result.get("proof",[]) if result else []
                    native["native_inference_status"]=result.get("status") if result else None
                    accepted="native_proof" if good else "native_unproven"
                else:
                    required={"qm_read","vqc_forward","entity_infer",
                              "entity_decide","qrl_step","entity_voice_check",
                              "qchat_encode/qchat_next"}
                    good=bool(native_result.get("ok") and result
                              and result.get("kind")=="mission"
                              and result.get("status")==1
                              and result.get("supported") is True
                              and result.get("voice",{}).get("faithful") is True
                              and required.issubset(actions))
                    native["policy_action"]=result.get("action") if good else None
                    native["goal_position"]=result.get("goal") if good else None
                    native["native_supported"]=result.get("supported") if result else False
                    native["native_action_is_real_world_command"]=False
                    accepted="native_plan" if good else "native_unproven"
            # Do not publish a conclusion based on data that changed while
            # the original native program was being evaluated in the copy.
            latest=self.view.snapshot()
            if latest["view_sha256"]!=original["view_sha256"]:
                return _report(
                    goal,graph,status="blocked_concurrent_change",
                    memory=original,blocked_at="reverify_source_unchanged",
                    source_unchanged=False,
                    sandbox_executed=True,
                    overlay_count=pre["unverified_overlay_count"])
            return _report(
                goal,graph,status=accepted,memory=original,native=native,
                overlay_count=pre["unverified_overlay_count"],
                blocked_at="run_original_XI_C1_Zero_proof" if accepted=="native_unproven" and goal.kind=="prove_alert"
                else "run_original_XI_QMemory_VQC_Entity_QRL_QChat" if accepted=="native_unproven"
                else None,
            )
