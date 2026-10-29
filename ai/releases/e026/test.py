#!/usr/bin/env python3
"""Compare original and XI candidate using exact independently obtained answers."""
import argparse, hashlib, json, shutil, subprocess
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("runtime");p.add_argument("capsules");p.add_argument("output");a=p.parse_args()
runtime=str(Path(a.runtime).resolve());root=Path(a.capsules).resolve();out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True)
rows=[];scores={"development":{"baseline":0,"candidate":0,"total":48},"transfer":{"baseline":0,"candidate":0,"total":48}};controls=0
seed=root/"controller.rvp"
def ask(app,state,text,lang):
    return subprocess.check_output([runtime,"app-turn",str(app),str(state),str(state),lang,text],text=True).strip()
for split,prefix in [("development","bifaq"),("transfer","tulor")]:
    for i in range(24):
        subject=prefix+chr(97+i)
        for variant,app in [("baseline",root/"authentic-E025.rxe"),("candidate",root/"BBY-Q.rxe")]:
            state=out/"temporary.rvp";shutil.copy2(seed,state)
            ask(app,state,"aprende que "+subject+" es animal","es")
            ask(app,state,"aprende que "+subject+" requiere agua","es")
            for lang in ["es","en"]:
                one=ask(app,state,("que es " if lang=="es" else "what is ")+subject,lang)
                two=ask(app,state,("que requiere "+subject if lang=="es" else "what does "+subject+" require"),lang)
                expected=one+" "+two
                if lang=="es":
                    query="que es "+subject+(" y que requiere" if split=="development" else " y que necesita?")
                else:
                    query="what is "+subject+(" and what does it require" if split=="development" else " and what does it need?")
                answer=ask(app,state,query,lang)
                assert subject in one.lower() and "animal" in one.lower(),("Definition control",one)
                assert subject in two.lower() and ("agua" if lang=="es" else "water") in two.lower(),("Requirement control",two)
                ok=answer==expected;scores[split][variant]+=int(ok)
                rows.append({"split":split,"version":variant,"subject":subject,"language":lang,"input":query,"output":answer,"expected_from_atomic_queries":expected,"exact":ok})
            if variant=="candidate":
                # Querying missing facts must use the same atomic abstention, never a stale subject.
                for lang in ["es","en"]:
                    missing="ausente"+chr(97+i)
                    one=ask(app,state,("que es " if lang=="es" else "what is ")+missing,lang)
                    two=ask(app,state,("que requiere "+missing if lang=="es" else "what does "+missing+" require"),lang)
                    query=("que es "+missing+" y que requiere" if lang=="es" else "what is "+missing+" and what does it require")
                    answer=ask(app,state,query,lang)
                    assert answer==one+" "+two,("Unknown referent",query,answer,one,two)
                    controls+=1
                if i == 0:
                    # Negation/conflict uses the original native evidence policy.
                    ask(app,state,"aprende que "+subject+" no requiere agua","es")
                    for lang in ["es","en"]:
                        one=ask(app,state,("que es " if lang=="es" else "what is ")+subject,lang)
                        two=ask(app,state,("que requiere "+subject if lang=="es" else "what does "+subject+" require"),lang)
                        query=("que es "+subject+" y que requiere" if lang=="es" else "what is "+subject+" and what does it require")
                        assert ask(app,state,query,lang)==one+" "+two,("Negation or conflict lost",lang)
                        controls+=1
                    mixed="que es "+subject+" y que requiere otroreferente"
                    reference=ask(root/"authentic-E025.rxe",state,mixed,"es")
                    assert ask(app,state,mixed,"es")==reference,"Unsupported mixed subjects must retain the legacy refusal"
                    controls+=1
                audit=out/"audit.xi"
                audit.write_text("#!reverse-pc-machine-v1\nset r0 0\nset r1 0\nlabel scan\nset r7 8800000000000000000\nadd r7 r0\nload8 r2 $r7\nadd r1 r2\nadd r0 1\ncmp r0 512\njlt scan\nprint r1\nhalt\n")
                result=subprocess.check_output([runtime,"run",str(audit),str(state),str(state)],text=True)
                values=[json.loads(line)["value"] for line in result.splitlines() if line.startswith("{")]
                assert values==[0],("Composition scratch leak",values);controls+=1
            state.unlink()
report={"stage":"E026-TwoFacts-dev","scores":scores,"unknown_and_scratch_controls":controls,
"seed_sha256":hashlib.sha256(seed.read_bytes()).hexdigest(),"candidate_sha256":hashlib.sha256((root/"BBY-Q.rxe").read_bytes()).hexdigest(),
"scope":"Four engineered ASCII question forms in XI; exact concatenation of two native evidence-backed atomic answers. Transfer to new subjects within four engineered forms; synonyms normalized in XI, not a held-out language benchmark. No learned pattern claim. Separate native process per turn.",
"production_deployed":False}
(out/"results.json").write_text(json.dumps(report,indent=2)+"\n")
(out/"transcripts.jsonl").write_text("".join(json.dumps(x,ensure_ascii=False)+"\n" for x in rows))
print(json.dumps(report,indent=2),flush=True)
print(json.dumps({"sample":rows[:4],"transfer_examples":[r for r in rows if r["split"]=="transfer"][:4]},ensure_ascii=False),flush=True)
assert all(scores[s]["candidate"]==48 for s in scores),"Incomplete composition coverage"
