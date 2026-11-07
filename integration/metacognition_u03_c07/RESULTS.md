# BBY Q U03 / C07 — Resultados auditados de metacognición

**Estado:** implementación opt-in en PR #93. No fusionar ni instalar todavía.
**Base:** C06 PR #92, `ab5433dacc7571ff706662ddb05682f50b99080a`.
**Herramientas:** REVERSE-PC XI/Ether y mundo-X fijados en las CI anteriores.

## Evidencia de dos campañas y por qué se hicieron ambas

**Primera campaña:** [GitHub Actions #42386081041](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42386081041),
[evidencia C07 inicial](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42386081041/artifacts/13579447589).

El modelo XI acertó las 180 clases de la primera prueba sintética, con
procedencia 180/180 (100 %), control sin procedencia 120/180 (66,7 %) y
sin contraste 168/180 (93,3 %). Sin embargo, su **ECE de 0,325**
indicó que los scores no estaban bien alineados con la frecuencia
empírica de acierto. **La exactitud no equivale a buena calibración.**

Para corregir ese problema se amplió la búsqueda de temperatura
`0,01...4,0` **usando solo los 135 casos de validación**.
Como los resultados del primer test ya se habían observado, no se
reutilizó aquel test para proclamar un nuevo récord. Se reservó una
partición **CHALLENGE** nueva, con otras 180 proposiciones, entidades,
fuentes y distractores autorizados pero no pertinentes.

**Segunda campaña:** [CI #42386450584 aprobada](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42386450584),
[artefacto de entrenamiento/calibración y RVPC2](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42386450584/artifacts/13579516959).

## Selección exclusivamente con validación

- 540 ejemplos para entrenar, 135 para validar la época,
  temperatura y umbral. El primer test de 180 queda como evidencia
  de auditoría anterior. CHALLENGE de 180 se abrió después de seleccionar
  todos los candidatos de la campaña nueva.
- Clases equilibradas: responder, pedir evidencia, reportar contradicción.
- Entrenamiento, inferencia y 3 scores de clase en **XI nativo**.
  No se leen etiquetas por el canal de inferencia.
- Épocas seleccionadas: completo 1, sin procedencia 5,
  sin contraste 5; temperaturas 0,01 / 0,25 / 0,18.
  Todos eligieron umbral selectivo 0,4 por validación.
- La regla de seguridad separada rechaza respuestas sin evidencia aceptada
  y contradicciones genuinas. Los resultados del modelo **antes** de
  esta regla se muestran por separado; atribuir a XI los rechazos
  de esa regla sería engañoso.

## Test CHALLENGE: 180 casos (60 por clase)

| Modelo nativo | Aciertos XI / 180 | Exactitud | F1 macro | Brier multiclase | ECE 10 bins |
|---|---:|---:|---:|---:|---:|
| C07: procedencia + contraste | **168** | **93,33 %** | 0,9327 | **0,0453** | **0,0391** |
| Sin comprobación de procedencia | 108 | 60,00 % | 0,5893 | 0,4767 | 0,1579 |
| Sin indicador directo de contraste | 132 | 73,33 % | 0,7222 | 0,1959 | 0,1778 |

La medición se basa en un modelo entrenado que encontró **12
abstenciones injustificadas** al añadir distractores al caso positivo.
No hubo respuestas inseguras en esta muestra con la regla fail-closed.
No se corrigieron esos doce errores usando el test CHALLENGE.

### Matriz de confusión XI C07 completo

Filas = etiqueta real, columnas = salida nativa XI.
Orden: **responder, pedir evidencia, reportar contradicción**.

| Etiqueta | Responder | Pedir evidencia | Conflicto |
|---|---:|---:|---:|
| Evidencia suficiente | 48 | **12** | 0 |
| Evidencia insuficiente | 0 | 60 | 0 |
| Contradicción | 0 | 0 | 60 |

Esto significa que C07 fue demasiado conservador en 12 de los 60
casos respondibles. Distingue todos los conflictos del conjunto
acotado, pero aún no sabe evitar abstenciones con demasiados
distractores. **No representa un sistema de verdad completo.**

### ¿Qué mejoró realmente en la calibración?

| Medición del modelo completo en CHALLENGE | Antes de temperatura | Después, calibrada en validación |
|---|---:|---:|
| ECE (menor es mejor) | 0,5035 | **0,0391** |
| Brier multiclase (menor es mejor) | 0,4945 | **0,0453** |
| Exactitud (no depende de temperatura) | 93,33 % | 93,33 % |

El sistema emite un **score de clase calibrado para este conjunto**,
no una probabilidad de verdad de una noticia, una afirmación humana
ni un acontecimiento físico. En fuera de distribución no existe
garantía de la misma calibración.

### Evaluación selectiva con regla de seguridad

| Modelo | Respuestas emitidas | Respuestas sin respaldo | Abstenciones injustificadas | Conflictos omitidos |
|---|---:|---:|---:|---:|
| Completo | 48/180 | 0 | 12 | 0 |
| Sin procedencia | 24/180 | 0 | 36 | 0 |
| Sin contraste | 48/180 | 0 | 0 | 0 |

**Advertencia:** los ceros en "respuestas sin respaldo" y "conflictos
omitidos" también reflejan la regla explícita que verifica evidencia
antes de permitir la respuesta, no solo los pesos aprendidos. Para
medir capacidad nativa usar la matriz de confusión de arriba.

## Integración real y checkpoint

- Modo de observación `MetaSession` junto a C06:
  no sustituye la respuesta de C1 y jamás escribe predicciones a
  la base SQLite. La API exige evidencia explícita.
- 4 escenarios desconocidos rechazados con petición de evidencia.
  Contradicciones, hechos sintéticos respaldados y evidencia ausente
  probados; replay, feedback, rollback y reapertura U02 aprobados.
- Checkpoint C07 nativo independiente: **12.210 bytes RVPC2**,
  SHA-256:
  `fd0d68731996771adcfc1bf8bd2a6f634d96dcc042fdb87efbb97103b0e59ecb`.
- El checkpoint C06 y sus pesos siguen íntegros, igual que los
  **159 archivos originales protegidos**.
- **Cero APK**. No se modificaron la lógica nativa original,
  el simulador REVERSE-PC ni sus límites.

## Límites verificables y siguientes tareas

1. La "procedencia" es una **simulación de fuente atestada + digest
   de contenido**, no firma digital ni prueba de veracidad real.
2. Los casos parten de un mismo generador de evidencias con tres
   atributos, etiquetas binarias, una política de caducidad y nombres
   nuevos. El reto CHALLENGE añade información irrelevante, pero
   NO representa conversaciones espontáneas ni fuentes reales.
3. Los pesos aprenden a combinar **características preparadas** por
   un verificador de procedencia. No aprenden solos qué es una
   fuente fidedigna del mundo real.
4. La cobertura segura fue 48/60 casos respondibles, no 60/60.
   Los 12 rechazos excesivos son un objetivo específico de C08.
5. La calibración y la seguridad de CHALLENGE no son extrapolables
   a decisiones financieras, médicas ni otro dominio de alto riesgo.
6. No se demostró ventaja cuántica: se utilizó un programa de
   clasificación supervisado **ejecutado en XI**, no un circuito
   arbitrario de 1.000 cúbits ni hardware cuántico.
7. La integración sigue siendo opt-in y de **solo observación**;
   no hay mejora prometida del rendimiento conversacional global.

**Conclusión de C07:** aprendizaje epistemológico y calibración medidos,
reducción clara frente a ablaciones, doce abstenciones injustificadas
identificadas y preservación total del sistema anterior.
C08 puede abordar específicamente la adquisición activa de evidencia
y reducir las abstenciones sin introducir afirmaciones sin respaldo.
