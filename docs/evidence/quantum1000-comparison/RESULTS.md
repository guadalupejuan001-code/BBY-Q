# Comparación ejecutada: grupos independientes y registro conectado

## Veredicto

La cantidad anterior era correcta: 1.000 cúbits por agente repartidos en grupos. El registro conectado actual también tiene 1.000 y su conectividad está verificada, pero conectar los grupos no produjo una ventaja general en estas tareas.

El control conserva los grupos y utiliza CZ y el aprendizaje actual. Frente a ese control, el conectado pasó de 91,41% a 91,15% en clasificación lineal, de 54,69% a 55,73% en señal densa y mantuvo 81,25% en QRL (medias IID de tres semillas). La mejora de QRL respecto al diseño histórico —66,15% a 81,25%— también aparece sin conectar los grupos, por lo que no puede atribuirse únicamente a la conectividad.

El entrenamiento conectado consumió entre 1,44 y 1,61 veces la CPU del control, y entre 1,87 y 2,04 veces la del anterior, según la tarea. En el benchmark separado de inferencia congelada consumió 76,29 ms de CPU por forward, frente a 29,34 ms del control y 25,05 ms del anterior. Esta segunda medición no se presenta como entrenamiento ni como episodios completos de QRL. La memoria de entrenamiento fue parecida y no empeoró en todas las tareas.

El resultado práctico es mayor conectividad, con aprendizaje parecido al control y mayor coste de ejecución en estas pruebas. No hay motivo experimental para llamar incorrecta a la organización anterior por su número de cúbits, ni para declarar superior al registro conectado en rendimiento general.

## Alcance y protocolo

Se completaron 27 campañas nuevas de 1.000 episodios: tres diseños × tres tareas × tres semillas (173, 941 y 2026). Todos mantienen 1.000 cúbits simulados por agente; no se usó qsim.

El diseño anterior conserva su CNOT y sus cuatro gradientes de ángulo por decisión. El control utiliza el aprendizaje actual (CZ y 1.000 gradientes), pero mantiene 250 componentes independientes de cuatro. El actual utiliza un componente MPS conectado de 1.000. La comparación control/actual mantiene datos, parámetros iniciales, tasas, algoritmos y episodios; cambia preparación, representación de estado y conexiones. La comparación histórica también incluye los cambios de compuertas y optimización.

Cada modelo entrenado se evaluó sin actualizarlo en 128 casos IID y 128 OOD nuevos, con semilla 827391, fijada antes de ejecutar las campañas. Los controles inicial y de observaciones anuladas usan 32 casos por conjunto. El entorno genera todos los datos, transiciones y recompensas en XI. Python solo organiza y registra.

## Aciertos después de 1.000 episodios

Media de tres semillas; entre paréntesis, mínimo–máximo observado. Los casos de prueba son comunes entre semillas, por lo que no se presentan como 384 muestras independientes ni se agrupan sus intervalos Wilson.

| Tarea / conjunto | Anterior, CNOT | Control, CZ | Actual conectado, CZ |
|---|---:|---:|---:|
| VQC lineal / IID | 90.62% (89.84–91.41) | 91.41% (89.84–93.75) | 91.15% (89.84–92.19) |
| VQC lineal / OOD | 96.09% (94.53–96.88) | 95.57% (92.97–96.88) | 95.31% (92.97–97.66) |
| VQC señal densa / IID | 54.43% (49.22–63.28) | 54.69% (49.22–64.06) | 55.73% (49.22–67.19) |
| VQC señal densa / OOD | 53.12% (50.00–59.38) | 53.12% (50.00–59.38) | 53.65% (50.00–60.94) |
| QRL secuencial sencillo / IID | 66.15% (44.53–98.44) | 81.25% (44.53–100.00) | 81.25% (44.53–100.00) |
| QRL secuencial sencillo / OOD | 64.84% (48.44–92.19) | 77.60% (53.91–89.84) | 76.82% (53.91–90.62) |

## Tiempo de entrenamiento y memoria

CPU nativa total por campaña, media entre semillas. Incluye solicitudes de guardado/inspección de hitos; excluye los procesos de evaluación separados. QRL puede necesitar distinta cantidad de decisiones según lo aprendido, por lo que los diarios y el CSV conservan también decisiones y CPU por decisión.

