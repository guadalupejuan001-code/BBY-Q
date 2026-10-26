# E012 — Más conocimiento, relaciones y evidencia en XI

Base: E011, `main` **4a23c3e7f068923284c28daa170887523c12acce**.
La entidad continúa desde su checkpoint real de 21.252 bytes; no se repiten
E004–E011. La integración con REVERSE OS permanece pospuesta.

## Qué se enseñó y qué se programó

Se incorporaron **176 identidades simbólicas nuevas**, **374 entradas
léxicas ES/EN** y **185 afirmaciones con procedencia**. Se reutilizan
directamente los 22 conceptos E010, leyendo sus nombres originales:
por ejemplo, el mismo gato de E010 participa ahora en clasificaciones.
No se copian sus palabras ni se crea otra autoridad de memoria.

| Materia | Contenido de las lecciones |
|---|---|
| Seres vivos | Mamíferos, vertebrados, organismos, otras categorías y ejemplos |
| Cuerpo y sistema nervioso | Cerebro, neuronas, células, axones, dendritas y señales |
| Procesos mentales | Memoria, atención, percepción, aprendizaje, emociones y vocabulario de conciencia |
| Agua | Estados posibles, evaporación, condensación, hielo y vapor |
| Astronomía | Sol, planetas, satélites y cuerpos celestes |
| Química y medidas | Elementos básicos y unidades de longitud, masa, tiempo y temperatura |
| Software y método | XI, Ether, BBY Q, datos, evidencias, hipótesis y experimentos |

Las fuentes primarias educativas y el alcance de cada una están en
[`sources.json`](../ai/xi/knowledge/data/sources.json): NIH, NASA, USGS,
NIST, IUPAC y Universidad de Hawái. El **glosario del profesor** y los
controles formales se identifican por separado: no se presentan como
observaciones científicas independientes. Son afirmaciones seleccionadas
de enseñanza; no una revisión completa de esas disciplinas.

El aprendizaje léxico y factual, la consulta, las deducciones y la
construcción de respuestas se ejecutan exclusivamente en **XI**. El
runtime REVERSE-PC preexistente y Mundo X conservan sus revisiones fijadas.
Los scripts de transporte y el examinador no responden por la IA.

**Programado por ingeniería:** separar palabras, normalizar mayúsculas
y caracteres españoles, mantener el grafo, buscar caminos, contrastar una
familia candidata de reglas y construir triples de salida.
**Adquirido desde las lecciones:** palabras, referentes proporcionados
por el profesor, hechos, fuentes y qué relaciones cuentan con evidencia
para composición. No se afirma que BBY Q inventó BFS o una lógica universal.

Los conceptos nuevos son **simbólicos**, con identificadores enseñados;
no se descubrieron mirando fotografías ni viviendo experiencias humanas.

## Una autoridad y una entrada de texto

La región `7400000000000000000` se añade al mismo RVPC2. Cada hecho usa
una celda dispersa de Ether calculada desde S/R/O; se conserva por separado
la procedencia del apoyo positivo y del negativo. Un índice permite auditar
los hechos registrados sin recorrer todo el espacio de direcciones.

La entrada acepta estas microgramáticas:

```text
gato es organismo?
qué es neurona?
qué conserva memoria?
what studies philosophy?
```

Los marcadores de pregunta, predicados y nombres se reconocen por sus
roles aprendidos; las palabras concretas no aparecen en el clasificador.
El mismo programa resuelve variantes de mayúsculas, espacios, `¿...?`,
acentos, alias sin acento enseñados y combinaciones ES/EN.

La entrada nativa decide si corresponde usar el conocimiento E012 o
el **mismo programa aritmético E011**. El anfitrión no analiza el mensaje
para elegir un motor. La matemática previa no se vuelve a implementar.

También se conserva el acceso a E009: la misma entrada identifica sus
palabras originales y llama a los programas `language/ask.xi` y `speak.xi`
existentes. Una fachada de lectura restaura sus descriptores temporales
tras emitir la respuesta. No duplica su léxico ni sus hechos. Sus formas
originales siguen en español; no se inventan traducciones para ellas.

Los términos con sentidos incompatibles se explicitan: una figura
«estrella» y una «estrella_astronómica» no se funden silenciosamente;
tampoco la figura «corazon» y «corazón_órgano». La polisemia abierta
todavía no está resuelta.

## Deducir con límites y conservar la duda

Una relación solo admite composición tras **dos cierres distintos**
verificados desde hechos directos. Repetir un cierre no sustituye otro.
Una relación de sucesor numérico sirve de control no transitivo.

