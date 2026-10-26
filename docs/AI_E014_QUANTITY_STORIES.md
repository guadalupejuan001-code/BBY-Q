# E014 — Cantidades, personas y objetos en pequeñas historias

Base de código: E013 `6c3a417f9550aa4551f57aa6492642309c85bfde`.
Continúa el checkpoint E012 auténtico, SHA-256
`8961833bb7140d7b63494dbd96ff02136559fd25eeca5a51f65fe3148131844f`.
No vuelve a enseñar E004–E012. REVERSE OS permanece pospuesto.

## Avance observable

La misma entrada nativa puede llevar cuentas de un episodio ficticio:

```text
ana tiene dos manzanas y recibe tres manzanas
→ cinco
cuántas manzanas tiene ana?
→ cinco
luis tiene ocho peras y pierde tres peras
→ cinco
ana has two apples and receives three apples
→ five                    [preferencia de salida EN]
how_many apples has ana?
→ five
```

La cuenta distingue **persona y objeto**, conserva cantidades entre turnos
y sobrevive a cerrar/reabrir la sesión. El sujeto puede omitirse después de
la conjunción dentro del mismo turno. También puede cambiar explícitamente:

```text
ana tiene dos manzanas y luis tiene tres manzanas y recibe cuatro manzanas
→ siete                  [Luis: 7; Ana: 2]
```

Son microhistorias con una gramática diseñada, no comprensión abierta de
problemas verbales. `how_many` es un marcador de una palabra; `how many`
todavía no está admitido. La respuesta es una cantidad, no una explicación
libre. «Da/gives» reduce la cuenta del donante; no transfiere automáticamente
objetos a un receptor que no aparece en esta gramática.

## Entrenamiento real y mecanismos programados

Se añaden **45 entradas léxicas**, para un total de **419** en la región de
conocimiento E012. Nombres, objetos, singular/plural, verbos y marcadores
usan sus identificadores compartidos; las cantidades reutilizan los números
E010 y su interpretación E011. Los **185 hechos** anteriores no se sustituyen
por las historias del examen.

El profesor proporciona **14 consecuencias distintas** para siete conceptos
verbales: `tiene/has`, `recibe/receives`, `pierde/loses`, `compra/buys`,
`da/gives`, `encuentra/finds` y el control artificial `zorp`.
Cada ejemplo aporta cantidad anterior, cantidad mencionada y consecuencia
observada. XI contrasta tres candidatos diseñados: asignar, añadir y quitar.

Una habilidad requiere al menos **dos pares distintos** y un candidato
compatible único. Repetir el mismo ejemplo no basta. Dos observaciones
ambiguas sin cambio tampoco habilitan un verbo. Una lección incompatible
se rechaza transaccionalmente. Las observaciones posteriores refinan la
máscara de candidatos; se guardan los dos primeros testigos distintos.

Un control aislado conserva exactamente el mismo texto `zorp` pero cambia
las consecuencias enseñadas: la respuesta cambia de 5 a 11. Esto comprueba
que la operación procede del estado aprendido. Ese estado de control no se
publica como el modelo final.

**Programado:** gramática y enlace entre módulos, familia de tres efectos,
roles supervisados de marcadores, búsqueda de pares, límites y transacciones.
**Aprendido:** vocabulario y referentes simbólicos suministrados, asociación
de cada verbo con sus consecuencias. No se afirma que descubrió por sí sola
la sintaxis, inventó la aritmética o tuvo experiencias reales con manzanas.

Todos los cálculos y respuestas usan directamente `dialogue/interpret.xi`
y `dialogue/respond.xi` originales. El código Python es examinador y transporte;
no contiene una ruta de respuesta usada por BBY Q. El runtime REVERSE-PC y
Mundo X permanecen en sus revisiones fijadas, sin otra IA externa.

## Memoria, dudas y publicación

La extensión vive en `7500000000000000000`, dentro del mismo RVPC2:

| Región | Función |
|---|---|
| `+0..7` | Esquema, marcadores y número de cuentas |
| `+8..15` | Estado, razón, último par/cantidad y número de acciones aceptadas |
| `+16..63` | Control temporal, se limpia al terminar |
| `+1000..1127` | Hasta 16 pares persona/objeto, con cantidades de 16 bits |
| `+2000..2127` | Candidato de todo el turno; nunca es otra autoridad persistente |
| `+2200..2215` | Respaldo temporal del contexto aritmético anterior |
| `+10000 + ID*24` | Candidatos, habilitación y testigos de cada verbo |

El motor prepara todas las acciones y solo publica si el turno completo es
válido. Si una tercera acción produciría una cantidad negativa, las dos
primeras tampoco se guardan. Un par desconocido no equivale a cantidad cero:
`recibe` y `pierde` necesitan una cuenta previa; `tiene` puede establecerla.

`Ana tiene dos manzanas?` se rechaza como pregunta no admitida, sin establecer
una cantidad. Solo el formato interrogativo con marcador (`cuántas ...`)
consulta las cuentas. El lector XI conserva temporalmente la presencia de
`?`/`¿` en `K+47` y lo limpia al terminar. Las preguntas factuales antiguas de
tres palabras tienen prioridad y siguen accediendo al mismo grafo anterior.

