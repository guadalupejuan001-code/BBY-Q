# BBY Q U03 C14 — Resultados verificados de benchmarks y ablaciones nativas XI

**Estado:** ejecución de GitHub Actions [#42446685508 aprobada](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42446685508); [artefacto JSON con todas las muestras #13603503107](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42446685508/artifacts/13603503107). [PR #100](https://github.com/guadalupejuan001-code/BBY-Q/pull/100), en **borrador**, basada exactamente en C13 PR #99 y commit `5e88433895218ad90ee18f7380c49a69a51bc07e`.

**Resultado general:** C14 ha identificado costos por paquetes XI ejecutados realmente, demostrado paridad de controles congelados/caché, evaluado **40 ablaciones** y dos escritores SQLite por brazo. No se modificó ningún algoritmo XI, no se produjo un nuevo modelo y **no se promovió ninguna optimización**.

## Protocolo nativo, sin etiquetas filtradas
- **6 tareas nuevas predefinidas** y distintas de las semillas, reglas y nombres de C11–C13; 2 repeticiones de cada tarea × 3 rutas = **36 mediciones con XI original**, 12 por ruta.
- Rutas: **U02 `frozen`**, **C12 entrenado no promovido** y **C13 caché experimental sobre U02 frozen**. Etiquetas de clase del generador XI original obtenidas en una sesión separada *después de las 36 predicciones*; ninguna se introdujo en inferencia.
- Los tres recorridos obtuvieron **12/12 clases correctas, 12/12 reglas correctas, 12/12 voces fieles y 12/12 recibos exitosos**. La caché preservó el SHA del recibo y snapshot U02, pero **no se demostró una ganancia de exactitud** del modelo entrenado.

### Latencia de extremo a extremo (Linux host, incluye autenticación)

| Ruta | Mediana por solicitud | Sesiones XI originales |
|---|---:|---:|
| U02 congelado | **3.060,631 ms** | 12 |
| C12 conjunto, no promovido | **3.134,711 ms** | 12 |
| C13 caché inmutable opt-in, no promovida | **2.959,761 ms** | 12 |

En esta campaña, el contraste pareado U02 frozen vs caché dio una reducción del **3,30 %**, 10/12 pares más rápidos; NO se atribuye una mejora garantizada: las campañas C13 previas obtuvieron **2,08–2,95 %**, y C14 no midió una ruta C13 cache sobre el banco C12 entrenado con el mismo protocolo. La decisión previa de **no habilitar la caché** permanece.

## Costos disjuntos por paquete real XI

Mediana del tiempo de ejecución de paquetes (ms), **por dueño de banco/llamada, sin doble contabilidad**. Los tiempos etiquetados son duraciones de paquetes síncronos incluyendo interacción host–XI, NO CPU exclusivo por compuerta ni tiempo puro del circuito.

| Grupo | U02 frozen | C12 conjunto no promovido | U02 + caché C13 |
|---|---:|---:|---:|
| C1 | **465,123** | 494,447 | 463,321 |
| VQC | **236,213** | 236,178 | 235,500 |
| QRL | **48,004** | 47,980 | 48,042 |
| QMemory | **1,321** | 1,335 | 1,345 |
| Entity | **3,995** | 3,969 | 4,030 |
| QChat | **114,760** | 115,097 | 113,907 |
| XI transporte y comandos sin grupo | **807,370** | 829,662 | 805,643 |
| XI mixto | 0 | 0 | 0 |

La mediana de U02 utiliza **48 paquetes `XiSession.execute`** por misión (rango 46–48). Las medianas de distintas clases no se suman para reconstruir una mediana global, pues son observaciones pareadas no necesariamente del mismo caso. El sistema comprobó que los intervalos exactos de paquetes no se solapan y que la suma de categorías de cada corrida es idéntica al total de paquetes.

El turno nativo completo medido fue **2.792,136 ms (U02 frozen)** y **~1.122,958 ms de ese turno no quedaron atribuidos al tiempo de espera de paquetes**; esa diferencia engloba Python, SQLite, preparación/serialización y sobrecarga de instrumentación, pero C14 **no determina cuánto corresponde exclusivamente a cada subproceso**. El paquete no clasificado de ~807 ms contiene transporte y operaciones XI sin llamada asignable, no solamente IPC.

### CPU, memoria, SQLite y entrada/salida

| Métrica del runner Linux, ruta U02 frozen | Observación |
|---|---:|
| Copia SQLite por petición (mediana) | **50,470 ms** |
| Autenticación y apertura de sesión | **141,498 ms** |
| Auditoría C09 posterior | **59,581 ms** |
| CPU del proceso Python por petición (mediana) | **998,454 ms** |
| CPU nativa observada `/proc` por turno (mediana, aproximada) | **1.645 ms** |
| Pico RSS acumulado del proceso Python | **187.548 KiB** (~183 MiB) |
| Fuente enviada a XI por turno (mediana) | **2.625.782 bytes** |
| SQL ejecutado por 12 misiones, `INSERT` + `UPDATE` | **144** sentencias |
| `/proc/self/io write_bytes` observado en 12 misiones | **2.107.990.016 bytes** |

Los contadores RSS son máximos acumulativos de un proceso compartido; no prueban una mejora de memoria. Las escrituras observadas no se traducen directamente en desgaste físico SSD y los `read_bytes=0` de esta campaña no significan cero lecturas (caché de página del host). Las sentencias SQL se cuentan, no miden latencia SQL exclusiva.

## Ablaciones XI nativas: 4 casos por control y por brazo

Cada condición es el **control existente en U02**, ejecutado en un SQLite descartable. Los dos brazos `frozen` y C12 conjunto obtuvieron **los mismos resultados por condición**:

| Condición | Clase correcta | Regla correcta | Voz fiel/terminada | Acciones modificadas vs normal |
|---|---:|---:|---:|---:|
| Normal | 4/4 | 4/4 | 4/4 | — |
| QMemory borrada | 4/4 | **2/4** | 4/4 | 2/4 |
| VQC ablacionado | **1/4** | 4/4 | 4/4 | 3/4 |
| QRL ablacionado | 4/4 | 4/4 | 4/4 | 2/4 |
| QChat/voz ablacionado | 4/4 | 4/4 | **0/4** | 0/4 |

Se ejecutaron **40 ensayos de ablación, 20 por brazo**. La voz deshabilitada causó recibos `ok=False` (0/4) según el contrato de U02; se mantienen esos rechazos, **no se descartan como datos inválidos**. La acción QRL es una propuesta simulada; cambiarla no demuestra una recompensa mejor ni peor. Un tamaño de 4 es insuficiente para estimar causalidad general o probar IA general.

## Interferencia A→B→A y concurrencia SQLite real

- En ambos brazos se ejecutó una secuencia de tres misiones en una misma sesión U02. **No cambió** la salida A al ejecutarla nuevamente después de B. Hubo 3/3 recibos y siete bancos íntegros por brazo.
- Dos conexiones U02 escribieron en paralelo solicitudes diferentes en una **misma base SQLite-WAL descartable**. Se conservaron **2/2 tareas**, los recibos, la sincronización C1/U02 y el replay exacto sin incremento adicional de revisión, tanto en `frozen` como en C12 conjunto.
- Tiempo total observado de esas dos solicitudes concurrentes: **4.834,582 ms** frozen y **4.834,061 ms** conjunto. Es una prueba pequeña de corrección concurrente, **no una ganancia de throughput**.

## Integridad y decisión

| Restricción | Resultado |
|---|---|
| Checkpoints y fuentes históricas protegidas | **159/159 intactos** |
| Auditoría de regiones originales de pesos/ángulos XI | Identidad conservada durante inferencia |
| Checkpoints SQLite originales U02/C12 | No modificados |
| Nueva memoria autoritativa | 0 |
| Modelo C12 promovido | No (no mejora sobre frozen) |
| Caché C13 promovida | No (evidencia insuficiente y no estable) |
| APK nueva | 0 |
| PR fusionada automáticamente | No |

**C15 — Estrés y concurrencia** debe ampliar escenarios de fallos inyectados, volumen, carreras WAL, reinicios y transacciones sin eliminar trazabilidad. C14 dejó datos reproducibles para priorizar la latencia de XI en paquetes de transporte/no clasificados y la preparación anfitriona, sin atribuir falsamente tiempo exclusivo de CPU ni ventaja cuántica física.

[Panel C00–C17](../../docs/BBY_Q_U03_PANEL.md) · [Estado JSON](../../docs/BBY_Q_U03_ESTADO.json) · [Continuidad C15](../../docs/BBY_Q_U03_SIGUIENTE.md).
