# E015 — Preguntas bilingües a partir de ejemplos de estructura

Continúa el checkpoint E014 publicado, sin repetir su enseñanza ni sustituir
conocimiento. Base de código: `274060436c0f1eb538f59c56cfa73b8ed10ec01c`.
REVERSE-PC y Mundo X permanecen en las revisiones fijadas por E014.

## Capacidad observable

```text
ana tiene ocho manzanas y pierde tres manzanas
→ cinco
¿Cuántas manzanas le quedan a Ana?
→ cinco
How many apples does Ana have?
→ five                       [salida seleccionada EN]
cuántas manzanas tiene ahora ana?
→ cinco
```

E014 exigía `how_many apples has ana?`. E015 acepta `how many` como dos
palabras y aprende nueve estructuras de pregunta: auxiliares ingleses,
dos órdenes de pregunta en español, «le quedan a» y posiciones de
«ahora/now». Mayúsculas, acentos y espacios reutilizan el lector existente.
El idioma de salida continúa siendo una preferencia independiente del de
entrada; ambas lenguas consultan la misma cuenta persistente.

La respuesta sigue siendo una cantidad. Esto amplía comprensión dentro
del dominio de cuentas; no añade redacción libre ni gramática general.

## Qué aprende y qué está programado

El profesor proporciona **18 demostraciones** de texto, junto con las
identidades de persona, objeto y verbo de consulta. No proporciona una
plantilla, cantidad ni respuesta a la pregunta. XI resuelve cada palabra
con el vocabulario compartido y produce una secuencia de posiciones:
persona, objeto, verbo de asignación o marcador literal aprendido.

Dos ejemplos deben compartir esa estructura y variar **tanto la persona
como el objeto** para habilitarla. Repetir un ejemplo o cambiar solo la
persona no basta. Las asociaciones de nueve palabras funcionales o alias
se enseñan por la vía léxica existente: 419 → **428 entradas**.

| Elemento | Procedencia |
|---|---|
| Posiciones de los roles y de los marcadores en nueve estructuras | Inducidas en XI desde demostraciones con roles supervisados |
| Identidades de persona/objeto/verbo y significado de palabras nuevas | Proporcionadas por el profesor; vocabulario compartido con E014 |
| Familia de tres roles variables y marcadores literales | Diseñada en el programa |
| Dos testigos, límites, coincidencia y rechazo de interpretaciones incompatibles | Programados en XI |
| Cantidades, operaciones, cuentas y respuesta numérica | Implementación y aprendizaje E010–E014 conservados |

Se examinan **todas** las estructuras habilitadas. Si más de una atribuye
roles distintos al mismo texto, BBY Q se abstiene. Una estructura válida
normaliza únicamente las posiciones semánticas resueltas a la consulta
E014; no reescribe la entrada original ni calcula la respuesta fuera de XI.
Las preguntas no crean cuentas, no consumen objetos y no enseñan su respuesta.

Python es examinador y transporte; C++ sigue siendo el bootstrap y adaptador
original. La inteligencia nueva está en `ai/xi/grammar/`. No se añade otro
modelo ni una segunda autoridad de memoria.

## Memoria y continuidad

La región nueva es `7600000000000000000`, dentro del RVPC2 anterior:

| Posición | Uso |
|---|---|
| `+0..3` | Esquema y número de estructuras |
| `+8..11` | Comparación temporal de interpretaciones; se limpia |
| `+16..191` | Enseñanza y construcción temporal; se limpia |
| `+1000+i*64` | Registro de estructura: longitud, habilitación, dos testigos y posiciones |

La publicación contiene nueve estructuras y **cero cuentas del examen**.
Las regiones anteriores, sus hechos, pruebas, operadores, núcleo y enlaces
se comparan exactamente. Solo se añaden la región nueva, entradas léxicas
al final del vocabulario y roles de los conceptos funcionales nuevos.

Una pregunta reconocida conserva el contexto aritmético E011. Las entradas
no reconocidas conservan la conducta anterior: si llegan a la ruta aritmética
y fallan, invalidan la continuación numérica. El archivo se guarda antes de
anunciar cada respuesta y la caché de fuente incluye los módulos nuevos.

