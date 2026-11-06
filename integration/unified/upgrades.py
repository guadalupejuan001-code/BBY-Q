"""Transactional U01 upgrade: add the new readout, preserve personal learning."""
import json,tempfile
from pathlib import Path
from .common import C1,A,encoded,digest,material,integer,read
from . import perception as P

def bank_parameters(native):
    return {name:digest(b''.join(material(native,base+offset,8000) for offset in (0,10000,20000))+material(native,meta,48))
            for name,base,meta in [('vqc',A+100000,A+4000),('qrl',A+200000,A+5000)]}

def accepted(folder):
    manifest=Path(folder)/'manifest.json'
    if manifest.exists():return read(manifest).get('migrations',[])
    path=Path(folder)/'migrations.json'
    return read(path) if path.exists() else []

def upgrade(session,previous):
    """Called inside Session's BEGIN IMMEDIATE; no independent commit."""
    allowed=next((item for item in accepted(session.folder) if item['identity']==previous),None)
    if allowed is None or previous.get('version')!='U01':raise ValueError('Unified source/model identity changed; explicit migration required')
    if digest(encoded(previous))!=allowed['identity_sha256']:raise ValueError('Corrupt migration identity binding')
    if previous['c1']!=session.legacy.identity:raise ValueError('Migration cannot replace personal language state')
    old,sha=session.db.execute('SELECT snapshot,sha FROM unified_banks WHERE name="v3"').fetchone()
    metadata,metadata_sha,revision=session.db.execute('SELECT metadata,sha,revision FROM unified_state WHERE id=1').fetchone()
    if digest(old)!=sha or digest(metadata)!=metadata_sha:raise ValueError('Corrupt prior session; migration aborted')
    # Integrity of every bank is checked before staging the upgrade.
    session._banks()
    with tempfile.TemporaryDirectory(prefix='bbyq-u02-upgrade-') as temporary:
        directory=Path(temporary);old_path=directory/'personal.rvp';new_path=directory/'qualified.rvp';old_path.write_bytes(old);new_path.write_bytes(session.initial['v3'])
        with C1.XiSession(C1.RT/'build/xi_session',old_path) as live,C1.XiSession(C1.RT/'build/xi_session',new_path) as candidate:
            if integer(live,P.B)!=0:raise ValueError('The previous session already has an unexpected perception readout')
            if integer(candidate,P.B)!=P.MAGIC:raise ValueError('The upgrade requires a qualified native perception readout')
            before=bank_parameters(live)
            for address,raw in P.publish_region(candidate):
                for start in range(0,len(raw),4096):P.run(live,C1.stage_bytes(address+start,raw[start:start+4096]))
            if bank_parameters(live)!=before:raise ValueError('Upgrade changed personal quantum parameters')
            destination=directory/'upgraded.rvp';live.save(destination);next_bank=destination.read_bytes()
    identifier=digest(encoded({'identity':previous,'bank_sha256':sha}))
    session.db.execute('INSERT INTO unified_archives VALUES(?,?,?,?,?,?,?,?)',(identifier,'v3',old,sha,encoded(previous),metadata,metadata_sha,revision))
    session.db.execute('UPDATE unified_banks SET snapshot=?,sha=? WHERE name="v3"',(next_bank,digest(next_bank)))
    session.db.execute('UPDATE unified_state SET identity=?,revision=? WHERE id=1',(encoded(session.identity),revision+1))
