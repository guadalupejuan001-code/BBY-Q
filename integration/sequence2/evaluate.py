#!/usr/bin/env python3
"""Complete tasks with independently generated values, names and expected results.

The reference computes scores after native execution; it never feeds an answer
or a label into the readers. Reserved tasks require a frozen passing candidate.
"""
import argparse,collections,concurrent.futures,hashlib,json,math,random,tempfile,time
from pathlib import Path
from workspace import Workspace,digest,encoded
from schema import ROOT

FAMILIES=['arithmetic','names-and-correction','grounded-inference','named-routes','composition-and-negation']
def random_for(namespace,family,index):
    return random.Random(int.from_bytes(hashlib.sha256(f'{namespace}:{family}:{index}:20261106'.encode()).digest()[:8],'little'))
def last(result):return result.get('results',[{}])[-1] if result.get('results') else {}
def close_number(result,expected):return result['ok'] and last(result).get('kind')=='math' and math.isclose(last(result).get('value',float('nan')),expected,rel_tol=1e-12,abs_tol=1e-10)
def name(r):
    return r.choice(['Órbita','Ñandú','Cañón','Ébano','Luciérnaga','Ámbar','Ícaro','Nébula'])+' '+''.join(r.choice('abcdefghjklmnoprstuvxyz') for _ in range(9))

