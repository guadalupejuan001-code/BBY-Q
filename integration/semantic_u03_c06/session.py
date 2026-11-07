"""Optional U03 shadow semantic inference, original C1/entity remain authoritative.

The trained XI semantic readout is an independent RVPC2 checkpoint. It only
reports a provisional 3-way semantic tag beside the frozen U02 outcome.
No routing override, training, SQLite change or model-bank modification.
"""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import struct

from integration.unified.common import C1
from integration.codifier_u03_c05.session import SemanticSession
from .dataset import LABELS
from .features import features
from .train import NATIVE, B, VOCAB, OUTPUT, stage_features


class ShadowSemanticSession(SemanticSession):
    """Native trained XI semantics in observation-only mode, explicit opt-in."""

    def __init__(self, database, *, checkpoint: str | Path, report: str | Path,
                 readers=None, parallel_hash_workers=4, memo=None):
        self._head = None
        self.last_learned_semantic = None
        manifest = json.loads(Path(report).read_text())
        if manifest.get("schema") != "BBYQ-U03-C06-ordered-semantic-v1":
            raise ValueError("C06 unknown learned model format")
        if manifest.get("selected_mode") != "semantic" or not manifest.get("passed"):
            raise ValueError("C06 semantic checkpoint has not passed selection")
        path = Path(checkpoint)
        if sha256(path.read_bytes()).hexdigest() != manifest["trained_checkpoint_sha256"]:
            raise ValueError("C06 learned model SHA-256 identity mismatch")
        if sha256(NATIVE.read_bytes()).hexdigest() != manifest["native_source_sha256"]:
            raise ValueError("C06 native source does not match trained head")
        super().__init__(database, readers=readers,
                         parallel_hash_workers=parallel_hash_workers, memo=memo)
        try:
            self._head = C1.Model(path, VOCAB, OUTPUT)
            self._head.library += "\n" + NATIVE.read_text()
        except BaseException:
            self.close()
            raise
        self._manifest_sha256 = sha256(Path(report).read_bytes()).hexdigest()

    def turn(self, request_id, prompt, payload=None, fail_after=None, control=None):
        self.last_learned_semantic = None
        # U02 turn remains authoritative, including its original exception,
        # feedback, idempotence and transaction behavior.
        result = super().turn(request_id, prompt, payload=payload,
                              fail_after=fail_after, control=control)
        if self.last_semantic is not None:
            body = stage_features(features(prompt, mode="semantic"))
            events = self._head.run(
                body + "call c06_predict\n"
                + f"mem_materialize {B + 16} 8"
            )
            frames = [e for e in events if e["type"] == "memory_materialization"]
            if len(frames) != 1:
                raise AssertionError("C06 shadow head did not return exactly one prediction")
            predicted = struct.unpack("<q", bytes.fromhex(frames[0]["hex"]))[0]
            if predicted not in range(len(LABELS)):
                raise ValueError("Native C06 prediction not in supported classes")
            self.last_learned_semantic = {
                "label_id": predicted,
                "semantic_class": LABELS[predicted],
                "model": "XI-native-C06",
                "authoritative": False,
                "routed_to_C1": False,
                "updated_previous_checkpoints": False,
                "model_manifest_sha256": self._manifest_sha256,
            }
        return result

    def close(self):
        head, self._head = self._head, None
        if head is not None:
            head.__exit__(None, None, None)
        super().close()
