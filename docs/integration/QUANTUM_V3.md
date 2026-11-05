# Integración de los VQC3/QRL3 ya entrenados en BBY Q

Esta entrega reúne el acceso a los agentes existentes desde el lanzador `bbyq.mjs`.
No crea un algoritmo conversacional, no reentrena la entrega de 10.000 episodios
y no transforma sus tareas numéricas en comprensión de lenguaje.

## Modelo integrado

- VQC3 y QRL3: 1.000 cúbits funcionales y 1.000 ángulos por agente.
- Checkpoint histórico con 10.000 episodios por agente, conservando los antiguos
  800/800. SHA-256:
  `eaba877ad9921e55fb4c191bea31dd2eb85ff3c72ba5261c3568709757926e76`.
- Ruta original nativa de Ether con grupos entrelazados de cuatro, identificador
  173. No usa MPS y no convierte los grupos en un componente global de 1.000.
- La variante conectada MPS (identificador 174), sus archivos y sus programas
  quedan conservados por separado. Esta integración no ejecuta esa variante.
- El modelo integrado conserva clasificación lineal y navegación con
  deslizamientos. Las variantes de paridad/señal densa del informe pertenecen a
  otros checkpoints y no se adjudican a este archivo combinado.

El circuito y todo el aprendizaje siguen en `ai/xi/quantum3`. JavaScript maneja
sesiones y comandos; Python transmite al intérprete. No hay otro modelo externo,
simulador externo ni aprendizaje implementado en el adaptador.

## Preparar y ejecutar

Compilar REVERSE-PC y Ether en las revisiones fijadas por el manifiesto. El
directorio de runtime debe contener `build/reverse_pc`, `build/xi_session` y
`scripts/xi_session_client.py`:

```sh
bash REVERSE-PC/scripts/build-xi-session.sh mundo-X REVERSE-PC/build

node bbyq.mjs quantum v3 prepare MI_SESION --runtime=REVERSE-PC
node bbyq.mjs quantum v3 status MI_SESION
node bbyq.mjs quantum v3 results MI_SESION
node bbyq.mjs quantum v3 classify MI_SESION entradas.json
node bbyq.mjs quantum v3 act MI_SESION 3 6 --greedy
```

`entradas.json` contiene 1.000 valores numéricos finitos compatibles con la
codificación del agente. `act` recibe posición y objetivo entre 0 y 6.
El estado informa de episodios reales, parámetros, ancho y arquitectura; no
deduce el aprendizaje de la cantidad de cúbits registrados.

Para elegir otro ejecutable Python, usar `--python=RUTA` durante `prepare`
o la variable `BBYQ_PYTHON`. El runtime y las fuentes quedan fijados por hash
en la sesión. Un cambio posterior se rechaza antes de modificar su modelo.

## Continuar el aprendizaje existente

```sh
node bbyq.mjs quantum v3 learn-class MI_SESION clase-001 entradas.json 1
node bbyq.mjs quantum v3 learn-episode MI_SESION episodio-001 --slip=0.15 --horizon=12
node bbyq.mjs quantum v3 export MI_SESION NUEVO_MODELO.rvp
```

El mismo identificador y la misma entrada devuelven el recibo existente sin
entrenar dos veces. Reutilizar el identificador con otros datos falla.
Los inputs de enseñanza se copian antes de ejecutar para que el recibo
corresponda exactamente a los bytes consumidos.

Un bloqueo excluye escritores concurrentes. Cada actualización produce un
archivo inmutable nuevo y publica `HEAD.json` de forma atómica; los originales
siguen disponibles en `versions/`. Una interrupción anterior a la publicación
puede dejar un archivo huérfano, que nunca se carga automáticamente. Si queda
`.write-lock` tras terminar un proceso, comprobar primero que ese proceso ya
no existe antes de retirarlo. Las sesiones conservan hasta 4.096 recibos de
actualización; el checkpoint exportado conserva todo el aprendizaje.

La inferencia no actualiza pesos ni publica otro checkpoint. `export` rechaza
destinos existentes. Un error de datos, del runtime o de integridad conserva
el último estado confirmado.

## Comprobaciones y alcance

```sh
BBYQ_QUANTUM_RUNTIME=/ruta/REVERSE-PC \
  node --test integration/quantum3/tests/launcher.test.mjs
```

