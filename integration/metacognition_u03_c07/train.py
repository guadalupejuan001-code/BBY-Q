#!/usr/bin/env python3
"""C07 native XI epistemic learning with validation-only calibration.

All three 3-class heads are trained by the unchanged XI interpreter.
Evidence provenance features contain NO supervised class labels, and native
inference receives neither a teacher label nor a gold decision. Each
ablation gets the same epochs/examples/native parameter count.

Calibrate softmax temperature and the selective-answer threshold ONLY on
validation, before opening the disjoint heldout test once.
"""
from __future__ import annotations

import argparse
from hashlib import sha256
import json
import math
from pathlib import Path
import random
import shutil
import struct
import tempfile
import time

from integration.audit_u03_c00.profile import ROOT, freeze_assets, apk_files
from integration.semantic_u03_c06.train import C1, C1Build, VOCAB, OUTPUT
from .dataset import split, verify_disjoint, LABELS
from .features import FEATURE_COUNT, CLASSES, MODES, SCHEMA, evidence_features, is_unsupported

BASE = 8150000000013000000
NATIVE = ROOT / "ai/xi/c07/epistemic-head.xi"
TEMPERATURES = (0.25,0.35,0.5,0.7,1.0,1.5,2.0,3.0,4.0)
THRESHOLDS = (0.4,0.45,0.5,0.55,0.6,0.65,0.7,0.75,0.8,0.85,0.9,0.95,0.99)


def stage_vector(values):
    if len(values) != FEATURE_COUNT:
        raise ValueError("C07 malformed training vector")
    return "".join(f"fstore {BASE+256+8*i} {float(v):.17g}\n"
                   for i,v in enumerate(values))


def train_epoch(model, data, mode, epoch):
    cases = list(data)
    random.Random(2026110707 + epoch).shuffle(cases)
    for offset in range(0, len(cases), 48):
        program = "".join(
            stage_vector(evidence_features(row.query, row.evidence, mode=mode))
            + f"store64 {BASE+8} {row.label}\ncall c07_train\n"
            for row in cases[offset:offset+48]
        )
        model.run(program)
    learned = struct.unpack("<2q",model.memory(BASE,16))
    seen = learned[0]
    if seen != epoch*len(data) or seen < 1:
        raise AssertionError("C07 XI native update count unexpected")
    return {"seen": seen, "training_examples":len(data),
            "mistakes":struct.unpack("<q",model.memory(BASE+24,8))[0]}


def infer(model, examples, mode):
    result = []
    for offset in range(0,len(examples),36):
        batch = examples[offset:offset+36]
        # Do not stage BASE+8 or any label/address from the supervision bank.
        program = "".join(
            stage_vector(evidence_features(row.query,row.evidence,mode=mode))
            + "call c07_predict\n"
            + f"mem_materialize {BASE+16} 8\n"
            + f"mem_materialize {BASE+64} 24\n"
            for row in batch
        )
        events = model.run(program)
        raw = [event for event in events if event["type"]=="memory_materialization"]
        if len(raw)!=2*len(batch):
            raise AssertionError("XI C07 incomplete decisions or score vectors")
        for i in range(len(batch)):
            label = struct.unpack("<q",bytes.fromhex(raw[2*i]["hex"]))[0]
            scores = struct.unpack("<3d",bytes.fromhex(raw[2*i+1]["hex"]))
            if label not in (0,1,2) or not all(math.isfinite(v) for v in scores):
                raise AssertionError("XI C07 emitted invalid metacognitive evidence")
            if label != max(range(3),key=lambda j:scores[j]):
                raise AssertionError("XI decision does not equal its native maximum score")
            result.append({"predicted":label,"scores":[float(v) for v in scores]})
    return result


def probabilities(scores, temperature):
    if temperature<=0 or not math.isfinite(temperature):
        raise ValueError("C07 invalid calibration temperature")
    logits = [v/temperature for v in scores]
    hi = max(logits)
    e = [math.exp(v-hi) for v in logits]
    z = sum(e)
    return [v/z for v in e]


