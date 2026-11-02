# Verificación final de la misión VQC3/QRL3

Fecha: 2 de noviembre de 2026. Resultado: **misión experimental completada y verificada**.
La revisión volvió a ejecutar el intérprete XI compilado desde las fuentes fijadas,
restauró los modelos entregados y contrastó los diez ciclos de la solicitud original.
No fue necesario modificar los algoritmos ni volver a entrenar las campañas largas.
Las limitaciones de aprendizaje medidas siguen documentadas.

Datos completos de esta revisión: [FINAL_VERIFICATION.json](FINAL_VERIFICATION.json).
La evidencia original y los resultados por ciclo están en [REPORT.md](REPORT.md)
y [CYCLES.md](CYCLES.md).

## Resultado de las comprobaciones nuevas

- Compilación correcta de REVERSE-PC `59ac79386bc427620a10227489eb7f7be12c55c7`
  con Mundo X/Ether `e2778d962af22f6f1a0794058dd4685fc2573966`.
- 2.127 comprobaciones del simulador aprobadas, incluyendo 2.000 derivadas
  causales no nulas y un oráculo denso independiente; error máximo 3,34e-16.
- 24 comprobaciones de agentes aprobadas: gradientes frente a diferencias
  finitas, inferencia independiente de la etiqueta oculta, rollback,
  reanudación idéntica y conservación del entrenamiento anterior.
- En el checkpoint principal entrenado se comprobó una derivada no nula del
  score respecto de **cada uno de los 1.000 ángulos de cada agente**, para
  entradas de prueba explícitas. Esta comprobación no alteró sus parámetros.
  No se limita a contar cúbits registrados o a probar primitivas aisladas.
- QRL3 continuó cuatro episodios en memoria y obtuvo los mismos parámetros
  ejecutándolos seguidos o guardando y restaurando después del segundo.
  El archivo principal de 10.000 episodios permaneció intacto.
- Se compararon nuevamente 8.000 observables con el equivalente clásico
  analítico: error máximo 7,24e-16; los parámetros después de diez ejemplos
  difirieron como máximo 2,23e-16. No se demostró ventaja cuántica.
- Los modos congelado y conjunto ejecutaron aprendizaje real, observaron
  2.000 cúbits y respetaron la conservación o actualización de VQC según el
  modo. El planificador ejecutó XI sin cambiar los parámetros del modelo.
- Los **132 checkpoints indexados** coincidieron en sus hashes comprimidos
  y descomprimidos. Las 18 campañas conservaron los prefijos declarados.
  Los tiempos, medianas y experiencias de los diarios completos coinciden
  con sus manifiestos; las fuentes XI coinciden con las condiciones archivadas.
- Los dos diarios parciales originales permanecen identificados como tales.
  Sus repeticiones completas tienen parámetros finales idénticos; no se
  rellenaron tiempos ausentes ni se contaron los originales como diarios completos.
- La comparación de fuentes desde `1e48cb03b27aadbea0c1f4684306128dc1e637ae`
  no encontró cambios en los modelos cuánticos previos ni en C12/C14/C15.

## Evaluación reservada reproducida desde los checkpoints

Cada resultado de esta tabla coincidió exactamente con la campaña publicada.
Las columnas de tiempo conservan las medianas originales verificadas en los
diarios; no son una nueva medición del teléfono ni una comparación de inteligencia.

| Agente y tarea | Episodios | Casos IID/OOD | IID | OOD | ms/episodio | ms/actualización |
| --- | --- | --- | --- | --- | --- | --- |
| VQC3 lineal | 10.000 | 128/128 | 94,53 % | 96,88 % | 48,87 | 13,76 |
| VQC3 paridad | 10.000 | 128/128 | 71,09 % | 81,25 % | 48,27 | 13,73 |
| VQC3 señal densa | 10.000 | 128/128 | 53,12 % | 57,81 % | 44,75 | 12,78 |
| QRL3 navegación básica | 10.000 | 64/64 | 100,00 % | 82,81 % | 191,04 | 57,98 |
| QRL3 con deslizamientos | 10.000 | 64/64 | 98,44 % | 93,75 % | 226,48 | 68,47 |

La evaluación volvió a ejecutar políticas aleatorias y observaciones anuladas,
comprobó que evaluar no modifica los parámetros y exportó ocho trayectorias
QRL con estados, acciones, probabilidades, transiciones y recompensas.

Curvas y comparación temporal: [aprendizaje](learning_curves.png),
[tiempo y memoria](timing_memory.png), [coste de simulación](simulation_cost.png).

## Contraste con los diez ciclos solicitados