Las pruebas usan el ejecutor XI real y el modelo entregado: 10.000 episodios
restaurados por agente, 1.000 cúbits observados por decisión, reanudación de
aprendizaje supervisado y por refuerzo, inferencia sin mutación, repetición de
solicitudes, conflictos, rollback e integridad. La CI también ejecuta el comando
raíz de BBY Q.

El generador de conversación existente se conserva. Las tareas numéricas V3
se conectan al chat como se describe a continuación. Entrenar generación de
lenguaje dentro de esos agentes requiere un diseño y una validación propios.
No se empaqueta ni se declara validada otra APK.

## Integración de V3 en las conversaciones de BBY Q

El módulo cuántico de X10 reconocía únicamente los comandos VQC2/QRL2. Ahora
el prefijo explícito `quantum v3` carga el checkpoint VQC3/QRL3 ya entrenado:

```sh
export BBYQ_QUANTUM_RUNTIME=/ruta/REVERSE-PC
node bbyq.mjs --build MI_BUILD_X10 turn MI_CHAT consulta-001 'quantum v3 estado'
node bbyq.mjs --build MI_BUILD_X10 turn MI_CHAT consulta-002 'quantum v3 resultados'
node bbyq.mjs --build MI_BUILD_X10 turn MI_CHAT consulta-003 'quantum v3 planea 3 6'
```

`quantum v3 clasifica [1000 números]` admite el mismo arreglo JSON numérico que
el comando de consola. También se acepta `--module=quantum` y el prefijo
`cuántico v3`. XI reconoce los comandos y sus posiciones/objetivos; JSON es
transporte estructurado de los valores del clasificador. Las respuestas son
presentaciones de sus resultados numéricos, no lenguaje aprendido por V3.

El modelo vive en una fila separada `quantum3_state` dentro de la misma
transacción SQLite del turno. Un error o rollback no publica el modelo ni el
recibo. Los bancos X09, P02 y VQC2/QRL2 se conservan. Las consultas no entrenan;
el entrenamiento explícito continúa disponible mediante los comandos de
consola anteriores. Si falta el runtime V3, se devuelve un error y no se elige
otro agente como sustituto. `status` informa la conexión V3 por separado.
El reconocedor utiliza las instrucciones de bytes del ejecutor X10 anterior;
solo la evaluación V3 requiere el runtime numérico con `xi_session`.

La acción QRL ahora verifica en XI si posición y objetivo ya coinciden. En ese
caso devuelve `terminal=true`, `action=null` y cero cúbits observados. Los
otros 42 pares conservan las mismas probabilidades y acciones que el modelo
evaluado. No se añade una regla de dirección para reemplazar su política.

## Errores identificados y límites medidos

| Hallazgo | Cambio o alcance |
| --- | --- |
| El chat seguía en VQC2/QRL2 aunque existía la consola V3 | Ruta V3 nativa y persistente en las conversaciones. |
| Se pedía un movimiento incluso con la meta alcanzada | Estado terminal sin acción. |
| Las métricas podían atribuirse a cualquier checkpoint | Resultados vinculados al SHA-256 exacto y a las fuentes XI evaluadas; tras cambiar cualquiera, `applicable=false`. |
| Se confundía el contador de episodios con capacidades generales | El estado publica las tareas y limitaciones medidas. |
| Cobertura QRL estrecha: entrenamiento con objetivos 0/6 e inicio 3 | Se identifica la meta fuera del entrenamiento; 33/42 direcciones correctas al ampliar objetivos. Requiere una campaña nueva para mejorarla. |
| VQC lineal no transfiere a paridad/radial/señal densa sin entrenamiento | Resultados entre 46–52 %; no se sustituye su checkpoint por uno destinado a otra tarea. |
| Los ángulos cambiaron, pero restaurarlos no redujo aciertos en 128 casos | No se atribuye a su ajuste una mejora de precisión demostrada. |

La evidencia reproducida está en
`docs/evidence/quantum3-evaluation/summary.json`, con semillas, hashes, controles
y recorridos nativos. VQC3 obtuvo 374/384 y QRL3 376/384 en sus tareas sintéticas.
Los 1.000 cúbits participan por agente, conservando sus 250 grupos originales
de cuatro; no es un registro global entrelazado de 1.000. No se demuestra una
ventaja cuántica ni aprendizaje más rápido que un modelo clásico.

No se reentrena ni se reemplaza el checkpoint con esta integración. Las
sesiones de consola anteriores conservan sus hashes de fuente originales; las
sesiones nuevas fijan además las fuentes del paso terminal.
