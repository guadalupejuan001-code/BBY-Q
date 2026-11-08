"""C14 precise host-side disjoint XI packet attribution, *not* gate timings.

The original XiSession.execute is called unmodified. Every synchronous
packet has exactly one owning category based on the actual bank and executable
pre-HALT calls. Mixed/transport packets are separate instead of duplicating
their whole wall time across multiple components. This instruments **XI
packet+IPC wall**, not exclusive gate CPU or real quantum hardware.
"""
from __future__ import annotations

from collections import defaultdict
import os
import time
from typing import Any

from integration.audit_u03_c00.profile import (
    invoked_calls, cpu_ms, io_counters, difference, vmhwm_kib, stats,
)
from integration.unified.common import C1


BANKS = ("C1", "VQC", "QRL", "QMemory", "Entity", "QChat", "XI-transport", "XI-mixed")


def packet_owner(bank: str, calls: list[str]) -> str:
    """Classify one *packet* once, never bill a multi-call packet repeatedly."""
    s = set(calls)
    if bank in ("language", "router", "text", "intent"):
        return "C1" if any(c.startswith(("c1_", "c2_", "uq_", "zero_")) for c in s) else "XI-transport"
    if bank == "memory":
        return "QMemory" if any(c.startswith("qm_") for c in s) else "XI-transport"
    if bank == "entity":
        return "Entity" if any(c.startswith("entity_") for c in s) else "XI-transport"
    if bank == "voice":
        return "QChat" if any(c.startswith(("qchat_", "entity_voice_")) for c in s) else "XI-transport"
    if bank == "v3":
        qrl = any(c == "qrl_step" or c.startswith("entity_qrl_") for c in s)
        vqc = any(c in ("vqc_sample", "select_agent", "forward",
                        "u2_apply", "u2_project", "u2_forward") or c.startswith("vqc_")
                  for c in s)
        if qrl and vqc:
            return "XI-mixed"
        if qrl:
            return "QRL"
        if vqc:
            return "VQC"
    return "XI-transport"


def bank_for_path(path: Any) -> str:
    name = str(path).rsplit("/", 1)[-1].lower()
    for prefix in ("language", "router", "text", "intent", "v3", "memory", "entity", "voice"):
        if name == prefix + ".rvp" or name.startswith(prefix + "."):
            return prefix
    return "unknown"


