#!/usr/bin/env python3
"""Package EXACT original BBY Q U02 source/checkpoints plus C00-C15 evidence for Android.

This packages an authenticated, read-only *copy* of original release files.
No original repo source, weight, training/feedback or 159 frozen bytes change.
Generated build assets (C1/Zero compiled XI) are included as derived outputs.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import json
import zipfile
import sys
import subprocess

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
OUT = ROOT / "android-u03/app/src/main/assets/u03"


def build():
    from integration.audit_u03_c00.profile import freeze_assets
    frozen = freeze_assets(ROOT)
    if len(frozen) != 159:
        raise AssertionError(f"U03 original 159 protected assets mismatch: {len(frozen)}")

    include = set(frozen)
    # Preserve all BBY Q AI source, historical results and experimental
    # C00-C15 source in the APK rather than silently dropping completed work.
    # Native runtime executes only the verified original U02 entrypoint.
    directories = ("integration", "ai", "docs")
    # All source needed by original Session imports is byte-for-byte unchanged.
    for dirname in directories:
        for path in (ROOT / dirname).rglob("*"):
            if path.is_file() and not path.name.endswith((".pyc", ".apk")) and "__pycache__" not in path.parts:
                include.add(path.relative_to(ROOT).as_posix())

    # Retain the prototype source and evidence without pretending all
    # host-only stress scripts (resource / subprocess / procfs) run on Android.
    for folder in (ROOT / "integration").glob("*u03*"):
        if folder.is_dir():
            for path in folder.rglob("*"):
                if path.is_file() and path.suffix in (".py", ".md", ".json"):
                    include.add(path.relative_to(ROOT).as_posix())
    for name in ("BBY_Q_U03_PANEL.md", "BBY_Q_U03_ESTADO.json",
                 "BBY_Q_U03_SIGUIENTE.md"):
        include.add("docs/" + name)

    # Release manifests authenticate ORIGINAL sources outside runtime modules
    # too (e.g. bbyq, bbyq.mjs, CI yaml and frozen seed banks). If omitted,
    # original U02 MUST reject startup: never bypass or weaken that check.
    for manifest_path in (
        "integration/unified/release/manifest.json",
        "integration/sequence2/release/manifest.json",
        "integration/entity/release/manifest.json",
    ):
        pinned = json.loads((ROOT / manifest_path).read_text())
        include.update(pinned.get("sources", {}))
        include.update(pinned.get("native_source_sha256", {}))

    # Release identity includes these fixed sources.
    include.update((
        "ai/xi/qchat100/model.xi",
        "ai/xi/qmemory/model.xi",
        "ai/xi/quantum3/common.xi",
        "ai/xi/quantum3/benchmarks.xi",
        "ai/xi/quantum3/step.xi",
        "ai/xi/balance/qrl3-curriculum.xi",
        "ai/xi/entity/workspace.xi",
        "ai/xi/entity/credit.xi",
        "ai/xi/entity/feedback.xi",
        "ai/xi/unified/perception-decoder.xi.in",
        "ai/xi/unified/perception-head.xi.in",
        "ai/personal/zero/core.xi.in",
        "ai/personal/zero/model.mjs",
        "ai/personal/zero/schema.mjs",
        "integration/zero/build.mjs",
        "integration/sequence2/engine.py",
        "integration/sequence2/tools.py",
        "integration/sequence2/workspace.py",
        "integration/sequence2/schema.py",
        "integration/sequence2/data.py",
        "integration/sequence2/grammar.py",
        "integration/qchat100/engine.py",
        "integration/entity/engine.py",
        "integration/entity/protocol.json",
        "integration/balance/release/qchat100/vocabulary.json",
        "build/sequence2/model.xi",
        "build/sequence2/schema.json",
        "build/zero/zero.xi",
        "build/zero/schema.json",
    ))
    shim = ROOT / "android-u03/scripts/xi_session_mobile.py"
    if not shim.is_file():
        raise FileNotFoundError(str(shim))
    virtual = {"deps/reverse-pc/scripts/xi_session_client.py": shim.read_bytes()}
    # The mobile adapter lives only in a NEW APK bundle, not within the original
    # REVERSE-PC repo, and delegates 100% of operations to original XI JNI.
    files = {name: (ROOT / name).read_bytes() for name in sorted(include)}
    files.update(virtual)
    assert all(k in files and sha256(files[k]).hexdigest() == v for k,v in frozen.items())

    # Avoid nonessential large generated outputs and accidental .git packaging.
    for name, value in files.items():
        if not value and not name.endswith(".py"):
            raise AssertionError("Unexpected empty model/source: " + name)
        if Path(name).is_absolute() or ".." in Path(name).parts:
            raise AssertionError("Unsafe bundle path: " + name)

    OUT.mkdir(parents=True, exist_ok=True)
    archive = OUT / "bbyq-u03-runtime.zip"
    with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6) as out:
        for name, data in sorted(files.items()):
            out.writestr(name, data)
    manifest = {
        "schema": "BBYQ-U03-Android-authenticated-runtime-v1",
        "android_package": "com.bbyq.u03.training",
        "android_version": "U03.18.0-personal",
        "android_label": "BBY Q 0",
        "personal_interface": "conversation_and_model",
        "apk_source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "mobile_sources_sha256": {p.name: sha256(p.read_bytes()).hexdigest()
            for p in sorted((ROOT / "android-u03/app/src/main/python").glob("*.py"))},
        "training_guide_sha256": sha256((ROOT / "android-u03/app/src/main/assets/training-guide.html").read_bytes()).hexdigest(),
        "base_c15_sha": "f644f6657d7e49e4d7f83ed7257a21ad823c871a",
        "architecture": "BBY Q -> w4U -> QdU",
        "production_core": "U02 original frozen XI C1 VQC3 QRL3 QMemory E02 QChat100",
        "experimental_c11_c12_promoted": False,
        "C13_cache_enabled": False,
        "protected_count": len(frozen),
        "protected_sha256": frozen,
        "file_count": len(files),
        "files_sha256": {k: sha256(v).hexdigest() for k,v in sorted(files.items())},
        "archive_sha256": sha256(archive.read_bytes()).hexdigest(),
        "archive_bytes": archive.stat().st_size,
        "android_gpu_backend_ported": False,
        "historical_android_E02_replaced": True,
        "checkpoints_modified": False,
        "new_memory_authorities": 0,
    }
    (OUT / "mobile-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"ok":True, "protected":len(frozen), "files":len(files),
        "archive_bytes":archive.stat().st_size,
        "bundle_sha256":manifest["archive_sha256"],
        "current_runtime":"original U02", "experimental_promoted":False}))
    return manifest


if __name__ == "__main__":
    build()

