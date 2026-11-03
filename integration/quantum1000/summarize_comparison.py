#!/usr/bin/env python3
"""Check every native campaign and publish compact, auditable comparisons."""
import argparse
import csv
import gzip
import hashlib
import json
from pathlib import Path
import shutil
import statistics
from compare_topologies import VARIANTS, SEEDS, TASKS, publish, sha

p=argparse.ArgumentParser()
p.add_argument('--campaigns',required=True)
p.add_argument('--validation',required=True)
p.add_argument('--benchmark',required=True)
p.add_argument('--output',required=True)
p.add_argument('--models',required=True)
args=p.parse_args()
root=Path(args.campaigns).resolve();out=Path(args.output).resolve();models=Path(args.models).resolve()
out.mkdir(parents=True,exist_ok=True);models.mkdir(parents=True,exist_ok=True)
protocol=json.loads((root/'PROTOCOL.json').read_text())
assert protocol['harness_sha256']==sha(Path(__file__).with_name('compare_topologies.py'))
assert protocol['training_seeds']==list(SEEDS) and protocol['variants']==list(VARIANTS)
rows=[];checks=[];checkpoint_index=[]
for agent,task in TASKS:
    for seed in SEEDS:
        for variant in VARIANTS:
            name=f'{agent}-{task}-seed{seed}-{variant}'
            source=root/name;d=json.loads((source/'result.json').read_text())
            assert d['conditions']['agent']==agent and d['conditions']['task']==task
            assert d['conditions']['variant']==variant and d['conditions']['training_seed']==seed
            assert d['conditions']['episodes']==protocol['episodes_per_campaign']
            assert not d['conditions']['train_holdout_seed_overlap']
            assert d['training']['episodes']==protocol['episodes_per_campaign']
            journal=gzip.decompress((source/'training.jsonl.gz').read_bytes())
            assert hashlib.sha256(journal).hexdigest()==d['journal_sha256']
            lines=[json.loads(x) for x in journal.decode().splitlines()]
            assert [x['episode'] for x in lines]==list(range(1,protocol['episodes_per_campaign']+1))
            assert sha(source/'training.jsonl.gz')==d['compressed_journal_sha256']
            for split in ['iid','ood']:
                m=d['trained'][split]
                assert m['samples']==protocol['holdout_samples_per_split']
                assert sum(m['correctness'])==m['successes']
                assert m['successes']/m['samples']==m['rate']
            destination=out/'campaigns'/name;destination.mkdir(parents=True,exist_ok=True)
            for filename in ['result.json','conditions.json','structure.json','training.jsonl.gz','worker.log']:
                shutil.copyfile(source/filename,destination/filename)
            for checkpoint in d['checkpoints']:
                compressed=source/checkpoint['file']
                assert sha(compressed)==checkpoint['sha256']
                assert hashlib.sha256(gzip.decompress(compressed.read_bytes())).hexdigest()==checkpoint['decompressed_sha256']
                target=models/name/checkpoint['file'];target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(compressed,target)
                checkpoint_index.append(dict(checkpoint,campaign=name))
            rows.append(d)
checks.append('27 complete journals: consecutive real episodes and compressed/decompressed hashes verified')
checks.append('Every final IID/OOD count was recalculated from the saved individual outcomes')
checks.append('Every initial/100/final checkpoint was decompressed and authenticated')
for agent,task in TASKS:
    for seed in SEEDS:
        paired=[d for d in rows if d['conditions']['agent']==agent and d['conditions']['task']==task and d['conditions']['training_seed']==seed]
        assert len({x['initial_model']['parameter_sha256'] for x in paired})==1
        assert len({tuple(x['conditions']['cpu_affinity']) for x in paired})==1
checks.append('All paired variants share initial learned parameters and CPU affinity')
groups=[]
def stats(values):
    return {'mean':statistics.mean(values),'minimum':min(values),'maximum':max(values),'values':values}
