#!/usr/bin/env python3
"""Real learned routing plus durable, atomic and idempotent native operations."""
import argparse,concurrent.futures,json,tempfile
from pathlib import Path
from workspace import Workspace,ROOT

def main():
    p=argparse.ArgumentParser();p.add_argument('--readers',type=Path,default=ROOT/'integration/sequence2/release');args=p.parse_args();checks=[]
    with tempfile.TemporaryDirectory(prefix='c1-transactions-') as folder:
        database=Path(folder)/'session.sqlite'
        with Workspace(database,args.readers) as w:
            taught=w.turn('teach','Recuerda que mi nave se llama Niña Ámbar.')
            assert taught['ok'],taught
            before=w.snapshot();replay=w.turn('teach','Recuerda que mi nave se llama Niña Ámbar.')
            assert taught==replay and w.snapshot()==before
            try:w.turn('teach','Recuerda que mi nave se llama Otra.')
            except ValueError:pass
            else:raise AssertionError('A request ID accepted different input')
            checks.append('exact replay is idempotent; conflicting request reuse is rejected')
            try:w.turn('crash','Recuerda que mi nave se llama Cambio y luego calcula 7 + 3.',fail_after=1)
            except RuntimeError as error:assert str(error)=='Injected failure after native operation'
            else:raise AssertionError('Injected failure did not reach the native operation')
            assert w.snapshot()==before
            assert w.db.execute('SELECT count(*) FROM requests WHERE id="crash"').fetchone()[0]==0
            checks.append('failure after a native write rolls back snapshot, dictionary and request record')
            failed=w.turn('bad-math','Recuerda que mi nave se llama Otra y luego calcula 9 / 0.')
            assert not failed['ok'] and failed['status']==4 and w.snapshot()==before,failed
            negative=w.turn('negative','Ahora no calcules 25 por 4.')
            assert negative['ok'] and not negative['committed'] and w.snapshot()==before,negative
            checks.append('later arithmetic failure and negative request publish no partial changes')
        with Workspace(database,args.readers) as w:
            answer=w.turn('recall','¿Cómo se llama mi nave?');assert answer['ok'] and answer['results'][-1]['value']=='Niña Ámbar',answer
            before=w.snapshot();metadata=w.db.execute('SELECT metadata FROM state WHERE id=1').fetchone()[0]
            w.db.execute('UPDATE state SET metadata=? WHERE id=1',(metadata+b' ',))
            try:w.turn('bad-dictionary','¿Cómo se llama mi nave?')
            except ValueError as error:assert 'dictionaries' in str(error)
            else:raise AssertionError('Dictionary corruption was ignored')
            w.db.execute('UPDATE state SET metadata=? WHERE id=1',(metadata,))
            snapshot=w.db.execute('SELECT snapshot FROM state WHERE id=1').fetchone()[0]
            w.db.execute('UPDATE state SET snapshot=? WHERE id=1',(snapshot+b' ',))
            try:w.turn('bad-snapshot','¿Cómo se llama mi nave?')
            except ValueError as error:assert 'snapshot' in str(error)
            else:raise AssertionError('Native checkpoint corruption was ignored')
            w.db.execute('UPDATE state SET snapshot=? WHERE id=1',(snapshot,))
            assert w.snapshot()==before
            checks.append('reopen retains the committed name; dictionary and checkpoint corruption fail closed')
        def simultaneous(_):
            with Workspace(database,args.readers) as w:return w.turn('parallel','Recuerda que mi robot se llama Ébano Azul.')
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:results=list(pool.map(simultaneous,range(2)))
        assert results[0]==results[1] and results[0]['ok'],results
        with Workspace(database,args.readers) as w:
            assert w.db.execute('SELECT count(*) FROM requests WHERE id="parallel"').fetchone()[0]==1
            answer=w.turn('parallel-recall','¿Cómo se llama mi robot?');assert answer['results'][-1]['value']=='Ébano Azul'
        checks.append('two sessions retrying the same task publish exactly one result')
    report={'passed':True,'count':len(checks),'checks':checks,'learned_routing_used':True,'apk_built':False}
    path=ROOT/'build/sequence2/workspace-checks.json';path.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))

if __name__=='__main__':main()
