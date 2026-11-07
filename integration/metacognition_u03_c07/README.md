# BBY Q U03 — C07: Metacognición y calibración de evidencia (experimental)

**Base:** C06 PR #92, commit `ab5433dacc7571ff706662ddb05682f50b99080a`.
**Sin APK, sin modificar C1 ni los 159 archivos protegidos, sin reemplazar modelos.**

## Objetivo medible

C07 entrena en el **intérprete XI nativo** una cabeza epistemológica que aprende
una de tres decisiones en una tarea experimental de evidencia **explícita**:

- **Responder (`answer`)** cuando existe evidencia coherente y suficiente.
- **Pedir evidencia (`ask_for_evidence`)** cuando falta, está vencida o no tiene procedencia suficiente.
- **Señalar contradicción (`report_conflict`)** cuando dos fuentes válidas y pertinentes se contradicen.

No se considera verdadera una afirmación solamente porque BBY Q la pronuncie.
C07 utiliza proposiciones tipadas **suministradas** como contexto del experimento,
no comprueba la verdad de páginas web, documentos reales ni el mundo físico.

## Qué es aprendido y qué es un control explícito

`ai/xi/c07/epistemic-head.xi` implementa una cabeza de tres clases
y diez características con actualización supervisada tipo perceptrón **en XI**.
Solo las operaciones `c07_train` reciben etiquetas.
La predicción nativa entrega la clase y tres scores `float64`, que
se materializan con el protocolo RVPC2 original.

`features.py` lee observaciones, su procedencia registrada,
fecha y hash de contenido, y computa cantidades de evidencia positiva,
negativa, ausente y contradictoria. **No** lee la etiqueta de entrenamiento.

**Importante:** la comprobación de procedencia es sintética: un registro
de emisores permitidos, bandera de atestación y hash SHA-256 de contenido.
Eso NO es una firma digital real del emisor ni garantiza veracidad.

`guarded_action` aplica una envoltura de seguridad declarada:
ninguna inferencia puede convertirse en respuesta afirmativa cuando no hay
evidencia aceptada, y dos fuentes válidas contrapuestas no se reducen a una
afirmación única. Esta envoltura **no es aprendizaje ni capacidad XI**.
Los resultados muestran por separado la exactitud del modelo XI y la
conducta después de aplicar esa regla.

## Diseño experimental y anticontaminación

- **540** ejemplos de entrenamiento, **135** de validación y **180** de
  prueba reservada, balanceados entre las tres clases.
- Entidades y procedencias completamente disjuntas entre particiones.
- Etiquetas generadas por situaciones declaradas de forma independiente
  del vector de características y comprobadas por un oráculo de referencia.
- Misma cabeza nativa, número de pesos y presupuesto para tres variantes:
  modelo completo, sin información de procedencia y sin indicador directo
  de contraste. El entrenamiento sigue siendo completamente nativo XI.
- La **validación** elige época, temperatura de softmax y umbral de
  confianza de respuestas; la prueba reservada se abre **después** de todas
  las elecciones. Ningún gradiente usa datos de test.
- Se informan precisión, F1 macro, matriz de confusión, NLL, Brier
  multiclase, ECE de 10 intervalos, cobertura, respuestas inseguras,
  abstenciones injustificadas y conflictos ignorados.
- La confianza calibrada mide la **probabilidad empírica de que el
  clasificador acierte la clase en esta tarea sintética**, no la probabilidad
  de verdad de una afirmación sobre el mundo.
- Casos fuera de dominio (predicado desconocido, evidencia de fuente
  desconocida, evidencia falsificada) deben solicitar prueba adicional.

## Conexión con BBY Q unificado: modo observación

`MetaSession` hereda la sesión de observación C06, carga
el nuevo checkpoint C07 y ofrece `assess_evidence(query, evidence)`.
Esa evaluación produce una recomendación, los scores calibrados y los motivos
de procedencia, pero NO cambia rutas de C1, voz QChat100, memoria QMemory,
feedback, SQLite ni los checkpoints anteriores.

Si falla una inferencia opcional C06/C07, nunca se sustituye un turno
ya confirmado por un falso error de entrenamiento. La identidad SHA-256 de
ambos checkpoints nuevos se comprueba antes de cargar. Un modelo corrompido
se rechaza.

## Reproducción

GitHub Actions:
`.github/workflows/bbyq-u03-c07-metacognition.yml`

Revisiones fijadas de REVERSE-PC y mundo-X de C00–C06:

    bash deps/reverse-pc/scripts/build-xi-session.sh deps/mundo-x deps/reverse-pc/build
    python3 -m unittest integration.metacognition_u03_c07.test_metacognition -v
    python3 -m integration.semantic_u03_c06.train --epochs 6 --out build/c06/training-report.json
    python3 -m integration.metacognition_u03_c07.train --epochs 8 --out build/c07/training-report.json
    python3 -m integration.metacognition_u03_c07.verify_integration

La CI comprueba los 159 hashes de fuentes y checkpoints, regresión C1/U02,
reapertura RVPC2 de los modelos nuevos, rollback, replay y que no se compila
Android. Los datos, estadísticas, pesos de C07 y modelos se publican solo
como artefacto CI de laboratorio.

## Limitaciones y criterios de aceptación

**No se debe declarar C07 general** por obtener alta precisión dentro de
este dominio sintético. Aprender a distinguir fuentes declaradas y ausencia
de evidencia no implica veracidad de información externa, metacognición
abierta, comprensión de contradicciones complejas ni calibración fuera
de distribución.

El contraste debe medirse también frente a ablaciones. Si el modelo
completo no supera los controles, reportarlo y conservar como experimento,
sin inventar una ganancia.

Solo se considerará C07 terminado cuando:
- la CI demuestre entrenamiento/aprendizaje XI real y reapertura,
- publique NLL, ECE, Brier y abstenciones,
- pase 4 casos fuera de distribución sin respuestas inventadas,
- preserve todos los checkpoints anteriores y las respuestas U02,
- y siga sin APK ni integración automática en `main`.

**C08:** utilizar la incertidumbre para generar preguntas de aclaración
específicas y aprender a partir de respuestas confirmadas, sin incorporar
automáticamente datos no verificados.
