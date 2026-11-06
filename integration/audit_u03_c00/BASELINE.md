# C00 — Registro inicial de evidencia e hipótesis

## Evidencia heredada (no mediciones de C00)

La PR #85 preserva el commit ae3afcf52500954ce8849d9bf7c8f0286f5b172b.

| Prueba de la versión U02 | Resultado publicado |
| --- | ---: |
| Integración, persistencia y rollback | 9/9 |
| Readout, gradientes y aislamiento | 7/7 |
| Migración U01 de bancos | 5/5 |
| Clasificación de intención | 488/490 |
| Generación de texto C1 | 134/141 |
| Misiones cooperativas nuevas | 200/200 |
| Clasificaciones independientes tipadas | 1024/1024 |
| APK construida por U02 | No |

Referencias:

- [PR #85](https://github.com/guadalupejuan001-code/BBY-Q/pull/85)
- [CI nativa U02](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42180864178)
- [CI C1](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42180864079)
- [Guardia Android: fases omitidas](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42180864087)
- [Documento de la versión U02](../unified/README.md)

La CI U02 completó una serie de 200 misiones con dos trabajadores en
alrededor de cinco minutos según la duración de su paso. Incluye apertura,
ejecución, cierre y controles. No constituye una medida por turno ni una
prueba de rendimiento físico Android.

## Riesgos previamente conocidos

1. La frase "necesito más ejemplos para aprender" es un rechazo textual
   especial, todavía sin evidencia de calibración metacognitiva.
2. El codificador de intención conserva dos fallos y el generador siete.
   Ni las reservas perfectas ni los contratos declarados demuestran AGI.
3. BEGIN IMMEDIATE durante la inferencia podría crear colas en escritores.
4. XI recibe texto del programa por llamada; se recrean procesos y snapshots.
5. Los 1000 cúbits virtuales por agente corresponden a una topología concreta,
   no a simulación exacta eficiente de estados arbitrarios.

## Hipótesis para C01 (pendientes de experimentación)

- H1: sesiones/programas XI residentes reducen tráfico e inicialización.
- H2: snapshots inmutables y confirmación corta reducen contención sin perder atomicidad.
- H3: caché VQC versionada evita recomputación de observaciones idénticas.
- H4: mediciones CPU/E/S por operación identifican dónde optimizar primero.

**No se declara ninguna aceleración antes de medirla.** Los próximos cambios
deberán repetirse contra la base fijada y superar las pruebas nativas,
regresión funcional, idempotencia y restauración.
