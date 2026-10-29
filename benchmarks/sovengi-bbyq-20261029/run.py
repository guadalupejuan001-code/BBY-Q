#!/usr/bin/env python3
"""External test orchestration only. Native BBY Q and original SOVENGI stay separate."""
import argparse,base64,copy,gzip,hashlib,json,os,platform,resource,shutil,statistics,subprocess,sys,threading,time,traceback
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
def digest(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
 return h.hexdigest()
def write(p,x):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
def affinity():
 cpus=os.sched_getaffinity(0);os.sched_setaffinity(0,{min(cpus)});return sorted(os.sched_getaffinity(0))
def inventory_sov(root):
 catalog=json.loads((root/'configs/conversation-models.json').read_text())['entries']
 rows=[]
 for e in catalog:
  d=root/e['path'];w=d/'weights.safetensors'
  actual=digest(w);assert actual==e['weightsSha256'],e['name']
  rows.append({'name':e['name'],'path':e['path'],'weight_bytes':w.stat().st_size,'sha256':actual,'model_id':e['modelId']})
 return rows
def timeline(suite):
 rows=[dict(c,phase='quality',repetition=0) for c in suite['cases']]
 byid={c['id']:c for c in suite['cases']}
 for rep in range(1,suite['timing_repetitions']['repetitions']+1):
  rows += [dict(byid[k],phase='repeat',repetition=rep) for k in suite['timing_repetitions']['ids']]
 return rows

def worker(a):
 affinity();out=Path(a.out);suite=json.loads(Path(a.cases).read_text());records=[];start=time.perf_counter()
 sovroot=Path(a.sov).resolve();runtime=str(Path(a.runtime).resolve());app=Path(a.app).resolve();baseline=out/'baseline.rvp'
 if a.arm=='bbyq':
  raw=gzip.decompress(base64.b64decode(Path(a.checkpoint).read_text()));baseline.write_bytes(raw)
  assert digest(baseline)==suite['conditions']['bbyq_checkpoint_sha256']
  assert digest(app)==suite['conditions']['bbyq_app_sha256']
  init={'seconds':time.perf_counter()-start,'app_bytes':app.stat().st_size,'state_bytes':len(raw),'state_gzip_bytes':len(gzip.compress(raw,mtime=0)),'runtime_bytes':Path(runtime).stat().st_size}
 else:
  sys.path.insert(0,str(sovroot/'src'))
  import torch
  torch.set_num_threads(1);torch.set_num_interop_threads(1)
  from ia_propia.sovengi import Sovengi
  from ia_propia.conversation.catalog import load_catalog
  before=inventory_sov(sovroot)
  available=load_catalog(sovroot/'configs/conversation-models.json',sovroot)
  assert len(available)==35 and all(e['available'] for e in available)
  config=json.loads((sovroot/'configs/gnosis.json').read_text());config['projectRoot']=str(sovroot);config['brain']['state_dir']=str((out/'private-sovengi').resolve())
  conf=out/'isolated-sovengi.json';write(conf,config);product=Sovengi(conf)
  init={'seconds':time.perf_counter()-start,'catalog_models':len(before),'weights_bytes':sum(e['weight_bytes'] for e in before),'torch':torch.__version__,'weights':before,'configuration_changes':['projectRoot resolves same checkout','state_dir redirects mutable conversation state to disposable test directory']}
 write(out/(a.arm+'-initialization.json'),init)
 try:
  for index,case in enumerate(timeline(suite)):
   row={k:case[k] for k in ['id','category','language','phase','repetition','facts','question','criterion']};setup=[]
   try:
    if a.arm=='bbyq':
     live=out/'current-dialogue.rvp';shutil.copy2(baseline,live)
     for fact in case['facts']:
      ts=time.perf_counter();p=subprocess.run([runtime,'app-turn',str(app),str(live),str(live),case['language'],fact],capture_output=True,text=True,timeout=30)
      setup.append({'input':fact,'output':p.stdout.rstrip(),'stderr':p.stderr,'returncode':p.returncode,'seconds':time.perf_counter()-ts})
      if p.returncode:raise RuntimeError('Native setup failed: '+p.stderr)
     ts=time.perf_counter();p=subprocess.run([runtime,'app-turn',str(app),str(live),str(live),case['language'],case['question']],capture_output=True,text=True,timeout=30);elapsed=time.perf_counter()-ts
     row.update(output=p.stdout.rstrip(),seconds=elapsed,status='ok' if p.returncode==0 else 'error',stderr=p.stderr,returncode=p.returncode,setup=setup,state_bytes_after=live.stat().st_size)
    else:
     session=product.connect('comparison-'+str(index),context_session_id='comparison-'+str(index))
     # Same user facts, same final question. No expected answers or fabricated assistant turns.
     messages=[{'role':'user','content':x} for x in case['facts']+[case['question']]]
     ts=time.perf_counter();response=session.request({'schemaVersion':1,'operation':'conversation.reply','input':{'messages':messages,'max_new_tokens':48,'temperature':0,'seed':20261029}});elapsed=time.perf_counter()-ts
     row.update(output=response.get('result',{}).get('text',''),seconds=elapsed,status=response['status'],raw_response=response)
    row['rss_peak_self_kib']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
   except Exception as e:
    row.update(status='exception',error=type(e).__name__+': '+str(e),traceback=traceback.format_exc(),setup=setup)
   records.append(row);write(out/(a.arm+'-responses.json'),records)
   print(json.dumps({'event':'response','arm':a.arm,'id':row['id'],'phase':row['phase'],'status':row['status'],'seconds':row.get('seconds'),'output':row.get('output','')},ensure_ascii=False),flush=True)
 finally:
  if a.arm=='sovengi':product.close()
 if a.arm=='sovengi':
  after=inventory_sov(sovroot);assert before==after,'SOVENGI weights changed';immutable={'weights_unchanged':True,'models':len(after)}
 else:
  assert digest(app)==suite['conditions']['bbyq_app_sha256'];assert digest(baseline)==suite['conditions']['bbyq_checkpoint_sha256']
  immutable={'app_unchanged':True,'original_checkpoint_unchanged':digest(Path(a.checkpoint))==a.checkpoint_file_sha}
 write(out/(a.arm+'-worker-summary.json'),{'initialization':init,'immutability':immutable,'rss_peak_self_kib':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'rss_peak_children_kib':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'elapsed_seconds':time.perf_counter()-start,'cpu_affinity':sorted(os.sched_getaffinity(0))})

def tree_rss(pid):
 total=0
 try:
  status=Path('/proc/%d/status'%pid).read_text();total=int(next(x.split()[1] for x in status.splitlines() if x.startswith('VmRSS:')))*1024
  children=Path('/proc/%d/task/%d/children'%(pid,pid)).read_text().split()
  for child in children:total+=tree_rss(int(child))
 except (OSError,StopIteration,ValueError):pass
 return total
def main(a):
 out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
 before_checkpoint=digest(a.checkpoint);suite=json.loads(Path(a.cases).read_text())
 write(out/'protocol-frozen.json',suite)
 env=os.environ.copy();env.update(OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',OPENBLAS_NUM_THREADS='1',TOKENIZERS_PARALLELISM='false',PYTHONHASHSEED='0')
 runs={};started=time.perf_counter()
 # Sequential arms on the same runner. Model loads and setup are reported separately.
 for arm in ['bbyq','sovengi']:
  cmd=[sys.executable,str(Path(__file__).resolve()),'--arm',arm,'--runtime',a.runtime,'--sov',a.sov,'--app',a.app,'--checkpoint',a.checkpoint,'--cases',a.cases,'--out',a.out,'--checkpoint-file-sha',before_checkpoint]
  logfile=out/(arm+'-worker.log');peak=0
  with logfile.open('w') as log:
   p=subprocess.Popen(cmd,stdout=log,stderr=subprocess.STDOUT,env=env)
   while p.poll() is None:
    peak=max(peak,tree_rss(p.pid));time.sleep(.01)
  runs[arm]={'returncode':p.returncode,'sampled_process_tree_peak_rss_bytes':peak}
  print(logfile.read_text(),flush=True)
  summary=out/(arm+'-worker-summary.json')
  if summary.exists():runs[arm]['summary']=json.loads(summary.read_text())
  answers=out/(arm+'-responses.json')
  if answers.exists():
   rows=json.loads(answers.read_text());quality=[x for x in rows if x['phase']=='quality'];repeat=[x for x in rows if x['phase']=='repeat']
   runs[arm]['quality_calls']=len(quality);runs[arm]['technical_errors']=sum(x['status']!='ok' for x in rows)
   runs[arm]['quality_latency_median_ms']=statistics.median([x['seconds']*1000 for x in quality if 'seconds' in x]) if any('seconds' in x for x in quality) else None
   runs[arm]['repeat_latency_median_ms']=statistics.median([x['seconds']*1000 for x in repeat if 'seconds' in x]) if any('seconds' in x for x in repeat) else None
   runs[arm]['repeat_by_case_ms']={key:[x['seconds']*1000 for x in repeat if x['id']==key and 'seconds' in x] for key in suite['timing_repetitions']['ids']}
   modelids=set()
   for x in rows:modelids.update(x.get('raw_response',{}).get('result',{}).get('ensemble',{}).get('modelIdsExecuted',[]))
   if arm=='sovengi':runs[arm]['actually_executed_model_ids']=sorted(modelids)
  write(out/'partial-results.json',runs)
 report={'version':suite['version'],'environment':{'platform':platform.platform(),'python':platform.python_version(),'cpu_count':os.cpu_count(),'cpu_model':next((x.split(':',1)[1].strip() for x in Path('/proc/cpuinfo').read_text().splitlines() if x.startswith('model name')),'unknown'),'memory_total':next(x for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemTotal:')),'runner':os.environ.get('RUNNER_OS'),'logical_cpu_affinity_per_worker':1},'protocol_sha256':digest(a.cases),'runs':runs,'elapsed_seconds':time.perf_counter()-started,'original_checkpoint_unchanged':before_checkpoint==digest(a.checkpoint),'training_executed':False,'semantic_review':'pending manual review of original outputs against frozen criteria','scope':'Same fictional facts and questions, one runner, one logical CPU. BBY Q uses persistent XI facts in disposable state; SOVENGI receives all supplied facts in its original context pipeline and uses its default rotating ensemble. End-to-end query latency, not equivalent token work. Native process startup/state IO included; SOVENGI model loading is lazy and first calls include it. RSS is sampled sum over worker and descendants, excludes driver; shared pages may be counted twice. No power/energy or Android measurements.'}
 write(out/'results.json',report);print('COMPARISON_REPORT_JSON='+json.dumps(report,ensure_ascii=False),flush=True)
 assert all(x['returncode']==0 for x in runs.values()),'One or more workers failed; see retained partial evidence'
 assert all(x.get('quality_calls')==32 for x in runs.values()),'Incomplete quality cases'
 assert report['original_checkpoint_unchanged']

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--arm',choices=['bbyq','sovengi']);p.add_argument('--runtime',required=True);p.add_argument('--sov',required=True);p.add_argument('--app',required=True);p.add_argument('--checkpoint',required=True);p.add_argument('--cases',required=True);p.add_argument('--out',required=True);p.add_argument('--checkpoint-file-sha');a=p.parse_args()
 worker(a) if a.arm else main(a)
