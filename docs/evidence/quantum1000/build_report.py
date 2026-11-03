#!/usr/bin/env python3
"""Package measured campaigns, checkpoints and figures; no agent computation."""
import csv
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
BUILD=ROOT/'build'
MODELS=ROOT/'models/quantum1000'
def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def save_gz(target,raw):
    target.parent.mkdir(parents=True,exist_ok=True)
    data=gzip.compress(raw,mtime=0)
    if target.exists() and target.read_bytes()!=data:raise RuntimeError('refusing to replace a different checkpoint: '+str(target))
    target.write_bytes(data)
def metric(d):return d.get('accuracy',d.get('success_rate'))

names=['connected-vqc-linear-1000','connected-vqc-dense-1000','connected-qrl-easy-1000',
       'connected-cz-vqc-linear-1000','connected-cz-vqc-dense-1000','connected-cz-qrl-easy-1000']
campaigns=[];checkpoints=[];curves=[]
for name in names:
    source=BUILD/name;d=json.loads((source/'manifest.json').read_text())
    assert d['completed_episodes']==1000
    log=(source/'training.jsonl').read_bytes();rows=[json.loads(x) for x in log.splitlines()]
    assert len(rows)==1000 and [r['episode'] for r in rows]==list(range(1,1001))
    final=d['milestones'][-1]
    assert final['model']['rotation_parameters_updated']==final['model']['readout_parameters_changed']==1000
    assert final['connected_register']['qubits']==1000 and final['connected_register']['nonproduct_bipartitions']==999
    dest=OUT/'campaigns'/name;dest.mkdir(parents=True,exist_ok=True)
    for file in ['manifest.json','conditions.json']:shutil.copyfile(source/file,dest/file)
    (dest/'training.jsonl.gz').write_bytes(gzip.compress(log,mtime=0))
    variant=d.get('entangler','cnot')
    code='557f6e4dc797c2d622250a9d8131e179e06a5cb8' if variant=='cz' else '33a42a4a00618cdaff1b204b13b0b7c9223fcdab'
    campaigns.append({'name':name,'variant':variant,'code_commit':code,'manifest':d,
        'training_journal_sha256':hashlib.sha256(log).hexdigest()})
    for m in d['milestones']:
        curves.append({'campaign':name,'variant':variant,'agent':d['identity']['agent'],
            'task':d['identity']['task'],'episodes':m['episodes'],'iid':metric(m['iid']),
            'ood':metric(m['ood']),'evaluation_cases':m['iid']['examples'],
            'angles_updated':m['model']['rotation_parameters_updated']})
        if m['episodes'] not in [100,1000]:continue
        src=source/m['checkpoint'];assert digest(src)==m['checkpoint_sha256']
        target=MODELS/name/(src.name+'.gz');save_gz(target,src.read_bytes())
        checkpoints.append({'name':str(target.relative_to(ROOT)),'agent':d['identity']['agent'],
            'entangler':variant,'task':d['identity']['task'],'new_training_episodes':m['episodes'],
            'checkpoint_sha256':digest(src),'gzip_sha256':digest(target),'gzip_bytes':target.stat().st_size})

holds={}
for name in ['connected-cz-vqc-holdout','connected-cz-qrl-holdout','connected-cnot-qrl-holdout']:
    src=BUILD/(name+'.json');data=json.loads(src.read_text())
    assert data['samples_per_split']==64 and data['evaluation_seed']==20261103 and not data['training_seed_overlap']
    shutil.copyfile(src,OUT/(name+'.json'));holds[name]=data

main=BUILD/'BBYQ-VQC3-QRL3-1000x2-CONECTADOS-CZ.rvp'
model_target=MODELS/(main.name+'.gz');save_gz(model_target,main.read_bytes())
model_manifest=json.loads(main.with_suffix('.manifest.json').read_text())
assert model_manifest['merged_checkpoint_sha256']==digest(main)
assert model_manifest['total_active_qubits']==2000 and model_manifest['quantum_components']==2
for role in ['vqc','qrl']:assert model_manifest['models'][role]['training_episodes_in_checkpoint']==1000
shutil.copyfile(main.with_suffix('.manifest.json'),OUT/'model.json')
for name in ['info','action','class-update','episode-update']:
    src=BUILD/('connected-cz-final-'+name+'.json')
    if src.exists():shutil.copyfile(src,OUT/('cli-'+name+'.json'))
