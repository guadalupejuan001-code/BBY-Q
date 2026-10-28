# E029 — hechos de conversación natural en XI

## Problema observado

E028 recupera, identifica entidades y compone dos relaciones a partir de fragmentos E027, pero el usuario tenía que escribir un comando especial `@ctx add`. En conversaciones normales, una frase como `El motor solar requiere energía.` no se admitía al archivo contextual. El PR #33, que reúne la composición E026 con E027, sigue su ciclo autónomo independiente; este cambio no sustituye ni altera ese trabajo.

## Incremento E029

El código `ai/releases/e029/natural-intake.xi` detecta **afirmaciones explícitas y simples** en texto conversacional, y las transmite al archivo E027 sin que el usuario tenga que conocer comandos. Se ejecuta **antes de E028**; una pregunta o frase fuera del subconjunto seguro sigue su ruta original a E028 y E025.

Mensajes de ejemplo:

```text
El motor solar es dispositivo.
El motor solar requiere energía.
¿Qué es motor solar y qué requiere?
```

El agente responde a las dos primeras frases «Registré esa afirmación.» y a la última con una composición apoyada en fragmentos del archivo (por ejemplo, `motor solar es dispositivo [#000]. motor solar requiere energía [#001].`). La formulación reconoce que **el usuario lo afirmó**, no que se haya verificado externamente.

### Formas soportadas

- Afirmación ES/EN: `ENTIDAD es VALOR`, `ENTIDAD requiere VALOR`, `ENTIDAD necesita VALOR`, `ENTITY is VALUE`, `ENTITY needs VALUE`, `ENTITY requires VALUE`.
- Negaciones sencillas: `no es`, `no requiere`, `no necesita`, `is not`, `does not need`, `does not require`, para que E028 se abstenga conservadoramente cuando haya evidencia negativa.
- Presentación conversacional: `recuerda que ...`, `te cuento que ...`, `remember that ...`, `please remember that ...`.
- Entidades con varias palabras y artículo inicial `el`, `la`, `the`. El registro normaliza solo mayúsculas ASCII; conserva bytes UTF-8.
- Un punto final es opcional. Máximo 48 bytes de entidad, 80 bytes de valor y 224 bytes de afirmación; el límite general de entrada sigue siendo 255 bytes.

### Exclusiones importantes

No se admite automáticamente una pregunta, una orden original `aprende que`, contenido incierto introducido por `creo que`, `quizás`, `tal vez`, `maybe`, `i think`, `parece que`, etc., ni texto con varias cláusulas unidas por `y` / `and`, puntuación ambigua o una sintaxis desconocida. El texto rechazado **no se archiva automáticamente**. No equivale a entender prosa libre, tomar notas de párrafos ni detectar la veracidad de una afirmación. Estos son filtros conservadores, no una solución definitiva contra todas las instrucciones adversarias.

La entrada afirmativa pasa a los métodos de archivo persistente E027. XI reescribe una copia lógica de la entrada como `@ctx add ...` y reutiliza los mismos controles de capacidad, persistencia, limpieza y fallo transaccional. El proceso anfitrión no extrae entidades ni genera ninguna respuesta.

## Composición y fuentes

E029 usa un único ejecutable XI encadenado:
`E029 natural-intake -> E028 question engine -> E027 archive -> E025 original`.

La semilla RVPC2 E025 y sus registros no se reemplazan; los hechos aprendidos antes siguen disponibles. Cada fuente archivada continúa con su ID `[#NNN]`, y la ruta E028 permite respuestas breves, preguntas dobles, seguimiento del sujeto y abstención por conflictos dentro de las formas reconocidas. Un `@ctx clear` borra el archivo sin eliminar el conocimiento E025.

El módulo E026 de composición factual tiene su propio PR y pruebas. Esta modificación no afirma haberlo fusionado. Los dos caminos necesitan reconciliar prioridad y evidencia antes de desplegarse en Android.

## Reproducción y criterio de promoción

```sh
node ai/releases/e027/build.mjs /ruta/reverse_pc evidence/e027-original
node ai/releases/e029/build.mjs /ruta/reverse_pc evidence/e029
node ai/releases/e029/test.mjs /ruta/reverse_pc evidence/e029 evidence/e029-test
```

La CI `.github/workflows/bbyq-e029.yml` compila el runtime de REVERSE-PC fijado y ejecuta: E025 (31 controles), W4u (21), admisión natural de afirmaciones en ES/EN, ausencia de ingesta silenciosa de preguntas/dudas, negación y contradicción, 24 entidades diferentes, recuperación después de muchas notas, examen E028 completo y regresiones E027. La enseñanza y el examen se mantienen en estados desechables; los ejemplos no se publican como conocimiento de BBY-Q.

**Condición de aceptación:** mejora reproducible sobre la ausencia de ingreso natural en E028, conservación de las respuestas fundamentales existentes, ninguna regresión del archivo E027 y W4u; informe de resultados guardado en CI. No se declaran aprobaciones antes de ejecutarla.

## Etapas siguientes

1. Enseñar un esquema configurable de relaciones y sinónimos en XI, con experimentos reservados, para no aumentar el código con una frase fija por cada patrón.
2. Extracción de **dos o más proposiciones de un turno**, delimitando sujetos y relaciones y publicando de forma atómica; los fragmentos ambiguos deben pedir aclaración, no convertirse en hechos.
3. Índice de entidad/relación para evitar releer 512 fragmentos en cada consulta. Medir memoria lógica, disco, latencia y costo real de la consulta.
4. Reconciliar evidencia E025/E026/E027 con reglas explícitas de prioridad, negación, retractación, fuente y fecha.
5. Construir un instalador RXE para REVERSE-PC y verificar Android por separado. Ninguna etapa anterior equivale a un despliegue APK.
