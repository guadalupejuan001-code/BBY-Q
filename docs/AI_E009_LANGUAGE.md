# BBY Q E009 — lenguaje simbólico fundamentado en XI

## Objetivo y límite de la afirmación

Primera etapa verificable de BBY Q para **aprender palabras, relacionar
conceptos, deducir relaciones y expresarlas con una oración**, construida
sobre los cuatro conocimientos E008 ya existentes.

**No** es un modelo lingüístico generativo ni comprende el español de
forma general. No usa un modelo ajeno; toda la lógica del aprendiz,
la clasificación epistémica, las búsquedas de conocimiento y la
composición de la frase están en el **dialecto XI propio**. El runtime
existente de REVERSE-PC todavía usa bootstrap C++; el binario no es
MX autoalojado ni realiza síntesis de voz.

Una frase correcta aquí se obtiene porque el agente resuelve términos
contra el estado aprendido y construye un enunciado nuevo a partir
de IDs de conceptos; **no** mediante una tabla con frases enteras
almacenadas. Las palabras, hechos y respuestas de prueba viven en
lecciones externas (programas XI de entrada), no en los algoritmos de
`ground.xi`, `relate.xi`, `calibrate.xi`, `ask.xi` o `speak.xi`.

## Una sola entidad persistente

**Nacimiento:** `birth.xi` exige un estado E008 real con cuatro bancos
aprendidos (REVERSE-PC/Mundo X) y añade la firma `76,71,1` en
la región lógica `7100000000000000000`, dentro del **mismo RVPC2**.
No se inicializa un segundo sistema de memoria ni se copian pesos.
E008 conserva el esquema 6 y sus cuatro bancos inalterados.

| Offset desde 7100000000000000000 | Uso |
|---|---|
| +0..+2 | Firma `76,71,1`; no contiene palabras precargadas |
| +16/+17/+18 | Cantidad de palabras / conceptos / hechos |
| +19 | Contador acotado de observaciones léxicas |
| +100/+101..+108 | Longitud y bytes ASCII de una forma léxica |
| +120..+122 | Tres señales sensoriales categóricas 0..3 |
| +125 | Evento de aprendizaje de palabra |
| +140/+150/+160 | Tres formas léxicas con longitud/bytes: S, R y O |
| +170/+175 | Hecho positivo/negativo y tipo de evento 2/3 |
| +180..+182 | IDs temporales de palabras resueltas |
| +190..+195 | Resultado compacto: estado, sujeto, relación, objeto, testigo, profundidad |
| +196 | Contador acotado de preguntas |
| +240..+243 | Decisión sobre siguiente estudio y concepto objetivo |
| +600+ID | Huella no lingüística del concepto |
| +1000+16×slot | Forma original: longitud, concepto, bytes y evidencia |
| +2000+ID | Composición transitiva permitida por evidencia (0/1) |
| +2100/+2150+ID | Apoyos/contraejemplos para la propiedad |
| +3000+8×slot | Hecho: sujeto, predicado, objeto y cuentas positiva/negativa |

El programa deriva la huella de señales `x,y,z` con valores 0..3:
`1 + ((4*x + y)*4 + z)`. No recibe como respuesta el ID del
concepto: **lo asigna en el primer encuentro de una huella**.
Una segunda palabra con el mismo vector sensorial apunta al
mismo concepto (sinónimo operativo). Una misma palabra con otra
huella se rechaza, para no alterar silenciosamente significados.

Este mecanismo es una asociación con **sensores artificiales
cuantizados**, no percepción de objetos reales. Las huellas simples
pueden colisionar semánticamente y no representan polisemia.

## Aprendizaje de relaciones

`relate.xi` recibe una muestra `sujeto relación objeto` con
resultado 1 (observado) o 0 (refutado), ya expresada en formas
cuyo significado sensorial fue vinculado. Resuelve cada forma
contra el vocabulario persistente y crea/refuerza una relación
en la misma Ether Memory. Afirmaciones y negaciones se conservan
por separado: **nunca se borra la historia contradictoria**.

En este prototipo, una relación directa necesita dos muestras
coherentes para considerarse fundada.

`calibrate.xi` inspecciona caminos `S R M`, `M R O` y
observaciones directas `S R O`: solo habilita inferencia por
composición en predicados que cuenten **al menos dos ejemplos
confirmatorios independientes de camino** y **ninguna negación
fundada** del mismo tipo. No contiene los nombres «contiene»,
«incluye», «toca» o «mira» como reglas de inferencia.

La prueba de composición sigue siendo una **gramática pequeña**:
predicados binarios, hechos positivos/negativos y un máximo de
dos pasos. No prueba inferencia lógica arbitraria, semántica
profunda o descubrimiento de axiomas universales.

## Preguntar, hablar y decidir qué aprender después

`ask.xi` recibe tres palabras del esquema `S R O` y devuelve:

- `1` — la afirmación tiene apoyo directo o una prueba de dos pasos;
- `2` — existe refutación directa suficientemente confirmada;
- `0` — palabra desconocida, falta de prueba o evidencia contradictoria.

