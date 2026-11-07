# C04 — Resultados de planificación selectiva y SHA paralelo

**Estado:** CI C04 aprobada en la revisión anterior a la precisión terminológica
del contador de ejecuciones, sin diferencias de estado.
- [Ejecución verificada de GitHub Actions](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42345963529)
- [Evidencia completa, artefacto JSON](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42345963529/artifacts/13563588466)
- [PR #90](https://github.com/guadalupejuan001-code/BBY-Q/pull/90)

La fuente U02 de XI, los pesos, los checkpoints y las decisiones permanecen
iguales. La planificación difiere la apertura de procesos y una consulta
**de metadatos** VQC cuando ninguna etapa necesita ese banco. No omite
las mediciones/circuitos de inferencia ni los updates de aprendizaje.
La comprobación SHA-256 de los siete bancos persistentes se realiza sobre
bytes inmutables con hasta cuatro trabajadores.

## Medidas del mismo runner Linux, dos repeticiones por escenario

Comparación **C03 cacheada original** frente a **C04 con la misma caché C03**,
por tanto el beneficio no se atribuye erróneamente a la descompresión de C03.
El runner de esta prueba fue AMD EPYC 9V74, cuatro CPU lógicas, Python 3.12.16.

| Operación | C03 original (ms) | C04 (ms) | Diferencia de latencia | Procesos XI sin arrancar | Paquetes EXEC C03 → C04 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Aritmética | 1647,403 | 1448,507 | 12,1 % menos | 4 | 30 → 29 |
| Conversación/texto | 1856,474 | 1703,982 | 8,2 % menos | 4 | 28 → 27 |
| Estado | 1522,988 | 1378,969 | 9,5 % menos | 4 | 21 → 20 |
| Lectura QMemory | 1491,298 | 1309,821 | 12,2 % menos | 3 | 22 → 21 |
| Política QRL | 1789,423 | 1882,738 | 5,2 % más | 1 | 31 → 30 |
| Misión completa | 2223,569 | 2286,899 | 2,8 % más | 0 | 48 → 48 |
| Feedback verificado | 3320,237 | 3478,459 | 4,8 % más | 0 | 113 → 113 |
| Replay exacto | 0,189 | 0,188 | Prácticamente igual | 0 | 0 → 0 |

**Importante:** los EXEC reducidos para operaciones sencillas corresponden
a un `mem_materialize` de consulta de versión del readout VQC,
que no modifica el banco persistente. El conteo de ejecución de circuitos
estatales de misión y feedback es idéntico. La garantía central es identidad
exacta de todos los bancos y resultados.

## Validación realizada

- Los mismos resultados nativos, recibos, historial (excluyendo exclusivamente
  `elapsed_ms` del generador de texto, una duración de reloj variable),
  159 fuentes/checkpoints protegidos y hashes de todos los bancos.
- Replay idempotente, rollback tras fallo, correcciones de memoria, migración U01,
  actualizaciones de VQC/QRL/QMemory/voz y lectura de hechos derivados.
- Se abre solo QMemory para guardar/leer asociaciones.
- Se abren V3, voz y coordinador para políticas; los cuatro motores cuando
  una misión o entrenamiento necesita cada uno.
- Una consulta simbólica que depende de una observación desactualizada
  activa VQC y recalcula su premisa nativa.
- No hay paralelismo de estados cuánticos ni cambios de representación:
  el único paralelismo implementado es el cálculo SHA independiente.

## Pros / contras

**Beneficios comprobados en esta campaña:** menos procesos para peticiones
sencillas, ahorro de consulta readout sin uso y menos latencia en esas tareas.

**Contrapartida:** planificación, lanzamiento diferido, verificación SHA con
ThreadPool y control de recursos tienen sobrecarga; en tareas que usan todos
los motores, C04 fue ligeramente más lento. Por tanto, esta campaña **no
demuestra una mejora universal**. La selección automática del presupuesto
de hashes o el rediseño de bancos es trabajo futuro.

## Límites

Dos observaciones por caso no bastan para un intervalo de confianza.
El rendimiento de un runner Linux cambia según carga, cachés y CPU. No hay
datos de batería, RAM residente o FPS del Android físico. El benchmark no
implica ventaja cuántica ni inteligencia general.

El código está en una rama opt-in; **sin APK**, sin fusión automática y sin
publicación a Android.
