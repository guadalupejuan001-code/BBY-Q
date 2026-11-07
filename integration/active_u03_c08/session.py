"""C08 verified active-learning checkpoint in U03 observational meta session.

C1 is still the only user-facing response authority. C08 supplements C07
epistemic findings and creates a follow-up question when more verified
evidence is required. It NEVER auto-labels an unverified external statement,
writes a training receipt to a personal database or changes U02 banks.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

from integration.unified.common import C1
from integration.metacognition_u03_c07.session import MetaSession
from integration.metacognition_u03_c07.features import is_unsupported
from integration.metacognition_u03_c07.train import (
    NATIVE, infer, probabilities, guarded_action
)
from integration.metacognition_u03_c07.dataset import LABELS
from .dataset import Unlabeled
from .learner import ask_for_verification


class ActiveMetaSession(MetaSession):
    """Explicitly selected candidate, only read-only predictions."""

    def __init__(self, database, *, c06_checkpoint, c06_report,
                 c07_checkpoint, c07_report, c08_checkpoint, c08_report,
                 readers=None, parallel_hash_workers=4, memo=None):
        self._active_head=None
        self.last_active_learning=None
        report=json.loads(Path(c08_report).read_text())
        if report.get("schema")!="BBYQ-U03-C08-verified-active-learning-v1":
            raise ValueError("Unknown C08 active learning schema")
        if report.get("passed") is not True or not report.get("no_training_on_C07_CHALLENGE"):
            raise ValueError("C08 unverified acquisition report")
        path=Path(c08_checkpoint)
        if not path.is_file() or sha256(path.read_bytes()).hexdigest()!=report["active_model_sha256"]:
            raise ValueError("C08 trained model does not match signed manifest digest")
        source=Path(c07_checkpoint)
        if sha256(source.read_bytes()).hexdigest()!=report["source_model_sha256"]:
            raise ValueError("C08 cannot authenticate original C07 starting point")
        chosen=next((model for model in report["comparisons"] if model["mode"]=="active"),None)
        if chosen is None:
            raise ValueError("C08 report lacks active candidate")
        self._temp=chosen["temperature"]
        self._threshold=chosen["answer_threshold"]
        self._promoted=report["promotion_mode"]=="active"
        self._manifest_sha=sha256(Path(c08_report).read_bytes()).hexdigest()
        super().__init__(
            database, c06_checkpoint=c06_checkpoint,c06_report=c06_report,
            c07_checkpoint=c07_checkpoint,c07_report=c07_report,
            readers=readers,parallel_hash_workers=parallel_hash_workers,memo=memo
        )
        try:
            self._active_head=C1.Model(path,["<pad>"],["<eos>"])
            self._active_head.library+="\n"+NATIVE.read_text()
        except BaseException:
            self.close()
            raise

    def assess_evidence_active(self, query:dict, evidence) -> dict:
        """Return both C07 and C08 assessments without committing knowledge."""
        self.last_active_learning=None
        baseline=super().assess_evidence(query,evidence)
        if is_unsupported(query,evidence):
            output={
                "baseline":baseline,"active":None,
                "comparison_only":True,"promoted_on_validation":self._promoted,
                "clarification":"Se necesita evidencia apropiada para esa consulta.",
                "changed_C1_response":False,
                "written_to_previous_banks":False,
            }
            self.last_active_learning=output
            return output
        row=SimpleNamespace(query=query,evidence=tuple(evidence))
        try:
            observation=infer(self._active_head,[row],"provenance")[0]
            p=probabilities(observation["scores"],self._temp)
            act=guarded_action(row,observation,self._temp,self._threshold)
            clarify=None
            if act==1:
                case=Unlabeled(
                    "ephemeral-not-a-training-label",
                    query,tuple(evidence),"pool"
                )
                clarify=ask_for_verification(case,observation)["question"]
            result={
                "baseline":baseline,
                "active":{
                    "native_class":LABELS[observation["predicted"]],
                    "safety_action":LABELS[act],
                    "calibrated_class_confidence":round(max(p),6),
                    "confidence_scope":"synthetic-class accuracy, NOT truth probability",
                },
                "promoted_on_validation":self._promoted,
                "comparison_only":True,
                "clarification":clarify,
                "changed_C1_response":False,
                "written_to_previous_banks":False,
                "manifest_sha256":self._manifest_sha,
            }
        except Exception as exc:
            # This is an optional diagnostic after the authoritative
            # original model has run. Failure must not retroactively
            # invalidate the genuine C1/SQLite transaction.
            result={
                "baseline":baseline, "active":None,
                "comparison_only":True,
                "promoted_on_validation":self._promoted,
                "clarification":"No se pudo comprobar el candidato; se conserva C07.",
                "error_type":type(exc).__name__,
                "changed_C1_response":False,
                "written_to_previous_banks":False,
            }
        self.last_active_learning=result
        return result

    def close(self):
        model,self._active_head=self._active_head,None
        if model is not None:
            model.__exit__(None,None,None)
        super().close()
