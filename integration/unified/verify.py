#!/usr/bin/env python3
"""Integration checks against native banks, persistence and failure paths."""
import argparse,concurrent.futures,json,tempfile
from pathlib import Path
from .common import ROOT,C1,Legacy,Entity,encoded,digest,read,write
from .session import Session

def good(session,identifier,text,payload=None):
    value=session.turn(identifier,text,payload);assert value['ok'],value;return value

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--readers',type=Path,default=ROOT/'integration/unified/release');args=parser.parse_args();checks=[]
    with tempfile.TemporaryDirectory(prefix='bbyq-unified-check-') as temporary:
        directory=Path(temporary);database=directory/'personal.sqlite'
        with Legacy.Workspace(database) as old:
            assert old.turn('old-name','Recuerda que mi nave se llama Niña Ámbar.')['ok']
        with Session(database,args.readers) as session:
            value=good(session,'old-recall','¿Cómo se llama mi nave?');assert value['results'][-1]['value']=='Niña Ámbar'
            full='guarda la regla Faro Azul con valor 1 observa Nara con muestra 88113 y resuelve desde 3'
            result=good(session,'full',full);mission=result['results'][-1]
            assert mission['action']==1 and mission['voice']['faithful'] and mission['class']==0 and mission['goal']==6,mission
            operations={t['operation'] for t in result['trace']}
            assert {'c1_encode_input/c1_next','qm_exchange','qm_read','vqc_forward','entity_infer','qrl_step','entity_decide','qchat_encode/qchat_next','entity_voice_check'}<=operations
            before=session.snapshot();assert session.turn('full',full)==result and session.snapshot()==before
            try:session.turn('full',full+' otra')
            except ValueError:pass
            else:raise AssertionError('Request ID collision accepted')
            checks.append('one natural-language request executes every quantum component and commits one shared task; exact replay does not execute twice')
            try:session.turn('crash','guarda la regla Otra con valor 0 observa Brisa con muestra 122121 y resuelve desde 3',fail_after=2)
            except RuntimeError:pass
            else:raise AssertionError('Injected failure did not run')
            assert session.snapshot()==before
            assert session.db.execute('SELECT count(*) FROM unified_requests WHERE id="crash"').fetchone()[0]==0
            assert session.db.execute('SELECT count(*) FROM unified_supervision WHERE name="otra"').fetchone()[0]==0
            checks.append('failure after quantum memory and VQC mutations rolls back every bank, symbolic projection, dictionary, supervision and receipt')
            good(session,'bridge-rule','si alguien es clase cero entonces es alerta')
            query=good(session,'bridge-query','dime si observación Nara es alerta')
            assert query['results'][-1]['status']==1 and query['results'][-1]['proof'],query
            checks.append('native C1 reasoning consumes the actual VQC classification and derives a symbolic conclusion with proof')
            explained=good(session,'explain','explica la última tarea')['results'][-1]
            assert explained['action']==mission['action'] and explained['trace']==mission['trace']
            # Correction after the task must not change its original teacher.
            good(session,'correct','corrige la regla Faro Azul a 0')
            original=session.snapshot()
            try:session.turn('feedback-crash','aprende de la última tarea',fail_after=1)
            except RuntimeError:pass
            else:raise AssertionError('Learning failure was not injected')
            assert session.snapshot()==original
            assert session.db.execute('SELECT feedback_id FROM unified_tasks WHERE id=?',(mission['task_id'],)).fetchone()[0] is None
            feedback=good(session,'feedback','aprende de la última tarea');learned=feedback['results'][-1]
            assert learned['success'] and all(learned['changed'].values()),learned
            assert set(learned['updates'])=={'entity','vqc','qrl','memory','voice','router'}
            assert session.snapshot()['banks']['router']!=original['banks']['router']
            assert session.snapshot()['banks']['text']==original['banks']['text']
            current=good(session,'retained','lee la regla Faro Azul')['results'][-1];assert current['value']==0,current
            snapshot=session.snapshot();assert session.turn('feedback','aprende de la última tarea')==feedback and session.snapshot()==snapshot
            try:session.turn('feedback-again','aprende de la última tarea')
            except ValueError:pass
            else:raise AssertionError('Duplicate feedback trained twice')
            assert session.snapshot()==snapshot
            checks.append('verified learning changes every learned bank, rolls back all gradients on failure, retains corrected live memory, uses the immutable original task teacher and rejects duplicate learning')
            negative=good(session,'cancel','no resuelvas Nara');assert not negative['committed'] and session.snapshot()==snapshot
            data=[(i%23-11)/100 for i in range(1000)];payload={'observations':data}
            observed=good(session,'external','observa Brisa Nueva',payload)['results'][-1]
            assert observed['observations']==1000
            shared=good(session,'external-task','resuelve Brisa Nueva usando la regla Faro Azul desde 3')['results'][-1]
            frame,_=session._task(shared['task_id']);assert frame['input']['values']==data and len(frame['input']['values'])==1000
            assert observed['input_sha256']==digest(encoded(frame['input']))
            current=session.snapshot()
            for invalid in ([0.0]*999,[0.0]*999+[float('nan')],[0.0]*999+[True],[0.0]*999+[10**400]):
                try:session.turn('invalid','observa Brisa Nueva',{'observations':invalid})
                except ValueError:pass
                else:raise AssertionError('Malformed sensor payload accepted')
                assert session.snapshot()==current
            try:session.turn('label-leak','observa Brisa Nueva',{'labels':{'class':1,'rule':0}})
            except ValueError:pass
            else:raise AssertionError('Teacher labels accepted in inference')
            assert session.snapshot()==current
            checks.append('typed observations preserve all 1000 values; malformed arrays and inference-time teacher labels leave the session unchanged')
        # A legacy client can keep writing the original facts table. The next
        # unified turn imports that exact state without replacing quantum banks.
        with Legacy.Workspace(database) as old:
            assert old.turn('legacy-correction','Corrige el nombre de mi nave a Ébano Lunar.')['ok']
        with Session(database,args.readers) as session:
            answer=good(session,'restart','¿Cómo se llama mi nave?');assert answer['results'][-1]['value']=='Ébano Lunar',answer
            recalled=good(session,'restart-quantum','lee la regla Faro Azul');assert recalled['results'][-1]['value']==0
            assert any(row['request_id']=='old-name' for row in session.history())
            assert any(row['request_id']=='feedback' for row in session.history())
            checks.append('restart and compatible legacy writes preserve personal names, quantum memory, shared task history and learned banks in the same database')
            # Corruption is detected before any new operation can publish state.
            before=session.snapshot();raw=session.db.execute('SELECT snapshot FROM unified_banks WHERE name="memory"').fetchone()[0]
            session.db.execute('UPDATE unified_banks SET snapshot=? WHERE name="memory"',(raw+b'x',))
            try:session.turn('corrupt','calcula 3 + 4')
            except ValueError:pass
            else:raise AssertionError('Corrupt bank was accepted')
            session.db.execute('UPDATE unified_banks SET snapshot=? WHERE name="memory"',(raw,));assert session.snapshot()==before
            checks.append('a corrupted native bank is rejected before inference and cannot publish a partial result')
        def retry(_):
            with Session(database,args.readers) as session:return session.turn('simultaneous','guarda la regla Bruma con valor 1')
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:duplicates=list(pool.map(retry,range(2)))
        assert duplicates[0]==duplicates[1] and duplicates[0]['ok']
        with Session(database,args.readers) as session:
            assert session.db.execute('SELECT count(*) FROM unified_requests WHERE id="simultaneous"').fetchone()[0]==1
            assert good(session,'simultaneous-recall','lee la regla Bruma')['results'][-1]['value']==1
            missing=good(session,'missing','resuelve Nara usando la regla Desconocida desde 3')['results'][-1]
            assert missing['action']==-1 and not missing['supported'] and missing['voice']['faithful']
        checks.append('simultaneous retries commit one quantum write; a missing premise produces the native learned refusal instead of a fabricated action')
    report={'passed':True,'count':len(checks),'checks':checks,'apk_built':False}
    destination=ROOT/'build/unified/integration-checks.json';destination.parent.mkdir(parents=True,exist_ok=True);write(destination,report);print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