for agent,task in TASKS:
    variants={}
    for variant in VARIANTS:
        selected=sorted([x for x in rows if x['conditions']['agent']==agent and x['conditions']['task']==task and x['conditions']['variant']==variant],key=lambda x:x['conditions']['training_seed'])
        assert [x['conditions']['training_seed'] for x in selected]==sorted(SEEDS)
        variants[variant]={split:stats([x['trained'][split]['rate'] for x in selected]) for split in ['iid','ood']}
        variants[variant]['training_cpu_seconds']=stats([x['training']['native_cpu_ms']/1000 for x in selected])
        variants[variant]['training_cpu_ms_per_decision']=stats([x['training']['native_cpu_ms']/x['training']['decisions'] for x in selected])
        variants[variant]['training_peak_rss_mib']=stats([x['training']['peak_rss_kib']/1024 for x in selected])
        variants[variant]['rotation_parameters_changed']=[x['milestones'][-1]['model']['rotation_parameters_changed'] for x in selected]
        variants[variant]['initial_iid']=stats([x['initial']['iid']['rate'] for x in selected])
        variants[variant]['zeroed_iid']=stats([x['observations_zeroed']['iid']['rate'] for x in selected])
    contrasts={}
    for reference in ['historical4','blocked4']:
        contrasts[reference]={split:stats([a-b for a,b in zip(variants['connected1000'][split]['values'],variants[reference][split]['values'])]) for split in ['iid','ood']}
    groups.append({'agent':agent,'task':task,'variants':variants,'connected_minus_reference':contrasts})
validation=json.loads(Path(args.validation).read_text());assert validation['ok']
benchmark=json.loads(Path(args.benchmark).read_text())
shutil.copyfile(root/'PROTOCOL.json',out/'PROTOCOL.json')
shutil.copyfile(args.validation,out/'validation.json')
shutil.copyfile(args.benchmark,out/'forward-benchmark.json')
summary={'campaigns':len(rows),'training_episodes':sum(d['training']['episodes'] for d in rows),
    'total_training_decisions':sum(d['training']['decisions'] for d in rows),
    'qubits_per_agent':1000,'training_seeds':list(SEEDS),'tasks':groups,
    'holdout_samples_per_split_per_trained_model':protocol['holdout_samples_per_split'],
    'initial_and_zeroed_samples_per_split':protocol['initial_and_zeroed_samples_per_split'],
    'forward_only_benchmark':benchmark['summary'],'checks':checks,
    'aggregation':'Mean and observed min/max across three training seeds. The same test cases repeat across seeds; no pooled confidence interval or significance claim.',
    'runtime_binary_sha256':rows[0]['conditions']['runtime_binary_sha256']}
publish(out/'summary.json',summary);publish(out/'CHECKPOINTS.json',checkpoint_index)
with (out/'results.csv').open('w',newline='') as f:
    writer=csv.writer(f);writer.writerow(['agent','task','seed','variant','iid','ood','training_cpu_s','training_decisions','peak_rss_mib','angles_changed'])
    for d in rows:
        c=d['conditions'];writer.writerow([c['agent'],c['task'],c['training_seed'],c['variant'],d['trained']['iid']['rate'],d['trained']['ood']['rate'],d['training']['native_cpu_ms']/1000,d['training']['decisions'],d['training']['peak_rss_kib']/1024,d['milestones'][-1]['model']['rotation_parameters_changed']])
def percentage(s):return f"{100*s['mean']:.2f}% ({100*s['minimum']:.2f}–{100*s['maximum']:.2f})"
labels={'historical4':'Anterior: grupos de 4 / CNOT','blocked4':'Control: grupos de 4 / CZ','connected1000':'Actual: 1.000 conectados / CZ'}
task_labels={'linear':'VQC lineal','dense':'VQC señal densa','line_easy':'QRL secuencial sencillo'}
text=['# Comparación ejecutada: grupos independientes y registro conectado','',
    '## Alcance y protocolo','',
    f"Se completaron {len(rows)} campañas nuevas de {protocol['episodes_per_campaign']:,} episodios: tres diseños × tres tareas × tres semillas (173, 941 y 2026). Todos mantienen 1.000 cúbits simulados por agente; no se usó qsim.",
    '',
    'El diseño anterior conserva su CNOT y sus cuatro gradientes de ángulo por decisión. El control utiliza el aprendizaje actual (CZ y 1.000 gradientes), pero mantiene 250 componentes independientes de cuatro. El actual utiliza un componente MPS conectado de 1.000. La comparación control/actual mantiene datos, parámetros iniciales, tasas, algoritmos y episodios; cambia preparación, representación de estado y conexiones. La comparación histórica también incluye los cambios de compuertas y optimización.',
    '',
    'Cada modelo entrenado se evaluó sin actualizarlo en 128 casos IID y 128 OOD nuevos, con semilla 827391, fijada antes de ejecutar las campañas. Los controles inicial y de observaciones anuladas usan 32 casos por conjunto. El entorno genera todos los datos, transiciones y recompensas en XI. Python solo organiza y registra.',
    '',
    '## Aciertos después de 1.000 episodios','',
    'Media de tres semillas; entre paréntesis, mínimo–máximo observado. Los casos de prueba son comunes entre semillas, por lo que no se presentan como 384 muestras independientes ni se agrupan sus intervalos Wilson.',
    '',
    '| Tarea / conjunto | Anterior, CNOT | Control, CZ | Actual conectado, CZ |',
    '|---|---:|---:|---:|']
