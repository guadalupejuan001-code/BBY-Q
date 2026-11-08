# BBY Q U03 C13 — RESULTADOS de optimización XI autenticada

**Estado:** [CI nativa #42443472416 aprobada](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42443472416) · [artefacto JSON #13602796673](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42443472416/artifacts/13602796673) · [PR #99](https://github.com/guadalupejuan001-code/BBY-Q/pull/99) (borrador).  
**Base exacta:** [PR #98 C12](https://github.com/guadalupejuan001-code/BBY-Q/pull/98), commit `d31d60bb0ee356b004e9e1e2d819aa361ef3a9db`.  
**Advertencia:** estos son resultados de simulador XI/Ether en **Linux**, no medidas de Android, hardware cuántico ni FPS.

## Decisión predefinida

La caché autenticada de bytes inmutables hizo más rápido el **arranque U02**, pero la mejora de latencia de extremo a extremo no alcanzó **3 % en ninguno de los dos brazos**. La condición de aceptación se había fijado **antes de medir**: ambas medianas debían mejorar al menos 3 %, manteniendo recibos idénticos. Por ello **no se recomienda habilitar la caché ni promocionar modelo alguno**; permanece como experimento opt-in en la rama C13.

## Comparación pareada en mismo runner

Cuatro casos sintéticos nuevos y disjuntos de C11/C12 × 3 repeticiones, **12 pares por brazo**, alternando original y caché. Cada petición se evalúa sobre una copia SQLite nueva; el tiempo incluye la autenticación SHA-256 de la caché **amortizada**, no se esconde ese coste.

| Brazo | Original (mediana) | Cache C13 (mediana) | Delta | Reducción |
|---|---:|---:|---:|---:|
| U02 congelado | 2.934,053 ms | 2.852,722 ms | 81,331 ms | **2,77 %** |
| C12 conjunto experimental | 2.923,514 ms | 2.837,243 ms | 86,271 ms | **2,95 %** |

Se observaron **10/12 pares más rápidos** en U02 y **9/12** en C12. Algunos pares empeoraron, y una muestra de 12 por brazo no acredita una mejora estable de producción.

### Cuellos de botella medidos por fase

| Fase, mediana por tarea (Linux) | U02 original | U02 caché | C12 original | C12 caché |
|---|---:|---:|---:|---:|
| Copia SQLite | 219,335 ms | 219,878 ms | 267,750 ms | 221,439 ms |
| Autenticación y arranque | **141,141 ms** | **31,602 ms** | **139,980 ms** | **31,595 ms** |
| Ejecución original U02/XI | **2.496,838 ms** | 2.465,302 ms | **2.469,590 ms** | 2.477,052 ms |
| Auditoría C09 | 60,909 ms | 61,261 ms | 61,069 ms | 61,398 ms |
| Cierre de sesión | 4,716 ms | 5,056 ms | 4,965 ms | 5,015 ms |
| Puerta SHA amortizada | 0,087 ms | 10,656 ms | 0,089 ms | 10,572 ms |

El **cálculo/turno XI consume aproximadamente 84–85 %** de la latencia del caso típico, aun cuando la caché acelera la carga autenticada de modelos. Los cambios de duración dentro de la ejecución XI no pueden atribuirse causalmente a la caché; los circuitos no cambiaron.

## CPU, RAM, I/O y operaciones XI

- CPU del proceso anfitrión, mediana por tarea: U02 **475,015 → 374,248 ms**; C12 **471,941 → 366,075 ms**. Son valores observados de este runner, no ahorro de CPU nativo garantizado.
- Perfil de **una misión** con instrumentación (que añade sobrecarga): **46 paquetes `XiSession.execute`**, 6 aperturas de sesión nativa, 5 guardados y 6 cierres; **2.552.717 bytes** de fuente enviados a XI. El CPU nativo observado fue ~**1.530–1.540 ms** en esa muestra; el máximo RSS nativo observado ~**74.908–75.024 KiB**. Los tiempos de paquetes compartidos se solapan por motor, y NO representan tiempo exclusivo de cada puerta.
- Pico RSS acumulativo del proceso Python en el runner: **177.400 KiB** (~173 MiB). Es una medida del proceso completo, no una mejora de RAM entre brazos.
- I/O `/proc/self/io` observado: aproximadamente **2,13 GB de escritura atribuida al proceso por 12 tareas** en cada brazo/variante. Los `read_bytes` observados fueron cero por la caché de página del host; **cero no demuestra que no hubo lecturas**, y esta atribución no representa directamente desgaste físico de una SSD.

### Ablaciones nativas, sin alterar respuestas

Se compararon diez controles por brazo (normal y cuatro ablaciones sobre dos casos). **Todos los recibos, las acciones simuladas, las clases, reglas, voces y snapshots posteriores fueron idénticos** entre C12 original y C13 con caché.

En los dos casos: al borrar QMemory se perdió una de dos reglas, la ablación VQC cambió una clasificación, la ablación QRL cambió las dos acciones simuladas y al desactivar QChat se perdió la fidelidad de ambas salidas. Son observaciones descriptivas, no estimaciones causales generales. No se entrenó ningún módulo durante inferencia.

## Integridad y siguientes límites

- **159 fuentes/checkpoints históricos protegidos intactos**; no se editó ninguna ruta original de REVERSE-PC, XI/Ether o U02.
- Se conservaron los **seis hashes de pesos/ángulos nativos** y snapshots posteriores exactos; siete bancos U02 y sincronización C1 comprobados. SQLite fuente inalterado, cero nuevas memorias autoritativas.
- El control `frozen` sigue siendo la elección; la versión conjunta C12 no mejoró la exactitud y no fue promovida. No se creó ningún APK ni se fusionó automáticamente ninguna PR.
- **C14 — Benchmarks y ablaciones:** perfilar XI por operaciones y costes exclusivos (no paquetes solapados), medir más repeticiones bajo cargas heterogéneas, identificar ahorros en serialización, arranque de procesos nativos y escritura/copias SQLite, y reevaluar un conjunto de ablaciones mayor. Mantener datos predefinidos y comparadores originales.

[Panel C00–C17](../../docs/BBY_Q_U03_PANEL.md) · [Estado JSON](../../docs/BBY_Q_U03_ESTADO.json) · [Continuidad C14](../../docs/BBY_Q_U03_SIGUIENTE.md).