El módulo conserva un ID intermedio como **testigo** cuando infiere
una relación no observada directamente. `speak.xi` busca las formas
léxicas persistidas y emite sus bytes ASCII en orden. El CLI
XI devuelve números por `print`; Bash en CI los representa como
caracteres para mostrar la transcripción, **sin sustituir el
algoritmo de la IA**.

`reflect.xi` interpreta el estado epistémico para planificar el
siguiente estudio: `0` usar lo ya justificado, `1` pedir
evidencia sobre relación desconocida, `2` fundamentar una
palabra no reconocida. Guarda la decisión en el mismo estado.
Aún **no realiza automáticamente** la siguiente observación.

## Protocolo reproducible y resultados

GitHub Actions
[BBY Q E009](https://github.com/guadalupejuan001-code/BBY-Q/actions/workflows/bbyq-language.yml)
construye primero los 4 bancos E008, y recién entonces
`birth.xi` añade el subsistema. Los programas de lecciones
construidos por el trabajo de CI son **datos de enseñanza en
sintaxis XI**, nunca instrucciones implementando otro modelo.

Se prueban dos mundos artificiales independientes, con vocabularios
completamente distintos, sin modificar los programas inteligentes.
En cada uno: **10 formas, 8 conceptos sensoriales distintos, 9
relaciones originales** con evidencia repetida. Las variantes léxicas
comparten sensores: `cofre=caja` y `guarda=contiene`, o bien
`recinto=sala` y `alberga=incluye`.

### Primera colección de conceptos

| Pregunta formulada | Respuesta XI decodificada | Motivo |
|---|---|---|
| cuarto contiene llave (antes de aprender composición) | `?` | Sin regla justificada |
| cuarto contiene llave (después) | `cuarto contiene llave (via caja).` | Deducción por hecho intermedio |
| cuarto guarda llave | `cuarto contiene llave (via caja).` | Sinónimo del predicado |
| cofre contiene bolsa | `caja contiene bolsa.` | Sinónimo del sujeto |
| luz toca bolsa | `no: luz toca bolsa.` | Negación aprendida |
| luz toca llave | `?` | No generaliza un predicado sin fundamento |
| nube contiene llave | `?` | Término no aprendido |
| cuarto contiene llave tras reiniciar RVPC2 | `cuarto contiene llave (via caja).` | Persistencia |

A continuación se refutó un ejemplo de composición previamente
confirmado, se volvió a calibrar el sistema y el agente **retiró
la inferencia**. Tres nuevas confirmaciones restablecieron evidencia
suficiente y la inferencia fue **recuperada sin reprogramar XI**.

### Segundo mundo y vocabulario independiente

| Pregunta | Respuesta XI decodificada |
|---|---|
| edificio incluye libro antes de composición | `?` |
| edificio incluye libro después | `edificio incluye libro (via sala).` |
| edificio alberga libro | `edificio incluye libro (via sala).` |
| recinto incluye armario | `sala incluye armario.` |
| ojo mira armario | `no: ojo mira armario.` |
| ojo mira libro | `?` |

No existe ningún código que relacione las palabras del primer
mundo con las del segundo; las composiciones se aprendieron de
cada campaña por separado.

**Controles:** se rechazó un cambio contradictorio de huella
para una palabra conocida (rollback y ausencia de archivo de
salida), se verificó que `speak.xi` no modificara ni un byte
del RVPC2, se auditaron todos los bytes de entrada borrados y se
demostró preservación de los cuatro bancos E008.

## Límites cuantitativos y honestidad

- Máximo **32 palabras**, **16 conceptos** sensoriales,
  **48 hechos** alojables (la calibración actual admite menos de 25).
- Únicamente palabras minúsculas ASCII de **1..8 bytes**:
  sin acentos, inflexión, pronombres, polisemia o preguntas abiertas.
- No hay un analizador de español natural. Las lecciones y preguntas
  usan eventos estructurados de exactamente **tres palabras**.
- `speak.xi` emite texto por códigos ASCII; no voz, fonética,
  audio ni interfaz conversacional humana.
- El modelo no está conectado a imágenes, micrófono ni sensores
  reales: «fundamentado» significa observaciones simbólicas
  de un mundo artificial bajo controles.
- La inferencia binaria por dos pasos puede fallar en ambigüedad,
  relaciones no transitivas o mundos ruidosos, y no es
  demostración de inteligencia general ni conciencia.
- Todos los algoritmos de aprendizaje y emisión son XI original;
  el intérprete preexistente continúa compilado con un bootstrap
  C++, que **no** se ha sustituido por MX autoalojado.
- No se usaron qubits activos ni aceleración cuántica en el
  subsistema semántico.

**Próximo paso:** enseñar nombres y relaciones mediante
señales variables/no sintéticas, producir lenguaje de
múltiples tipos de oración, ampliar el protocolo textual
sin sustituir la IA por un modelo de terceros y probar
razonamiento en tareas no prefijadas durante el entrenamiento.
