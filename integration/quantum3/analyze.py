#!/usr/bin/env python3
"""Build tables and scientific figures exclusively from recorded experiments."""
import argparse
import csv
import json
from pathlib import Path
import statistics
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

parser=argparse.ArgumentParser()
parser.add_argument('--campaigns',required=True)
parser.add_argument('--evidence',required=True)
parser.add_argument('--output',required=True)
parser.add_argument('--allow-partial',action='store_true')
args=parser.parse_args()
root=Path(args.campaigns).resolve();evidence=Path(args.evidence).resolve()
out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
primary=['vqc-linear-s173','vqc-parity-s173','vqc-dense-s173-replay','qrl-easy-s173','qrl-slip-s173-v2']
baselines=['classical-parity-s173','analytic-parity-s173','classical-dense-s173-replay','classical-qrl-easy-s173','analytic-qrl-slip-s173']
manifests={p.parent.name:json.loads(p.read_text()) for p in root.glob('*/manifest.json')}
if not args.allow_partial:
    assert all(n in manifests and manifests[n]['completed_episodes']==10000 for n in primary+baselines), 'long campaigns unfinished'
labels={'linear':'Lineal','parity':'Paridad','dense':'Señal densa','line_easy':'Navegación básica','line_slip':'Navegación con deslizamientos'}
colors={'linear':'#28769A','parity':'#C58C2A','dense':'#9460A2','line_easy':'#248570','line_slip':'#CA6351'}
all_rows=[];runs={};incomplete=[]
for name,m in manifests.items():
    samples=[json.loads(s) for s in (root/name/'training.jsonl').read_text().splitlines()]
    if len(samples)<max(p['episodes'] for p in m['milestones']):
        incomplete.append({'campaign':name,'journal_rows':len(samples),'recorded_completed_episodes':m['completed_episodes'],
                           'action':'Original retained; complete journal obtained in separate replay campaign'})
        continue
    native=[0.];transport=[0.];experiences=[0]
    for r in samples:
        native.append(native[-1]+r['episode_ms']/1000)
        transport.append(transport[-1]+r['transport_ms']/1000)
        experiences.append(experiences[-1]+int(r.get('decisions',1)))
    variant='Clásico analítico equivalente' if m['identity'].get('analytic_classical_equivalent') else 'Clásico cosenos' if m['identity']['classical'] else 'Cuántico simulado'
    records=[]
    for point in m['milestones']:
        ep=point['episodes'];vqc=m['identity']['agent']=='vqc'
        metric='accuracy' if vqc else 'success_rate'
        row={'campaign':name,'agent':m['identity']['agent'],'task':m['identity']['task'],
             'variant':variant,'seed':m['identity']['seed'],'coupling':m['identity'].get('joint_mode','independent'),
             'episodes':ep,'training_experiences':experiences[ep],
             'iid_score':point['iid'][metric],'ood_score':point['ood'][metric],
             'iid_low95':point['iid']['wilson95'][0],'iid_high95':point['iid']['wilson95'][1],
             'evaluation_examples':point['iid']['examples'],'native_training_seconds':native[ep],
             'transport_training_seconds':transport[ep],
             'median_episode_ms':statistics.median(r['episode_ms'] for r in samples[:ep]) if ep else 0,
             'median_update_ms':statistics.median(r['update_ms'] for r in samples[:ep]) if ep else 0,
             'peak_native_rss_mib':point['usage']['peak_rss_kib']/1024,
             'quantum_payload_bytes':point['usage']['quantum_payload_bytes'],
             'rotation_parameters_updated':point['model']['rotation_parameters_updated'],
             'readout_parameters_changed':point['model']['readout_parameters_changed'],
             'effective_quantum_qubits_per_agent':0 if m['identity']['classical'] else 1000,
             'checkpoint':point['checkpoint'],'checkpoint_sha256':point['checkpoint_sha256']}
        all_rows.append(row);records.append(row)
    runs[name]=dict(conditions=m,records=records)