def quality(examples, predictions, temperature):
    n=len(examples)
    if n==0 or len(predictions)!=n:
        raise ValueError("C07 quality mismatch")
    confusion=[[0,0,0] for _ in range(3)]
    brier = nll = 0.
    bins=[[] for _ in range(10)]
    correct=0
    for row, pred in zip(examples, predictions):
        predicted=pred["predicted"]
        gold=row.label
        confusion[gold][predicted]+=1
        correct+=int(gold==predicted)
        p=probabilities(pred["scores"],temperature)
        brier+=sum((p[j]-(1 if j==gold else 0))**2 for j in range(3))
        nll+=-math.log(max(p[gold],1e-15))
        confidence=max(p)
        bins[min(9,int(confidence*10))].append((confidence,float(predicted==gold)))
    f1s=[]
    for i in range(3):
        tp=confusion[i][i]
        fp=sum(confusion[j][i] for j in range(3) if j!=i)
        fn=sum(confusion[i][j] for j in range(3) if j!=i)
        denom=2*tp+fp+fn
        f1s.append(2*tp/denom if denom else 0.)
    ece=sum(len(bucket)/n*abs(
        sum(p for p,_ in bucket)/len(bucket)-sum(y for _,y in bucket)/len(bucket)
    ) for bucket in bins if bucket)
    return {
        "accuracy":round(correct/n,6), "correct":correct, "total":n,
        "macro_f1":round(sum(f1s)/3,6),
        "brier_multiclass":round(brier/n,6),
        "negative_log_likelihood":round(nll/n,6),
        "ECE_10_bins":round(ece,6),
        "confusion_rows_gold":confusion,
    }


def guarded_action(row, pred, temperature, threshold):
    if is_unsupported(row.query,row.evidence):
        return 1
    probabilities_=probabilities(pred["scores"],temperature)
    outcome=pred["predicted"]
    # On supported in-domain evidence, a low-confidence answer must not be
    # presented as an established fact.
    if outcome==0 and max(probabilities_) < threshold:
        return 1
    return outcome


def selective_quality(rows, predictions, temperature, threshold):
    actual=[guarded_action(row,pred,temperature,threshold)
            for row,pred in zip(rows,predictions)]
    n=len(rows)
    unsafe=sum(out==0 and row.label!=0 for out,row in zip(actual,rows))
    unjustified=sum(out==1 and row.label==0 for out,row in zip(actual,rows))
    conflicts_missed=sum(out!=2 and row.label==2 for out,row in zip(actual,rows))
    answered=sum(out==0 for out in actual)
    correctly_answered=sum(out==0 and row.label==0 for out,row in zip(actual,rows))
    return {
        "total":n, "answered":answered,
        "answered_coverage":round(answered/n,6),
        "correct_answered":correctly_answered,
        "unsafe_answers":unsafe,
        "risk_among_answered":round(unsafe/answered,6) if answered else None,
        "unjustified_abstentions":unjustified,
        "conflicts_missed":conflicts_missed,
        "correct_actions":sum(out==row.label for out,row in zip(actual,rows)),
    }


def select_temperature(validation, prediction):
    # NLL selection based ONLY on validation data, not heldout test.
    scores=[(quality(validation,prediction,t)["negative_log_likelihood"],t)
            for t in TEMPERATURES]
    return min(scores)[1]


def select_threshold(validation, prediction, temperature):
    # Objective: at most 2% unsafe answers on validation and maximum
    # justified coverage, with deterministic tie-break.
    ranked=[]
    for threshold in THRESHOLDS:
        m=selective_quality(validation,prediction,temperature,threshold)
        if m["unsafe_answers"] <= max(0,int(.02*len(validation))):
            ranked.append((-m["correct_answered"],m["unsafe_answers"],threshold))
    return min(ranked)[2] if ranked else 0.99


def native_validation(checkpoint, data, mode):
    with C1.Model(checkpoint, ["<pad>"], ["<eos>"]) as model:
        model.library += "\n"+NATIVE.read_text()
        return infer(model,data,mode)


def learn_variant(mode, train, validation, directory, epochs):
    initial=Path(directory)/(mode+"-initial.rvp")
    C1.birth(initial,4096)
    history=[]
    best=None
    with C1.Model(initial, ["<pad>"], ["<eos>"]) as model:
        model.library += "\n"+NATIVE.read_text()
        for epoch in range(1,epochs+1):
            details=train_epoch(model,train,mode,epoch)
            predicted=infer(model,validation,mode)
            score=quality(validation,predicted,1.)
            file=Path(directory)/f"{mode}-epoch-{epoch}.rvp"
            model.s.save(file)
            history.append({"epoch":epoch, "train":details,"validation_uncalibrated":score})
            rank=(score["macro_f1"],score["accuracy"],-score["negative_log_likelihood"])
            if best is None or rank>best["rank"]:
                best={"rank":rank, "epoch":epoch,"path":file}
    if best is None:
        raise AssertionError("C07 did not train native XI head")
    val_predictions=native_validation(best["path"],validation,mode)
    if quality(validation,val_predictions,1.)!=history[best["epoch"]-1]["validation_uncalibrated"]:
        raise AssertionError("C07 selected native checkpoint failed to reproduce validation")
    t=select_temperature(validation,val_predictions)
    threshold=select_threshold(validation,val_predictions,t)
    return {
        "mode":mode, "path":best["path"], "epoch":best["epoch"],
        "checkpoint_sha256":sha256(best["path"].read_bytes()).hexdigest(),
        "epochs":history,
        "validation_original":quality(validation,val_predictions,1.),
        "validation_calibrated":quality(validation,val_predictions,t),
        "validation_selective":selective_quality(validation,val_predictions,t,threshold),
        "temperature":t,"answer_threshold":threshold,
    }