| Tarea | Anterior: CPU s / MiB | Control: CPU s / MiB | Actual: CPU s / MiB |
|---|---:|---:|---:|
| VQC lineal | 64.07 / 19.56 | 89.58 / 18.15 | 130.97 / 18.19 |
| VQC señal densa | 69.01 / 19.59 | 95.04 / 18.16 | 137.24 / 17.76 |
| QRL secuencial sencillo | 282.90 / 22.03 | 328.96 / 22.21 | 528.00 / 23.84 |

## Latencia de inferencia aislada

Esta medición es solo el forward de un agente con parámetros e inputs congelados; no representa entrenamiento ni episodios completos de QRL. Se ejecutó después de las campañas, en serie y con orden alternado, en el mismo núcleo: cinco rondas de 40 forwards por diseño y cinco calentamientos por ronda. Medianas entre rondas.

| Diseño | CPU ms / forward | Transporte ms / forward | RSS MiB |
|---|---:|---:|---:|
| Anterior: grupos de 4 / CNOT | 25.049 | 24.869 | 11.49 |
| Control: grupos de 4 / CZ | 29.339 | 28.790 | 11.60 |
| Actual: 1.000 conectados / CZ | 76.289 | 76.273 | 11.91 |

## Verificaciones y límites

- 27 complete journals: consecutive real episodes and compressed/decompressed hashes verified.
- Every final IID/OOD count was recalculated from the saved individual outcomes.
- Every initial/100/final checkpoint was decompressed and authenticated.
- All paired variants share initial learned parameters and CPU affinity.
- Se verificaron 2.000 cúbits activos en cada diseño. Anterior/control: 500 componentes de cuatro entre ambos agentes; actual: dos componentes de 1.000 y 999 cortes entrelazados por agente.
- El control con CNOT reproduce exactamente los 1.000 observables y el score del circuito anterior. Los gradientes completos del control y del conectado coinciden con diferencias finitas; se verificó también la reanudación idéntica del control.
- Tres semillas y estas tareas sintéticas no prueban una superioridad general. Mayor conectividad, mayor entrelazamiento y mayor exactitud predictiva son propiedades distintas.
- Los modelos nuevos de esta comparación se guardan por separado. No se modificaron los agentes productivos ni los checkpoints anteriores.

## Diagnóstico posterior de estabilidad

Sin entrenar ni seleccionar modelos nuevos, se inspeccionaron las salidas guardadas y seis estados QRL explícitos por modelo. En la semilla 2026, los tres diseños QRL alcanzaron 44,53% IID y favorecieron ir a la derecha con más de 99% de probabilidad desde el centro tanto con objetivo izquierdo como derecho. Esta política sesgada ya aparece en el diseño anterior. El histórico de la semilla 941 mostró el sesgo contrario, mientras el control y el conectado aprendieron a distinguir los dos objetivos.

En señal densa, las semillas 941 y 2026 asignaron todos los 128 casos IID a una sola clase en los tres diseños; la semilla 173 sí produjo ambas clases. Estos problemas de estabilidad no son una pérdida de cúbits. El diagnóstico es posterior a las evaluaciones principales y no se utilizó para ajustar parámetros. Los valores individuales están en [diagnostics.json](diagnostics.json).

## Reproducción

```bash
bash /ruta/REVERSE-PC/scripts/build-xi-session.sh /ruta/mundo-X /ruta/REVERSE-PC/build
python integration/quantum1000/validate_comparison.py --runtime /ruta/REVERSE-PC --output build/topology-preflight
python integration/quantum1000/compare_topologies.py all --runtime /ruta/REVERSE-PC --episodes 1000 --samples 128 --workers 6 --output build/topology-comparison
python integration/quantum1000/benchmark_comparison.py --runtime /ruta/REVERSE-PC --output build/topology-benchmark
```

Fuentes fijadas: BBY-Q `d21f6b3fa867febf9559dbab0fc0b0ae453d879a`; REVERSE-PC `08c363e6c6855c14026c86046af7183a45f45a98`; mundo-X `e2778d962af22f6f1a0794058dd4685fc2573966`. Los cuatro archivos XI históricos se contrastaron con los blobs de la PR #67. Hash del ejecutor recompilado: `6c840f2a440523f2ce65bfdb7e19dc56855135f5a44e14bfa64db795f8de1ff6`.

[Protocolo](PROTOCOL.json) · [Resumen numérico](summary.json) · [CSV por semilla](results.csv) · [Verificación](validation.json) · [Benchmark crudo](forward-benchmark.json) · [Hashes de modelos](CHECKPOINTS.json)

[Modelos y checkpoints](../../../models/quantum1000-comparison) · [Hardware y compilador](hardware.json) · [Compilación del ejecutor](runtime-build.log)
