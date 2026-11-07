# BBY Q U03 C06 — Entrenamiento semántico nativo y ablaciones

## Evidencia inicial verificada (7 de noviembre de 2026)

- **PR:** [#92](https://github.com/guadalupejuan001-code/BBY-Q/pull/92)
- **Primera CI de entrenamiento aprobada:** [GitHub Actions #42382592751](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42382592751)
- **Datos completos y checkpoint original elegido:** [BBYQ-U03-C06-native-semantic-evidence](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42382592751/artifacts/13578541139)
- **Revisión de integración posterior:** CI adicional en la PR #92, sin cambiar el experimento de entrenamiento.

La cabeza de tres clases se entrenó realmente en el intérprete nativo XI,
con 24 parámetros `float64`, algoritmo perceptrón
multiclase, mini-lotes y etiquetas accesibles **solo** por la función
`c06_train`. La predicción `c06_predict`
recibe ocho características y no recibe ni lee una etiqueta.

El código Python genera fuentes e inputs y evalúa errores, pero no actualiza
los pesos matemáticos. Se eligió la época usando únicamente validación y
se reabrió el estado nativo seleccionado desde RVPC2 antes de probarlo.

## Particiones verificadas

| Conjunto | Ejemplos | Plantillas | Uso |
|---|---:|---:|---|
| Entrenamiento | 360 | 18 | Actualizar pesos XI |
| Validación | 90 | 9 | Elegir época |
| Prueba reservada | 120 | 9 | Solo evaluar modelo elegido |

No hay plantillas, nombres de entidad ni frases duplicadas entre los tres
conjuntos. El generador conserva SHA-256 para cada partición en el JSON
descargable y garantiza 1/3 de ejemplos por clase.

## Validación del aprendizaje y test reservado

| Modelo XI | Época elegida (solo validación) | Validación | Test reservado | Macro-F1 test |
|---|---:|---:|---:|---:|
| C05 con orden de negación/acción | 1 | 90/90 (100 %) | **120/120 (100 %)** | 1,0000 |
| C05 sin relaciones de orden | 4 | 60/90 (66,7 %) | 81/120 (67,5 %) | 0,6662 |
| Características de superficie | 1 | 70/90 (77,8 %) | 93/120 (77,5 %) | 0,7461 |

### Matrices de confusión del test

Filas = etiquetas reales; columnas = respuestas XI del modelo.
Clases, en orden: **prohibir la acción**, **ejecutar excluyendo tema**,
**solicitud afirmativa**.

| Modelo | Real: prohibición | Real: exclusión | Real: afirmación |
|---|---|---|---|
| C05 con orden | [40, 0, 0] | [0, 40, 0] | [0, 0, 40] |
| Sin orden | [14, 26, 0] | [13, 27, 0] | [0, 0, 40] |
| Superficie | [13, 27, 0] | [0, 40, 0] | [0, 0, 40] |

**Interpretación válida:** dentro de esta gramática y estas plantillas,
conservar la relación entre una negación y la posición de la acción
aporta información predictiva que desaparece en los dos controles.
El test se abrió una sola vez tras la selección; no se tunearon los
parámetros a partir del resultado.

La cabeza C06 no es el generador conversacional de C1. La precisión en una
clasificación de tres clases no demuestra comprensión general, capacidad de
inferencia abierta, transferencia fuera de esta gramática ni AGI.

## Checkpoint entrenado y preservación

- Formato: **RVPC2 nativo**, ejecutado y guardado por REVERSE-PC XI.
- Imagen nueva: `build/c06/semantic-trained.rvp`
  (**9.104 bytes**).
- SHA-256 del checkpoint:
  `ed0f0067e43fcab74ba81c574bca983d8a497322ae5d7e8218f7a2941aa53018`.
- Verificación independiente: el SHA-256 del archivo comprimido en el
  artefacto coincide con el manifiesto de entrenamiento.
- **159 fuentes y checkpoints protegidos anteriores intactos**.
- Ninguna APK generada, ninguna modificación de la rama `main`.
- Cabeza nueva optativa: la clasificación original C1, sus entrenamientos y
  la memoria personal siguen siendo la autoridad.

## Restricciones y limitaciones

1. **Extracción de características parcialmente simbólica:** C05 aplica
   reglas de spans para posiciones de verbos y negaciones. El modelo XI
   aprende a combinar estas características; no aprende automáticamente
   la gramática de extracción ni lemas desconocidos.
2. **Separación de etiquetas:** C06 no usa los campos
   `polarity` ni `negation.kind` de C05,
   ni introduce etiquetas humanas en la inferencia; sí utiliza sus
   posiciones ancladas al texto original.
3. **Ablaciones acotadas:** los controles retiran el orden; no son una
   comparación con modelos de lenguaje grandes de igual presupuesto
   ni cuantifican el rendimiento conversacional completo.
4. **Datos sintéticos:** 120/120 refleja estas 9 plantillas reservadas,
   no conversaciones reales; los resultados deben comprobarse después
   en datos humanos variados, negación de varias cláusulas y coreferencia.
5. **Modelo independiente:** la integración en una sesión unificada,
   aun en modo sombra, no equivale a sustituir rutas aprendidas. La
   activación autorizada requeriría una campaña end-to-end de decisiones.
6. **Sin ventaja cuántica demostrada:** esta cabeza es un algoritmo
   supervisado ejecutado por XI sobre el simulador propio, pero
   no un circuito nuevo de 1.000 cúbits ni una computadora cuántica física.

**Decisión:** conservar este checkpoint como candidato nativo separado,
con interfaces explícitas y posibilidad de reversión. No modificar los
modelos congelados ni generar APK hasta las fases posteriores.


## Integración de observación comprobada

La [segunda CI completa #42383154492](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42383154492)
volvió a entrenar el candidato seleccionado y comprobó la integración real
con `ShadowSemanticSession`, sin modificar rutas ni pesos antiguos.

- **7/7** predicciones de la cabeza XI en sesiones U03 reales, solo en
  modo observación.
- Los mismos resultados U02, recibos, checkpoint, historial, feedback,
  replay y rollback que el original.
- Se rechazó el intento de abrir un checkpoint nuevo con SHA-256 alterado.
- El nuevo checkpoint RVPC2 conservó el mismo hash antes/después de ejecutar
  las predicciones: la cabeza no se entrenó en producción.
- **159** archivos protegidos intactos, **cero APK** y sin instalación Android.
- La cabeza todavía **no decide** qué respuesta recibe el usuario ni reemplaza
  al clasificador de intención C1.

[Evidencia y checkpoint RVPC2 de la CI final](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42383154492/artifacts/13578676074).