with (out/'curves.csv').open('w',newline='') as file:
    writer=csv.DictWriter(file,fieldnames=list(all_rows[0]));writer.writeheader();writer.writerows(all_rows)
(out/'data.json').write_text(json.dumps({'physical_quantum_hardware':False,'runs':runs},indent=2)+'\n')
(out/'journal-integrity.json').write_text(json.dumps(incomplete,indent=2)+'\n')

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,
                     'axes.spines.right':False,'axes.titleweight':'bold','figure.dpi':160})
def axis(ax):
    ax.set_xscale('symlog',linthresh=10);ax.set_xticks([0,10,100,1000,10000],labels=['0','10','100','1.000','10.000'])
    ax.set_ylim(0,1.04);ax.set_yticks([0,.25,.5,.75,1],labels=['0%','25%','50%','75%','100%'])
    ax.set_xlabel('Episodios de entrenamiento acumulados');ax.grid(axis='y',alpha=.18)
def draw(ax,name,label=None,style='-',color=None):
    rr=runs[name]['records'];task=rr[0]['task']
    ax.plot([r['episodes'] for r in rr],[r['iid_score'] for r in rr],style,
            marker='o' if style=='-' else None,ms=3.8,lw=1.9 if style=='-' else 1.5,
            color=color or colors[task],label=label or labels[task])
    r=rr[-1]
    if style=='-':ax.errorbar(r['episodes'],r['iid_score'],yerr=[[r['iid_score']-r['iid_low95']],[r['iid_high95']-r['iid_score']]],
                              color=color or colors[task],capsize=3,linewidth=1)

fig,axes=plt.subplots(2,1,figsize=(10.3,8.2),layout='constrained')
for n in primary[:3]:draw(axes[0],n)
if 'analytic-parity-s173' in runs:draw(axes[0],'analytic-parity-s173','Equivalente clásico de paridad','--','#263442')
axes[0].set_title('VQC3 · clasificación de ejemplos reservados');axis(axes[0]);axes[0].set_ylabel('Precisión');axes[0].legend(loc='lower right',fontsize=8)
for n in primary[3:]:draw(axes[1],n)
if 'classical-qrl-easy-s173' in runs:draw(axes[1],'classical-qrl-easy-s173','Clásico · navegación básica','--','#4B5660')
if 'analytic-qrl-slip-s173' in runs:draw(axes[1],'analytic-qrl-slip-s173','Equivalente clásico · deslizamientos',':','#263442')
axes[1].set_title('QRL3 · episodios reservados con decisiones secuenciales');axis(axes[1]);axes[1].set_ylabel('Tasa de éxito');axes[1].legend(loc='lower right',fontsize=8)
fig.suptitle('1.000 cúbits funcionales por agente · aprendizaje ejecutado en XI',fontsize=14,fontweight='bold')
fig.savefig(out/'learning_curves.png',dpi=180);fig.savefig(out/'learning_curves.svg');plt.close(fig)

fig,axes=plt.subplots(1,3,figsize=(13,4.6),layout='constrained')
last=[runs[n]['records'][-1] for n in primary]
x=list(range(len(last)));names=['VQC\nlineal','VQC\nparidad','VQC\ndensa','QRL\nbásico','QRL\nruido']
for ax,key,title,ylabel in zip(axes,['median_episode_ms','median_update_ms','peak_native_rss_mib'],
                              ['Tiempo por episodio','Tiempo de actualización','Pico de memoria del proceso'],
                              ['Milisegundos','Milisegundos','MiB de RSS'],strict=True):
    vals=[r[key] for r in last]
    bars=ax.bar(x,vals,color=[colors[r['task']] for r in last],width=.7)
    ax.set_xticks(x,names,fontsize=8);ax.set_title(title,fontsize=11);ax.set_ylabel(ylabel);ax.grid(axis='y',alpha=.15)
    ax.set_ylim(0,max(vals)*1.22)
    for bar,v in zip(bars,vals):ax.text(bar.get_x()+bar.get_width()/2,v+max(vals)*.025,f'{v:.1f}',ha='center',fontsize=8)