checkpoints.append({'name':str(model_target.relative_to(ROOT)),'agent':'vqc+qrl','entangler':'cz',
    'new_training_episodes_per_agent':1000,'checkpoint_sha256':digest(main),
    'gzip_sha256':digest(model_target),'gzip_bytes':model_target.stat().st_size})
(OUT/'CHECKPOINTS.json').write_text(json.dumps(checkpoints,indent=2)+'\n')
with (OUT/'curves.csv').open('w',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(curves[0]));writer.writeheader();writer.writerows(curves)

fig,axes=plt.subplots(1,2,figsize=(11,4),layout='constrained')
for ax,agent,task,title in [(axes[0],'vqc','linear','VQC3: clasificación lineal'),(axes[1],'qrl','line_easy','QRL3: navegación')]:
    for c in campaigns:
        d=c['manifest']
        if d['identity']['agent']!=agent or d['identity']['task']!=task:continue
        ms=d['milestones'];color='#13836b' if c['variant']=='cz' else '#7866b3'
        x=[m['episodes'] for m in ms];y=[metric(m['iid']) for m in ms]
        n=ms[0]['iid']['examples']
        ax.plot(x,y,marker='o',color=color,label=f'{c["variant"].upper()} — IID, n={n}')
        ax.plot(x,[metric(m['ood']) for m in ms],linestyle='--',color=color,label=f'{c["variant"].upper()} — OOD')
    ax.set_xscale('symlog',linthresh=10);ax.set_xticks([0,10,100,300,1000],['0','10','100','300','1.000'])
    ax.set_ylim(0,1.04);ax.set_xlabel('Episodios de entrenamiento');ax.set_title(title)
    ax.set_ylabel('Precisión' if agent=='vqc' else 'Tasa de éxito');ax.grid(alpha=.2);ax.legend(fontsize=8)
fig.savefig(OUT/'learning-curves.svg');fig.savefig(BUILD/'connected-learning-curves.png',dpi=160);plt.close(fig)

results={'physical_quantum_hardware':False,'qubits_per_agent':1000,'quantum_components_per_agent':1,
    'neighbour_edges_per_forward':999,'theta_gradients_per_decision':1000,
    'native_runtime_commit':'4e201ec515da268612ab9e06eba090988814fda6',
    'native_runtime_merge':'08c363e6c6855c14026c86046af7183a45f45a98',
    'campaigns':campaigns,'fresh_holdouts':holds,'model':model_manifest,
    'timing_definitions':{'episode':'Native XI full forward, measured gradients, environment and parameter update',
      'update':'Optimizer/eligibility bookkeeping. The X/Z observations and angle-gradient calculation occur in forward and are included in episode time.',
      'memory':'Linux native XI worker VmHWM after exec, excludes Python transport; campaigns may run concurrently'},
    'limits':['One training seed; simple synthetic tasks; validation sets of 16 or 32 and fresh evaluation of 64 cases per split',
      'No 10000-episode campaigns repeated for these connected architectures',
      'MPS has no truncation but finite bond and memory budgets; arbitrary deep 1000-qubit circuits are not demonstrated',
      'Default CZ single-site observation cones contain a site and its neighbours; all 1000 feed the common agent output',
      'Earlier planning and joint-training modules remain preserved in quantum3 and are not revalidated for the new default circuit',
      'Native Linux runs and CI do not measure performance on the user phone']}
(OUT/'data.json').write_text(json.dumps(results,indent=2)+'\n')
lines=['# Resultados: registros conectados de 1.000 cúbits','',
    'Se eliminó la separación fija en grupos de cuatro. Cada agente utiliza un componente de 1.000 sitios, 999 enlaces y entrenamiento de sus 1.000 ángulos. Los modelos anteriores permanecen intactos.','',
    '## Campañas reales','',
    'Todas ejecutaron 1.000 episodios desde parámetros nuevos, semilla 173, con checkpoints a 100 y 1.000. Una muestra etiquetada cuenta como episodio VQC; un episodio QRL contiene varias decisiones. Las cifras de esta tabla son **validación**, utilizada al seleccionar la arquitectura.','',
    '| Circuito | Agente / tarea | IID | OOD | Casos por conjunto | Entrenamiento nativo (s) | Mediana episodio (ms) | Bucle de actualización (ms) | RSS XI (MiB) |',
    '|---|---|---:|---:|---:|---:|---:|---:|---:|']
