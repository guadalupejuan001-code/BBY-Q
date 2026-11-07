"""C07 opt-in metacognitive assessment beside unified BBY Q.

The original U02/C06 answer remains authoritative. The trained C07 XI
checkpoint is read-only. The new method assesses only explicit, typed
laboratory evidence and reports (a) the native learned class, (b) a
validation-calibrated class score, (c) a conservative safety action.
No semantic state is written to SQLite or an original XI bank.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from types import SimpleNamespace

from integration.unified.common import C1
from integration.semantic_u03_c06.session import ShadowSemanticSession
from .dataset import LABELS, trusted
from .features import SCHEMA, evidence_features, is_unsupported
from .train import NATIVE, infer, probabilities, guarded_action


class MetaSession(ShadowSemanticSession):
    def __init__(self, database, *, c06_checkpoint, c06_report,
                 c07_checkpoint, c07_report, readers=None,
                 parallel_hash_workers=4, memo=None):
        self._meta_head = None
        self.last_metacognition = None
        report = json.loads(Path(c07_report).read_text())
        if report.get("schema") != SCHEMA or report.get("mode_selected") != "provenance":
            raise ValueError("C07 unrecognized epistemic training manifest")
        if report.get("passed") is not True:
            raise ValueError("C07 model has not passed validation")
        file=Path(c07_checkpoint)
        if not file.is_file() or sha256(file.read_bytes()).hexdigest()!=report["trained_checkpoint_sha256"]:
            raise ValueError("C07 epistemic checkpoint SHA-256 mismatch")
        if sha256(NATIVE.read_bytes()).hexdigest()!=report["source_sha256"]:
            raise ValueError("C07 inference code differs from trained model")
        selected=next((v for v in report["modes"] if v["mode"]=="provenance"),None)
        if selected is None:
            raise ValueError("C07 missing selected calibration")
        self._temperature=selected["temperature"]
        self._threshold=selected["answer_threshold"]
        self._manifest_sha256=sha256(Path(c07_report).read_bytes()).hexdigest()
        super().__init__(
            database,checkpoint=c06_checkpoint,report=c06_report,
            readers=readers,parallel_hash_workers=parallel_hash_workers,memo=memo
        )
        try:
            self._meta_head=C1.Model(file,["<pad>"],["<eos>"])
            self._meta_head.library+="\n"+NATIVE.read_text()
        except BaseException:
            self.close()
            raise

    def assess_evidence(self,query:dict,evidence) -> dict:
        """Observation-only result; not a factual verdict or user response."""
        self.last_metacognition=None
        if is_unsupported(query,evidence):
            result={
                "recommended_action":"ask_for_evidence",
                "reason":"Unsupported or malformed evidence schema",
                "native_class":None,"calibrated_class_confidence":None,
                "authoritative":False, "written_to_prior_banks":False,
                "not_real_world_truth_probability":True,
            }
            self.last_metacognition=result
            return result
        case=SimpleNamespace(query=query,evidence=tuple(evidence))
        prediction=infer(self._meta_head,[case],"provenance")[0]
        p=probabilities(prediction["scores"],self._temperature)
        action=guarded_action(case,prediction,self._temperature,self._threshold)
        values={row["value"] for row in evidence if trusted(row,query)}
        reason=(
            "Opposing supported observations" if len(values)==2
            else "No supported observation" if len(values)==0
            else "Supported evidence; native confidence gate applied"
        )
        result={
            "recommended_action":LABELS[action],
            "native_class":LABELS[prediction["predicted"]],
            "calibrated_class_confidence":round(max(p),6),
            "confidence_kind":"heldout-task class confidence, NOT truth probability",
            "threshold":self._threshold,"temperature":self._temperature,
            "reason":reason,
            "supported_evidence_count":sum(trusted(row,query) for row in evidence),
            "manifest_sha256":self._manifest_sha256,
            "authoritative":False,"written_to_prior_banks":False,
            "not_real_world_truth_probability":True,
        }
        self.last_metacognition=result
        return result

    def close(self):
        head,self._meta_head=self._meta_head,None
        if head is not None:
            head.__exit__(None,None,None)
        super().close()
