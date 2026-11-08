# BBY Q U03 C12 — RESULTADOS NATIVOS XI

**Ciclo verificado:** [PR #98](https://github.com/guadalupejuan001-code/BBY-Q/pull/98), basada exactamente en C11 [PR #97](https://github.com/guadalupejuan001-code/BBY-Q/pull/97), commit `4bf3a7aebe3f18bb8b7616264362e2f612faba30`.  
**Ejecución:** [CI GitHub Actions #42441627503, aprobada](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42441627503).  
**Evidencia:** [Artefacto JSON, checkpoints sintéticos y panel](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42441627503/artifacts/13601539793).

## Decisión

Se verificó experimentalmente que seis regiones **nativas XI de pesos/ángulos** cambiaron durante dos ciclos de feedback supervisado. **No se demostró mejora de exactitud ni de calidad respecto del control U02 congelado**: 4/4 en validación y 6/6 en el test reservado para ambos. Se conserva la elección `frozen`; ningún candidato se promociona a producción.

La ejecución es del simulador **XI/Ether/REVERSE-PC en Linux**, no de hardware cuántico físico ni Android. Las tareas y las etiquetas son sintéticas y limitadas al contrato U02.

## Diseño predefinido e integridad

- Dos entrenamientos nuevos (`Olmo/Cauce Dorado` y `Bambu/Clave Boreal`), cuatro casos de validación y seis casos de prueba reservados; seis misiones de carga distintas. Ninguna semilla, nombre ni regla coincide con los de C11.
- Las evaluaciones abarcan las siete posiciones soportadas (0–6) y reglas explícitas de ambos valores 0/1. **El bit de regla pertenece a la petición del usuario**; la clase VQC se compara con una etiqueta generada por otra sesión nativa XI después de todas las predicciones.
- Un único snapshot U02 original común, copias SQLite descartables, control `frozen` y candidato `joint-verified`. La decisión de selección se cerró usando solo validación.
- **159 archivos de checkpoints/fuentes protegidos sin cambios**, 7 bancos U02 autenticados, C1 sincronizado y cero autoridades de memoria nuevas. Ningún APK ni fusión a `main`.

## Entrenamiento y auditoría de pesos reales

| Auditoría XI | Con feedback conjunto | Congelado |
|---|---|---|
| Feedback supervisado independiente | 2 tareas verificadas | 0 |
| Pesos VQC3 | Cambiaron | Sin cambios |
| Pesos QRL3 | Cambiaron | Sin cambios |
| Ángulos QMemory | Cambiaron | Sin cambios |
| Pesos Entity | Cambiaron | Sin cambios |
| Pesos QChat100 | Cambiaron | Sin cambios |
| Readout VQC/U02 | Cambió | Sin cambios |

El feedback original U02 informó dos actualizaciones del router C1 y dos tandas de 18 operaciones de entrenamiento de QChat. Los seis hashes independientes se tomaron sobre regiones nativas, no sobre contadores de la imagen RVPC2. No se atribuye un delta de pesos específico al lector C1 sin una medición separada.

## Exactitud y cooperación entre bloques

| Evaluación | U02 congelado | Conjunto XI entrenado |
|---|---:|---:|
| Validación: clase correcta | **4/4** | **4/4** |
| Validación: regla correcta y voz fiel | **4/4** | **4/4** |
| Test reservado: clase correcta | **6/6** | **6/6** |
| Test reservado: regla correcta y voz fiel | **6/6** | **6/6** |
| Test: trazas completas C1/QMemory/VQC/Entity/QRL/QChat | **6/6** | **6/6** |

Los seis motores aparecen efectivamente en las trazas de las diez evaluaciones normales por brazo. Esto demuestra ejecución coordinada en estos contratos, **no** inteligencia general, causalidad cuántica física ni ventaja predictiva.

## Capacidad e interferencia observadas

| Prueba en una sesión XI | U02 congelado | Conjunto XI |
|---|---:|---:|
| Carga de seis misiones nuevas: recibos exitosos | **6/6** | **6/6** |
| Carga: clases correctas frente a XI separado | 6/6 | 6/6 |
| Carga: QMemory recuperó la regla suministrada | 6/6 | 6/6 |
| Carga: sincronización C1/U02 | 6/6 | 6/6 |
| Carga: trazas de seis motores | 6/6 | 6/6 |
| A→B→A: recibos y sincronización | 3/3 | 3/3 |
| A inicial vs A después de B: cambios de salida | **Ninguno** | **Ninguno** |
| Deltas de parámetros nativos durante inferencia sin feedback | Ninguno | Ninguno |

La secuencia A→B→A conservó exactamente clase, regla, meta, acción simulada, soporte y fidelidad de voz bajo las condiciones probadas. La capacidad evaluada es **seis tareas en secuencia**, no un máximo de qubits ni de memoria.

## Ablaciones U02 (2 casos, solo candidato entrenado)

| Control | Clase correcta | Regla correcta | Voz fiel/terminada |
|---|---:|---:|---:|
| Normal | 2/2 | 2/2 | 2/2 |
| QMemory borrada | 2/2 | **1/2** | 2/2 |
| VQC ablacionado | 2/2 | 2/2 | 2/2 |
| QRL ablacionado | 2/2 | 2/2 | 2/2 |
| QChat/voz ablacionada | 2/2 | 2/2 | **0/2** |

La ablación QMemory alteró una regla, su meta y una acción; en estos dos casos, la ablación VQC no cambió la clase, y la de QRL no cambió la acción. Eso **no significa** que VQC o QRL sean prescindibles: no se evaluó una función de recompensa externa ni un número de muestras suficiente para concluir efectos causales generales.

## Coste medido en runner Linux

Mediana de tiempo de pared **por misión**, incluyendo copia SQLite, arranque de sesión XI y ejecución nativa:

| Prueba | Congelado | Entrenado |
|---|---:|---:|
| Validación | 2.349,475 ms | 2.412,226 ms |
| Test reservado | 2.172,798 ms | 2.204,079 ms |
| Carga secuencial (solo paso dentro de sesión) | 1.865,561 ms | 1.763,856 ms |
| Interferencia A→B→A (solo paso) | 1.663,613 ms | 1.714,277 ms |
| Entrenamiento dos tareas (total brazo) | 4.429,199 ms sin feedback | 10.161,257 ms con feedback |

Campaña completa de C12: **120.639,702 ms** en ese runner. Las variaciones por carga del host y el diferente ámbito de las mediciones impiden interpretar estos pocos valores como una ganancia de velocidad; no son métricas Android.

## Fallos y próximos criterios

No hubo fallo de CI en el commit de campaña evaluado, pero la muestra es pequeña, sintética y basada en un único generador de etiquetas de XI. No se comprobó interacción con el mundo, lenguaje libre ni ventaja cuántica sobre hardware o contra un modelo clásico equiparado.

**C13 (Optimización global)** debe perfilar dónde se gasta el tiempo, separar arranque/serialización de cálculo nativo, repetir mediciones con suficientes muestras y conservar el control `frozen`. No asumir mejora ni promocionar el candidato por el cambio de pesos. La rama queda en PR borrador, sin fusión ni APK.

[Panel C00–C17](../../docs/BBY_Q_U03_PANEL.md) · [Estado JSON](../../docs/BBY_Q_U03_ESTADO.json) · [Siguiente C13](../../docs/BBY_Q_U03_SIGUIENTE.md).
