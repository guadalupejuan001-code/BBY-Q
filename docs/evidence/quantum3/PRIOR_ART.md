# Antecedentes y comparación externa de VQC3/QRL3

Revisión realizada el **2 de noviembre de 2026**. Los resultados de aprendizaje
de la entrega siguen en [REPORT.md](REPORT.md) y su reproducción en
[FINAL_VERIFICATION.md](FINAL_VERIFICATION.md).

**Conclusión:** existen antecedentes de QML a 1.024 cúbits y de QRL modular
a 800. En las fuentes revisadas no se identificó un experimento previo que
documente exactamente una política QRL entrenada con 1.000 cables funcionales
según la definición siguiente. Eso deja la prioridad específica sin resolver;
no constituye una demostración de ser el primero del mundo. La medición nueva
frente a qsim tampoco establece un récord de velocidad o memoria.

**Estado de la comparación entre agentes completos: pendiente.** qsim no
ejecutó el entrenamiento, los episodios, la planificación ni la persistencia
de QRL3. Por tanto, esta prueba no responde a una comparación de los sistemas
completos y no determina un ganador entre qsim y BBY Q. Los tiempos parciales
se conservan como evidencia de una comprobación auxiliar del cálculo.

## Qué se investigó

La definición de trabajo exige que la política o el modelo de valor evalúe
1.000 cables cuánticos simulados distintos, que sus observables afecten las
decisiones y que reciba actualizaciones de entrenamiento. La capacidad nominal
de un chip, el número de episodios o un agente clásico que controla un sistema
cuántico no satisfacen esa definición por sí solos.

QRL3 tiene 1.000 cables en 250 bloques independientes de cuatro. Los 1.000
observables alimentan una lectura común; los cuatro gradientes por decisión
recorren cíclicamente los ángulos. Las tareas de navegación repiten cuatro
canales latentes. Este alcance se conserva al compararlo con otros trabajos.

Se consultaron dos buscadores, descubrimiento bibliográfico de texto completo,
artículos originales, apéndices y código público. Las consultas principales,
fechas, criterios de exclusión y fichas de fuentes están en
[PRIOR_ART.json](PRIOR_ART.json). Es una búsqueda dirigida, no una certificación
exhaustiva de prioridad mundial.

## Antecedentes comprobados

