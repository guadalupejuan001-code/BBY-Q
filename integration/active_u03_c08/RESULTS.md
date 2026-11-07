# BBY Q U03 C08 — Auditoría de aprendizaje activo y resultados (sin APK)

**PR:** [#94](https://github.com/guadalupejuan001-code/BBY-Q/pull/94)  
**CI verificada, último commit de código:** [GitHub Actions #42389307671](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42389307671)  
**Evidencia íntegra:** [artefacto JSON + RVPC2 nativo](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42389307671/artifacts/13580822851)

## Decisión de salida

**La ingeniería de adquisición, verificación de etiquetas y entrenamiento
nativo está implementada y pasó todas sus pruebas, pero NO se demostró
aprendizaje nuevo ni ventaja de C08 sobre C07.** No se promociona
C08 a la ruta estable, no se cambia el modelo de respuestas y no se genera
APK. La rama permanece como prototipo de laboratorio opt-in.

El punto de partida C07 había mostrado **12 abstenciones injustificadas**
ante distractores en su reserva CHALLENGE. C08 no usó ninguna de esas
etiquetas para entrenar y no se ha demostrado que haya corregido
aquel fallo específico.

## Qué se ejecutó

1. **360** candidatos sin etiqueta, presentados al modelo C07 congelado
   para seleccionar casos por puntuación XI, incertidumbre y evidencia
   observada.
2. **96** casos adquiridos, con preguntas específicas de aclaración.
   Antes de revelar la etiqueta, el verificador sintético comprobó
   identidad de caso, hash de contenido, autoría declarada y coherencia
   de evidencia. No son firmas reales de emisores externos.
3. Entrenamiento **XI nativo** con `c07_train`
   sobre un checkpoint nuevo RVPC2. Igual presupuesto para el control
   aleatorio (96 casos confirmados y hasta dos rondas).
4. **135** casos de validación para seleccionar ronda, temperatura,
   umbral y elegibilidad de promoción. El test no participó.
5. **180** casos reservados después de la selección para comparar
   C07 congelado, C08 activo y C08 aleatorio.
6. Integración en modo observación con BBY Q, conservando respuestas,
   recibos, memoria, feedback, replay, rollback y los bancos originales.

## Dos pruebas independientes sin mejora demostrada

### Primera reserva C08

La [CI piloto #42388230030](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42388230030)
dio **180/180** en C07, C08 activo y C08 aleatorio.
Los tres modelos empataron. El resultado **no se presentó como una mejora**,
y C08 no fue promovido.

### Nueva reserva de estrés v2

Se declaró una familia distinta, con fuentes y sujetos nuevos,
`C08-dual-irrelevant-signed-stress-v2`. Cada consulta
incluye dos registros **firmados sintéticamente y pertinentes para otras
entidades/propiedades**, que no deben contar como evidencia de la
pregunta. La nueva prueba se abrió una vez y después de elegir todos
los parámetros en validación.

| Modelo | Validación 135 | Test v2 180 | Respuestas respaldadas | Abstenciones injustificadas | Riesgo entre respuestas |
|---|---:|---:|---:|---:|---:|
| C07 congelado | 135/135 | **180/180** | 60 | 0 | 0 observado |
| C08 adquisición activa | 135/135 | **180/180** | 60 | 0 | 0 observado |
| C08 adquisición aleatoria | 135/135 | **180/180** | 60 | 0 | 0 observado |

Los tres alcanzaron **Brier multiclase 0,000142** y **ECE 0,002657**
sobre este nuevo conjunto, con idéntica predicción nativa y la misma
matriz de confusión: diagonal de 60/60 por clase. Es una tarea
sintética saturada y **NO** evidencia de mejora debida a C08, de
calibración general ni de veracidad del mundo real.

**Nota de precisión:** las cero respuestas sin respaldo también dependen
de la salvaguarda explícita del sistema C07; no representan únicamente
capacidad aprendida por XI.

## Prueba obligatoria de modificación real de pesos

Se inspeccionaron **directamente los 30 coeficientes float64 del modelo
XI**, no solo el hash RVPC2 completo ni el contador de operaciones:

| Estado | Actualizaciones XI de la ronda elegida | Errores/correcciones de pesos XI | SHA-256 de coeficientes |
|---|---:|---:|---|
| C07 original | 0 | 0 | `7c3208e75dec782b6cca443160b2c654af0be8121f10d6d80dd989b979b7d058` |
| C08 activo | 96 | **0** | **idéntico a C07** |
| C08 aleatorio | 96 | **0** | **idéntico a C07** |

Se programaron hasta 192 llamadas XI de entrenamiento por candidato
(dos rondas), y la validación eligió la primera ronda para ambos.
Al no haber errores con los ejemplos seleccionados, el perceptrón
**no modificó ninguno de sus pesos**. El checksum del contenedor RVPC2
sí cambió debido a sus contadores de entrenamiento; **un checksum nuevo
NO demuestra aprendizaje nuevo**.

- SHA-256 del banco original C07:
  `fd0d68731996771adcfc1bf8bd2a6f634d96dcc042fdb87efbb97103b0e59ecb`.
- SHA-256 del banco candidato C08:
  `0bb44c4d3da0797934abf1fe51d76354ed54d7f470cb1897c5bae48c8c432448`.
- Ambos tienen coeficientes idénticos.
- La comparación incluye un control aleatorio con **idéntico
  presupuesto** de ejemplos confirmados.

**El modelo elegido es C07 congelado; C08 no se promocionó.**

## Integridad, pruebas y limitaciones

Las pruebas nativas, incluidas las verificaciones originales de C1/U02,
gradientes, migración, feedback y rollback, aprobaron. También aprobaron
la detección de etiquetas/hashes de profesor falsificados, fuentes
ajenas, preguntas pendientes de verificación, 3 inferencias de observación,
la reapertura de U02, y el rechazo de un checkpoint nuevo adulterado.

**159 fuentes y checkpoints protegidos permanecen intactos.
C06 y C07 son exactamente los mismos estados. Cero APK.**

Limitaciones verificadas:

- La verificación del profesor es **sintética**, con digest de
  contenido y emisores permitidos. No autentica personas ni confirma
  hechos reales.
- Las preguntas de aclaración son propuestas generadas; no se
  contactó a usuarios reales ni se incorporó su información a memoria.
- La adquisición selecciona por incertidumbre y señales de evidencia,
  pero **sin errores nativos que corregir**, no puede demostrar la
  superioridad frente al azar.
- Ni el primer test ni el test de estrés v2 se usaron para ajustar los
  pesos después de observarlos. Los dos resultados son empates.
- El fallo anterior de 12 abstenciones de C07 **permanece abierto**.
  No repetir aquel test como entrenamiento; diseñar después una
  distribución *genuinamente independiente* y desafiante, incluyendo
  incertidumbre de procedencia real, revisiones contradictorias,
  información parcial y fuentes con autenticación externa.
- Ningún resultado implica inteligencia general, ventaja cuántica,
  respuesta fiable a afirmaciones externas ni mejora de conversación
  de extremo a extremo.

## Resultado de ingeniería C08

El circuito operacional ya existe:
**detectar incertidumbre → seleccionar un ejemplo sin etiqueta →
formular pregunta → exigir confirmación → comprobar integridad del
recibo → actualizar en XI solo si existe un error → validar contra
la versión anterior → decidir si es seguro promocionar**.

La campaña actual demostró que el mecanismo puede ejecutarse sin
comprometer ningún checkpoint, pero no que mejore los pesos del modelo.
La decisión **correcta y probada** fue conservar C07 y documentar
ese resultado en lugar de presentar un progreso inexistente.