## Examen reproducible

El protocolo usa Ana/Luis y manzanas/peras al enseñar. El examen principal
usa Eva/Tom y libros/pelotas, con cantidades nuevas en cada contexto:

- **720 preguntas** sobre 720 contextos numéricos nuevos, semilla `150627`.
- Los mismos nueve tipos de pregunta fallan sin la extensión; añadir solo
  vocabulario tampoco basta para responderlos.
- **1.522 consultas del currículo E012** sobre el checkpoint E015, relaciones
  E009 y continuidad aritmética E011.
- Preguntas desconocidas, negación no admitida, palabras fuera del léxico,
  orden incorrecto, exceso de palabras y UTF-8 incompleto.
- Testigos repetidos, variación insuficiente, roles inválidos y enseñanza
  con interpretaciones incompatibles.
- Reinicio con recuperación de cuentas, corrupción detectada por auditoría,
  fallo de guardado y excepción XI después de actualizar el candidato.
- Invalidación de caché al modificar el módulo de gramática.

El protocolo y sus mediciones quedan en
`docs/evidence/e015-results.json`. La regresión E014 independiente reproduce
su checkpoint y sus pruebas de historias, transacciones y retención.

Resultado local: **3.080 verificaciones aprobadas**, incluidas las 720
consultas nuevas y las 1.522 del currículo anterior. Las 720 consultas usan
120 textos distintos; cambian las cantidades en cada contexto, sin afirmar
que sean 720 estructuras diferentes. La regresión E014 también aprueba sus
**5.291 verificaciones** y reproduce exactamente su checkpoint publicado.

| Medición local Linux x86-64 | Resultado |
|---|---:|
| Consultas nuevas, mediana / p95 | 10,45 / 14,50 ms |
| RAM residente durante esa sesión | 4,15 MiB |
| Tamaño del nuevo estado RVPC2 | 174.811 bytes |
| Aumento respecto a E014 | 5.514 bytes |

Comparación intercalada con **el mismo checkpoint E015** y 30 repeticiones
por caso: deducción factual con código E014, 7,38 ms; con código E015,
7,69 ms (+4,2 %). Las ocho tareas antiguas comparadas muestran un costo
de 4,2–7,6 % en la mediana de sesión. Es una ampliación de capacidad con un
costo medido, no una aceleración. Las mediciones incluyen guardado antes
de responder; no incluyen la comparación Python de la respuesta. La memoria
residente no se confunde con el pico RSS de arranque del proceso.

El detalle de la comparación está en `docs/evidence/e015-performance.json`,
y la regresión independiente en `docs/evidence/e015-e014-regression.json`.
Se emplea el examinador E013 existente, con el código E014 como
`baseline_root`, el código E015 como `candidate_root`, **el mismo estado**
para ambos, `--native-repeats 30 --ui-repeats 1 --session-binary ...`.

## Reproducir y usar

Con el runtime y el adaptador nativo E013 preparados:

```bash
base64 -d ai/checkpoints/BBYQ_E015_Grammar_ES_EN.rvp.gz.b64 | gzip -dc > bbyq.rvp
python3 ai/native/session_client.py /ruta/bbyq_session bbyq.rvp --language es
```

Para reproducir la enseñanza desde el padre conservado:

```bash
base64 -d ai/checkpoints/BBYQ_E014_Quantity_Stories_ES_EN.rvp.gz.b64 | gzip -dc > parent.rvp
python3 ai/xi/grammar/tests/native-grammar.py /ruta/reverse_pc /ruta/bbyq_session parent.rvp --out evidence/e015 --cases 720
```

El manifiesto `ai/checkpoints/e015-manifest.json` contiene hashes de los dos
estados, de los datos y revisiones del runtime. CI compara todo el estado
lógico reproducido, núcleo y enlaces con el checkpoint publicado.

Límites conservados: 255 bytes, 15 palabras, cantidades 0–65535 y 16 cuentas
por episodio. La familia permite como máximo 16 estructuras. Todavía faltan
concordancia productiva, pronombres, más tiempos verbales, transferencia de
objetos entre personas y generación de frases completas. Estas pruebas no
son una medida de inteligencia general ni un benchmark de Android.
