#!/usr/bin/env python3
"""Examine the released E022 state without replaying its training.

Only XI receives questions, language and explicit disposable teaching turns.
This external examiner owns the expected answers, comparison and measurements.
"""
import argparse
import base64
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import statistics
import subprocess

ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[2]
spec = importlib.util.spec_from_file_location(
    "e022", ROOT.parent / "rephrase/tests/native-e022.py")
e022 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(e022)
CASES = json.loads((ROOT / "cases.json").read_text())
SHA = "33a2490be0d7a9252222991da1cd376e7cfb4ecb0014987c65d1b8b24278f20f"
CHECKPOINT = "ai/checkpoints/BBYQ_E022_Compositional_Requests_ES_EN.rvp.gz.b64"


def decode_checkpoint():
    data = gzip.decompress(base64.b64decode((REPO / CHECKPOINT).read_bytes()))
    assert hashlib.sha256(data).hexdigest() == SHA
    assert len(data) == 500410
    return data


def abstentions(language):
    return [e022.e021.SURFACE[4, language], e022.e021.SURFACE[11, language],
            e022.e017.conversation.ACTS[3, language], e022.e019.CLARIFY[language]]


def diagnostic_probes(binary, source, out, learned):
    out.mkdir(parents=True, exist_ok=True)
    state, program = out / "state.rvp", out / "conversation.xi"
    state.write_bytes(learned)
    program.write_bytes(subprocess.check_output(
        ["bash", str(source / "ai/xi/knowledge/link.sh"), "conversation"]))
    rows, groups = [], {}
    with e022.Session(binary, state, program) as session:
        for i in range(4):
            subject, other = f"diagnostico{i:03d}", f"alternodiagnostico{i:03d}"
            for lesson in [f"aprende que {subject} es clasea",
                           f"aprende que {subject} alcanza destino022",
                           f"aprende que {other} es claseb"]:
                raw, _ = session.request(lesson)
                assert e022.decode_result(raw) == e022.e021.SURFACE[1, 1]
            for case in CASES:
                question = case["text"].format(S=subject, OTHER=other)
                language, kind = case["language"], case["kind"]
                expected = (abstentions(language) if kind == "abstain" else
                            [e022.expected_answer(subject, language, kind)])
                before = e022.e021.knowledge(state)
                raw, elapsed = session.request(question, language)
                actual = e022.decode_result(raw)
                assert e022.e021.knowledge(state) == before, (
                    "a diagnostic query changed learned state", question)
                memory = e022.snapshot(state)[1]
                assert not any(memory.get(e022.N + j, 0)
                               for j in range(16, 128)), "rewrite scratch leaked"
                passed = actual in expected
                row = {"input": question, "language": language, "group": case["group"],
                       "output": actual, "expected": expected, "pass": passed, "ms": elapsed}
                rows.append(row)
                group = groups.setdefault(case["group"], {"correct": 0, "total": 0})
                group["correct"] += int(passed)
                group["total"] += 1
        metrics = session.metrics()
    # The same facts and references must remain usable after a process restart.
    with e022.Session(binary, state, program) as session:
        raw, _ = session.request("qué requiere diagnostico003")
        assert e022.decode_result(raw) == e022.e021.answer("diagnostico003", 1)
    return {"correct": sum(r["pass"] for r in rows), "total": len(rows),
            "groups": groups, "queries_do_not_write_knowledge": True,
            "restart": True, "metrics": metrics,
            "median_ms": statistics.median(r["ms"] for r in rows),
            "transcript": rows}


class ReleaseExaminer(e022.Examiner):
    def __init__(self, runtime, parent, out):
        e022.e018.Examiner.__init__(self, runtime, parent, out, expected_parent=SHA)
        for name in ["rephrase-teach", "rephrase-seal", "rephrase-audit"]:
            self.programs[name] = subprocess.check_output([
                "bash", str(ROOT.parent / "knowledge/link.sh"), name], text=True).split("\n", 1)[1]