def campaign(output, epochs=8):
    if not 1<=epochs<=20:
        raise ValueError("C07 epochs must be 1..20")
    before,apks=freeze_assets(),apk_files()
    corpus=verify_disjoint()
    train, validation=split("train"),split("validation")
    C1Build.main()
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter_ns()
    with tempfile.TemporaryDirectory(prefix="bbyq-c07-epistemic-trained-") as tmp:
        chosen=[learn_variant(mode,train,validation,tmp,epochs) for mode in MODES]
        # Validation selected all epochs, calibration and thresholds.
        # Only now is the heldout generator invoked ONCE.
        test=split("test")
        for model in chosen:
            predictions=native_validation(model["path"],test,model["mode"])
            model["heldout_raw"]=quality(test,predictions,1.)
            model["heldout_calibrated"]=quality(test,predictions,model["temperature"])
            model["heldout_selective"]=selective_quality(
                test,predictions,model["temperature"],model["answer_threshold"])
            model["test_predictions_sha256"]=sha256(json.dumps(
                predictions,sort_keys=True).encode()).hexdigest()
        main=next(v for v in chosen if v["mode"]=="provenance")
        dest=output.parent/"epistemic-trained.rvp"
        shutil.copyfile(main["path"],dest)
        if sha256(dest.read_bytes()).hexdigest()!=main["checkpoint_sha256"]:
            raise AssertionError("C07 stored native checkpoint differs from selected version")
        reloaded=native_validation(dest,validation,"provenance")
        if quality(validation,reloaded,main["temperature"])!=main["validation_calibrated"]:
            raise AssertionError("C07 saved native XI calibration not reproducible")
        if freeze_assets()!=before or apk_files()!=apks:
            raise AssertionError("C07 touched older checkpoint or generated APK")
        report={
            "schema":SCHEMA,
            "passed":True,
            "native_XI_trained_and_reopened":True,
            "model_scope":"synthetic evidence/uncertainty task only; not a general truth oracle",
            "dataset":corpus,"epochs":epochs,
            "mode_selected":"provenance",
            "prior_C06_checkpoint_unmodified":True,
            "frozen_asset_count":len(before),
            "frozen_asset_sha256_unchanged":True,
            "no_test_labels_in_training":True,
            "calibration_and_threshold_selected_on_validation_only":True,
            "test_seen_only_after_selection":True,
            "source_sha256":sha256(NATIVE.read_bytes()).hexdigest(),
            "trained_checkpoint_sha256":main["checkpoint_sha256"],
            "trained_checkpoint_file":"epistemic-trained.rvp",
            "checkpoint_format":"REVERSE-PC RVPC2",
            "modes":[{k:v for k,v in model.items() if k!="path"} for model in chosen],
            "limitations":[
                "Provenance records use synthetic content hashes, not independent cryptographic source authentication.",
                "A rule-based feature extractor marks trusted/fresh evidence before the XI head learns a decision.",
                "Calibrated probabilities estimate classifier correctness in the synthetic task, not probability real-world claims are true.",
                "The training/validation/test share the same generation policy but use different subjects and sources.",
                "The evidence gate is only safe for the declared three-predicate laboratory schema.",
                "Unfamiliar world facts and conversational contexts require external evidence; no general intelligence is demonstrated.",
            ],
            "apk_built":False,
            "wall_ms":round((time.perf_counter_ns()-started)/1e6,3),
        }
        output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n")
    return report


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--epochs",type=int,default=8)
    ap.add_argument("--out",type=Path,default=ROOT/"build/c07/training-report.json")
    args=ap.parse_args()
    result=campaign(args.out,epochs=args.epochs)
    print(json.dumps({
        "passed":True,
        "validation":{m["mode"]:m["validation_calibrated"]["accuracy"] for m in result["modes"]},
        "heldout":{m["mode"]:m["heldout_calibrated"]["accuracy"] for m in result["modes"]},
        "selective":{m["mode"]:m["heldout_selective"] for m in result["modes"]},
        "checkpoint":result["trained_checkpoint_sha256"],
        "prior_checkpoints_untouched":True,"apk_built":False,
    },ensure_ascii=False))


if __name__=="__main__":
    main()
