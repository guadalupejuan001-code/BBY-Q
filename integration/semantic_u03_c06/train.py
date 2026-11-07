#!/usr/bin/env python3
"""C06: real supervised XI training + independent split/ablation validation.

Three independent XI models: ordered C05 features, no-order ablation, and
a raw surface bag baseline.  Only train labels enter c06_train; validation
chooses checkpoint, and the heldout test is opened only AFTER all selections.
Models are saved to build/c06, never over U02 U03 checkpoints.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import random
import shutil
import struct
import tempfile
import time

from integration.audit_u03_c00.profile import ROOT, freeze_assets, apk_files
from integration.unified.common import C1
from integration.sequence2 import build as C1Build
from .dataset import LABELS, split, verify_disjoint
from .features import features, FEATURES, CLASSES, HEAD_SCHEMA

NATIVE = ROOT / "ai/xi/c06/semantic-head.xi"
B = 8150000000012000000
VOCAB = ["<pad>"]
OUTPUT = ["<eos>"]
MODES = ("semantic", "no-order", "bag")


def stage_features(feat):
    if len(feat) != FEATURES:
        raise ValueError("C06 invalid feature length")
    return "".join(f"fstore {B + 256 + 8*i} {float(v):.17g}\n"
                   for i, v in enumerate(feat))


def train_epoch(model, examples, mode, *, epoch: int):
    ordered = list(examples)
    random.Random(2026110706 + epoch).shuffle(ordered)
    # One native XI training packet for every 48 samples; teacher targets
    # never enter the C1 tokenization or inference-time feature channel.
    for index in range(0, len(ordered), 48):
        batch = ordered[index:index+48]
        program = "".join(
            stage_features(features(row.prompt, mode=mode))
            + f"store64 {B + 8} {row.label}\n"
            + "call c06_train\n"
            for row in batch
        )
        model.run(program)
    seen = struct.unpack("<q", model.memory(B, 8))[0]
    if seen != epoch * len(examples):
        raise AssertionError("XI learner failed to count native updates")
    mistakes = struct.unpack("<q", model.memory(B+24, 8))[0]
    if mistakes < 0:
        raise AssertionError("XI learner encountered malformed teacher")
    return {"examples_seen": seen, "native_online_mistakes_cumulative": mistakes}


def predict_batch(model, examples, mode, *, ablate=False):
    """No teacher labels in any XI inference body: proven by construction."""
    output = []
    for index in range(0, len(examples), 48):
        batch = examples[index:index+48]
        program = "".join(
            stage_features(features(row.prompt, mode=mode))
            + "call c06_predict\n"
            + f"mem_materialize {B + 16} 8\n"
            for row in batch
        )
        events = model.run(program)
        frames = [row for row in events if row["type"] == "memory_materialization"]
        if len(frames) != len(batch):
            raise AssertionError("C06 XI did not return one native decision per sample")
        for frame in frames:
            prediction = struct.unpack("<q", bytes.fromhex(frame["hex"]))[0]
            if not 0 <= prediction < CLASSES:
                raise AssertionError("Invalid native XI class")
            output.append(prediction)
    return output


def metrics(rows, predicted):
    if len(rows) != len(predicted):
        raise ValueError("C06 classification count mismatch")
    correct = sum(example.label == y for example, y in zip(rows, predicted))
    confusion = [[0]*CLASSES for _ in range(CLASSES)]
    for example, y in zip(rows, predicted):
        confusion[example.label][y] += 1
    f1s = []
    for i in range(CLASSES):
        tp = confusion[i][i]
        fp = sum(confusion[j][i] for j in range(CLASSES) if j != i)
        fn = sum(confusion[i][j] for j in range(CLASSES) if j != i)
        denom = 2*tp + fp + fn
        f1s.append(2*tp/denom if denom else 0)
    return {
        "correct": correct, "total": len(rows),
        "accuracy": round(correct/len(rows), 6),
        "macro_f1": round(sum(f1s)/CLASSES, 6),
        "per_class_f1": [round(x, 6) for x in f1s],
        "confusion_rows_true_columns_pred": confusion,
    }


def read_native_weights(model):
    raw = model.memory(B+1024, CLASSES*FEATURES*8)
    return [round(v, 6) for v in struct.unpack("<"+"d"*(CLASSES*FEATURES), raw)]


def evaluate_native_model(checkpoint, rows, mode):
    """Always open a fresh XI process; keeps split isolation auditable."""
    with C1.Model(checkpoint, VOCAB, OUTPUT) as model:
        model.library += "\n" + NATIVE.read_text()
        prediction = predict_batch(model, rows, mode)
        return metrics(rows, prediction), prediction


def train_candidate(mode, train, validation, directory, epochs):
    path = Path(directory) / (mode + "-initial.rvp")
    C1.birth(path, 4096)
    best = None
    history = []
    with C1.Model(path, VOCAB, OUTPUT) as native:
        native.library += "\n" + NATIVE.read_text()
        for epoch in range(1, epochs+1):
            details = train_epoch(native, train, mode, epoch=epoch)
            val_prediction = predict_batch(native, validation, mode)
            val_report = metrics(validation, val_prediction)
            candidate = Path(directory) / f"{mode}-epoch-{epoch}.rvp"
            native.s.save(candidate)
            weights = read_native_weights(native)
            history.append({"epoch": epoch, "training": details,
                            "validation": val_report,
                            "weights_sha256": sha256(
                                native.memory(B+1024, CLASSES*FEATURES*8)
                            ).hexdigest()})
            # Choose ONLY by validation macro-F1, then validation accuracy.
            score = (val_report["macro_f1"], val_report["accuracy"])
            if best is None or score > best[0]:
                best = (score, epoch, candidate, weights)
    if best is None:
        raise AssertionError("No independently selected C06 model")
    selected_score, selected_epoch, path, weights = best
    # Reopen the selected checkpoint through the original XI runtime; its
    # predictions must not depend on the state of the training process.
    reopened_val, _ = evaluate_native_model(path, validation, mode)
    if reopened_val != history[selected_epoch-1]["validation"]:
        raise AssertionError("Native C06 training not preserved in RVPC2 checkpoint")
    return {
        "mode": mode,
        "selected_epoch": selected_epoch,
        "validation": reopened_val,
        "epochs": history,
        "checkpoint": path,
        "checkpoint_sha256": sha256(path.read_bytes()).hexdigest(),
        "weights": weights,
    }


def campaign(out: Path, epochs=6):
    if not 1 <= epochs <= 20:
        raise ValueError("C06 epochs must be within 1..20")
    protected_before, apk_before = freeze_assets(), apk_files()
    disjoint = verify_disjoint()
    # A fixed run cannot inspect the held-out test until ALL model choices,
    # including the ablation, are frozen. Test split is instantiated below.
    train, validation = split("train"), split("validation")
    C1Build.main()
    out.parent.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter_ns()
    with tempfile.TemporaryDirectory(prefix="bbyq-c06-native-candidates-") as temp:
        selected = [
            train_candidate(mode, train, validation, temp, epochs)
            for mode in MODES
        ]
        # The heldout test is generated *after* validation selection, exactly
        # once and is NEVER part of a training update, hyperparameter selection,
        # gradient or model-choice decision.
        test = split("test")
        for result in selected:
            score, prediction = evaluate_native_model(
                result["checkpoint"], test, result["mode"]
            )
            result["heldout_test"] = score
            result["native_test_predictions_sha256"] = sha256(
                bytes(prediction)
            ).hexdigest()
        main = next(v for v in selected if v["mode"] == "semantic")
        ablations = [v for v in selected if v["mode"] != "semantic"]
        if main["heldout_test"]["correct"] <= max(
                v["heldout_test"]["correct"] for v in ablations):
            # Report honestly; never manufacture an improvement.
            advantage_proven = False
        else:
            advantage_proven = True

        new_checkpoint = out.parent / "semantic-trained.rvp"
        shutil.copyfile(main["checkpoint"], new_checkpoint)
        saved_sha = sha256(new_checkpoint.read_bytes()).hexdigest()
        if saved_sha != main["checkpoint_sha256"]:
            raise AssertionError("C06 saved model differs from selected native XI candidate")
        val_after, _ = evaluate_native_model(
            new_checkpoint, validation, "semantic"
        )
        if val_after != main["validation"]:
            raise AssertionError("Published C06 RVPC2 cannot reproduce selected validation")
        elapsed = (time.perf_counter_ns() - started)/1e6
        if freeze_assets() != protected_before or apk_files() != apk_before:
            raise AssertionError("C06 changed protected checkpoint files or built APK")
        report = {
            "schema": HEAD_SCHEMA, "passed": True,
            "native_XI_trainable": True,
            "native_XI_predictions": True,
            "frozen_C1_weights_modified": False,
            "checkpoint_format": "original REVERSE-PC RVPC2",
            "checkpoint_filename": "semantic-trained.rvp",
            "trained_checkpoint_sha256": saved_sha,
            "native_source_sha256": sha256(NATIVE.read_bytes()).hexdigest(),
            "dataset": disjoint,
            "epochs_budget": epochs,
            "modes": [
                {key: value for key, value in v.items() if key != "checkpoint"}
                for v in selected
            ],
            "selected_mode": "semantic",
            "semantic_outperforms_both_ablations": advantage_proven,
            "tested_only_after_selection": True,
            "input_features_exclude_labels_and_C05_inferred_polarity": True,
            "known_limits": [
                "This is a separate XI native supervised semantic-intent probe, not a retraining of C1/QChat100.",
                "C05 spans/positions encode linguistic structure; host-side extraction is not a learned parser.",
                "Heldout templates/entities are split-disjoint, but this is a small synthetic grammar, not open conversation.",
                "Ablations train the same native 3-class head on surface-only and order-removed features.",
                "Test labels are used solely to score final predictions after all validation selections.",
                "No native quantum advantage, AGI or Android performance follows from this result.",
                "Real pretrained C1 release and its persistent personal memory remain untouched.",
            ],
            "frozen_asset_count": len(protected_before),
            "frozen_assets_sha256_unchanged": True,
            "apk_built": False,
            "wall_ms": round(elapsed, 3),
        }
        out.write_text(json.dumps(report, ensure_ascii=False, indent=2,
                                  default=str)+"\n")
    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--epochs", type=int, default=6)
    ap.add_argument("--out", type=Path, default=ROOT/"build/c06/training-report.json")
    args = ap.parse_args()
    report = campaign(args.out, epochs=args.epochs)
    print(json.dumps({
        "passed": report["passed"],
        "dataset": report["dataset"]["counts"],
        "native_XI_trainable": True,
        "validation": {
            x["mode"]: x["validation"]["accuracy"] for x in report["modes"]
        },
        "heldout": {
            x["mode"]: x["heldout_test"]["accuracy"] for x in report["modes"]
        },
        "advantage_vs_both": report["semantic_outperforms_both_ablations"],
        "checkpoint": report["trained_checkpoint_sha256"],
        "checkpoints_untouched": True, "apk_built": False,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
