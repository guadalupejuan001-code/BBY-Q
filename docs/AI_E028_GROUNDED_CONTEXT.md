# E028 — Preguntas fundamentadas en la memoria contextual XI/Ether

## Qué cambia

E027 conserva hasta 512 fragmentos de 224 bytes (112 KiB de texto) en RVPC2, pero su búsqueda era explícita mediante `@ctx find`. E028 añade un **intérprete de preguntas y compositor de dos hechos dentro del mismo programa XI**: localiza por entidad, valida predicados, compara evidencia, selecciona fragmentos y produce texto acompañado de procedencia. El adaptador y el examinador no generan respuestas.

El **candidato** combina, en el orden de ejecución:

1. `ai/releases/e028/question-prefix.xi`: identificación explícita de intención, entidad, polaridad y combinación, con lectura directa de la memoria contextual E027.
2. `ai/releases/e027/context-prefix.xi`: comandos de archivo y limpieza existente, con invalidación del referente contextual en `clear`.
3. `ai/releases/e025/conversation-linked.xi`: inteligencia previa, saludos, hechos y acciones W4u originales, intactos. El checkpoint E025 original se usa como semilla sin entrenarlo de nuevo.

El módulo E026 de composición sobre la memoria factual E025 está en un PR independiente (#30); esta versión **no afirma haber fusionado E026**. E028 implementa una vía de composición distinta, anclada a la evidencia textual E027.

## Entradas de ejemplo

```text
@ctx add motor solar es dispositivo
@ctx add motor solar requiere energia
que es motor solar y que requiere
¿qué necesita el motor solar?
what is motor solar and what does it need?
y qué requiere?
```

Para los dos primeros fragmentos, una respuesta esperada en español es:

```text
motor solar es dispositivo [#000]. motor solar requiere energia [#001].
```

`#000` y `#001` corresponden a las posiciones reales de esos hechos en el archivo de contexto. El programa no inserta ninguna cifra de procedencia sin seleccionar y examinar un registro E027. Si hay un valor ausente o incompatible, se abstiene de afirmar una combinación.

## Alcance preciso del lenguaje

- Entidades: nombre anclado al inicio de un fragmento, de hasta 48 bytes (admite varias palabras y comparación ASCII sin distinción de mayúsculas/minúsculas).
- Afirmaciones **en un único fragmento y con una sola relación**: `ENTIDAD es VALOR`, `ENTIDAD requiere VALOR`, `ENTIDAD necesita VALOR`, `ENTIDAD is VALUE`, `ENTIDAD needs VALUE`, `ENTIDAD requires VALUE`. Se acepta un punto final.
- Negaciones reconocidas: `no es`, `no requiere`, `no necesita`, `is not`, `does not need`, `does not require`. La presencia de evidencia negativa para la relación examinada provoca abstención conservadora.
- Preguntas ES: `que/qué es ENTIDAD`, `que/qué requiere ENTIDAD`, `que/qué necesita ENTIDAD`, más combinaciones `que/qué es ENTIDAD y que/qué requiere/necesita`.
- Preguntas EN: `what is ENTITY`, `what does ENTITY need/require` y `what is ENTITY and what does it need/require`.
- Seguimiento después de una respuesta contextual válida: `y qué requiere`, `y qué necesita`, `and what does it need`, pronombres `it` y `eso`. Se conserva **un** referente demostrado; no existe resolución general de correferencias.
- Reconoce opcionalmente `¿`, `?`, los artículos `el`, `la`, `the` en la pregunta y nombres con espacios.
- Valor factual de hasta 80 bytes, una sola proposición y caracteres simples; se rechazan varias puntuaciones de escritura que crean ambigüedad. No se inferirán hechos de prosa libre, citas, listas, párrafos extensos ni textos indirectos.
- Para una pregunta sin evidencia en E027 y de una sola propiedad, delega al intérprete original E025, conservando su memoria previa. Para una pregunta compuesta no respaldada **no inventa una segunda propiedad**.

## Propiedades de seguridad y compatibilidad

- El archivo E027 se consulta por sus descriptores de offset y longitud guardados. Cada coincidencia compara el sujeto **exacto** antes de seleccionar predicados. No se mezclan hechos de entidades distintas ni se usa una respuesta asociada solo a una palabra suelta.
- Dos valores positivos diferentes para el mismo predicado se consideran conflicto y provocan abstención. Dos valores idénticos no lo provocan. Una negación también obliga a abstenerse de afirmar ese predicado, incluso si es sobre otro valor: es conservador, no un razonador lógico completo.
- Las respuestas solo incluyen relaciones recuperadas con posiciones del archivo. El foco de entidad se actualiza tras un éxito comprobado, se invalida con `@ctx clear`, y no cambia los hechos antiguos de E025.
- El programa conserva la posibilidad de abrir **un RVPC2 creado por E027** y recuperar sus fragmentos sin conversión ni reescritura de la semilla; se añaden únicamente instrucciones candidatas.
- Los datos de examen se enseñan a copias de estado desechables. No se promueven al checkpoint E025.
- La entrada individual permanece limitada a 255 bytes; el almacenamiento de 112 KiB **no es** una ventana de atención de 112 KiB.
- No se ha realizado despliegue Android ni se afirma aprendizaje lingüístico de todas las formulaciones.

## Examen reproducible

```sh
node ai/releases/e027/build.mjs /ruta/reverse_pc evidence/e027-original
node ai/releases/e028/build.mjs /ruta/reverse_pc evidence/e028
node ai/releases/e028/test.mjs /ruta/reverse_pc evidence/e028 evidence/e027-original evidence/e028-results
node ai/releases/e027/test.mjs /ruta/reverse_pc evidence/e028 evidence/e027-regression
```

La CI también ejecuta las 31 pruebas de E025 y 21 de W4u en el runtime de REVERSE-PC fijado a `a1b935ae0adf38615996bac92727e95289ad7cc1`, con Mundo X `e2778d962af22f6f1a0794058dd4685fc2573966`. Se evaluarán sujetos de desarrollo y sujetos no usados para diseñar el caso, ES/EN, hechos originales antiguos, conflictos, negación, limpieza, no contaminación del contexto y búsqueda de un tema antiguo tras centenares de fragmentos.

Los resultados se registran **cuando termine la ejecución**, no por el mero hecho de existir el código o este archivo.

## Siguiente etapa

- Indexación más eficiente por sujeto y relación para evitar un recorrido lineal de hasta 512 descriptores por consulta.
- Extracción de proposiciones múltiples con roles y negación formal; enlaces entre entidades, alias supervisados y reversión de hechos.
- Integración consistente de las fuentes E025/E026 con las fuentes E027, sin mezclar grados de confianza ni asumir que las dos arquitecturas hacen lo mismo.
- Evaluaciones separadas de entrenamiento y examen sobre diversidad lingüística, latencia y consumo en Android.