| Fuente primaria | Escala comprobada y alcance | Qué permite concluir |
| --- | --- | --- |
| [Bermejo et al., QCNN](https://arxiv.org/html/2408.12739v2), preprint 2024, publicación 2026 | Clasificación de sistemas de 1.024 cúbits mediante un sustituto clásico de baja localidad; recursos disponibles en una laptop moderna. | Hay antecedentes generales de QML a esta anchura. El método es diferente de nuestro producto exacto por bloques. No se identificó un pico de RAM en el texto y apéndices revisados. |
| [Park et al., Quantum Mario](https://arxiv.org/html/2509.00713v1), 2025 | Experimentos con hasta 100 subcircuitos de ocho cables: 800 en total. La cifra de 2.000 aparece como ejemplo de escalado, no como configuración experimental reportada. | La idea de una política QRL que agrega circuitos independientes ya tiene antecedente. El servidor declarado tiene 128 núcleos, 503 GB de RAM y A100 de 40 GB; esas capacidades no son consumo RSS. |
| [Schenk et al., CERN](https://arxiv.org/pdf/2209.11044), preprint 2022, publicación 2024 | Experimentos con QBM de 16 y 128 cúbits; actor clásico y crítico basado en QBM, con annealing simulado y físico. | Existe QRL entrenado para control de haces; el modelo de 128 no demuestra un agente de 1.000. |
| [Kruse et al., Benchmarking QRL](https://arxiv.org/html/2502.04909v2), 2025 | Compara políticas PQC, Q-learning, energía libre y amplificación en gridworlds; el ejemplo 3x3 contrasta cuatro y nueve cúbits. | Ofrece criterios de comparación por tarea y coste. Esas dos cifras no se presentan aquí como el máximo de todos sus experimentos. |
| [Crawford et al., QBM-RL](https://arxiv.org/pdf/1612.05695), preprint 2016, publicación 2018 | Las pruebas de las figuras 3-4 utilizan 16 o 20 nodos ocultos, mediante annealing cuántico simulado. | Es un antecedente de aprendizaje por refuerzo cuántico, con otra representación; no se identificó una política de 1.000 cables. |
| [Minor embedding con RL](https://re.public.polimi.it/handle/11311/1312686), registro institucional 2026 | PPO construye embeddings que abarcan más de mil cúbits del sistema de destino. | Esa cifra corresponde al embedding, no prueba una política cuántica con esa anchura. |
| [Quafu-RL](https://cpb.cpsjournals.org/EN/10.1088/1674-1056/ad3061), 2024 | El resumen menciona una plataforma con hasta 136 cúbits. | No se equipara capacidad de la plataforma con cúbits efectivamente utilizados por cada política. |
| [Park, revisión QRL](https://onlinelibrary.wiley.com/doi/10.4218/etrij.2024-0153), 2024 | La sección 3.3.2 considera prospectivamente más de mil cúbits tolerantes a fallos. | Es una perspectiva futura; no documenta ese experimento simulado. |

La comparación anterior de BBY Q con el artículo de QCNN no resolvía por sí
misma la prioridad de **QRL**, porque una tarea de clasificación y una política
de refuerzo son categorías distintas. La revisión actual hace esa distinción.

## Comprobación auxiliar del circuito con qsim

| Operación | Cobertura de la referencia qsim |
| --- | --- |
| Evaluación del circuito con parámetros congelados | Ejecutada y cronometrada. |
| Gradientes seleccionados y una actualización SGD de VQC | Comprobación numérica fuera del cronómetro principal. |
| Episodios QRL, recompensas y actualización de la política | No ejecutados. |
| Campañas de 100, 1.000 y 10.000 episodios | No ejecutadas. |
| Generalización y comparación de curvas de aprendizaje | No ejecutadas. |
| Planificación, integración VQC3/QRL3 y persistencia recuperable | No ejecutadas. |

Esta cobertura corresponde al adaptador qsim. Las campañas originales de
BBY Q sí están documentadas en [REPORT.md](REPORT.md).

Se creó una referencia independiente con el núcleo público
[qsim](https://github.com/quantumlib/qsim), fijado en
`50cac4b3fa331450b70387735479a00e223b8d25`. El adaptador conserva exactamente
la topología de BBY Q: dos registros de 1.000 cables, cada uno descompuesto en
250 estados de cuatro. Aplica las mismas RY, CNOT y observaciones en binaria64,
con los ángulos y pesos del modelo entregado.

**El adaptador es nuevo código de referencia de esta investigación.** No se
presenta como prueba de que qsim hubiera publicado anteriormente un agente RL
de 1.000 cúbits. Tampoco es una reproducción del entrenamiento de Mario o de
las QCNN de la tabla.

Se utilizaron ocho entradas por agente, 20 repeticiones medidas por entrada y
dos rondas con orden qsim/XI/XI/qsim, en el mismo entorno Linux de CPU. Ambos
backends usan ejecución secuencial. La preparación de entradas queda fuera de
los cronómetros nativos. Para evitar arrastrar el máximo de RAM previo a exec
del hijo de Python, ambos informan VmHWM de su ejecutable Linux; la envoltura
de XI solo adapta esa medición y conserva su fuente y lógica originales.

| Circuito congelado | XI: mediana nativa | qsim: mediana nativa | XI: pico RSS | qsim: pico RSS |
| --- | --- | --- | --- | --- |
| VQC3, 1.000 cables | 25,145 ms | 0,178 ms | 12,87 MiB | 2,08 MiB |
| QRL3, 1.000 cables | 26,425 ms | 0,176 ms | 14,79 MiB | 2,08 MiB |

La razón de tiempos de este cálculo congelado fue aproximadamente 141-150.
XI incluye el coste de sus instrucciones y del almacenamiento genérico Ether;
el adaptador qsim ejecuta un recorrido compilado en C++. Esa razón no es una
medición del tiempo de entrenamiento de dos agentes completos. No permite
afirmar que qsim aprende más rápido o que supera al sistema BBY Q.

La verificación comparó **32.000 observables** y **32.016 valores de parámetros
tras una actualización SGD de VQC**. El error absoluto máximo fue 8,89e-16
en observables, 1,78e-15 en scores, 1,39e-17 en gradientes y 2,23e-16 en los
parámetros actualizados. El archivo entrenado de entrada permaneció intacto.

Los 19-22 MiB informados anteriormente corresponden a las campañas completas
con otra instrumentación y carga. Esta tabla mide inferencia congelada con un
criterio de memoria posterior a exec; no reemplaza retrospectivamente esos
registros ni mezcla la RAM instalada de una máquina con el RSS de un proceso.

Fuentes y comandos: [benchmark reproducible](../../../benchmarks/quantum3-reference/README.md).
Datos de esta ejecución: [qsim-reference-trained.json](qsim-reference-trained.json).
La [CI dedicada](https://github.com/guadalupejuan001-code/BBY-Q/actions/workflows/quantum3-qsim-reference.yml)
repite la comparación numérica con parámetros de prueba reproducibles; el
ensayo local anterior utilizó los parámetros del modelo entregado.

## Código público de agentes completos revisado posteriormente

Se inspeccionó [nicomeyer96/qrl-benchmark](https://github.com/nicomeyer96/qrl-benchmark),
código de Meyer et al., ICML 2025, en el commit
`c20b9efb056b840225e23a1192c2d5fc5d70986d`. Es un trabajo distinto del artículo
de Kruse et al. con el mismo título que aparece en la tabla anterior.

Su código incluye políticas DDQN/PPO, interacción con un entorno de selección
de antenas, actualizaciones de parámetros y evaluación. `train.sh` especifica
configuraciones cuánticas de 6, 8, 10, 12 y 14 cúbits. El entrenamiento DDQN
devuelve los parámetros del modelo y del optimizador junto con métricas;
eso no implica que se haya verificado una reanudación completa, ya que el
logger publica `save_data` sin implementación.

Esta revisión fue **de código, sin ejecutar una campaña externa**. El entorno,
la arquitectura y las anchuras difieren de QRL3. No se ha portado el entorno
a XI ni adaptado el agente publicado a la tarea de BBY Q. Por tanto, encontrar
este repositorio no completa una comparación experimental y no proporciona
un antecedente comprobado de una política de 1.000 cúbits.

Para completar la comparación pendiente hacen falta ejecuciones completas
en una tarea común, presupuestos de experiencias y evaluación acordes,
varias semillas y mediciones con la misma cobertura. El estado seguirá siendo
pendiente hasta disponer de esos resultados, sus comandos y checkpoints.

## Afirmaciones que sostienen los resultados

| Afirmación | Estado |
| --- | --- |
| BBY Q entrena agentes simulados con 1.000 cables funcionales por agente en XI/Ether. | Verificada por las campañas y las pruebas causales originales. |
| Es el primer QML simulado de esta anchura. | Hay antecedentes relacionados a 1.024 cúbits. |
| Es el primer QRL entrenado con exactamente estos criterios de 1.000 cables. | No se encontró una coincidencia previa entre las fuentes revisadas; prioridad mundial aún no establecida. |
| Es el primero en combinar circuitos pequeños dentro de una política QRL. | Existe el antecedente modular de 2025. |
| Usa menos RAM que aquel estudio de QCNN o que Mario. | No determinado: faltan mediciones comparables de consumo y las tareas son diferentes. |
| qsim supera a VQC3/QRL3 como agentes completos. | No evaluado. La prueba auxiliar no ejecutó agentes completos en qsim. |

La contribución comprobada es la implementación y validación de los agentes
en XI/Ether. Una declaración de prioridad más amplia requiere comparar nuevas
fuentes independientes. Una declaración de superioridad de aprendizaje requiere
entrenamiento completo en la misma tarea, con las mismas evaluaciones y recursos.
