#!/usr/bin/env python3
"""Independent generated tasks for the programmed native symbolic agent.
The Python reference scores results; it never supplies an answer to XI.
"""
import argparse,collections,hashlib,json,math,random,tempfile,time
from pathlib import Path
from engine import Engine,ROOT,BUILD,build,sha
FAMILIES=['chains','relational','contradictions','routes','arithmetic','mixed-restart']
def rng(namespace,family,index):return random.Random(int.from_bytes(hashlib.sha256(f'630511:{namespace}:{family}:{index}'.encode()).digest()[:8],'little'))
def last(result):return result['results'][-1]
def statuses(result):return [r['status'] for r in result.get('results',[]) if r['op'] in [3,4,5]]
def case(namespace,family,index):
 r=rng(namespace,family,index);tag='n'+str(r.randrange(10**8,10**9));started=time.perf_counter()
 with Engine() as e:
  if family=='chains':
   n=r.randint(3,8);subject=tag+'a';kinds=[tag+'t'+str(i) for i in range(n+1)]
   lines=['resuelve:',f'{subject} es {kinds[0]}']+[f'si $x es {a} entonces $x es {b}' for a,b in zip(kinds,kinds[1:])]+[f'¿{subject} es {kinds[-1]}?',f'¿{tag}ausente es {kinds[-1]}?']
   result=e.run('\n'.join(lines));correct=statuses(result)==[1,0] and len(result['results'][0]['proof'])==n+1
  elif family=='relational':
   a,b,c,d=[tag+s for s in 'abcd'];p,q,s=[tag+v for v in ['relacion','dependencia','resultado']]
   lines=['resuelve:',f'{a} {p} {b}',f'{b} {q} {c}',f'{d} {q} {d}',f'si $x {p} $y y $y {q} $z entonces $x {s} $z',f'¿{a} {s} {c}?',f'¿{a} {s} {d}?']
   result=e.run('\n'.join(lines));correct=statuses(result)==[1,0] and len(result['results'][0]['proof'])==3
  elif family=='contradictions':
   a,b=tag+'sujeto',tag+'estado';result=e.run(f'recuerda que {a} es {b}\nrecuerda que {a} no es {b}\n¿{a} es {b}?');observed=[result['status']]
   observed.append(e.run(f'corrige que {a} no es {b}\n¿{a} es {b}?')['status']);observed.append(e.run(f'olvida que {a} no es {b}\n¿{a} es {b}?')['status']);correct=observed==[2,-1,0]
  elif family=='routes':
   n=r.randint(9,28);nodes=[tag+'p'+str(i) for i in range(n)];edges={(nodes[i],nodes[i+1]) for i in range(n-1)}
   for _ in range(n//2):
    a,b=r.sample(nodes,2);edges.add((a,b))
   goal=nodes[-1] if index%5 else tag+'inalcanzable';lines=['resuelve:']+[f'{a} conecta {b}' for a,b in sorted(edges)]+[f'ruta desde {nodes[0]} hasta {goal}'];result=e.run('\n'.join(lines));out=last(result)
   distances={nodes[0]:0};queue=collections.deque([nodes[0]])
   while queue:
    a=queue.popleft()
    for x,b in sorted(edges):
     if x==a and b not in distances:distances[b]=distances[a]+1;queue.append(b)
   if goal not in distances:correct=out['status']==0
   else:
    reverse={v:k for k,v in e.vocab.items()};path=[reverse[i] for i in out.get('path',[])];correct=out['status']==1 and path[0]==nodes[0] and path[-1]==goal and len(path)-1==distances[goal] and all((a,b)in edges for a,b in zip(path,path[1:]))
  elif family=='arithmetic':
   a,b,c,d=[r.randint(1,50) for _ in range(4)]
   if index%5==0:
    expression=f'calcula {a} / ({b} - {b})';result=e.run(expression);correct=result['status']==4
   else:
    expression=f'calcula -({a} + {b}) * {c} / {d} + 0.5';expected=-(a+b)*c/d+.5;result=e.run(expression);correct=result['status']==1 and math.isclose(last(result)['result'],expected,rel_tol=1e-12,abs_tol=1e-10)
  else:
   # Persisted new names/rules must transfer to a later session; temporary
   # premises must remain local, while numeric tools share the same task.
   a,b,c=tag+'persona',tag+'clase',tag+'meta'
   with tempfile.TemporaryDirectory(prefix='bbyq-zero-restart-') as folder:
    with Engine(folder) as first:
     first.run(f'recuerda que {a} es {b}\naprende regla: si $x es {b} entonces $x es {c}');first.save()
    with Engine(folder) as second:
     result=second.run(f'¿ella es {c}?\ncalcula ({index}+7)*2');correct=statuses(result)==[1,1] and last(result)['result']==(index+7)*2
     result2=second.run(f'resuelve:\n{tag}temp conecta {tag}fin\nruta desde {tag}temp hasta {tag}fin');correct&=result2['status']==1
     result3=second.run(f'ruta desde {tag}temp hasta {tag}fin');correct&=result3['status']==0
 return {'family':family,'index':index,'correct':bool(correct),'elapsed_ms':(time.perf_counter()-started)*1000,'result_status':result['status']}
def checks():
 result=[]
 with Engine() as e:
  e.run('recuerda que alfa es origen\naprende regla: si $x es origen entonces $x es destino')
  assert e.run('¿alfa es destino?')['status']==1
  assert e.run('olvida regla: si $x es origen entonces $x es destino\n¿alfa es destino?')['status']==0;result.append('rule removal invalidates derived conclusions')
  assert e.run('aprende regla: si $x no es origen entonces $y es destino')['status']==4;result.append('unbound variables rejected even with negative premises')
  e.run('aprende regla: si $x es origen entonces $x es destino')
  assert e.run('¿alfa es destino?',budget=1)['status']==3;result.append('resource exhaustion differs from unknown')
  e.run('olvida que alfa es origen');assert e.run('¿alfa es destino?')['status']==0;result.append('fact removal invalidates derived conclusions')
  assert e.run('hola puedes inventar cualquier cosa')['unsupported'];result.append('unsupported text does not create a proof')
  assert e.run('calcula 2 (3)')['status']==4;result.append('implicit malformed arithmetic rejected')
  assert e.run('¿dato es desconocido?\ncalcula 2 + 3')['status']==0;result.append('a successful later tool does not hide an unknown earlier goal')
  e.run('correcto');n=e.integer(944);e.run('incorrecto');assert e.integer(944)==n+1;result.append('native shared feedback learns without editing facts')
  e.parse('recupera faro');e.stage(192,[14]);e.stage(216,[1])
  from engine import Z
  e.raw(f'fstore {Z+208} .9');e.call(5);assert e.numbers(16384,4)[2]==e.schema['words']['uno'];result.append('quantum-memory output projects to a grounded symbolic term')
  e.parse('observa senal muestra 10');e.stage(192,[15]);e.stage(216,[1]);e.raw(f'fstore {Z+208} .1');e.call(5);assert e.numbers(16384,4)[2]==e.schema['words']['clase0'];result.append('classifier output projects without unresolved numeric placeholders')
  e.stage(216,[0]);e.call(5);assert e.integer(16)==0;result.append('a missing observation creates no asserted premise')
 return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--reserved',action='store_true');p.add_argument('--namespace');p.add_argument('--output',type=Path,default=ROOT/'build/zero-development.json');args=p.parse_args();build()
 namespace=args.namespace or ('zero-reserved' if args.reserved else 'zero-development');n=20 if args.reserved else 4
 pinned={str(path.relative_to(ROOT)):sha(path) for path in [ROOT/'ai/personal/zero/core.xi.in',ROOT/'ai/personal/zero/model.mjs',ROOT/'ai/personal/zero/schema.mjs']}
 if args.reserved:(ROOT/'build/ZERO-RESERVED-OPENED.json').write_text(json.dumps({'namespace':namespace,'source_hashes':pinned},indent=2)+'\n')
 rows=[case(namespace,f,i) for f in FAMILIES for i in range(n)];extra=checks();k=sum(r['correct'] for r in rows)
 report={'version':'BBY-Q-0-1','namespace':namespace,'source_hashes':pinned,'programmed_symbolic_engine':True,'general_intelligence_demonstrated':False,'correct':k,'tasks':len(rows),'accuracy':k/len(rows),'families':{f:{'correct':sum(r['correct'] for r in rows if r['family']==f),'tasks':n} for f in FAMILIES},'checks':extra,'cases':rows,'limits':['Controlled grammar, at most two premises and three rule variables.','Finite native work window and explicit search budget.','General-purpose symbolic composition and user-taught knowledge, not an open-ended foundation model or an AGI benchmark.','The existing quantum specialists remain unchanged and are invoked for applicable typed observations.']}
 args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k not in ['cases','source_hashes','limits']},ensure_ascii=False))
 if k!=len(rows):raise SystemExit(1)
if __name__=='__main__':main()