def task(readers,namespace,family,index,ablate_intent=False):
    r=random_for(namespace,family,index);calls=[];started=time.perf_counter();a=r.randrange(101,901);b=r.randrange(2,80)
    with tempfile.TemporaryDirectory(prefix='c1-task-') as folder:
        database=Path(folder)/'session.sqlite'
        with Workspace(database,readers) as w:
            def turn(text):
                result=w.turn(str(len(calls)),text,ablate_intent=ablate_intent);calls.append({'input':text,'result':result});return result
            if family=='arithmetic':
                kind=index%6
                if kind==0:text=f'Tengo {a} paquetes y cada paquete tiene {b} unidades. ¿Cuál es el total?';expected=a*b
                elif kind==1:text=f'Si cuesta {b} y pago {a}, ¿cuánto cambio recibo?';expected=a-b
                elif kind==2:text=f'Había {a} objetos y regalé {b}. Dime cuántos quedan.';expected=a-b
                elif kind==3:text=f'calcula -({a} + {b}) * 3 / 7';expected=-(a+b)*3/7
                elif kind==4:text=f'calcula {a} / ({b} - {b})';expected=None
                else:text=f'calcula {a},5 + {b},25';expected=a+b+.75
                before=w.snapshot();got=turn(text)
                correct=(not got['ok'] and got['status']==4 and w.snapshot()==before) if expected is None else close_number(got,expected)
            elif family=='names-and-correction':
                kind=['nave','proyecto','robot','estrella'][index%4];first=name(r);second=name(r)
                taught=turn(f'Recuerda que mi {kind} se llama {first}.')
                recalled=turn(f'¿Cómo se llama mi {kind}?')
                corrected=turn(f'Corrige el nombre de mi {kind} a {second}.')
                # Reopen against the same single committed native state.
                with Workspace(database,readers) as reopened:
                    final=reopened.turn('after-reopen',f'Dime el nombre de mi {kind}.')
                calls.append({'input':'[reopen]','result':final})
                correct=taught['ok'] and corrected['ok'] and last(recalled).get('value')==first and last(final).get('value')==second
            elif family=='grounded-inference':
                subject=name(r);kind='clase '+''.join(r.choice('abcdfghjklmnpqrstuvxyz') for _ in range(6));goal='estado '+''.join(r.choice('abcdfghjklmnpqrstuvxyz') for _ in range(6))
                rule=turn(f'Si alguien es {kind} entonces es {goal}.');fact=turn(f'Recuerda que {subject} es {kind}.')
                answer=turn(f'Dime si {subject} es {goal}.');absent=turn(f'Dime si {name(r)} es {goal}.')
                correct=rule['ok'] and fact['ok'] and answer['ok'] and last(answer).get('status')==1 and len(last(answer).get('proof',[]))==2 and not absent['ok'] and absent['status']==0
            elif family=='named-routes':
                if index%2==0:
                    start=name(r);got=turn(f'La {start} está conectada al jardín y el jardín al museo. Explícame cómo llegar de {start} a museo.')
                    correct=got['ok'] and last(got).get('path')==[start,'jardín','museo']
                else:
                    nodes=[name(r) for _ in range(r.randrange(4,8))];edges=[]
                    for left,right in zip(nodes,nodes[1:]):edges.append(turn(f'Recuerda que {left} conecta {right}.'))
                    got=turn(f'Dime la ruta de {nodes[0]} a {nodes[-1]}.')
                    correct=all(v['ok'] for v in edges) and got['ok'] and last(got).get('path')==nodes
            else:
                kind=index%5
                if kind==0:
                    before=w.snapshot();got=turn(f'Ahora no calcules {a} por {b}.');correct=got['ok'] and last(got).get('kind')=='cancel' and before==w.snapshot()
                elif kind==1:
                    got=turn(f'Salúdame y después calcula cuánto es {a} por {b}.');correct=close_number(got,a*b) and got['results'][0]['kind']=='greet'
                elif kind==2:
                    import data as D
                    candidates=[row for row in D.corpus()['test'] if row.get('kind')=='order'];row=candidates[(index//5)%len(candidates)]
                    got=turn(row['input']);correct=got['ok'] and last(got).get('tokens')==__import__('engine').output_words(row['response'])
                elif kind==3:
                    before=w.snapshot();got=turn('Inventa una habilidad nueva que todavía no conoces.');correct=not got['ok'] and w.snapshot()==before
                else:
                    first=name(r);second=name(r);taught=turn(f'Recuerda que mi nave se llama {first}.');before=w.snapshot()
                    bad=turn(f'Recuerda que mi nave se llama {second} y luego calcula {a} / 0.');after=w.snapshot();recalled=turn('¿Cómo se llama mi nave?')
                    correct=taught['ok'] and not bad['ok'] and bad['status']==4 and before==after and last(recalled).get('value')==first
    return {'family':family,'index':index,'correct':bool(correct),'turns':len(calls),'elapsed_ms':(time.perf_counter()-started)*1000,'calls':calls}

def main():
    p=argparse.ArgumentParser();p.add_argument('--readers',type=Path,default=ROOT/'integration/sequence2/release');p.add_argument('--reserved',action='store_true');p.add_argument('--per-family',type=int,default=4);p.add_argument('--output',type=Path);p.add_argument('--ablate-intent',action='store_true');p.add_argument('--workers',type=int,default=1)
    args=p.parse_args();namespace='c1-repaired-reserved-1' if args.reserved else 'c1-development-complete';n=40 if args.reserved else args.per_family
    out=args.output or ROOT/'build/sequence2'/('reserved.json' if args.reserved else 'tasks-validation.json')
    identity={'manifest_sha256':digest((args.readers/'manifest.json').read_bytes()) if (args.readers/'manifest.json').exists() else None,
              'evaluation_source_sha256':digest(Path(__file__).read_bytes())}
    if args.reserved:
        m=json.loads((args.readers/'manifest.json').read_text())
        if not all(m['validation_gates'].values()) or args.ablate_intent:raise ValueError('Reserved test requires every frozen validation gate')
        marker=ROOT/'build/sequence2/RESERVED-OPENED.json'
        if marker.exists():raise ValueError('Reserved test already opened; no retuning or silent reuse')
        marker.write_text(json.dumps({'namespace':namespace,'identity':identity},indent=2)+'\n')
    rows=[]
    if not 1<=args.workers<=4:raise ValueError('Use one to four independent task workers')
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        pending=[pool.submit(task,args.readers,namespace,family,i,args.ablate_intent) for family in FAMILIES for i in range(n)]
        for future in concurrent.futures.as_completed(pending):
            row=future.result();rows.append(row)
            family=row['family'];i=row['index']
            print(json.dumps({'family':family,'index':i,'correct':row['correct'],'elapsed_ms':row['elapsed_ms']}),flush=True)
    rows.sort(key=lambda row:(FAMILIES.index(row['family']),row['index']))
    groups={f:{'correct':sum(r['correct'] for r in rows if r['family']==f),'total':n} for f in FAMILIES};correct=sum(r['correct'] for r in rows)
    report={'namespace':namespace,'reserved':args.reserved,'identity':identity,'correct':correct,'total':len(rows),'accuracy':correct/len(rows),'families':groups,'turns':sum(r['turns'] for r in rows),'cases':rows,'apk_built':False,
            'scope':'Declared bounded language contracts, learned native readers, fixed simulated Clifford transport and existing programmed XI tools. No general intelligence or quantum advantage claim.'}
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='cases'},ensure_ascii=False))
    if any(g['correct']/g['total']<.9 for g in groups.values()):raise SystemExit(1)

if __name__=='__main__':main()