fig.suptitle('Medianas reales del intérprete · un episodio VQC = un ejemplo; QRL = varios pasos',fontsize=11)
fig.savefig(out/'timing_memory.png',dpi=180);plt.close(fig)

coupling=evidence/'cycle07-matched-comparison.json'
if coupling.exists():
    c=json.loads(coupling.read_text());fig,axes=plt.subplots(1,2,figsize=(10.3,4.3),layout='constrained')
    xx=list(range(3));names=['Independiente','VQC congelado','Conjunto alternado']
    for ax,key,title in [(axes[0],'iid','Política estocástica · casos básicos'),(axes[1],'greedy_ood','Decisión greedy · objetivos nuevos')]:
        vals=[r[key]['success_rate'] for r in c['results']]
        bars=ax.bar(xx,vals,color=['#28769A','#248570','#C58C2A'],width=.62)
        ax.set_xticks(xx,names,fontsize=8);ax.set_ylim(0,1.13);ax.set_yticks([0,.25,.5,.75,1],labels=['0%','25%','50%','75%','100%'])
        ax.set_title(title,fontsize=10);ax.grid(axis='y',alpha=.15)
        for b,v in zip(bars,vals):ax.text(b.get_x()+b.get_width()/2,v+.02,f'{v:.1%}',ha='center',fontsize=9)
    fig.suptitle('VQC3 → QRL3 · 1.000 episodios por política · mismos 32 casos por condición',fontsize=11)
    fig.savefig(out/'integration.png',dpi=180);plt.close(fig)

profile=evidence/'cycle08-profile/summary.json'
if not profile.exists():profile=evidence/'cycle08-concurrent-profile/summary.json'
if profile.exists():
    data=json.loads(profile.read_text())['results'];fig,axes=plt.subplots(1,2,figsize=(10.3,4.2),layout='constrained')
    for binary in sorted({r['binary'] for r in data}):
        rr=sorted([r for r in data if r['binary']==binary],key=lambda r:r['block_width'])
        label='Antes' if 'reference' in binary else 'Optimizado'
        axes[0].plot([r['block_width'] for r in rr],[r['median_native_ms'] for r in rr],'-o',label=label,ms=4)
        axes[1].plot([r['block_width'] for r in rr],[r['quantum_stats']['payload_bytes']/1024 for r in rr],'-o',label=label,ms=4)
    for ax in axes:ax.set_xlabel('Cúbits por bloque entrelazado');ax.set_xticks([1,2,4,5,8]);ax.grid(alpha=.15);ax.legend()
    axes[0].set_ylabel('Mediana nativa por circuito (ms)');axes[0].set_title('Coste de simulación de 1.000 cúbits')
    axes[1].set_ylabel('Payload cuántico (KiB)');axes[1].set_title('Estado almacenado, con metadatos')
    fig.savefig(out/'simulation_cost.png',dpi=180);plt.close(fig)

def pct(value):return f'{100*value:.2f} %'
def table(headers,rows):
    return '| '+' | '.join(headers)+' |\n| '+' | '.join(['---']*len(headers))+' |\n'+''.join('| '+' | '.join(map(str,r))+' |\n' for r in rows)
result_rows=[]
for n in primary:
    r=runs[n]['records'][-1]
    result_rows.append([('VQC3' if r['agent']=='vqc' else 'QRL3')+' · '+labels[r['task']],str(r['episodes']),pct(r['iid_score']),pct(r['ood_score']),
                        f"{r['median_episode_ms']:.2f}",f"{r['median_update_ms']:.2f}",str(r['training_experiences']),f"{r['peak_native_rss_mib']:.2f}"])

# Descriptive sustained-improvement threshold, not a preregistered sample
# complexity claim: +10 percentage points VQC, +20 QRL above its own baseline.
improvement=[]
for n in primary:
    rr=runs[n]['records'];threshold=rr[0]['iid_score']+(.1 if rr[0]['agent']=='vqc' else .2)
    observed=next((r for i,r in enumerate(rr) if r['episodes'] and all(x['iid_score']>=threshold for x in rr[i:])),None)
    improvement.append([n,f'{threshold:.2%}',str(observed['episodes']) if observed else 'No alcanzado de forma sostenida',
                        str(observed['training_experiences']) if observed else '—'])