Antes de cada deducción, XI vuelve a comprobar sus testigos. Si aparece
una negación o conflicto pertinente, suspende la regla; al retirar la
evidencia contradictoria puede recuperarla. Una refutación directa del
objetivo impide sustituirla por una cadena hipotética. Un dato ausente
produce «?», no una negación inventada.

La búsqueda BFS conserva padres y devuelve el camino real. Ejemplo observado:

```text
gato es organismo. [gato -> mamífero -> vertebrado -> organismo]
```

Esto es deducción simbólica dentro de una familia diseñada. Dos ejemplos
no prueban que una generalización empírica sea universalmente verdadera.

## Evaluación local separada

El programa de consulta recibe **solo texto y preferencia de idioma**.
Las respuestas esperadas permanecen en el examinador. Los caminos se
verifican arista por arista contra la evidencia enseñada.

| Prueba | Casos aprobados | Qué verifica |
|---|---:|---|
| Consultas directas ES/EN | 370 | Recuperación de 185 hechos ya enseñados |
| Relaciones inferidas no enseñadas directamente | 234 | Composición; son 117 conclusiones en dos idiomas |
| Preguntas por objetos de una relación | 318 | Construcción y enumeración de respuestas desde el grafo |
| Nuevas formulaciones mezcladas ES/EN | 600 | Alias, acentos, mayúsculas y espacios en tres semillas |
| Total de estas cuatro categorías | **1.522** | No equivale a 1.522 hechos nuevos ni a inteligencia general |

Además pasan:

- Un grafo con nombres desconocidos para el código, otra relación y
  **ocho pasos de prueba**, con ciclos que terminan correctamente.
- Abstención ante datos desconocidos y ante «bbyq tiene conciencia?».
- Contradicción, retirada y restauración de una regla, y rechazo de
  etiquetas que intentan cambiar el sentido de una palabra ya conocida.
- Rechazo transaccional de roles, procedencia o versión inválidos.
- Cuatro consultas E009 desde la nueva entrada: prueba de dos pasos,
  sinónimos, refutación y desconocimiento; todos sus bytes previos intactos.
- Cinco auditorías nativas sin modificar el archivo auditado.
- Integridad del núcleo completo y de todo el conocimiento anterior.

Durante consultas aritméticas solo cambia la memoria de trabajo E011
prevista para esos turnos. Al terminar, **todos los bytes lógicos previos**
coinciden con el checkpoint padre. Las consultas de conocimiento no
modifican palabras, hechos, reglas ni recuerdos anteriores.

El estado final ocupa **157.115 bytes**, SHA-256
`8961833bb7140d7b63494dbd96ff02136559fd25eeca5a51f65fe3148131844f`.
Se conserva en `ai/checkpoints/` con manifiesto y compresión de transporte.
Los datos brutos y el informe están en los artefactos de CI; el resumen
local está en `docs/evidence/e012-results.json`.

## Reproducir y consultar

```bash
base64 -d ai/checkpoints/BBYQ_E011_Compositional_ES_EN.rvp.b64 > parent.rvp
python3 ai/xi/knowledge/tests/native-knowledge.py /ruta/reverse_pc parent.rvp \
  --out evidence/e012 --random-cases 200 --seeds 170627 270629 370631

base64 -d ai/checkpoints/BBYQ_E012_Knowledge_ES_EN.rvp.gz.b64 | gzip -dc > bbyq.rvp
bash ai/xi/knowledge/text.sh /ruta/reverse_pc bbyq.rvp '¿qué es neurona?' es
bash ai/xi/knowledge/text.sh /ruta/reverse_pc bbyq.rvp 'gato es organismo?' es
bash ai/xi/knowledge/text.sh /ruta/reverse_pc bbyq.rvp 'dos mas tres' es
```

## Lo que todavía falta del currículo original

Esta ampliación **no equivale a doce años de vida o educación**. Faltan
letras y sílabas con composición productiva, imágenes y objetos reales,
memoria de experiencias variadas, gramática abierta, problemas verbales,
aprendizaje autónomo de nuevas estrategias y transferencia entre tareas.
Estudiar conceptos mentales no demuestra experiencia subjetiva del software.

Límites actuales: preguntas de tres palabras, 255 bytes de entrada,
palabras de 32 bytes, ASCII y español Latin-1 UTF-8; 512 entradas léxicas
nuevas y 512 hechos registrados; ocho respuestas por pregunta, ocho
testigos por relación, 64 expansiones BFS y 31 pasos de prueba. Los nombres
compuestos usan guiones bajos. No hay comprensión general de textos.

El siguiente avance útil es ampliar estructuras de frases y referentes,
resolver problemas verbales y relacionar conceptos con observaciones reales,
midiendo cada capacidad aparte. Añadir miles de frases sin esas pruebas
solo aumentaría el almacenamiento.