class ExclusivePacketTrace:
    """Context-scoped synchronous trace; no patches persist after __exit__.

    Not thread-safe globally; C14 never runs concurrent benchmarks while the
    instrumentation is attached. Concurrent SQLite test runs separately.
    """

    def __init__(self):
        self.events: list[dict[str, Any]] = []
        self._original: dict[str, Any] = {}
        self._names: dict[int, str] = {}
        self._active = False

    def __enter__(self):
        session_class = C1.XiSession
        self._cls = session_class
        self._original = {name: getattr(session_class, name)
                          for name in ("__init__", "execute", "save", "close")}
        original = self._original
        trace = self

        def init(instance, *args, **kwargs):
            start = time.perf_counter_ns()
            out = original["__init__"](instance, *args, **kwargs)
            bank = bank_for_path(args[1] if len(args)>1 else kwargs.get("image", "unknown"))
            trace._names[id(instance)] = bank
            trace.events.append({
                "kind": "open", "bank": bank,
                "duration_ms": (time.perf_counter_ns()-start)/1e6,
            })
            return out

        def execute(instance, source):
            bank=trace._names.get(id(instance), "unknown")
            calls=invoked_calls(source)
            owner=packet_owner(bank, calls)
            pid=instance.process.pid
            before_cpu=cpu_ms(pid)
            before_io=io_counters(pid)
            t0=time.perf_counter_ns()
            try:
                return original["execute"](instance,source)
            finally:
                t1=time.perf_counter_ns()
                after_cpu=cpu_ms(pid)
                after_io=io_counters(pid)
                trace.events.append({
                    "kind": "execute", "bank": bank, "owner": owner,
                    "start_ns": t0, "end_ns": t1,
                    "duration_ms": (t1-t0)/1e6,
                    "native_cpu_ms_approx": max(0,after_cpu-before_cpu)
                        if after_cpu is not None and before_cpu is not None else None,
                    "native_io_bytes": difference(after_io,before_io),
                    "native_vm_hwm_kib": vmhwm_kib(pid),
                    "source_bytes": len(source.encode("utf-8")),
                    "calls": calls,
                })

        def save(instance, target):
            t=time.perf_counter_ns()
            try:
                return original["save"](instance,target)
            finally:
                trace.events.append({
                    "kind":"save",
                    "bank":trace._names.get(id(instance),"unknown"),
                    "duration_ms":(time.perf_counter_ns()-t)/1e6,
                })

        def close(instance):
            t=time.perf_counter_ns()
            try:
                return original["close"](instance)
            finally:
                trace.events.append({
                    "kind":"close",
                    "bank":trace._names.get(id(instance),"unknown"),
                    "duration_ms":(time.perf_counter_ns()-t)/1e6,
                })

        session_class.__init__=init
        session_class.execute=execute
        session_class.save=save
        session_class.close=close
        self._active=True
        return self

    def __exit__(self,*exc):
        for name, function in self._original.items():
            setattr(self._cls,name,function)
        self._active=False

    def summarize(self) -> dict[str, Any]:
        rows=[x for x in self.events if x["kind"]=="execute"]
        sorted_rows=sorted(rows,key=lambda x:x["start_ns"])
        if any(a["end_ns"]>b["start_ns"] for a,b in zip(sorted_rows,sorted_rows[1:])):
            raise AssertionError("C14 host XI packet spans overlap; no exclusive attribution")
        classified=defaultdict(list)
        for row in rows:
            if row["owner"] not in BANKS:
                raise AssertionError("C14 invented an unsupported XI owner")
            classified[row["owner"]].append(row)
        wall_by_owner={name:round(sum(r["duration_ms"] for r in classified[name]),3)
                       for name in BANKS}
        total=sum(r["duration_ms"] for r in rows)
        if abs(sum(wall_by_owner.values())-total)>0.01:
            raise AssertionError("C14 attributed a packet more than once")
        io={"read_bytes":0, "write_bytes":0}
        for row in rows:
            for name in io:
                io[name]+=row["native_io_bytes"].get(name,0)
        by_kind={}
        for kind in ("open","save","close"):
            samples=[r["duration_ms"] for r in self.events if r["kind"]==kind]
            by_kind[kind]={"n":len(samples),"wall_ms":stats(samples)}
        calls=defaultdict(int)
        for row in rows:
            for call in row["calls"]:
                calls[call]+=1
        rss=[r["native_vm_hwm_kib"] for r in rows if r["native_vm_hwm_kib"] is not None]
        cpus=[r["native_cpu_ms_approx"] for r in rows if r["native_cpu_ms_approx"] is not None]
        return {
            "packets":len(rows),
            "nonoverlapping_host_packet_spans":True,
            "total_packet_wall_ms":round(total,3),
            "disjoint_packet_host_wall_ms_by_owner":wall_by_owner,
            "packet_count_by_owner":{name:len(classified[name]) for name in BANKS},
            "source_bytes_to_XI":sum(row["source_bytes"] for row in rows),
            "commands_pre_halt":dict(sorted(calls.items())),
            "approx_child_process_cpu_ms":round(sum(cpus),3) if cpus else None,
            "native_vm_hwm_kib_observed_max":max(rss) if rss else None,
            "native_io_bytes_observed":io,
            "xi_process_lifecycle":by_kind,
            "attribution":"exclusive synchronous execute-packet wall by owning XI bank/call; not exclusive gate/core CPU",
            "multi_call_packets_never_double_counted":True,
        }
