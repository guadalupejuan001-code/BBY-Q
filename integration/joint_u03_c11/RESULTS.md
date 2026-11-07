# BBY Q U03 C11 — Aprendizaje conjunto: resultados nativos y ablaciones

**Estado:** implementación experimental con entrenamiento XI comprobado; ninguna mejora de exactitud demostrada ni promoción.  
**PR:** [#97](https://github.com/guadalupejuan001-code/BBY-Q/pull/97), basada en C10 PR #96, commit `147cfe804d413110400a7da528d286529f749fa9`.

**CI de código y experimento aprobada:** [GitHub Actions #42401341401](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42401341401).  
[Evidencia JSON y candidato SQLite sintético](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42401341401/artifacts/13585940761).

## Qué es realmente nuevo en C11

El programa U02 **ya ejecutaba el feedback conjunto**: Entity, VQC3, QRL3, QMemory, QChat100 y el lector C1 se actualizan mediante XI y SQLite en una sola transacción. C11 no los ha inventado ni sustituido.

Se añadió un procedimiento reproducible para partir de **un checkpoint U02 común**, comparar tres protocolos de supervisión, auditar regiones reales de parámetros en las imágenes RVPC2 y probar ablaciones nativas en copias independientes. No modifica la memoria personal original.

## Diferencia comprobada entre entrenamiento y cambio de pesos

La actualización conjunta se ejecutó con una tarea sintética cuyos datos de clase y regla se verifican **en la rama de feedback nativo**. La confirmación en la CI muestra:

| Región nativa medida directamente | Feedback conjunto | Solo resultado escalar | Sin entrenamiento |
|---|---|---|---|
| Pesos VQC3 | **Modificados** | Sin cambios | Sin cambios |
| Pesos QRL3 | **Modificados** | Sin cambios | Sin cambios |
| Ángulos QMemory | **Modificados** | Sin cambios | Sin cambios |
| Pesos Entity/E02 | **Modificados** | **Modificados** | Sin cambios |
| Pesos QChat100 | **Modificados** | **Modificados** | Sin cambios |
| Readout VQC/U02 | **Modificado** | Sin cambios | Sin cambios |
| Lector C1 | Banco y contador de entrenamiento modificados | Banco y contador modificados | Sin cambios |

**Precisión:** los seis primeros checksums proceden de regiones de pesos/ángulos consultadas por XI, excluyendo contadores. El lector C1 está verificado como banco y llamada `c1_train`, pero su delta de peso exacto no se mide aquí por separado; no se debe afirmar lo contrario.

El feedback conjunto original comunicó una actualización Entity, VQC, QRL, QMemory, readout y lector, y **18 operaciones de entrenamiento QChat**. Las identidades nativas antes/después del feedback también divergieron. Así se prueba ejecución y modificación real, no necesariamente una mejora predictiva.

### Corrección necesaria descubierta en la primera campaña

U02 recupera una etiqueta de clase/regla de una tarea sintética incluso cuando el comando solo dice «evalúa la última tarea con resultado 1». Por tanto, el primer comparador de resultado escalar **no era una ablación válida** y la CI lo rechazó.

Se corrigió suprimiendo el vínculo **solo en la tabla de supervisión de la copia experimental escalar**, sin alterar la tarea original ni el código U02 congelado. La nueva prueba verificó que VQC, QRL y QMemory no reciben entrenamiento supervisado en ese control, mientras Entity y voz sí pueden actualizarse. La misma fuente U02 se usa en todas las condiciones.

## Evaluación independiente

Un ejemplo compuesto de entrenamiento: «guarda la regla Faro Azul con valor 1 observa Nara con muestra 88113 y resuelve desde 3». Los nombres y las semillas de validación y test son distintos y no se usan para actualizar pesos.

| Condición | Validación: clase y misión soportada/fiel | Test reservado: clase y misión soportada/fiel |
|---|---:|---:|
| **Conjunto, etiquetas verificadas** | **3/3** | **4/4** |
| Solo resultado escalar, sin clase/regla | 3/3 | 4/4 |
| U02 congelado, sin feedback | 3/3 | 4/4 |

Los resultados U02 se obtienen con sus contratos originales; la etiqueta de clase sintética se calcula **en una sesión XI separada solo después** de producir todas las predicciones. La tasa de acierto de clase fue del **100 % en los tres brazos** sobre un conjunto muy pequeño: dos clases positivas de cuatro en test, no hay sesgo total a una sola clase.

**Decisión de promoción:** `frozen` (sin entrenamiento nuevo). Aunque los pesos de los motores cambiaron con feedback verificado, **no se demostró mejora sobre el checkpoint original**. No se ha activado C11 como modelo de producción.

## Ablaciones de inferencia con el candidato conjunto (dos pruebas inéditas)

Se probaron las mismas dos misiones con cinco controles *del U02 original*, cada vez sobre un checkpoint descartable:

| Condición | Clase correcta | Asociación de memoria correcta | Voz fiel/terminada |
|---|---:|---:|---:|
| Misión normal | 2/2 | 2/2 | 2/2 |
| **QMemory borrada** | 2/2 | **0/2** | 2/2 |
| **VQC ablacionada** | **1/2** | 2/2 | 2/2 |
| **QRL ablacionado** | 2/2 | 2/2 | 2/2 |
| **QChat ablacionado** | 2/2 | 2/2 | **0/2** |

La ablación QRL alteró la acción sugerida en una de las dos misiones, sin permitir atribuir automáticamente una recompensa mejor/peor, porque no se evaluó una política de entorno independiente. La voz sin entrenamiento o ablacionada no debe confundirse con clasificación incorrecta: aquí sus fallos de fidelidad aparecen en una métrica separada.

**Limitación:** dos casos permiten mostrar la dependencia funcional de los componentes, pero no estimar con precisión un efecto estadístico ni una ventaja cuántica.

## Integridad y decisiones de ingeniería

| Garantía | Resultado |
|---|---|
| Checkpoint U02 inicial común para los tres brazos | Verificado |
| Etiqueta sintética fuera de inferencia | Verificado |
| Fallo inducido durante feedback | Rollback íntegro |
| Repetición de solicitud original | Sin doble entrenamiento |
| Feedback duplicado | Rechazado |
| 159 fuentes/checkpoints protegidos | **Intactos** |
| Otros proyectos/memoria personal | Sin cambios |
| Nuevas autoridades de memoria | **0** |
| APK generada | **0** |

Se guarda únicamente un **candidato sintético de laboratorio** `build/c11/joint-candidate.sqlite` y su informe. No sustituye el SQLite personal ni las imágenes congeladas anteriores.

## Alcance pendiente para C12

La ruta de aprendizaje XI sí se ejecuta de manera conjunta y sus pesos son reales dentro del simulador, pero el conjunto original ya resolvía todos los casos del test. Para demostrar una mejora de inteligencia se necesitan nuevos escenarios **independientes, más difíciles y predefinidos**, controles de igual presupuesto, más ejemplos de entrenamiento y evaluación multietapa, sin reusar las etiquetas de esta reserva.

El modelo todavía no constituye inteligencia general, verificación de hechos reales, ventaja cuántica física ni capacidad de tomar decisiones externas autónomas. **No fusionar la PR ni crear APK**.

[Panel permanente C00–C17](../../docs/BBY_Q_U03_PANEL.md) · [Estado JSON](../../docs/BBY_Q_U03_ESTADO.json) · [Continuidad C12](../../docs/BBY_Q_U03_SIGUIENTE.md).
