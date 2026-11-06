#!/usr/bin/env python3
"""Reproduce real U01 personal learning, then test a lossless atomic upgrade."""
import argparse,json,sqlite3,subprocess,sys,tempfile
from contextlib import ExitStack
from pathlib import Path
from .common import ROOT,C1,encoded,digest,read,write
from .session import Session
from .upgrades import bank_parameters
from . import perception as P

PREVIOUS='d716f487cd01438e1a74b9a52119352bc7bf5d94'
OLD_PROGRAM='''
import json,sys
from pathlib import Path
from integration.unified.session import Session
from integration.unified.common import ROOT
assert ROOT==Path.cwd().resolve()
with Session(sys.argv[1]) as session:
    for ident,text in [('old-name','Recuerda que mi nave se llama Niña Ámbar.'),('old-task','guarda la regla Faro Azul con valor 1 observa Nara con muestra 88113 y resuelve desde 3'),('old-feedback','aprende de la última tarea'),('old-observation','observa Bruma con muestra 1111914917'),('old-symbolic-rule','si alguien es clase uno entonces es alerta')]:
        result=session.turn(ident,text);assert result['ok'],result
        if ident=='old-observation':assert result['results'][-1]['class']==0
    print(json.dumps({'identity':session.identity,'snapshot':session.snapshot(),'history':session.history()},ensure_ascii=False))
'''

def sql_snapshot(database):
    with sqlite3.connect(database) as db:
        metadata,sha,identity,revision=db.execute('SELECT metadata,sha,identity,revision FROM unified_state').fetchone()
        return {'metadata_sha':sha,'identity':json.loads(identity),'revision':revision,'banks':dict(db.execute('SELECT name,sha FROM unified_banks')),'history':[json.loads(row[0]) for row in db.execute('SELECT result FROM requests ORDER BY rowid')]}

def copy_database(source,target):
    with sqlite3.connect(source) as original,sqlite3.connect(target) as copy:original.backup(copy)

def v3_parameters(database,directory,suffix):
    with sqlite3.connect(database) as db:raw=db.execute('SELECT snapshot FROM unified_banks WHERE name="v3"').fetchone()[0]
    path=directory/(suffix+'.rvp');path.write_bytes(raw)
    with C1.XiSession(C1.RT/'build/xi_session',path) as native:return bank_parameters(native)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--readers',type=Path,default=ROOT/'integration/unified/release');parser.add_argument('--fixture',type=Path);args=parser.parse_args();checks=[]
    with tempfile.TemporaryDirectory(prefix='bbyq-u02-upgrade-proof-') as temporary:
        directory=Path(temporary);database=directory/'personal.sqlite';old_checkout=None
        try:
            if args.fixture:copy_database(args.fixture,database)
            else:
                old_checkout=directory/'u01'
                subprocess.run(['git','worktree','add','--detach',str(old_checkout),PREVIOUS],cwd=ROOT,check=True,capture_output=True)
                (old_checkout/'deps').symlink_to(ROOT/'deps',target_is_directory=True)
                child=subprocess.run([sys.executable,'-c',OLD_PROGRAM,str(database)],cwd=old_checkout,check=True,capture_output=True,text=True)
                assert json.loads(child.stdout)['identity']['version']=='U01'
            before=sql_snapshot(database);parameters=v3_parameters(database,directory,'before')
            # Reject unknown identities without changing any bank or receipt.
            incompatible=directory/'incompatible.sqlite';copy_database(database,incompatible)
            with sqlite3.connect(incompatible) as db:
                identity=dict(before['identity']);identity['router_words']='0'*64
                db.execute('UPDATE unified_state SET identity=?',(encoded(identity),))
            rejected_before=sql_snapshot(incompatible)
            try:Session(incompatible,args.readers)
            except ValueError:pass
            else:raise AssertionError('An unbound predecessor identity was accepted')
            assert sql_snapshot(incompatible)==rejected_before
            checks.append('unknown predecessor identities are rejected without resetting data')
            # Abort at the last SQL update, after staging the new bank and
            # archive. SQLite must roll back the whole upgrade.
            with sqlite3.connect(database) as db:
                db.execute("CREATE TRIGGER injected_upgrade_abort BEFORE UPDATE OF identity ON unified_state BEGIN SELECT RAISE(ABORT,'injected upgrade abort'); END")
            try:Session(database,args.readers)
            except sqlite3.IntegrityError as error:assert 'injected upgrade abort' in str(error)
            else:raise AssertionError('Upgrade failure was not injected')
            assert sql_snapshot(database)==before
            with sqlite3.connect(database) as db:
                assert db.execute('SELECT count(*) FROM unified_archives').fetchone()[0]==0
                db.execute('DROP TRIGGER injected_upgrade_abort')
            checks.append('a failure after the native bank and archive writes rolls back the entire migration')
            with Session(database,args.readers) as session:
                migrated=sql_snapshot(database)
                assert migrated['identity']['version']=='U02' and migrated['revision']==before['revision']+1
                assert migrated['metadata_sha']==before['metadata_sha'] and migrated['history']==before['history']
                assert {k:v for k,v in migrated['banks'].items() if k!='v3'}=={k:v for k,v in before['banks'].items() if k!='v3'}
                assert v3_parameters(database,directory,'after')==parameters
                archive=session.db.execute('SELECT snapshot,sha,identity,metadata_sha FROM unified_archives').fetchone()
                assert digest(archive[0])==archive[1]==before['banks']['v3'] and json.loads(archive[2])==before['identity'] and archive[3]==before['metadata_sha']
                assert session.db.execute('SELECT count(*) FROM unified_archives').fetchone()[0]==1
                replay=session.turn('old-feedback','aprende de la última tarea')
                assert replay==next(row for row in before['history'] if row['request_id']=='old-feedback')
                if any(row['request_id']=='old-observation' for row in before['history']):
                    derived=session.turn('new-derived','dime si observación Bruma es alerta')
                    assert derived['ok'] and derived['results'][-1]['status']==1 and derived['results'][-1]['proof'],derived
                    assert any(row['operation']=='vqc_forward' for row in derived['trace'])
                    checks.append('U01-derived wrong facts are recomputed with U02 before new reasoning; historical receipts remain immutable')
                name=session.turn('new-recall','¿Cómo se llama mi nave?');assert name['ok'] and name['results'][-1]['value']=='Niña Ámbar'
                memory=session.turn('new-memory','lee la regla Faro Azul');assert memory['ok'] and memory['results'][-1]['value']==1
                decision=session.turn('new-mission','resuelve Nara usando la regla Faro Azul desde 3');assert decision['ok'] and decision['results'][-1]['action']==1
                after=session.snapshot()
            with Session(database,args.readers) as session:
                assert session.snapshot()==after and session.db.execute('SELECT count(*) FROM unified_archives').fetchone()[0]==1
            checks.append('real U01 personal gradients, original quantum parameters, names, memory, task frames, dictionaries and receipts survive U02 unchanged; the old v3 bank remains archived')
            checks.append('replaying prior feedback is exact and does not train twice; reopening does not repeat the upgrade')
        finally:
            if old_checkout is not None:
                link=old_checkout/'deps'
                if link.is_symlink():link.unlink()
                subprocess.run(['git','worktree','remove','--force',str(old_checkout)],cwd=ROOT,check=True,capture_output=True)
    report={'passed':True,'count':len(checks),'checks':checks,'previous_commit':PREVIOUS,'apk_built':False};write(ROOT/'build/unified/upgrade-checks.json',report);print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
