#!/usr/bin/env python3
"""Authenticate the delivered C18 build and prepare a real Android update test.

Only the CI debug certificate changes. The user's personal signing key is never
sent to CI. The old and new test APKs share this runner's debug certificate so
Android can perform an actual install -r while preserving the old app data.
"""
from hashlib import sha256
from pathlib import Path
import io
import json
import os
import re
import runpy
import subprocess
import sys
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[2]
REPO = "guadalupejuan001-code/BBY-Q"
ARTIFACT = 13651409873
ARCHIVE_SHA = "5c29458c27f617c6c0aa6ed7fe8286a2e07af35e04018bc4efa9366e7c5f1ca3"
APK_SHA = "50270cd08f8c5762aa2536231532fc4c306c3666cfb8848325c7ab440ab86647"
SOURCE = "c8ad566dcf1ee6f42244967b640cb79a70f4f144"


def payload(raw):
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        assert archive.testzip() is None
        result = {}
        for entry in archive.infolist():
            name = entry.filename.upper()
            signature = name.startswith("META-INF/") and (
                name.endswith((".SF", ".RSA", ".DSA", ".EC")) or name == "META-INF/MANIFEST.MF")
            if not signature:
                result[entry.filename] = sha256(archive.read(entry)).hexdigest()
        return result


def main():
    build_tools = Path(sys.argv[1])
    keystore = Path(sys.argv[2]).resolve()
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("Read-only Actions access is required for the authenticated C18 upgrade fixture")
    redirect = runpy.run_path(str(ROOT / "android-u03/scripts/recover-mobile-heads.py"))["ArtifactRedirect"]
    opener = urllib.request.build_opener(redirect())
    request = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/actions/artifacts/{ARTIFACT}/zip",
        headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28"})
    with opener.open(request, timeout=60) as response:
        archive_bytes = response.read()
    if sha256(archive_bytes).hexdigest() != ARCHIVE_SHA:
        raise RuntimeError("C18 Actions archive identity mismatch")
    with zipfile.ZipFile(io.BytesIO(archive_bytes)) as archive:
        raw = archive.read("build/android-c18/BBY-Q-0-Personal.apk")
    if sha256(raw).hexdigest() != APK_SHA:
        raise RuntimeError("C18 tested APK identity mismatch")
    with zipfile.ZipFile(io.BytesIO(raw)) as apk:
        manifest = json.loads(apk.read("assets/u03/mobile-manifest.json"))
    assert manifest["apk_source_commit"] == SOURCE
    assert manifest["android_version"] == "U03.18.0-personal"
    assert manifest["android_package"] == "com.bbyq.u03.training"

    folder = ROOT / "build/chat-upgrade-fixture"
    folder.mkdir(parents=True, exist_ok=True)
    original = folder / "C18-original.apk"
    baseline = folder / "C18-upgrade-baseline.apk"
    original.write_bytes(raw)
    if not keystore.is_file():
        raise RuntimeError("The explicit CI signing key used by Gradle is missing")
    signer = build_tools / "apksigner"
    subprocess.run([str(signer), "sign", "--ks", str(keystore), "--ks-type", "PKCS12", "--ks-key-alias", "androiddebugkey",
                    "--ks-pass", "pass:android", "--key-pass", "pass:android",
                    "--v4-signing-enabled", "false", "--out", str(baseline), str(original)], check=True)
    subprocess.run([str(signer), "verify", str(baseline)], check=True)
    if payload(raw) != payload(baseline.read_bytes()):
        raise RuntimeError("Preparing the update test changed C18 executable or asset bytes")
    badging = subprocess.check_output([str(build_tools / "aapt"), "dump", "badging", str(baseline)], text=True)
    package = re.search(r"package: name='([^']+)' versionCode='(\d+)' versionName='([^']+)'", badging)
    assert package and package.groups() == ("com.bbyq.u03.training", "4", "U03.18.0-personal")
    certificates = []
    for application in (baseline, ROOT / "build/android-c19/BBY-Q-0-Chats.apk",
                        ROOT / "android-u03/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk"):
        verification = subprocess.check_output([str(signer), "verify", "--print-certs", str(application)], text=True)
        certificate = re.search(r"Signer #1 certificate SHA-256 digest: ([0-9a-f]+)", verification)
        if not certificate:
            raise RuntimeError("Cannot verify the CI certificate for " + application.name)
        certificates.append(certificate.group(1))
    if len(set(certificates)) != 1:
        raise RuntimeError("Old APK, updated APK and instrumentation APK must share the explicit CI certificate")
    report = {
        "authenticated": True, "original_artifact_id": ARTIFACT,
        "original_artifact_sha256": ARCHIVE_SHA, "original_tested_apk_sha256": APK_SHA,
        "original_source_commit": SOURCE, "baseline_version_code": 4,
        "baseline_version_name": "U03.18.0-personal", "application_id": package.group(1),
        "baseline_apk_sha256": sha256(baseline.read_bytes()).hexdigest(),
        "only_ci_signature_changed": True, "user_signing_key_used_in_ci": False,
        "all_three_ci_certificates_identical": True, "ci_certificate_sha256": certificates[0],
    }
    out = ROOT / "build/android-c19"
    out.mkdir(parents=True, exist_ok=True)
    (out / "chat-upgrade-authentication.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))


if __name__ == "__main__":
    main()
