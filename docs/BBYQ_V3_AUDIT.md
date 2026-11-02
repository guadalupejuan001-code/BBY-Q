# VQC3 / QRL3 — auditoría y arquitectura ejecutable

## Ciclo 1: qué se encontró y conservó

Fuentes auditadas: BBY-Q `1e48cb03b27aadbea0c1f4684306128dc1e637ae`,
REVERSE-PC `b4eca490126de16bb130533ca695b97970f0cd39` y Mundo X/Ether
`e2778d962af22f6f1a0794058dd4685fc2573966` (dependencia fijada del ejecutor).
También se inspeccionó el árbol actual de Mundo X; no se alteró el upstream.

VQC2 trabaja con dos cúbits y busca entre ocho opciones discretas. Su búsqueda
de coste está implementada mediante aritmética XI. QRL2 usa una tabla pequeña
de valores y un entorno de dos pasos. No son VQC/QRL variacionales generales
de 1000 cúbits. No se modificaron sus fuentes ni sus espacios de memoria.

El checkpoint anterior `BBYQ-VQC1000-QRL1000-Entrenados-800.rvp`, SHA-256
`0d517085ef9b44c5ba41282748b3ed20676d7c908aeed445fbb1254f3aaf72f5`,
se restauró y ejecutó. Conserva 800 actualizaciones por agente GHZ, con 2000
cúbits activos en dos componentes de 1000. Dentro de ese archivo VQC2 está
sin entrenar (opción 255) y la tabla de QRL2 sigue inicial. El archivo original
no se sobrescribe. Los agentes GHZ existentes conservan sus parámetros binarios.

El informe previo muestra 50% de acierto ante etiquetas independientes nuevas:
la corrección de bits y la composición de paridades no demostraban todavía un
clasificador variacional continuo ni RL variacional de varios pasos.

## Ciclo 2: representación nueva

Cada agente V3 tiene 1000 cúbits simultáneos, 1000 ángulos entrenables y 1000
pesos de lectura, más sesgo. Usa un producto tensorial de 250 bloques de cuatro
cúbits. Cada bloque codifica cuatro ángulos de entrada mediante RY, aplica tres
CNOT en cadena, aplica cuatro RY parametrizadas y observa los cuatro Z.
Los 1000 resultados se combinan en un único logit normalizado por sqrt(1000).

No hay registro GHZ ornamental ni ejecución de un único circuito pequeño como
sustituto. Los 1000 cables participan en cada forward. El entrelazamiento se
limita al bloque; no es una simulación de un estado arbitrario entrelazado de
1000 cúbits. La memoria de amplitudes locales escala como suma de 2^b sobre
los bloques, no como 2^1000. El tamaño de bloque es una elección de topología.

XI calcula todo el aprendizaje. REVERSE-PC añade únicamente primitivas
genéricas de simulación, aritmética finita y transporte persistente. Ether
InverseMemory conserva parámetros, contadores, experiencias y checkpoints.
No hay función de pérdida, optimizador, objetivo ni política codificada en C++.

Cada forward independiente ejecuta 2000 RY, 750 CNOT y 1000 observaciones.
Se usan expectativas analíticas de Born, sin ruido de disparos y sin hardware
cuántico físico. El entrenamiento por bloque calcula derivadas de cuatro
coordenadas mediante ocho circuitos locales desplazados. Cada actualización
del clasificador usa además 64 RY, 24 CNOT y 32 observaciones para esas derivadas.

## Ciclos 3 y 4: aprendizaje real

VQC3 optimiza entropía cruzada por SGD en XI, registra además Brier y predice
una probabilidad logística. Los 1000 pesos se actualizan por ejemplo; cuatro
ángulos por actualización, con recorrido cíclico y escalado por 250.
La cobertura de ángulos efectivamente cambiados se mide en el checkpoint;
no se presenta una campaña de 100 ejemplos como si ya hubiera ajustado todos.

QRL3 implementa REINFORCE episódico: estados, acciones estocásticas, transiciones,
recompensa final, coste de pasos y baseline EMA. Los observables de sus 1000
cúbits determinan la probabilidad de acción. La recompensa completa actualiza
la política después del episodio. Cada episodio contiene varias decisiones;
no se enseña directamente qué acción tomar ni se actualiza una tabla de respuestas.

Los problemas son sintéticos y pequeños en estructura: clasificación lineal,
paridad, señal densa y navegación en una línea con o sin deslizamientos.
Las primeras tareas y la navegación repiten cuatro canales latentes sobre
1000 cables. Solo la tarea densa aporta 1000 entradas aleatorias independientes.
Anchura funcional no implica 1000 unidades independientes de información útil.

## Validación y límites

