"""Android entrypoint: original BBY Q U02 Session on the authentic JNI XI runtime.

Chaquopy only provides the Python orchestration which already existed in U02.
All inference, readout and feedback are executed by original XI/Ether in JNI.
No fake responses, no external AI backend, no silent C11/C12 promotion.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
import os
import shutil
import sys
import tempfile
import threading
import zipfile

_lock = threading.RLock()
_root = None
_db = None
_manifest = None


def _bytes_hash(data):
    return sha256(data).hexdigest()


def _verify_sources(root, expected):
    for filename, want in expected.items():
        path = root / filename
        if not path.is_file() or _bytes_hash(path.read_bytes()) != want:
            raise RuntimeError("Authenticated U02 source/checkpoint mismatch: " + filename)


def _activate_root(root):
    path = str(root)
    xi = str(root / "deps/reverse-pc/scripts")
    c1 = str(root / "integration/sequence2")
    for name in (path, xi, c1):
        if name in sys.path:
            sys.path.remove(name)
        sys.path.insert(0, name)
    # Node is unavailable on device; CI embeds the exact generated XI Zero
    # source and schema and authenticates them before U02 is initialized.
    import workspace
    def bundled_zero():
        for name in ("zero.xi", "schema.json"):
            if not (root / "build/zero" / name).is_file():
                raise RuntimeError("Missing verified XI Zero program: " + name)
    workspace.build_zero = bundled_zero


def initialize(files_dir: str, bundle_path: str, manifest_json: str) -> str:
    global _root, _db, _manifest
    with _lock:
        manifest = json.loads(manifest_json)
        if manifest["schema"] != "BBYQ-U03-Android-authenticated-runtime-v1":
            raise RuntimeError("Unexpected U03 mobile ABI/manifest")
        if manifest["protected_count"] != 159 or manifest["new_memory_authorities"] != 0:
            raise RuntimeError("U03 must preserve original 159 protected assets")
        if manifest["experimental_c11_c12_promoted"] or manifest["C13_cache_enabled"]:
            raise RuntimeError("Experimental model or cache silently activated")

        bundle = Path(bundle_path)
        if _bytes_hash(bundle.read_bytes()) != manifest["archive_sha256"]:
            raise RuntimeError("U03 bundle SHA-256 mismatch")
        base = Path(files_dir)
        root = base / ("runtime-" + manifest["archive_sha256"][:16])
        stamp = root / ".verified"
        if not stamp.is_file() or stamp.read_text() != manifest["archive_sha256"]:
            staging = Path(tempfile.mkdtemp(prefix="u03-model-", dir=base))
            try:
                expected = manifest["files_sha256"]
                with zipfile.ZipFile(bundle) as zip:
                    names = zip.namelist()
                    if set(names) != set(expected):
                        raise RuntimeError("Unexpected source/checkpoint membership in U03")
                    for name in names:
                        item = Path(name)
                        if item.is_absolute() or ".." in item.parts or name.endswith("/"):
                            raise RuntimeError("Invalid U03 bundle path")
                        data = zip.read(name)
                        if _bytes_hash(data) != expected[name]:
                            raise RuntimeError("Modified original XI source: " + name)
                        dest = staging / name
                        dest.parent.mkdir(parents=True,exist_ok=True)
                        dest.write_bytes(data)
                _verify_sources(staging,manifest["protected_sha256"])
                (staging / ".verified").write_text(manifest["archive_sha256"])
                if root.exists():
                    shutil.rmtree(root)
                staging.rename(root)
            finally:
                if staging.exists():
                    shutil.rmtree(staging)

        _verify_sources(root, manifest["protected_sha256"])
        _activate_root(root)
        private = base / "sessions"
        private.mkdir(parents=True, exist_ok=True)
        db = private / "u03-original.sqlite"
        from integration.unified.session import Session
        from integration.memory_u03_c09.view import UnifiedMemoryView
        with Session(db) as model:
            state = model.snapshot()
            audited = UnifiedMemoryView(model).snapshot()
            if len(state["banks"]) != 7 or not audited["C1_synchronized_with_U02"]:
                raise RuntimeError("U03 Android original banks failed SHA/sync audit")
            if audited["new_memory_authorities"] != 0:
                raise RuntimeError("U03 Android attempted to create new memory authority")
            if model.db.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise RuntimeError("U03 Android SQLite integrity check failed")
        _root, _db, _manifest = root, db, manifest
        return json.dumps({
            "ready": True, "entity":"U02", "cycles":"C00-C15",
            "components":["C1","VQC3","QRL3","QMemory","QChat100","E02"],
            "banks":len(state["banks"]),
            "checkpoint_identity_verified":True,
            "C1_U02_synchronized":True,
            "model_promoted":False,"cache_promoted":False,
            "gpu_C12_ported":False,"historical_assets":159,
            "private_sqlite":True,"apk_mode":"Android XI JNI + Python orchestration",
        },ensure_ascii=False)


def _require_ready():
    if _root is None or _db is None:
        raise RuntimeError("U03 XI runtime not yet initialized")


def _reply(result):
    if not result.get("ok"):
        return result.get("reason") or result.get("error") or (
            "El lector original XI no reconoció un contrato comprobado. "
            "No invento una respuesta.")
    parts = []
    for item in result.get("results",[]):
        kind = item.get("kind")
        if kind=="text":
            parts.append(item.get("text",""))
        elif kind in ("greet","cancel"):
            parts.append(item.get("text",""))
        elif kind=="math":
            parts.append("Resultado XI: "+str(item.get("value",item.get("status"))))
        elif kind=="mission":
            parts.append("Misión XI: clase "+str(item.get("class"))+
                         ", regla "+str(item.get("rule_value"))+
                         ", acción "+str(item.get("action"))+
                         ". Estado "+str(item.get("status")))
        elif kind=="feedback":
            parts.append("Feedback XI: "+json.dumps(item.get("updates",{}),
                                                     ensure_ascii=False))
        elif kind=="status":
            parts.append("Motores nativos: "+", ".join(item.get("components",[])))
        elif kind=="recall":
            parts.append("Memoria XI: "+str(item.get("value",item.get("status"))))
        elif kind=="explain":
            parts.append("Explicación: "+str(item.get("action",item.get("status"))))
        elif kind:
            parts.append(kind+": "+json.dumps(item,ensure_ascii=False)[:350])
    return "\n".join(parts) or "La operación original XI terminó sin texto público."


def turn(request_id:str, prompt:str, payload_json:str="") -> str:
    with _lock:
        _require_ready()
        from integration.unified.session import Session
        payload=json.loads(payload_json) if payload_json else None
        with Session(_db) as model:
            before=model.snapshot()
            output=model.turn(request_id,prompt,payload)
            after=model.snapshot()
            trace=output.get("trace",[])
            return json.dumps({
                "ok":bool(output.get("ok")),
                "reply":_reply(output),
                "receipt":output,
                "trace":trace,
                "native_XI":all(x.get("native") is True for x in trace),
                "original_U02":output.get("entity")=="U02",
                "before_revision":before["revision"],
                "after_revision":after["revision"],
                "C1_U02_synchronized":True,
            },ensure_ascii=False)


def status() -> str:
    with _lock:
        _require_ready()
        from integration.unified.session import Session
        from integration.memory_u03_c09.view import UnifiedMemoryView
        with Session(_db) as model:
            state=model.snapshot()
            audit=UnifiedMemoryView(model).snapshot()
            return json.dumps({
                "entity":"U02","snapshot":state,
                "bank_count":len(state["banks"]),
                "memory":audit,
                "U03_verified_C15":True,
                "C11_C12_unpromoted":True,
                "C13_cache_disabled":True,
                "GPU_virtual_compute_ported":False
            },ensure_ascii=False)


def panel() -> str:
    _require_ready()
    return (_root/"docs/BBY_Q_U03_PANEL.md").read_text()


def history() -> str:
    with _lock:
        _require_ready()
        from integration.unified.session import Session
        with Session(_db) as model:
            return json.dumps(model.history()[-25:],ensure_ascii=False)