report='''# VQC3 y QRL3: resultados verificables con 1.000 cúbits por agente

Se implementaron y ejecutaron dos agentes cuánticos simulados y entrenables
en XI. Cada forward utiliza 1.000 cúbits, con codificación, rotaciones continuas,
CNOT y observaciones que afectan la salida y los gradientes. Los 1.000 ángulos
y los 1.000 pesos por agente recibieron actualizaciones en las campañas largas.
El entrelazamiento se limita a 250 bloques de cuatro cúbits por agente.

Los resultados acreditan aprendizaje en estos problemas sintéticos; no una
capacidad de aprendizaje general ni una ventaja cuántica computacional.

## Campañas principales

'''+table(['Agente y tarea','Episodios','Acierto/éxito reservado','OOD','Mediana ms/episodio','Mediana ms/actualización','Experiencias','Pico RSS MiB'],result_rows)+'''
Un episodio VQC es un ejemplo etiquetado. Un episodio QRL incluye varios
estados, acciones y transiciones. Las tasas de ambas columnas corresponden a
tareas diferentes y no constituyen una competición de inteligencia.

Los tiempos nativos se miden dentro de XI. Las actualizaciones incluyen el
cálculo de gradientes y el cambio de parámetros, no un solo parámetro aislado.
El CSV conserva además la suma de tiempos con transporte y generación de
datos. El RSS es del proceso nativo, con los dos registros configurados;
excluye Python y las herramientas de análisis. Se ejecutaron varias campañas
concurrentes en un entorno con cuota de ocho vCPU. No son medidas del teléfono.

![Curvas](learning_curves.png)

Se guardaron y evaluaron los estados de 100, 1.000 y 10.000 episodios, además
de puntos intermedios. Son prefijos acumulativos del mismo entrenamiento, no
tres réplicas independientes. Los intervalos Wilson del 95 % describen la
incertidumbre del conjunto reservado, no la variación entre entrenamientos.

![Tiempo y memoria](timing_memory.png)

## Qué tan pronto se observó mejora

Se usa un criterio descriptivo: +10 puntos porcentuales para VQC y +20 para
QRL sobre su propia evaluación inicial, manteniéndose por encima en los
controles posteriores. Solo se conoce el primer control que lo cumple, no el
episodio exacto de inicio ni una complejidad de muestras universal.

'''+table(['Campaña','Umbral descriptivo','Primer control sostenido','Experiencias acumuladas'],improvement)+'''
## Cobertura funcional y coste

Cada forward de un agente independiente ejecuta 2.000 RY, 750 CNOT y 1.000
observaciones. El gradiente de cuatro ángulos requiere ocho circuitos locales
adicionales: 64 RY, 24 CNOT y 32 observaciones. Los 1.000 pesos de lectura se
actualizan por ejemplo o mediante las elegibilidades del episodio. Los ángulos
se recorren cíclicamente; cuatro gradientes por decisión no significa cuatro
cúbits activos. Los contadores de cambios no nulos están en cada manifiesto.

Se validaron 2.000 derivadas causales no nulas en los dos registros simultáneos.
Las mediciones son expectativas de Born analíticas en un simulador clásico,
sin disparos físicos. La anchura del bloque es una elección de topología, no
un límite global de cuatro cúbits. El coste de almacenamiento local crece
con suma de 2^b sobre los bloques; no se materializa un statevector de 2^1000.

![Coste de simulación](simulation_cost.png)

## Límites observados

- La señal densa contiene 1.000 entradas pseudoaleatorias por ejemplo. VQC3
  obtuvo un resultado cercano al azar; no se acreditó aprendizaje útil de esa
  tarea frente al baseline clásico de cosenos.
- Los primeros problemas y la navegación usan cuatro canales latentes
  repetidos sobre los 1.000 cables. Anchura funcional no equivale a 1.000
  variables independientes ni a entrelazamiento global.
- En navegación, la calidad depende de la semilla. Las réplicas de 1.000
  episodios y la caída OOD tras más entrenamiento se conservan; más episodios
  no garantizan mejor generalización.
- OOD significa ruido de entrada mayor o posiciones/objetivos reservados.
  La transferencia a otra regla de clasificación se mide por separado y no
  acredita una capacidad de resolver cualquier problema nuevo.

## Integración y planificación

Se comparó QRL independiente con VQC preentrenado y congelado y con entrenamiento
conjunto alternado. Los datos pareados usan los mismos 32 casos por condición.
Los modos conectados requieren además el preentrenamiento VQC y dos circuitos
de 1.000 cúbits por decisión. El entrenamiento conjunto aprende una tarea
auxiliar a partir del éxito observado; no es backpropagation end-to-end.

![Integración](integration.png)

El planificador XI hace dos rollouts por acción y horizonte tres, usando la
política aprendida para continuar y reglas de transición/recompensa conocidas.
Se probó también sin entrenamiento. Su capacidad proviene de búsqueda más
política; no se afirma que haya aprendido por sí solo el modelo del mundo.

## Comparación clásica y controles

El baseline de cosenos tiene el mismo número de parámetros y el mismo
optimizador. También se implementó un equivalente clásico analítico exacto de
este mapa cuántico particular. Coincidió con 8.000 observaciones con diferencia
máxima de 5,83e-16 y, tras diez ejemplos, con los parámetros hasta 2,23e-16.
Las curvas equivalentes se solapan. No se demuestra ventaja computacional
cuántica; una diferencia frente al baseline de cosenos puede provenir del
mapa de características y de su sesgo inductivo.

La inferencia conserva su resultado al permutar una etiqueta oculta. La
reanudación VQC conserva idénticos parámetros. Se evalúan políticas aleatorias,
modelos sin entrenamiento y observaciones anuladas. Los datos reservados usan
semillas distintas, comprobadas contra todas las semillas de entrenamiento.
Las reglas del entorno son explícitas; el agente no consulta la etiqueta en
inferencia ni una respuesta correcta de acción durante el aprendizaje.

## Conservación, código y CI

Se conserva el checkpoint anterior de 800/800 episodios y se comprueba su
SHA-256 antes y después. Los nuevos agentes usan memoria y rangos cuánticos
separados. Al combinarlos, coexisten 2.000 cúbits antiguos y 2.000 nuevos.
Las transferencias de parámetros se verifican byte a byte mediante los hashes
de los modelos y nunca reemplazan un archivo de entrada.

- [PR BBY-Q #67](https://github.com/guadalupejuan001-code/BBY-Q/pull/67)
- [PR REVERSE-PC #171](https://github.com/guadalupejuan001-code/REVERSE-PC/pull/171)
- [CI de entrenamiento e integración](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/41390512045)
- [CI de primitivas cuánticas](https://github.com/guadalupejuan001-code/REVERSE-PC/actions/runs/41388046247)

La prueba Android del saludo clásico de BBY Q falla también en la base original
con el mismo error; queda documentada y no se modifica ningún motor conversacional.
Las pruebas cuánticas, de integración y del sistema se informan por separado.

## Datos y reproducción

`curves.csv` y `data.json` contienen las curvas y condiciones, con hashes de
checkpoints, ejecutor y fuentes XI. Los manifiestos originales conservan sus
medidas; en los informes normalizados, hardware físico es falso y simulación
clásica es verdadero para los agentes cuánticos. Las fuentes, construcción y
comandos de uso están en el repositorio. Los modelos entrenados y sus prefijos
se entregan en el paquete de checkpoints con su índice SHA-256.
'''
(out/'REPORT.md').write_text(report)
print(json.dumps({'output':str(out),'campaigns':len(manifests),'curve_rows':len(all_rows),'primary_complete':all(manifests[n]['completed_episodes']==10000 for n in primary)}))