El contexto aritmético E011 se restaura después de los turnos de historias:
una cuenta de manzanas no sustituye el resultado que continúa `minus one`.
Las preguntas y el examen no enseñan sus respuestas al modelo.

El checkpoint publicado contiene vocabulario y habilidades nuevas, con
**cero cuentas ficticias del examen**. Para iniciar otro episodio, cerrar la
sesión y ejecutar `reset-episode.xi` conserva palabras, efectos y conocimiento
previo. La sesión nativa mantiene el guardado antes de anunciar cada respuesta.

## Pruebas y alcance

La evaluación nueva separa las 14 lecciones de sus entradas de examen:

- **600 historias** de una a tres acciones, con cantidades y combinaciones
  nuevas, alias, ES/EN mezclados, mayúsculas y espacios.
- **600 preguntas posteriores** sobre esas cuentas.
- Los **1.522 casos E012** completos ejecutados sobre el nuevo checkpoint,
  además de la regresión independiente de E012 y consultas E009/E011.
- **1.000 acciones consecutivas**, verificando el archivo después de cada
  respuesta; reinicio y recuperación de la misma cuenta.
- Capacidad real de 16 cuentas, rechazo de la 17, personas/objetos separados,
  episodio nuevo, límites numéricos, preguntas, negación no admitida,
  palabras desconocidas, sintaxis inválida y rollback de varios pasos.
- Fallo de guardado y excepción XI después de actualizar un candidato:
  se conservan tanto el archivo como las cuentas cargadas, sin anunciar éxito.
- Testigos repetidos/ambiguos, enseñanza invertida, transferencia a conceptos
  E012, caché de fuente invalidada al editar un módulo nuevo y seis auditorías.

El examinador compara todos los bytes aprendidos, núcleo y enlaces. No basta
con que una respuesta aislada tenga buen aspecto. Los detalles medidos y
percentiles se conservan en `docs/evidence/e014-results.json` y la comparación
con E013 en `docs/evidence/e014-performance.json`; son mediciones Linux
x86-64, no resultados de Android o frente a modelos grandes.

| Mediana medida en sesión residente | Tiempo |
|---|---:|
| Acción nueva sobre una cuenta, 1.000 turnos | 10,27 ms |
| p95 de esas acciones | 14,27 ms |
| Deducción factual representativa, código E013 | 7,06 ms |
| Misma deducción, mismo checkpoint, código E014 | 7,55 ms |

La ruta nueva añade alrededor de 0,49 ms (7 %) al caso factual comparado;
no se presenta como otra aceleración. Las dos variantes reciben exactamente
el mismo checkpoint de 169.297 bytes, con 419 entradas léxicas, y se intercalan
30 muestras por caso para aislar el costo del código. La mezcla de acciones
del examen es otra carga distinta. RAM residente muestreada durante las
acciones: aproximadamente 4,09–4,32 MiB; el máximo SELF de proceso completo
incluye el arranque y no se confunde con esa memoria residente. Los qubits
activos medidos continúan en cero.

Checkpoint aprendido: SHA-256
`c3b732c4d704c21d1d0f99b0f774840de1ab66281813c5664a920d580fdf27b5`.

Límites: 15 palabras y 255 bytes por turno; palabras de hasta 32 bytes;
cantidades 0–65535 en cada paso; 16 pares por episodio; hasta tres acciones
explícitas por turno según su longitud. No hay pronombres libres, transferencia
entre donantes/receptores, multiplicación/división ni lectura de enunciados
arbitrarios. Los cambios de cuenta describen ficción suministrada por el
usuario, no observaciones del mundo. No se midió aceleración cuántica.

## Reproducir y usar

Con el runtime y el adaptador E013 preparados:

```bash
base64 -d ai/checkpoints/BBYQ_E014_Quantity_Stories_ES_EN.rvp.gz.b64 | gzip -dc > bbyq.rvp
python3 ai/native/session_client.py /ruta/bbyq_session bbyq.rvp --language es
```

Cada línea es un turno; EOF cierra la sesión. La CLI existente también sirve:

```bash
bash ai/xi/knowledge/text.sh /ruta/reverse_pc bbyq.rvp 'ana tiene dos manzanas y recibe tres manzanas' es
bash ai/xi/knowledge/text.sh /ruta/reverse_pc bbyq.rvp 'cuántas manzanas tiene ana?' es
```

Para un episodio nuevo, con la sesión cerrada:

```bash
/ruta/reverse_pc run ai/xi/stories/reset-episode.xi bbyq.rvp nuevo-episodio.rvp
```

Para reproducir entrenamiento y examen desde el padre auténtico:

```bash
base64 -d ai/checkpoints/BBYQ_E012_Knowledge_ES_EN.rvp.gz.b64 | gzip -dc > parent.rvp
python3 ai/xi/stories/tests/native-stories.py /ruta/reverse_pc /ruta/bbyq_session parent.rvp --out evidence/e014 --stories 600 --turns 1000
```

El siguiente avance útil es ampliar relaciones entre participantes y aprender
estructuras de pregunta más variadas, conservando pruebas separadas por
capacidad. Este hito no equivale a educación humana ni a inteligencia general.