for c in campaigns:
    d=c['manifest'];m=d['milestones'][-1]
    lines.append(f'| {c["variant"].upper()} | {d["identity"]["agent"].upper()} / {d["identity"]["task"]} | {100*metric(m["iid"]):.2f}% | {100*metric(m["ood"]):.2f}% | {m["iid"]["examples"]} | {d["native_episode_total_ms"]/1000:.3f} | {d["median_episode_ms"]:.3f} | {d["median_update_ms"]:.3f} | {m["usage"]["peak_rss_kib"]/1024:.2f} |')
lines += ['', 'La medición del episodio incluye circuito y cálculo de gradientes. La columna de actualización mide el bucle de cambios/eligibilidades; no incluye las observaciones X/Z calculadas en el forward. RSS corresponde al proceso XI, no a toda la máquina. Las tareas y las cantidades de decisiones difieren: estos tiempos no ordenan tecnologías ni prueban una ventaja cuántica.','',
    'La variante CNOT conserva la conectividad pero aprendió poco en QRL. CZ conserva el mismo registro de 1.000 y mejoró el aprendizaje en estas tareas. La tarea densa conserva resultados modestos; los 1.000 cúbits no garantizan generalización.','',
    '![Curvas de validación](learning-curves.svg)','',
    '## Evaluación final con casos nuevos','',
    'Después de seleccionar CZ se utilizó la semilla nueva 20261103, 64 casos IID y 64 OOD, disjuntos del entrenamiento. No se ajustaron parámetros en esta evaluación. Los conjuntos IID/OOD de las curvas anteriores son de validación; no se presentan como esta prueba final.','',
    '| Agente / variante | Inicial IID | Entrenado IID | Entrenado OOD | Observaciones anuladas IID | Aleatorio IID |','|---|---:|---:|---:|---:|---:|']
for key,h in holds.items():
    random=h.get('random_policy',{}).get('iid');rnd=f'{100*metric(random):.2f}%' if random else '—'
    lines.append(f'| {h["agent"].upper()} / {"CNOT" if "cnot" in key else "CZ"} | {100*metric(h["initial"]["iid"]):.2f}% | {100*metric(h["trained"]["iid"]):.2f}% | {100*metric(h["trained"]["ood"]):.2f}% | {100*metric(h["observations_zeroed"]["iid"]):.2f}% | {rnd} |')
lines += ['', 'Los JSON de evaluación contienen intervalos Wilson del 95%, recompensas y cantidad de decisiones. Una sola semilla de entrenamiento y 64 casos por conjunto no establecen un resultado general. Anular observaciones es un control para comprobar que las mediciones afectan la política y la clasificación.','',
    '## Entrega y verificaciones','',
    '- Modelo combinado: dos componentes de 1.000, con 1.000 episodios nuevos por agente. Los parámetros combinados conservan los hashes de los dos entrenamientos de origen.',
    '- Los 999 cortes del estado de cada agente presentan entrelazamiento en la verificación. No se mide ni afirma entrelazamiento máximo.',
    '- Las pruebas verifican derivadas del score, cambios reales en los 1.000 ángulos, etiquetas ocultas, rollback y reanudación idéntica. En CZ las observaciones locales dependen de vecinos; la prueba de influencia primer→último corresponde a la variante CNOT, disponible explícitamente.',
    '- Los archivos anteriores se conservaron. La migración verifica el hash original y mantiene ángulos, pesos y sesgos en una copia; su rendimiento no se presume transferido.',
    '- El runtime quedó integrado en [REVERSE-PC #172](https://github.com/guadalupejuan001-code/REVERSE-PC/pull/172). La CI cuántica, las regresiones nativas con sanitizadores y la compilación APK pasan. Persiste el fallo previo del saludo clásico de escritorio; la misma aserción falla en la base anterior, según [runtime-ci.json](runtime-ci.json).',
    '- Estas campañas no repiten 10.000 episodios ni revalidan los módulos históricos de planificación/acoplamiento. Los resultados anteriores de grupos de cuatro no se atribuyen al circuito nuevo.','',
    '[Manifiesto del modelo](model.json) · [Hashes y checkpoints](CHECKPOINTS.json) · [Datos completos](data.json) · [Validación XI](validation.json) · [CSV](curves.csv)','',
    f'Modelo principal: [{model_target.name}](../../../{model_target.relative_to(ROOT)}). Descomprimir gzip antes de abrirlo con el runtime conectado.','']
(OUT/'RESULTS.md').write_text('\n'.join(lines))
print(json.dumps({'campaigns':len(campaigns),'checkpoints':len(checkpoints),'combined_sha256':digest(main),'gzip_bytes':model_target.stat().st_size,'report':str(OUT/'RESULTS.md')},indent=2))
