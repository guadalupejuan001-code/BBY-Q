#!/usr/bin/env python3
"""Run complete native-XI learning campaigns for three explicitly named designs.

Python schedules jobs, records metrics and saves evidence. Feature maps, gates,
gradients, labels, policies, trajectories and updates all execute in XI/Ether.
The blocked4 control changes only preparation/edges in the current XI learner.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import gzip
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import queue
import statistics
import subprocess
import sys
import time
import traceback
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
A = 8140000000000000000
VARIANTS = ("historical4", "blocked4", "connected1000")
SEEDS = (173, 941, 2026)
TASKS = (("vqc", "linear"), ("vqc", "dense"), ("qrl", "line_easy"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def sha(path):
    return digest(Path(path).read_bytes())


def publish(path, value):
    path = Path(path)
    pending = path.with_suffix(path.suffix + ".pending")
    pending.write_text(json.dumps(value, indent=2) + "\n")
    pending.replace(path)


def module(relative, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def prepared_blocks(label):
    return ("set r2 0\nlabel " + label + "\nmov r4 r15\nadd r4 r2\n"
            "qprepare $r4 4\nadd r2 4\ncmp r2 1000\njlt " + label)


def experiment(args, variant=None):
    variant = variant or args.variant
    historical = variant == "historical4"
    relative = "integration/quantum3/campaign.py" if historical else "integration/quantum1000/campaign.py"
    m = module(relative, "campaign_" + variant)
    settings = SimpleNamespace(runtime=args.runtime, session_binary=None, step_budget=10000000,
        agent=args.agent, task=args.task, seed=args.seed, episodes=args.episodes,
        eval_size=args.samples, classical=False, output=str(Path(args.output) / "transport"),
        resume=False, entangler="cz", joint_mode="independent")
    e = m.Experiment(settings)
    birth = (m.XI / "birth.xi").read_text()
    if variant == "blocked4":
        assert e.lib.count("qmps $r15 1000") == 1
        assert birth.count("qmps $r15 1000") == 1
        e.lib = e.lib.replace("qmps $r15 1000", prepared_blocks("comparison_prepare_blocks"))
        birth = birth.replace("qmps $r15 1000", prepared_blocks("comparison_birth_blocks"))
        marker = "label chain_entanglers\n"
        assert e.lib.count(marker) == 1
        # Omit exactly the 249 edges 3->4, 7->8, ..., 995->996.
        e.lib = e.lib.replace(marker, marker + "mov r6 r2\nmod r6 4\ncmp r6 3\nje edge_complete\n")
    return m, e, birth


def structure_probe(e, checkpoint, variant):
    with e.Session(e.binary, checkpoint) as s:
        features = "\n".join(f"fstore {A+300000+8*q} {0.008+0.00001*(q%11):.17g}" for q in range(1000))
        body = features + "\nqtrace reset\n"
        for role in (0, 1):
            body += f"store64 {A} {role}\ncall select_agent\ncall forward\n"
        body += "qtrace report\nstats"
        if variant == "connected1000":
            body += "\nqmpsinfo 5000\nqmpsinfo 7000"
        events, _ = s.execute(e.source(body))
    trace = next(x for x in events if x["type"] == "quantum_trace")
    stats = next(x for x in events if x["type"] == "stats")
    connected = variant == "connected1000"
    assert trace["distinct_rotated_qubits"] == trace["distinct_observed_qubits"] == 2000
    assert trace["preparations"] == (2 if connected else 500)
    assert trace["max_prepared_block"] == (1000 if connected else 4)
    assert trace["distinct_two_qubit_edges"] == (1998 if connected else 1500)
    assert stats["components"] == (2 if connected else 500)
    assert stats["largest_component"] == (1000 if connected else 4)
    registers = [x for x in events if x["type"] == "mps_register"]
    if connected:
        assert len(registers) == 2 and all(x["nonproduct_bipartitions"] == 999 for x in registers)
    return {"trace": trace, "stats": stats, "registers": registers,
            "note": "Probe uses a fresh unsaved session; training parameters are not changed."}


def evaluate(m, e, checkpoint, seed, samples, split, zeroed=False):
    checkpoint_hash = sha(checkpoint)
    prior_seed, prior_size = e.args.seed, e.args.eval_size
    e.args.seed, e.args.eval_size = seed, samples
    observations = []
    with e.Session(e.binary, checkpoint) as s:
        before = s.metrics()
        for i in range(samples):
            events, elapsed = s.execute(e.source(e.stage(split, i, ablate=zeroed)))
            observations.append(dict(m.metrics(events), elapsed_ms=elapsed, case=i))
        usage = s.metrics()
    e.args.seed, e.args.eval_size = prior_seed, prior_size
    assert sha(checkpoint) == checkpoint_hash, "Evaluation mutated a source checkpoint"
    if e.args.agent == "vqc":
        correctness = [int(x["probability"] >= .5) == int(x["label"]) for x in observations]
        brier = statistics.mean((x["probability"]-x["label"])**2 for x in observations)
    else:
        correctness = [bool(x["success"]) for x in observations]
        brier = None
    successes = sum(correctness)
    return {"seed": seed, "samples": samples, "successes": successes,
            "rate": successes/samples, "wilson95": m.wilson(successes, samples),
            "brier": brier, "mean_reward": statistics.mean(x["reward"] for x in observations) if e.args.agent == "qrl" else None,
            "decisions": sum(x.get("decisions", 1) for x in observations),
            "native_cpu_ms": usage["cpu_ms"]-before["cpu_ms"],
            "median_transport_ms": statistics.median(x["elapsed_ms"] for x in observations),
            "peak_rss_kib": usage["peak_rss_kib"], "correctness": correctness,
            "observations": observations}


def worker(args):
    if args.cpu is not None:
        os.sched_setaffinity(0, {args.cpu})
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    if (out / "result.json").exists():
        raise RuntimeError("Result already exists; retain it and choose another output")
    m, e, birth = experiment(args)
    protocol = {"variant": args.variant, "agent": args.agent, "task": args.task,
        "training_seed": args.seed, "evaluation_seed": args.test_seed,
        "episodes": args.episodes, "holdout_samples_per_split": args.samples,
        "initial_and_zeroed_samples_per_split": min(32, args.samples),
        "runtime_binary_sha256": sha(e.binary), "assembled_xi_library_sha256": digest(e.lib.encode()),
        "birth_sha256": digest(birth.encode()), "source_sha256": {p: sha(m.XI/p) for p in e.source_names},
        "cpu_affinity": sorted(os.sched_getaffinity(0)), "native_algorithms": "XI/Ether",
        "entangler": "cnot" if args.variant == "historical4" else "cz",
        "angle_gradients_per_decision": 4 if args.variant == "historical4" else 1000,
        "qubits_per_agent": 1000, "classical_simulation": True,
        "started_utc": datetime.now(timezone.utc).isoformat()}
    train_seeds = {m.sample_seed(args.seed, "train", i) for i in range(args.episodes)}
    holdout_seeds = {m.sample_seed(args.test_seed, split, i) for split in ("iid", "ood") for i in range(args.samples)}
    assert not train_seeds & holdout_seeds
    protocol["train_holdout_seed_overlap"] = False
    publish(out / "conditions.json", protocol)
    (out / "assembled-library.xi").write_text(e.lib)
    (out / "assembled-birth.xi").write_text(birth)
    empty = out / "empty.rvp"
    subprocess.run([str(e.cli), "init", str(empty)], check=True, capture_output=True)
    initial = out / "checkpoint-00000.rvp"
    with e.Session(e.binary, empty) as s:
        s.execute(birth + "\n" + e.lib)
        initial_model = e.model_state(s)
        s.save(initial)
    structural = structure_probe(e, initial, args.variant)
    publish(out / "structure.json", structural)
    control_samples = min(32, args.samples)
    initial_results = {split: evaluate(m, e, initial, args.test_seed, control_samples, split) for split in ("iid", "ood")}
    records, milestones = [], []
    checkpoints = [initial]
    with e.Session(e.binary, initial) as s:
        before = s.metrics()
        started = time.perf_counter()
        with (out / "training.jsonl").open("w") as journal:
            for index in range(args.episodes):
                events, elapsed = s.execute(e.source(e.stage("train", index, training=True)))
                record = dict(m.metrics(events), episode=index+1, transport_ms=elapsed)
                records.append(record)
                journal.write(json.dumps(record) + "\n")
                journal.flush()
                if (index+1) % 100 == 0:
                    print(json.dumps({"progress": index+1, "variant": args.variant, "agent": args.agent,
                        "task": args.task, "seed": args.seed,
                        "recent_episode_ms": statistics.median(x["episode_ms"] for x in records[-100:])}), flush=True)
                if index+1 in {100, args.episodes}:
                    checkpoint = out / f"checkpoint-{index+1:05d}.rvp"
                    s.save(checkpoint)
                    checkpoints.append(checkpoint)
                    milestones.append({"episodes": index+1, "checkpoint_sha256": sha(checkpoint),
                                       "model": e.model_state(s), "usage": s.metrics()})
        elapsed_seconds = time.perf_counter()-started
        usage = s.metrics()
    final = checkpoints[-1]
    final_model = milestones[-1]["model"]
    assert final_model["training_episodes_in_checkpoint"] == args.episodes
    assert final_model["readout_parameters_changed"] == 1000
    if args.variant != "historical4" and args.episodes >= 100:
        assert final_model["rotation_parameters_changed"] == 1000
    assert len(records) == args.episodes
    trained_results = {split: evaluate(m, e, final, args.test_seed, args.samples, split) for split in ("iid", "ood")}
    zeroed_results = {split: evaluate(m, e, final, args.test_seed, control_samples, split, zeroed=True) for split in ("iid", "ood")}
    result = {"conditions": protocol, "initial_model": initial_model, "structure": structural,
        "initial": initial_results, "trained": trained_results, "observations_zeroed": zeroed_results,
        "training": {"episodes": len(records), "decisions": sum(x.get("decisions", 1) for x in records),
            "native_episode_total_ms": sum(x["episode_ms"] for x in records),
            "native_update_total_ms": sum(x["update_ms"] for x in records),
            "native_cpu_ms": usage["cpu_ms"]-before["cpu_ms"],
            "transport_total_ms": sum(x["transport_ms"] for x in records),
            "median_episode_ms": statistics.median(x["episode_ms"] for x in records),
            "peak_rss_kib": usage["peak_rss_kib"], "wall_seconds_including_checkpoint_io": elapsed_seconds},
        "milestones": milestones,
        "finished_utc": datetime.now(timezone.utc).isoformat()}
    hashes = []
    for path in checkpoints:
        compressed = path.with_suffix(path.suffix + ".gz")
        with compressed.open("wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as z:
            z.write(path.read_bytes())
        hashes.append({"file": compressed.name, "sha256": sha(compressed), "decompressed_sha256": sha(path)})
    log = out / "training.jsonl"
    with (out / "training.jsonl.gz").open("wb") as raw, gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as z:
        z.write(log.read_bytes())
    result["checkpoints"] = hashes
    result["journal_sha256"] = sha(log)
    result["compressed_journal_sha256"] = sha(out / "training.jsonl.gz")
    publish(out / "result.json", result)
    print(json.dumps({"completed": str(out), "variant": args.variant, "agent": args.agent,
        "task": args.task, "seed": args.seed,
        "iid": trained_results["iid"]["rate"], "ood": trained_results["ood"]["rate"],
        "training_cpu_ms": result["training"]["native_cpu_ms"]}), flush=True)


def run_all(args):
    out = Path(args.output).resolve()
    out.mkdir(parents=True, exist_ok=True)
    cpus = sorted(os.sched_getaffinity(0))[:args.workers]
    protocol = {"fixed_before_campaigns": True, "training_seeds": SEEDS, "tasks": TASKS,
        "variants": VARIANTS, "episodes_per_campaign": args.episodes,
        "holdout_samples_per_split": args.samples, "holdout_seed": args.test_seed,
        "initial_and_zeroed_samples_per_split": min(32, args.samples),
        "primary_metric": "held-out accuracy VQC; stochastic success rate QRL",
        "controls": "blocked4 versus connected1000 keeps CZ, all-angle gradients, data, rates, initialization and episode budgets fixed",
        "historical_comparison": "historical4 preserves CNOT and four selected angle gradients; differences are not attributable only to connectivity",
        "measurement": "same single-thread binary; paired variants share CPU affinity; CPU time excludes separate evaluation sessions",
        "excluded_claims": ["quantum hardware", "universal quantum advantage", "general superiority from synthetic tasks"],
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "harness_sha256": sha(__file__), "parallel_lanes": len(cpus)}
    if (out / "PROTOCOL.json").exists():
        raise RuntimeError("Protocol/output exists; choose a new campaign directory")
    publish(out / "PROTOCOL.json", protocol)
    groups = queue.Queue()
    for agent, task in reversed(TASKS):
        for seed in SEEDS:
            groups.put((agent, task, seed))

    def lane(cpu):
        while True:
            try:
                agent, task, seed = groups.get_nowait()
            except queue.Empty:
                return
            offset = SEEDS.index(seed)
            order = VARIANTS[offset:] + VARIANTS[:offset]
            for variant in order:
                destination = out / f"{agent}-{task}-seed{seed}-{variant}"
                command = [sys.executable, str(Path(__file__).resolve()), "worker", "--runtime", args.runtime,
                    "--output", str(destination), "--agent", agent, "--task", task, "--seed", str(seed),
                    "--variant", variant, "--episodes", str(args.episodes), "--samples", str(args.samples),
                    "--test-seed", str(args.test_seed), "--cpu", str(cpu)]
                destination.mkdir(parents=True, exist_ok=True)
                with (destination / "worker.log").open("w") as log:
                    completed = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
                if completed.returncode:
                    raise RuntimeError(f"Campaign failed: {destination}; inspect worker.log")
                print(json.dumps({"completed_campaign": destination.name}), flush=True)
            groups.task_done()

    with ThreadPoolExecutor(max_workers=len(cpus)) as executor:
        futures = [executor.submit(lane, cpu) for cpu in cpus]
        for future in futures:
            future.result()
    print(json.dumps({"all_completed": True, "campaigns": 27}), flush=True)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("mode", choices=("worker", "all"))
    p.add_argument("--runtime", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--variant", choices=VARIANTS, default="connected1000")
    p.add_argument("--agent", choices=("vqc", "qrl"), default="vqc")
    p.add_argument("--task", default="linear")
    p.add_argument("--seed", type=int, default=173)
    p.add_argument("--test-seed", type=int, default=827391)
    p.add_argument("--episodes", type=int, default=1000)
    p.add_argument("--samples", type=int, default=128)
    p.add_argument("--cpu", type=int)
    p.add_argument("--workers", type=int, default=6)
    args = p.parse_args()
    if min(args.episodes, args.samples, args.workers) < 1:
        p.error("positive campaign sizes required")
    if args.mode == "worker":
        worker(args)
    else:
        run_all(args)


if __name__ == "__main__":
    main()
