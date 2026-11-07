# BBY Q U03 C08 — Aprendizaje activo XI con verificación previa (sin APK)

**Base:** C07 / PR #93 (`fb1e29ede885aafc34f2a801752e19664770f96c`).
Esta fase trabaja directamente en GitHub sobre una rama experimental y
conserva todas las identidades y checkpoints RVPC2 anteriores.

## Motivo concreto

La reserva CHALLENGE de C07 mostró **12 abstenciones injustificadas**
con evidencias sintéticas pertinentes acompañadas de distractores.
C08 no accede a las etiquetas de esa reserva ni retoca el código de
clasificación original para corregir esos casos a mano.

En su lugar:
1. El XI C07 original observa **360 candidatos sin etiquetas**.
2. Un selector elige **96** según sus scores nativos, incertidumbre,
   procedencia y discrepancias potenciales ante distractores.
3. Se generan preguntas de aclaración explícitas para cada candidato,
   incluyendo por qué se requiere evidencia o qué conflicto hay.
4. Solo los casos seleccionados son sometidos a un **verificador
   sintético independiente**; él confirma una etiqueta con un recibo
   de hash ligado al caso. Ninguna etiqueta de candidato está disponible
   antes de la selección.
5. Se hacen actualizaciones de pesos **con `c07_train`
   dentro de XI**, sobre un **nuevo checkpoint RVPC2**.
6. Un modelo de control recibe igual cantidad de etiquetas verificadas
   y operaciones nativas, pero los 96 casos se eligen aleatoriamente.
7. Una **validación nueva de 135 casos** escoge número de actualizaciones,
   temperatura, umbral y elegibilidad de promoción.
8. Una **prueba nueva de 180 casos** se abre solo después de congelar
   todas las decisiones, para comparar C07 original, C08 activo y control
   aleatorio. No se copian ni se usan las respuestas CHALLENGE de C07.

Los tres conjuntos tienen **sujetos, nombres, fuentes y UIDs disjuntos**.
La prueba reservada contiene distractores frescos y fuentes sintéticas,
no información personal ni noticias reales.

## Seguridad de etiquetas y fuentes

- La «verificación» de C08 consiste en un **oráculo sintético del entorno
  declarado** (fuentes en lista de control, fecha, bandera de atestación y
  SHA-256 de contenido). **No es una firma digital**, no contacta
  instituciones reales y no acredita veracidad sobre el mundo.
- Las preguntas generadas quedan en estado `pending-verification`;
  no envían mensajes ni se incorporan a la memoria personal.
- El modelo solo se actualiza después de una confirmación explícita de
  ese verificador sintético; los casos verdaderamente desconocidos
  continuarían pendientes en una implementación real.
- No debe interpretarse el score de clase calibrado como probabilidad de
  verdad de la afirmación; la calibración se evalúa dentro de esta tarea.
- El componente de seguridad de C07 sigue impidiendo respuestas sin
  evidencia admitida y señalando contradicciones. Estas restricciones
  **son reglas independientes de la red XI**, no méritos atribuibles al
  aprendizaje.
- El test CHALLENGE de C07 queda completamente fuera del entrenamiento
  C08. La nueva reserva C08 se genera después de elegir todos los modelos.

## Experimentos y costes

Las tres variantes:
- **C07 congelado:** cero actualizaciones, como referencia.
- **C08 activo:** 96 consultas adquiridas sin etiqueta, posteriormente
  verificadas; hasta 192 actualizaciones nativas en dos rondas.
- **C08 aleatorio:** misma reserva de adquisición y presupuesto;
  hasta 192 actualizaciones, mismas fuentes y política de verificación.

El presupuesto de adquisición prioriza escenarios con evidencia
pertinente y distractores, pero preserva exploración de casos
insuficientes y contradictorios. La validación compara la **cobertura
justificada** y penaliza respuestas inseguras, conflictos omitidos y
abstenciones injustificadas.

Solo se elige C08 para una **candidatura experimental de promoción**
si la validación mejora cobertura o disminuye rechazos excesivos,
sin degradar la seguridad frente a C07 congelado. No se promociona
automáticamente al clasificador de intención C1 ni a Android.

Se publican por variante: exactitud/F1 nativos, Brier, ECE,
cobertura selectiva, respuestas sin respaldo, abstenciones
injustificadas, conflictos omitidos, selección de ronda y el
checksum SHA-256. No se ocultan los fallos ni se promete mejora
hasta medir la prueba final.

## Integración con la entidad

`ActiveMetaSession` hereda `MetaSession`
y permite inspeccionar un clasificador XI actualizado junto a la
salida de C07, **sin sustituir respuestas C1, feedback, memoria
QMemory, registros SQLite ni snapshots de usuario**.
Rechaza un modelo o manifiesto cuyo SHA no coincida, conservando
el proceso anterior sin reentrenamiento silencioso.

## Reproducción

    bash deps/reverse-pc/scripts/build-xi-session.sh deps/mundo-x deps/reverse-pc/build
    python3 -m unittest integration.active_u03_c08.test_active -v
    python3 -m integration.semantic_u03_c06.train --epochs 6 --out build/c06/training-report.json
    python3 -m integration.metacognition_u03_c07.train --epochs 8 --out build/c07/training-report.json
    python3 -m integration.active_u03_c08.learner --out build/c08/active-report.json
    python3 -m integration.active_u03_c08.verify_integration

La CI host Linux: `.github/workflows/bbyq-u03-c08-active.yml`.
Verifica C1/U02, migración, readout original, calibración C07,
frozen SHA-256 de **159 archivos**, replay, rollback, las tres
variantes nativas y nueva reserva independiente.

## Límites

**C08 no construye una IA general ni un modelo que se autocorrija sin
supervisión.** Aprende una decisión de tres clases a partir de
características preparadas por el validador sintético C07.

La aplicación real requerirá un verificador de procedencia externo,
consentimiento y trazabilidad para admitir etiquetas humanas.
La retención de fuentes, manipulación de respuestas y falsificación
de pruebas son asuntos abiertos de arquitectura.

**Sin APK, sin cambios al runtime XI/Ether original ni a los checkpoints
anteriores. El modelo nuevo solo existe en la rama y artefactos CI.**
