#!/usr/bin/env python3
"""Independent factual-coverage diagnostic; no inference or learning outside XI."""
import argparse, hashlib, json, re, shutil, subprocess
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument("runtime"); p.add_argument("capsule_dir"); p.add_argument("output")
args = p.parse_args()
runtime = str(Path(args.runtime).resolve())
capsules = Path(args.capsule_dir).resolve()
out = Path(args.output).resolve(); out.mkdir(parents=True, exist_ok=True)
app = capsules / "BBY-Q.rxe"
seed = capsules / "controller.rvp"
app_hash = hashlib.sha256(app.read_bytes()).hexdigest()
seed_hash = hashlib.sha256(seed.read_bytes()).hexdigest()
cases = json.loads(Path(__file__).with_name("two-fact-cases.json").read_text())
rows, atomic, joint = [], [], []

def ask(state, query, language):
    return subprocess.check_output([runtime, "app-turn", str(app), str(state), str(state), language, query], text=True).strip()

def tokens(text):
    return set(re.findall(r"[a-z]+", text.lower()))

for case in cases:
    subject = case["subject"]
    state = out / (subject + ".rvp")
    shutil.copy2(seed, state)
    # Knowledge fixtures contain facts only, never an expected composite reply.
    for lesson in ["aprende que " + subject + " es animal", "aprende que " + subject + " requiere agua"]:
        response = ask(state, lesson, "es")
        rows.append({"phase": "knowledge_fixture", "subject": subject, "input": lesson, "output": response})
    for language, definition, requirement, combined, water in [
        ("es", "que es " + subject, "que requiere " + subject, case["es"], "agua"),
        ("en", "what is " + subject, "what does " + subject + " require", case["en"], "water"),
    ]:
        for query, fact in [(definition, "animal"), (requirement, water)]:
            response = ask(state, query, language)
            ok = {subject, fact}.issubset(tokens(response))
            atomic.append(ok)
            rows.append({"phase": "atomic_control", "subject": subject, "language": language, "input": query, "output": response, "fact_coverage": ok})
        response = ask(state, combined, language)
        ok = {subject, "animal", water}.issubset(tokens(response))
        joint.append(ok)
        rows.append({"phase": "two_fact_exam", "subject": subject, "language": language, "input": combined, "output": response, "two_fact_coverage": ok})
    state.unlink()
report = {
    "stage": "E025-two-fact-baseline", "subjects": len(cases),
    "atomic_fact_coverage": {"correct": sum(atomic), "total": len(atomic)},
    "two_fact_coverage": {"correct": sum(joint), "total": len(joint)},
    "immutable_app_sha256": app_hash, "immutable_seed_sha256": seed_hash,
    "immutable_sources_preserved": app_hash == hashlib.sha256(app.read_bytes()).hexdigest() and seed_hash == hashlib.sha256(seed.read_bytes()).hexdigest(),
    "new_model_checkpoint_published": False,
    "scope": "Factual token coverage in 48 fixed bilingual requests, not general language understanding or a complete hallucination metric. Facts taught only to disposable RVPC2 copies; each app-turn is a separate native process.",
    "cases_file": "ai/releases/e025/two-fact-cases.json",
}
(out / "results.json").write_text(json.dumps(report, indent=2) + "\n")
(out / "transcripts.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows))
print(json.dumps(report, indent=2), flush=True)
assert report["immutable_sources_preserved"], "Changed released capsule or seed"
assert all(atomic), "Atomic controls failed: inspect transcripts before interpreting joint coverage"
assert len(joint) == 48, "Incomplete diagnostic"