| Ciclo | Comprobación de cierre |
| --- | --- |
| 1. Auditoría | VQC2/QRL2 y GHZ diferenciados de V3; archivo 800/800 conservado y restaurado; fuentes previas intactas. |
| 2. Arquitectura | 1.000 cúbits funcionales por agente; operaciones, observaciones y sensibilidad causal comprobadas. |
| 3. VQC3 | Codificación, circuito, pérdida y SGD implementados en XI; los 1.000 ángulos y pesos cambiaron en las campañas largas. |
| 4. QRL3 | Política cuántica, decisiones secuenciales y retorno terminal en XI; el modelo principal contiene 46.131 decisiones. |
| 5. Entrenamiento | Prefijos acumulativos de 100, 1.000 y 10.000 conservados; varias tareas, dificultades y semillas. |
| 6. Velocidad | Tiempos, experiencias, memoria, curvas y coste por complejidad conservados y contrastados con los diarios. |
| 7. Integración | Comparación independiente/congelada/conjunta publicada; aislamiento y actualización de ambos modos repetidos. |
| 8. Optimización | Optimizaciones existentes de factores y transporte conservadas; compilación y exactitud numérica repetidas. |
| 9. Validación | Conjuntos separados, etiqueta oculta, controles aleatorios, ablaciones, equivalente clásico y reanudación comprobados. |
| 10. Entrega | Código y resultados fusionados, matriz CI cuántica aprobada y archivos entregados verificados por hashes. |

## Límites que permanecen

Los agentes usan **250 bloques entrelazados de cuatro cúbits por agente**.
Los 1.000 cúbits intervienen en cada forward independiente; los cuatro
gradientes calculados por decisión recorren los ángulos de forma cíclica.
Un prefijo de 100 ejemplos todavía no actualiza todos los ángulos de VQC;
las campañas largas sí lo hacen. Esta topología no representa un estado
denso arbitrario con entrelazamiento global de 1.000 cúbits.

Los problemas estructurados repiten cuatro canales latentes; la señal densa
usa 1.000 entradas generadas independientemente y su aprendizaje fue débil.
QRL sigue siendo sensible a la semilla y puede perder generalización con
más entrenamiento. La conexión conjunta es alternada, y la planificación
usa transiciones y recompensas conocidas. Los resultados acreditan capacidad
experimental en estas tareas, no aprendizaje universal.

La simulación es clásica y utiliza expectativas analíticas de Born. No hay
hardware cuántico físico ni ventaja computacional demostrada. El fallo previo
del saludo clásico Android sigue documentado fuera del alcance de esta misión.
Esta entrega no incluye una nueva APK ni una interfaz Android.

## Entrega y revisiones

- [Implementación BBY-Q #67](https://github.com/guadalupejuan001-code/BBY-Q/pull/67).
- [Primitivas y ejecución REVERSE-PC #171](https://github.com/guadalupejuan001-code/REVERSE-PC/pull/171).
- [Resultados BBY-Q #68](https://github.com/guadalupejuan001-code/BBY-Q/pull/68).
- [CI del código fusionado: cuatro trabajos aprobados](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/41395030234).
- [Modelo principal entrenado](https://chatgpt.com/library?file_id=libfile_d8d3a5f8bd388191a6fb5c830a1159f0&account_id=personal).
- [Paquete de checkpoints y métricas](https://chatgpt.com/library?file_id=libfile_79efe6f44fd481919910526c338e8800&account_id=personal).

SHA-256 del modelo principal:
`eaba877ad9921e55fb4c191bea31dd2eb85ff3c72ba5261c3568709757926e76`.

SHA-256 del ZIP entregado:
`879034b2c4b534f8266c28831390122d39651a4c02d79e59954a91b04f3b9382`.

## Repetición de las verificaciones esenciales

Con los repositorios fijados anteriores y los `.rvp.gz` descomprimidos:

```sh
bash REVERSE-PC/scripts/build-xi-session.sh mundo-X REVERSE-PC/build
python3 REVERSE-PC/tests/xi_continuous.py REVERSE-PC/build/reverse_pc REVERSE-PC/build/xi_session verification/primitives
python3 BBY-Q/integration/quantum3/validate.py --runtime REVERSE-PC --legacy-checkpoint paquete/legacy/BBYQ-VQC1000-QRL1000-Entrenados-800.rvp --output verification/agents
python3 BBY-Q/integration/quantum3/validate_analytic.py --runtime REVERSE-PC --checkpoint modelo.rvp --output verification/analytic.json
python3 BBY-Q/integration/quantum3/validate_integration.py --runtime REVERSE-PC --checkpoint modelo.rvp --output verification/integration.json
python3 BBY-Q/integration/quantum3/evaluate_final.py --runtime REVERSE-PC --campaign paquete/checkpoints/vqc-linear-s173 --output verification/vqc-linear
python3 BBY-Q/integration/quantum3/evaluate_final.py --runtime REVERSE-PC --campaign paquete/checkpoints/qrl-slip-s173-v2 --output verification/qrl-slip
```
