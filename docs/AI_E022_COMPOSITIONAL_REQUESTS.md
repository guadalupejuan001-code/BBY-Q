# E022 — Composición de peticiones y reformulaciones en XI

Continúa el E021 auténtico, SHA-256
`3246c34cb2d51037476f206020c55d8453a3060a4d2c511887c4b3fb3bdb4b1b`.
Conserva su aprendizaje anterior, incluidas las campañas de millones de ejemplos,
sin volver a enseñarlas como currículo nuevo. No se integra REVERSE OS ni se
conecta un modelo preentrenado. El adaptador nativo C++ permanece igual.

## Problema y comportamiento nuevo

E021 resolvía siete de las dieciséis reformulaciones del diagnóstico de
desarrollo. Las peticiones de definición con modificadores, algunas relativas
y los sujetos situados antes de la interrogación seguían fuera de alcance.
E022 enseña correspondencias entre fragmentos y entre cláusulas con variables.
En lugar de añadir una construcción por cada frase completa, puede combinar
una petición conocida, un modificador, una preposición y una coletilla.

Ejemplos del examen, después de enseñar la clasificación del sujeto:

```text
puedes hablarme un poco de neral
podrías explicarme brevemente acerca de neral por favor
can you tell me a little about neral
qué es lo que requiere neral
y hablando de neral qué requiere
say what neral requires in other words
```

Las consultas de definición invocan la clasificación conocida; no producen
una exposición libre sobre todos los atributos del sujeto. Las preguntas de
propiedad siguen consultando sus hechos y reglas. El idioma de salida se
configura en el cliente; no se detecta automáticamente.

La forma `which resources` está licenciada solo con `require/need`; consulta
ese predicado. No filtra los resultados por una categoría general de recursos.

## Aprendizaje, composición y autoridad de estado

Se enseñan **39 pares distintos de frases**, que inducen **33 reglas** de
normalización. Las reglas literales reciben una presentación explícita; las
seis reglas con variables reciben dos ejemplos con papeles diferentes. El
inductor XI intersecta las posibilidades literal/S/P/O en cada lado y exige
variación antes de promover las variables. No se suministran los índices de
las variables ni respuestas finales. Ambos textos de cada par se tokenizan
y resuelven dentro de XI en una misma transacción.

Se añaden 19 entradas léxicas. Las 224 construcciones antiguas se conservan;
las 33 reglas nuevas se cuentan aparte, porque pueden reutilizarse en muchas
frases. Se suprimieron dos correspondencias redundantes: `about/of` ya
compartían identidad con `de` en el léxico anterior.

El algoritmo de composición, sus tipos y sus barreras están diseñados. Se
aprenden los fragmentos, sus correspondencias y la colocación de los papeles.
No se declara descubrimiento autónomo de una teoría del lenguaje.

La región nueva es `N=8100000000000000000`, dentro del mismo RVPC2:

| Región relativa | Contenido |
|---|---|
| 0..15 | Esquema, publicación, cantidad de reglas y presentaciones |
| 10000..16143 | Banco izquierdo de restricciones inducidas, hasta 64 reglas |
| 20000..26143 | Banco derecho de restricciones inducidas |
| 30000..30511 | Modo, alcance y contador de cada correspondencia |
| 40000..72767 | Grafías canónicas iniciales; las variables se copian de la entrada |
| 16..127, 512..767, 1000..1601, 2000..2599 | Controles y vectores temporales; quedan en cero |

Se reconocen cabezas de petición, coletillas, modificadores y cláusulas
ancladas con papeles tipados. Las variantes léxicas que ya comparten identidad
no generan pasos de sustitución repetidos. Los fragmentos disjuntos se componen;
los candidatos igualmente específicos que discrepan sobre un mismo tramo
invalidan la normalización. Hay un máximo de ocho pasos, incluido activar
una cabeza: una correspondencia cíclica termina y recupera la entrada original.

La representación fuente sigue siendo XI textual. La memoria de diferencias
conserva solo los registros y grafías que difieren del fondo implícito; esto
no demuestra que el estado sea matemáticamente mínimo ni que comprima lenguaje
arbitrario de esta manera.

## Protección del significado y de lo aprendido

La ruta nueva acepta exclusivamente interpretaciones de consulta sin escritura.
Si la frase transformada no tiene una interpretación válida y única, restaura
los tres vectores originales y vuelve al intérprete anterior. No puede enseñar,
retirar hechos, crear alias ni elegir un acto social a través de la transformación.

La auditoría rechaza variables perdidas, sujetos literales introducidos en la
salida, marcadores de enseñanza y cambios de predicados factuales. Solo se
permite retirar la cópula de una relativa interrogativa supervisada. Un nombre
puede actuar como parte metalingüística de una petición literal —por ejemplo
`information`— sin cambiar su categoría léxica global. `un poco` también se
licencia como modificador de una petición de definición; no se elimina una
cantidad de una cuenta arbitraria.

