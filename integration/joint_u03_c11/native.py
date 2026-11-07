"""Independent native XI parameter SHA and synthetic-label oracle for C11.

Unlike a checkpoint SHA (which also changes with counters/readouts), these
digests target actual model weight/angle regions. C11 training itself is
the original U02 Session.turn feedback branch, never simulated by Python.
"""
from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import struct
import tempfile

from integration.unified.common import (
    C1, A, M, Q, E, material, run, floating, digest,
)
from integration.unified import perception as P

HEADS = ("vqc_weights", "qrl_weights", "qmemory_angles", "entity_weights",
         "qchat_weights", "vqc_readout")


def _pages(native,address,size,page=60000):
    return b"".join(
        material(native,address+offset,min(page,size-offset))
        for offset in range(0,size,page)
    )


def bank_weight_hashes(bank_blobs: dict[str, bytes]) -> dict[str,str]:
    """Hash real XI model parameters, excluding training counters/metadata.

    Native binary input is first authenticated by the original U02 Session,
    then copied to a temporary directory with per-bank native interpreters.
    This function never stages training calls.
    """
    required=("v3","memory","entity","voice")
    if not all(name in bank_blobs for name in required):
        raise ValueError("C11 cannot audit incomplete original XI banks")
    with tempfile.TemporaryDirectory(prefix="bbyq-c11-native-weights-") as tmp:
        paths={}
        for bank in required:
            path=Path(tmp)/(bank+".rvp")
            path.write_bytes(bank_blobs[bank])
            paths[bank]=path
        with C1.XiSession(C1.RT/"build/xi_session",paths["v3"]) as v, \
             C1.XiSession(C1.RT/"build/xi_session",paths["memory"]) as m, \
             C1.XiSession(C1.RT/"build/xi_session",paths["entity"]) as e, \
             C1.XiSession(C1.RT/"build/xi_session",paths["voice"]) as c:
            # The VQC/QRL original parameter arrays, not their 48-byte
            # optimizer metadata. Each has 3 windows of 8000 bytes.
            vqc=b"".join(material(v,A+100000+d,8000)
                        for d in (0,10000,20000))
            qrl=b"".join(material(v,A+200000+d,8000)
                        for d in (0,10000,20000))
            memory=_pages(m,M+64,24)
            entity=_pages(e,E+1000,40)
            voice=_pages(c,Q+100000,888832)+_pages(c,Q+990000,1016)
            try:
                readout=P.parameter_identity(v)
            except (ValueError,RuntimeError,StopIteration):
                # A missing readout may exist only on a legacy bank; fail
                # closed instead of pretending it changed.
                raise
    return {
        "vqc_weights":digest(vqc),
        "qrl_weights":digest(qrl),
        "qmemory_angles":digest(memory),
        "entity_weights":digest(entity),
        "qchat_weights":digest(voice),
        "vqc_readout":readout,
    }


def native_sample_teacher(v3_initial:bytes, seed:int) -> int:
    """Obtain an evaluation-only synthetic teacher AFTER XI inference.

    This is the ORIGINAL XI vqc_sample, executed on a separate, disposable
    original bank; never passed as a label to the model being measured.
    """
    if type(seed) is not int or not 0<=seed<=2147483647:
        raise ValueError("C11 synthetic sample seed outside U02 limits")
    with tempfile.TemporaryDirectory(prefix="bbyq-c11-oracle-only-") as tmp:
        path=Path(tmp)/"original-v3.rvp"
        path.write_bytes(v3_initial)
        with C1.XiSession(C1.RT/"build/xi_session",path) as native:
            run(native,(
                f"store64 {A+256} {seed}\n"
                f"store64 {A+272} 0\n"
                f"fstore {A+296} .1\n"
                "call vqc_sample"
            ))
            label=floating(native,A+128)
    if label not in (0.,1.):
        raise AssertionError("C11 original XI synthetic teacher not binary")
    return int(label)