def retention(runtime, binary, out, learned):
    out.mkdir(parents=True, exist_ok=True)
    parent = out / "released.rvp"
    parent.write_bytes(learned)
    e = ReleaseExaminer(runtime, parent, out)
    report = {}
    e022.smoke(e, binary, learned)
    report["e022_transfer"] = e022.transfer(e, binary, learned, 8)
    report["query_guards"] = e022.guards(e, binary, learned)
    e022.learning_controls(e, binary, learned)
    comparison = e022.comparisons(e, binary, learned)
    report["comparison"] = comparison["versions"]
    report["e021_transfer"] = e022.e021.text_transfer(e, binary, learned, 4)
    report["e021_topics"] = e022.e021.topic_and_integrity(e, binary, learned)
    report["e019_transfer"] = e022.e019.novel_dialogues(e, binary, learned, 4)
    report["e018_transfer"] = e022.e018.novel_dialogues(e, binary, learned, 20)
    e022.e018.controls(e, binary, learned)
    e022.e018.interfaces_and_rollback(e, binary, learned)
    e022.e018.retention(e, binary, learned)
    e022.e019.controls(e, binary, learned)
    e022.e019.restart_and_reset(e, binary, learned)
    scale_spec = importlib.util.spec_from_file_location(
        "e020", ROOT.parent / "scale/tests/native-e020.py")
    e020 = importlib.util.module_from_spec(scale_spec)
    scale_spec.loader.exec_module(e020)
    report["arithmetic_retention"] = e020.independent_text_exam(e, binary, learned)
    e.state.write_bytes(learned)
    e022.e017.audit(e)
    e.model_audit()
    e.run((ROOT.parent / "scale/audit.xi").read_text())
    e.run((ROOT.parent / "lingua/audit.xi").read_text())
    assert e.state.read_bytes() == learned
    report["checks"] = e.checks
    report["retrained"] = False
    report["published_state_unchanged"] = True
    (out / "raw.jsonl").write_text("".join(
        json.dumps(r, ensure_ascii=False) + "\n" for r in e.transcript))
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("runtime")
    parser.add_argument("session_binary")
    parser.add_argument("--baseline-root", type=Path)
    parser.add_argument("--out", type=Path, default=Path("evidence/e022-diagnostics"))
    parser.add_argument("--quick", action="store_true")
    args = parser.parse_args()
    out, binary = args.out.resolve(), Path(args.session_binary).resolve()
    out.mkdir(parents=True, exist_ok=True)
    encoded_before = (REPO / CHECKPOINT).read_bytes()
    learned = decode_checkpoint()
    report = {"checkpoint_sha256": SHA, "checkpoint_bytes": len(learned),
              "training_replayed": False, "new_released_world_facts": 0,
              "scope": "Regression fixtures from diagnosis, not an independent general-language benchmark",
              "source_sha256": {str(p.relative_to(REPO)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [ROOT / "cases.json", Path(__file__),
                                          ROOT.parent / "knowledge/read.xi",
                                          ROOT.parent / "lingua/clause.xi"]}}
    if args.baseline_root:
        report["before"] = diagnostic_probes(binary, args.baseline_root.resolve(), out / "before", learned)
        print("DIAGNOSIS_BEFORE", report["before"]["correct"], "/", report["before"]["total"], flush=True)
    report["after"] = diagnostic_probes(binary, REPO, out / "after", learned)
    failures = [r for r in report["after"]["transcript"] if not r["pass"]]
    assert not failures, failures
    print("DIAGNOSIS_AFTER", report["after"]["correct"], "/", report["after"]["total"], flush=True)
    if not args.quick:
        report["retention"] = retention(args.runtime, binary, out / "retention", learned)
    assert (REPO / CHECKPOINT).read_bytes() == encoded_before
    (out / "results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print("DIAGNOSIS_PASS", json.dumps({k: v for k, v in report.items()
          if k not in ["before", "after", "retention"]}, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