Los vetos anteriores de negación, enseñanza, retirada y alias se conservan.
No se añaden hechos del mundo al estado publicado. Los nombres y afirmaciones
de los exámenes se descartan restaurando el checkpoint aprendido. Los registros,
reglas, operadores y construcciones anteriores permanecen sin cambios, aparte
de los contadores necesarios para anexar vocabulario.

Se admiten comas como separadores de palabras con el modelo E022 activo.
Esto no implementa comas decimales, separadores de miles, varias afirmaciones
por turno o párrafos completos. Se comprueba que las preguntas con aspecto de
enseñanza y las cantidades con comas no alteren el conocimiento.

## Examen y límites de la comparación

Las dieciséis reformulaciones originales y otras 64 composiciones guiaron el
desarrollo. Se publican separadas del examen final de **110 frases completas**,
que no aparecen como pares de entrenamiento ni en esas 64 composiciones.
El examen final combina las piezas, cambia sujetos y utiliza `alcanza/reaches`
en posiciones variables enseñadas con `necesita/need` y `utiliza/use`.
Los fragmentos son supervisados; no es una prueba de comprender vocabulario
arbitrario ni un benchmark de conversación general.

Se transfieren esas 110 formas a ocho diálogos (880 consultas), con entidades
nuevas, mayúsculas, acentos y signos de pregunta. Las respuestas esperadas quedan
fuera del proceso del agente. Se prueba incertidumbre, varios referentes,
negación, contradicciones, reinicio, fallo de guardado y el cliente público.
Los controles de aprendizaje introducen pares idénticos, predicados cambiados,
sujetos o marcadores de enseñanza inyectados, correspondencias contradictorias,
una correspondencia contrafactual y un ciclo explícito. Todos usan copias
experimentales; no forman parte del estado publicado.

| Checkpoint | Composiciones nuevas | Reformulaciones de desarrollo | Consultas compartidas |
|---|---:|---:|---:|
| E020 | 1/110 | 0/16 | 32/32 |
| E021 | 1/110 | 7/16 | 32/32 |
| E022 | 110/110 | 16/16 | 32/32 |

En esas 110 consultas, la mediana fue 30,67 ms en E020, 37,38 ms en E021 y
63,62 ms en E022. Los anteriores se abstenían en 109 casos; esa diferencia
de trabajo limita la comparación de velocidad. Las 32 consultas compartidas
tuvieron medianas de 21,23, 27,93 y 29,66 ms, respectivamente. Esta ampliación
mejora la cobertura y añade coste; no demuestra una aceleración general.

La ejecución local completa aprobó **6.365 comprobaciones**, contadas
después de las auditorías finales de esa misma ejecución. No se suman contadores
de campañas distintas. La enseñanza nueva tardó **3.12 s**, con el
runtime compilado; incluye el vocabulario, los pares y las auditorías de
promoción, y excluye desarrollo, compilación y exámenes. Los tiempos de consultas
y métricas de sesión completos están en los resultados JSON.

[Resultados completos](evidence/e022-results.json) ·
[Comparación y transcripciones seleccionadas](evidence/e022-comparisons.json).

La regresión comprueba todas las 128 formas E021 con nuevos sujetos, sus ocho
temas y sus cambios de evidencia; también repite las construcciones E018/E019,
las 1.522 consultas antiguas en ambos formatos y las 1.024 cuentas reservadas
E020. La CI reproduce el aprendizaje nuevo, compara el estado lógico completo
y ejecuta las campañas anteriores sobre sus checkpoints auténticos.

El checkpoint E022 ocupa **500.410 bytes**, frente a 465.830
de E021: añade **34.580 bytes**. Su SHA-256 es
`33a2490be0d7a9252222991da1cd376e7cfb4ecb0014987c65d1b8b24278f20f`. Los registros léxicos K+U suman 667 entradas.
El estado publicado se guardó antes de enseñar los nombres del examen.

Persisten 255 bytes y 15 palabras por turno, ocho temas factuales, 64 nodos de
búsqueda, 32 de prueba y ocho resultados. La composición nueva se limita a
peticiones y cláusulas tipadas licenciadas. No hay generación libre de prosa,
resolución general de correferencias ni conversación abierta general.

REVERSE-PC permanece fijado en `6d4de14a2dfbce4b8a7f1cb50e29d11b9073fe98` y Mundo X
en `e2778d962af22f6f1a0794058dd4685fc2573966`. Se mide Linux, no Android. No se
atribuyen estos resultados a una ventaja cuántica. Python es currículo,
transporte y examinador; las decisiones del agente se ejecutan en XI.

```bash
python3 ai/xi/rephrase/tests/native-e022.py /ruta/reverse_pc /ruta/bbyq_session --out evidence/e022
base64 -d ai/checkpoints/BBYQ_E022_Compositional_Requests_ES_EN.rvp.gz.b64 | gzip -dc > bbyq.rvp
python3 ai/native/session_client.py /ruta/bbyq_session bbyq.rvp --language es
```
