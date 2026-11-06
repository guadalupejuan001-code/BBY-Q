#!/usr/bin/env python3
"""C01 failure isolation: native RESTORE rejects corrupt state without mutation."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from integration.unified.common import ROOT, C1
from .client import CachedXiSession


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    binary = ROOT / "deps/reverse-pc/build/reverse_pc"
    with tempfile.TemporaryDirectory(prefix="bbyq-c01-native-errors-") as folder:
        path = Path(folder)
        initial = path / "initial.rvp"
        baseline = path / "baseline.rvp"
        altered = path / "altered.rvp"
        recovered = path / "recovered.rvp"
        subprocess.run([str(binary), "init", str(initial)],
                       check=True, capture_output=True)
        with CachedXiSession(binary, initial) as session:
            session.save(baseline)
            # The cached server must reject an unrecognized ID without
            # interpreting any instruction or mutating Runtime.
            try:
                session._request("EXECREF", "999\n#!reverse-pc-machine-v1\nhalt\n")
            except RuntimeError as error:
                assert "Unknown cached library" in str(error)
            else:
                raise AssertionError("Unknown cached library ID accepted")

            code = (
                "#!reverse-pc-machine-v1\nbudget 1000000\n"
                "store8 1234567 17\nhalt\n"
            )
            session.execute(code)
            session.save(altered)
            assert sha(altered) != sha(baseline), "The state-write test was ineffective"

            corrupt = path / "corrupt.rvp"
            data = bytearray(initial.read_bytes())
            data[-1] ^= 0x80
            corrupt.write_bytes(data)
            try:
                session._request("RESTORE", str(corrupt))
            except RuntimeError:
                pass
            else:
                raise AssertionError("Corrupt restore was accepted")

            # Failed RESTORE must leave the *modified* runtime intact, so a
            # later successful RESTORE actually changes the live state.
            still_modified = path / "still-modified.rvp"
            session.save(still_modified)
            assert sha(still_modified) == sha(altered)
            session._request("RESTORE", str(initial))
            session.save(recovered)
            assert sha(recovered) == sha(baseline)
    print(json.dumps({
        "passed": True,
        "unknown_library_id_rejected": True,
        "corrupt_checkpoint_rejected": True,
        "failed_restore_left_state_unchanged": True,
        "restored_checkpoint_identical": True,
        "apk_built": False,
    }))


if __name__ == "__main__":
    main()