for g in groups:
    for split in ['iid','ood']:
        text.append('| '+task_labels[g['task']]+' / '+split.upper()+' | '+' | '.join(percentage(g['variants'][v][split]) for v in VARIANTS)+' |')
text += ['', '## Tiempo de entrenamiento y memoria','',
    'CPU nativa total por campaña, media entre semillas. Incluye solicitudes de guardado/inspección de hitos; excluye los procesos de evaluación separados. QRL puede necesitar distinta cantidad de decisiones según lo aprendido, por lo que los diarios y el CSV conservan también decisiones y CPU por decisión.',
    '', '| Tarea | Anterior: CPU s / MiB | Control: CPU s / MiB | Actual: CPU s / MiB |','|---|---:|---:|---:|']
for g in groups:
    text.append('| '+task_labels[g['task']]+' | '+' | '.join(f"{g['variants'][v]['training_cpu_seconds']['mean']:.2f} / {g['variants'][v]['training_peak_rss_mib']['mean']:.2f}" for v in VARIANTS)+' |')
text += ['', '## Latencia de inferencia aislada','',
    'Esta medición es solo el forward de un agente con parámetros e inputs congelados; no representa entrenamiento ni episodios completos de QRL. Se ejecutó después de las campañas, en serie y con orden alternado, en el mismo núcleo: cinco rondas de 40 forwards por diseño y cinco calentamientos por ronda. Medianas entre rondas.',
    '', '| Diseño | CPU ms / forward | Transporte ms / forward | RSS MiB |','|---|---:|---:|---:|']
for v in VARIANTS:
    b=benchmark['summary'][v];text.append(f"| {labels[v]} | {b['median_cpu_ms_per_forward']:.3f} | {b['median_transport_ms']:.3f} | {b['median_peak_rss_kib']/1024:.2f} |")
text += ['', '## Verificaciones y límites','']
text += ['- '+x+'.' for x in checks]
text += ['- Se verificaron 2.000 cúbits activos en cada diseño. Anterior/control: 500 componentes de cuatro entre ambos agentes; actual: dos componentes de 1.000 y 999 cortes entrelazados por agente.',
    '- El control con CNOT reproduce exactamente los 1.000 observables y el score del circuito anterior. Los gradientes completos del control y del conectado coinciden con diferencias finitas; su reanudación también se comprueba.',
    '- Tres semillas y estas tareas sintéticas no prueban una superioridad general. Mayor conectividad, mayor entrelazamiento y mayor exactitud predictiva son propiedades distintas.',
    '- Los modelos nuevos de esta comparación se guardan por separado. No se modificaron los agentes productivos ni los checkpoints anteriores.',
    '', '## Reproducción','', '```bash',
    'bash /ruta/REVERSE-PC/scripts/build-xi-session.sh /ruta/mundo-X /ruta/REVERSE-PC/build',
    'python integration/quantum1000/validate_comparison.py --runtime /ruta/REVERSE-PC --output build/topology-preflight',
    'python integration/quantum1000/compare_topologies.py all --runtime /ruta/REVERSE-PC --episodes 1000 --samples 128 --workers 6 --output build/topology-comparison',
    'python integration/quantum1000/benchmark_comparison.py --runtime /ruta/REVERSE-PC --output build/topology-benchmark',
    '```', '',
    'Fuentes fijadas: BBY-Q `d21f6b3fa867febf9559dbab0fc0b0ae453d879a`; REVERSE-PC `08c363e6c6855c14026c86046af7183a45f45a98`; mundo-X `e2778d962af22f6f1a0794058dd4685fc2573966`. Los cuatro archivos XI históricos se contrastaron con los blobs de la PR #67. Hash del ejecutor recompilado: `'+summary['runtime_binary_sha256']+'`.',
    '', '[Protocolo](PROTOCOL.json) · [Resumen numérico](summary.json) · [CSV por semilla](results.csv) · [Verificación](validation.json) · [Benchmark crudo](forward-benchmark.json) · [Hashes de modelos](CHECKPOINTS.json)']
(out/'RESULTS.md').write_text('\n'.join(text)+'\n')
print(json.dumps(summary,indent=2))