El intérprete pasó 2127 comprobaciones: oráculo denso aleatorio de 1/2/4/6
cúbits, derivadas no nulas en 2000 cables, restauración y rollback; error máximo
3.34e-16. Los agentes pasaron otras 24 comprobaciones reales: parameter shift
frente a diferencia finita del score completo (error máximo 2.20e-12),
reanudación idéntica de parámetros y coexistencia con el modelo anterior.
Se demostraron 4000 cúbits activos al combinar los antiguos y los nuevos.
La inferencia permanece idéntica al cambiar una etiqueta oculta.

No hay prueba de ventaja cuántica, razonamiento abierto, transferencia universal
ni simulación densa general de 1000 cúbits. El coste crece con el entrelazamiento
y con las dimensiones locales; no se eliminan coeficientes para fingir exactitud.

## Integración, planificación y referencia clásica exacta

`coupled.xi` usa los 1000 observables de VQC3 como ángulos de entrada de QRL3.
Se prueban por separado la representación congelada y el entrenamiento conjunto
alternado. Este último ajusta VQC3 para predecir el éxito realmente observado
en la experiencia; no es un gradiente end-to-end a través de ambos agentes.
La validación comprueba que los 2000 cúbits se observen y que el modelo congelado
no cambie, mientras el modo conjunto sí actualiza ambos.

`planning.xi` implementa búsqueda mediante dos rollouts por acción con horizonte
tres. La política cuántica guía las continuaciones; las reglas de transición y
recompensa son conocidas. Se comparan el modelo sin entrenamiento y el entrenado.
La planificación no aprende la dinámica ni demuestra razonamiento abierto.

Además del baseline de cosenos independientes, `analytic.xi` calcula en XI el
equivalente clásico exacto de este mapa cuántico local. Para el sitio i de un
bloque, la expectativa es cos(theta_i) por el producto de cos(x_j), j<=i,
menos sin(theta_i) sin(x_i) sin(x_(i+1)); en el último sitio se omite el segundo
seno de entrada. Esta expresión es específica de la topología validada.
La comparación de 8000 observables dio un error máximo de 5.83e-16; tras diez
actualizaciones los parámetros difirieron como máximo 2.23e-16. Esto impide
interpretar una mejora frente a otro baseline como ventaja computacional cuántica.

## Uso de los modelos

`integration/quantum3/cli.py` ofrece `info`, `classify`, `act`, `learn-class`
y `learn-episode`. El adaptador solo transporta entradas, resultados y estados.
La codificación, clasificación, política y actualización siguen en XI.
Los comandos de aprendizaje exigen un archivo de salida nuevo y conservan
el checkpoint de entrada. Ejemplos:

```sh
python integration/quantum3/cli.py --runtime /ruta/REVERSE-PC --state modelo.rvp info
python integration/quantum3/cli.py --runtime /ruta/REVERSE-PC --state modelo.rvp classify --inputs 1000-valores-normalizados.json
python integration/quantum3/cli.py --runtime /ruta/REVERSE-PC --state modelo.rvp act --position 3 --goal 6 --greedy
python integration/quantum3/cli.py --runtime /ruta/REVERSE-PC --state modelo.rvp learn-episode --slip .15 --horizon 12 --output siguiente.rvp
```

La etiqueta de clasificación y el significado de las acciones dependen del
problema entrenado, que se identifica en el informe y el manifiesto del modelo.

Referencias matemáticas: [Schuld et al., gradientes analíticos](https://doi.org/10.1103/PhysRevA.99.032331)
y [Vidal, simulación con entrelazamiento restringido](https://doi.org/10.1103/PhysRevLett.91.147902).

## Reproducción

La CI fija el ejecutor y Ether por SHA. Para una compilación local:

```sh
bash /ruta/REVERSE-PC/scripts/build-xi-session.sh /ruta/mundo-X /ruta/REVERSE-PC/build
python integration/quantum3/validate.py --runtime /ruta/REVERSE-PC --output build/validation
python integration/quantum3/campaign.py --runtime /ruta/REVERSE-PC --step-budget 10000000 --agent vqc --task parity --episodes 10000 --seed 173 --eval-size 128 --output build/vqc-parity
python integration/quantum3/campaign.py --runtime /ruta/REVERSE-PC --step-budget 10000000 --agent qrl --task line_slip --episodes 10000 --seed 173 --eval-size 64 --output build/qrl-slip
```

Cada campaña conserva condiciones, hashes del ejecutor y de XI, semillas
separadas, JSONL por episodio, evaluaciones y checkpoints RVPC2 comprimidos.
La reanudación exige el mismo código, ejecutor e identidad de campaña.
Los fallos de presupuesto se conservan aparte y no cuentan como episodios exitosos.
