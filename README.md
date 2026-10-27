# BBY Q — inteligencia artificial progresiva en tecnología propia

**Ruta activa: E019 — preguntas reformuladas y seguimiento del tema.**

Continúa E018 con 32 construcciones adicionales: 96 en total y 539 entradas
léxicas. Reconoce «sabes qué…», «do you know if…» y preguntas que reutilizan
un referente, como «¿y qué requiere?» o «what is it?». Cambiar de sujeto
consulta su propia evidencia. Si falta el tema, pide una pregunta completa.
La intención y las posiciones se enseñan con ejemplos; la gestión acotada
de referencias está implementada en XI. No implica comprensión general.

Conserva la respuesta breve, el protocolo compacto anterior, la misma memoria
RVPC2 y las dependencias fijadas. El código sigue en XI textual; la
compactación binaria del programa es trabajo pendiente. Continúa con un tema
factual activo y entradas de hasta 15 palabras, sin conversación abierta.

Prueba local: **5.617 verificaciones**, 1.024 problemas nuevos de pregunta
y las 1.522 consultas anteriores en ambos formatos. Las 32 sondas nuevas
pasan de 0/32 a 32/32; esa puntuación se limita a esas formas. El checkpoint
ocupa 319.274 bytes y conserva todos los registros aprendidos anteriores.

[Entrenamiento, intención de pregunta, contexto y límites de E019](docs/AI_E019_CONTEXT_QUESTIONS.md).

**E018 — continuar aprendiendo y responder con brevedad.**

Continúa el checkpoint E017 sin repetir sus lecciones. Aprende 25 formas
adicionales de preguntar, enseñar y retirar afirmaciones: 64 construcciones
en total y 533 entradas léxicas. Usa respuestas breves por defecto, conserva
todos los resultados y muestra la cadena de evidencia al pedir «¿por qué?».
Mantiene «No tengo información suficiente para responder» y las aclaraciones
de contradicción o ambigüedad.

Prueba local: 3.905 verificaciones, 60 diálogos nuevos de 12 turnos y las
1.522 consultas anteriores en respuesta breve y en la API compacta exacta.
Checkpoint: 298.808 bytes. La reducción de texto no supone una aceleración
general; sigue siendo conversación acotada, con 15 palabras por entrada.

[Entrenamiento, respuestas, incertidumbre y mediciones de E018](docs/AI_E018_CONCISE_DIALOGUE.md).

**E017 — aprender durante el diálogo, sobre E016.**

BBY Q aprende afirmaciones, palabras y alias mediante enseñanzas explícitas,
admite 39 construcciones supervisadas ES/EN, corrige contradicciones y deduce
sobre conceptos nuevos mostrando la evidencia. Añade calibración de dos
familias de reglas: transitividad y herencia de propiedades. Todo se ejecuta
en XI, en el mismo RVPC2 y sin repetir el entrenamiento anterior.

Prueba local: 4.376 verificaciones, 80 diálogos nuevos (640 turnos), los
1.522 casos anteriores en ambas superficies y crecimiento a 804 entradas
léxicas. El checkpoint conserva 524 entradas y ocupa 279.677 bytes.
RAM residente medida de la conversación: 6,88 MiB en Linux; Android no medido.
Las tareas anteriores cuestan más tiempo en esta ruta. Es una ampliación
hacia conversación abierta; todavía conserva gramática y razonamiento acotados.

[Aprendizaje, diagnóstico, límites y uso de E017](docs/AI_E017_OPEN_LEARNING.md).

**E016 — frases completas y diálogos cortos, sobre E015.**

BBY Q compone «Ana tiene cinco manzanas», entiende «ella recibe tres más»
y continúa preguntas como «¿y las peras?» o «¿y un perro?». Conserva el
referente al reiniciar y responde en español o inglés sobre la misma memoria.
Las frases de cantidades usan un orden inducido desde ejemplos y formas
nominales supervisadas. Los saludos y la presentación son textos enseñados.
La gramática y los temas siguen siendo acotados; no es conversación abierta.

Prueba local: 120 diálogos nuevos (960 turnos), 384 casos de concordancia y
límites, 1.522 consultas factuales con frases y las mismas 1.522 con el
protocolo anterior. Total: 4.668 verificaciones. Estado: 209.659 bytes;
RAM residente medida: 5,00 MiB en Linux x86-64; Android no medido.

[Enseñanza, conversaciones, mediciones y uso de E016](docs/AI_E016_CONVERSATION.md).

**E015 — estructuras de pregunta bilingües, sobre E014.**

BBY Q continúa su estado aprendido con nueve estructuras inducidas desde
18 demostraciones con roles supervisados. Puede responder a «how many apples
does ana have?» y «cuántas manzanas le quedan a ana?» sobre la misma cuenta,
sin exigir `how_many`. Dos ejemplos deben variar persona y objeto antes de
habilitar una estructura. Se añaden nueve entradas léxicas: 428 en total.
Prueba: 720 preguntas con referentes distintos a los de enseñanza y 1.522
consultas del currículo anterior. La gramática sigue limitada al dominio
de cuentas y la respuesta es una cantidad; REVERSE OS continúa pospuesto.

[Enseñanza de estructuras, controles y límites de E015](docs/AI_E015_GRAMMAR.md).

**E014 — cantidades y referentes en pequeñas historias, sobre E013.**

BBY Q aprende efectos de verbos a partir de consecuencias y conserva cuentas
por persona y objeto: «ana tiene dos manzanas y recibe tres manzanas» →
«cinco»; después puede consultar la misma cuenta. Son microhistorias con
gramática acotada, 16 cuentas por episodio y operaciones de asignar/sumar/restar.
Se añaden 45 entradas léxicas y 14 lecciones de consecuencias, conservando el
checkpoint anterior y la aritmética XI original. REVERSE OS sigue pospuesto.

[Entrenamiento, pruebas y uso de E014](docs/AI_E014_QUANTITY_STORIES.md).

**Base de rendimiento E013.**

La deducción de referencia pasó de 65,78 ms en la entrada CLI anterior a
7,29 ms entre turnos de la sesión E013, con guardado por respuesta.
Se probaron 1.000 turnos, hasta 512 hechos/512 entradas y fallos de escritura.
RAM residente medida de 3,79–4,34 MiB en Linux x86-64; Android no medido.

[Mediciones, método y límites de E013](docs/AI_E013_PERFORMANCE.md).

**E012 conserva el conocimiento bilingüe, relaciones y evidencia en XI.**

Continúa desde el checkpoint E011 real, conservando la entidad anterior.
Añade 176 identidades simbólicas, 374 entradas de vocabulario ES/EN y
185 afirmaciones con procedencia. Reutiliza directamente los 22 conceptos
E010 y la aritmética E011. Pruebas locales: 370 consultas de recuperación,
234 consultas de deducción nueva, 318 preguntas por relaciones y 600
variantes mixtas; además, un control de ocho pasos y ciclos.

La nueva base está en `ai/xi/knowledge/` y el estado aprendido se conserva
en `ai/checkpoints/`. Los conceptos nuevos son enseñados simbólicamente;
esto no equivale a experiencia humana, conversación abierta ni doce años
de aprendizaje. **REVERSE OS permanece pospuesto.**

[Currículo, evidencia, uso y límites de E012](docs/AI_E012_KNOWLEDGE.md).
[E011: texto composicional y aritmética conservada](docs/AI_E011_COMPOSITION.md).
E009 continúa enseñando relaciones y microoraciones;
E008 conserva los cuatro bancos previos y E007 su evolución anterior.
Todas las capacidades viven en el mismo estado RVPC2.

BBY Q **no utiliza SOVENGI, modelos de IA de terceros, Transformers ni
código Python/C++ para implementar su inteligencia**. Su estado y las
transacciones pertenecen a REVERSE-PC, XI, Inverse Ether Memory y Mundo X,
con **una sola autoridad persistente RVPC2 por agente**.

## E010 — Aprender como un niño es una inspiración, no un curso rígido

La entidad `ai/xi/school/` añade el **desarrollo adaptativo
bilingüe**, no un horario escolar: avanza únicamente cuando resuelve
suficientes casos independientes y retrocede si nuevas pruebas
contradicen una habilidad anterior.

**Ya aprendido en XI:**

- **Colores:** rojo/red, azul/blue, verde/green, amarillo/yellow.
  Distingue nuevas tonalidades mediante distancia entre triples RGB,
  con margen y abstención ante colores desconocidos.
- **Animales y símbolos:** gato/cat, perro/dog, ave/bird, pez/fish,
  y circulo/circle, cuadro/square, estrella/star, corazon/heart.
  Aún usa rasgos estructurados, no imágenes ni cámaras.
- **Cantidades:** los números 0–9 y sus nombres en ambos idiomas.
- **Operaciones:** observa consecuencias al juntar/quitar cantidades,
  infiere qué operador aumenta o disminuye y generaliza a ejemplos
  nuevos. No inventa un algoritmo universal de matemáticas.
- **Dos idiomas:** `set-language.xi` cambia cómo se expresa el
  **mismo concepto**, sin crear otro cerebro o conjunto de pesos.

**Prueba native E010**
([GitHub Actions](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40303541105)):
22 conceptos aprendidos, 44 observaciones repetidas, **60/60**
evaluaciones de reconocimiento en ES y EN, **10/10**
evaluaciones aritméticas no enseñadas, incluidos casos donde
la respuesta correcta es **«?»** por falta de capacidad numérica.

El modelo original E009 se **recuperó desde un estado real previamente
entrenado**, nunca empezó esta etapa borrando su léxico.
Su nuevo archivo RVPC2 ocupa **18.722 bytes**, conserva los
bancos E008 y utiliza cero enlaces cuánticos en este experimento.

El siguiente avance debe hacer que los ejemplos provengan de
**percepción real** en vez de listas con rasgos, y profundizar en
letras, construcción de palabras, aritmética y conocimiento objetivo
de atención, emociones y conciencia humana. Aprender esos temas
no implica que el software tenga conciencia.

[Arquitectura y resultados verificables de E010](docs/AI_E010_DEVELOPMENT.md).

## E009 — Aprender sus primeras palabras, conceptos y frases

La nueva unidad `ai/xi/language/` se **añade a una entidad E008 con
cuatro bancos de conocimiento reales**, usando una región diferente
dentro de la misma Inverse Ether Memory/RVPC2. No hay otro modelo,
Transformer ni motor de aprendizaje en Python/C++/JS.

- `birth.xi` nace con **cero palabras y cero hechos**.
- `ground.xi` vincula formas ASCII a tres señales categóricas
  **no lingüísticas** y descubre cuándo dos palabras son sinónimos
  del mismo referente.
- `relate.xi` aprende triples `sujeto, relación, objeto`,
  con evidencias afirmativas y negativas que pueden contradecirse.
- `calibrate.xi` identifica una propiedad composicional en un
  predicado mediante **ejemplos y contraejemplos**, no mediante
  su nombre.
- `readline.xi` recibe una **línea de texto real** como
  `cuarto contiene llave?`, divide sus palabras dentro de XI y
  la prepara para el razonamiento. No usa un tokenizador ajeno.
- `ask.xi` recupera hechos directos o los deduce mediante
  dos relaciones aprendidas. Rechaza inferencias sin suficiente
  evidencia en lugar de inventar información.
- `speak.xi` construye oraciones a partir de las palabras
  persistidas y emite bytes ASCII directamente desde XI.
- `reflect.xi` decide si corresponde **aprender una palabra nueva**,
  **investigar una relación** o usar conocimiento ya demostrado.

**Prueba nativa:** [campaña E009](https://github.com/guadalupejuan001-code/BBY-Q/actions/workflows/bbyq-language.yml)
enseña **dos vocabularios independientes**, cambia y recupera
generalizaciones, verifica sinónimos, preguntas nuevas, hechos
falsos, reinicios y auditorías de persistencia.

Ejemplos de **texto construido por XI**, no respuestas de un chatbot
externo:

```text
? cuarto contiene llave
cuarto contiene llave (via caja).

? cuarto guarda llave
cuarto contiene llave (via caja).

? luz toca bolsa
no: luz toca bolsa.

? nube contiene llave
?
```

En una segunda campaña, con nombres diferentes:

```text
? edificio incluye libro
edificio incluye libro (via sala).

? recinto incluye armario
sala incluye armario.
```

**Precisión terminológica:** este es un sistema experimental de
**lenguaje simbólico estructurado**, no conversación libre en español.
Las entradas pueden ser microoraciones de **tres palabras**
segmentadas por el propio XI, o triples estructurados. Los
conceptos proceden de observaciones sintéticas categóricas; la
salida usa ASCII sin audio y todavía no existen comprensión de
textos largos, gramática española abierta, voz ni aprendizaje
de la vida real.

[Arquitectura E009, protocolo, lecciones y límites científicos](docs/AI_E009_LANGUAGE.md).

## E008 — Cuatro conocimientos y una política de exploración

**Cinco agentes, cada uno con cuatro hipótesis propias dentro de un único
RVPC2**. Aprenden XOR, XNOR, AND y OR sin incorporar la regla del
generador del mundo en el programa de aprendizaje. Tras su aprobación,
`recall4.xi` compara predicciones antes de consultar las consecuencias,
selecciona un banco reconocido o **se abstiene** si las contradicciones
son demasiado grandes. No vuelve a entrenar los cuatro bancos al
cambiar de entorno.

`plan-next.xi` analiza los desacuerdos y residuos para decidir una
acción epistémica: usar lo aprendido, consultar un experimento
discriminante, investigar la región más sorprendente o ampliar
la representación. La política no ejecuta todavía investigaciones
físicas ni modifica su propia gramática sin pruebas.

**Validación final sellada**
([GitHub Actions 40289515756](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40289515756)):

- **20/20** situaciones conocidas identificadas; **15/15**
  desconocidas rechazadas sin alucinar una clase.
- **20/20** reconocidas bajo 15 % de corrupción independiente;
  **18/20** bajo 25 % (dos abstenciones seguras).
- **1.600 decisiones** adicionales con entradas cambiantes:
  1.070 selecciones correctas y 530 abstenciones, sin modificar
  las hipótesis ni romper la persistencia.
- Estado RVPC2 de semilla 42: **6.632 bytes** después de 320
  decisiones de longevidad. Las cuatro hipótesis ocupan
  un único espacio Ether con checksum por banco.
- **Cero qubits activos y cero entrelazamientos** en
  estos experimentos de aprendizaje simbólico en CPU clásica.

[Contrato, datos crudos, límites y evaluación de «organismo»](docs/AI_E008_CONSTELLATION.md).
[Archivos persistentes y resultados E008](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40289515756/artifacts/12635511438).

**Diagnóstico:** el proyecto avanza como agente computacional
persistente con aprendizaje y metacontrol limitado. Aún **no es
un organismo biológicamente vivo ni una IA general**, no controla
sus propios recursos/actuadores y la evolución de relaciones
permanece restringida a una gramática de dos signos.

## E007 — Ether Vault: una memoria que recuerda sin reaprender

La entidad aprende **A: XOR** y **B: XNOR** con un mismo jurado de E006.
Las hipótesis quedan en dos bancos compactos dentro de un solo RVPC2.
El selector `ai/xi/e007/recall.xi` compara ambas sobre experiencias
nuevas, intercambia la activa cuando la archivada supera por al menos
30/240 casos y alcanza 205/240, y destruye los datos temporales.

[CI E007: recuperación reversible con feedback parcialmente corrupto](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40285381399).
En cada semilla, la secuencia A→B→A-ruidoso→B-ruidoso→A→B→ruido→A→A
cambió de modelo cuando había evidencia y se mantuvo bajo ruido puro
o cuando el activo seguía siendo correcto. Se realizaron **cinco
recuperaciones sin volver a entrenar** las dos hipótesis.

- Estado final por semilla: dos hipótesis completas, una autoridad
  Inverse Ether Memory/RVPC2, **cero qubits activos**.
- Semilla 42: **6.162 bytes RVPC2**, 43 excepciones lógicas y
  cinco recuperaciones. Los dos modelos siguen disponibles.
- Los programas E007, incluido el selector y la transacción
  reversible, están exclusivamente en el lenguaje propio XI.
- El selector toleró entre 54 y 69 etiquetas corruptas de
  240 en tres semillas, usando un criterio comparativo estricto.
- Límite actual: dos contextos, dos señales categóricas y
  feedback binario; no se ha probado recuperación general.

[Contrato, evidencia y limitaciones de E007](docs/AI_E007_CONTEXT_VAULT.md).

## E006 — las ideas deben sobrevivir una prueba independiente

En `ai/xi/e006/` hay una entidad nueva (esquema 6) que entrena
relaciones candidatas en modo sombra. El `jury.xi` las compara con
las mismas relaciones desactivadas, sobre 240 experiencias no vistas,
**sin adaptar ninguno de los dos durante el examen**.

- Si el candidato mejora al menos 30/240 y acierta al menos 205/240,
  se promociona como conocimiento activo y se sella.
- De lo contrario, los descriptores espurios y las etiquetas de
  validación se eliminan transaccionalmente del RVPC2.
- La inferencia `infer-grid.xi` no utiliza relaciones no aprobadas.
  Un modelo sellado rechaza entrenamientos improvisados.

**GitHub Actions E006:** [ejecución 40283557920](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40283557920).
12 agentes/controles, tres semillas, 28.800 experiencias; los tres
modelos XOR aprobaron con **240/240** sobre un holdout nuevo y **9/9**
controles negativos/adversos fueron rechazados. Se verificó rollback,
ausencia de etiquetas persistentes, inferencia sellada y rechazo de
juicios repetidos.

[Contrato técnico y controles E006](docs/AI_E006_SHADOW_JURY.md).

**Próxima limitación:** preservar múltiples hipótesis para cambiar de
contexto sin perder las anteriores. E006 protege un único modelo activo;
aún no recupera automáticamente conocimientos previos.

## E005 — relaciones que no existían al nacer

En `ai/xi/e005/` están los programas propios:

- `birth.xi`: nace una entidad con tres pesos base y **cero relaciones
  compuestas** (esquema 5, separado de E004).
- `feed-xor.xi`, `feed-noise.xi`: generan consecuencias en el mismo
  espacio lógico con fuentes de datos desacopladas del aprendiz.
- `learn.xi`: predice antes de leer la consecuencia; tras errores
  recurrentes puede **materializar una composición de predicados**;
  guarda la nueva relación y borra el lote de observaciones y etiquetas
  en una transacción XI.
- `eval-xor.xi`, `eval-noise.xi`: prueban casos no usados en el
  entrenamiento y no modifican el estado.
- `linear-control.xi`, `rollback.xi`, `audit-clean.xi`,
  `input-fingerprint.xi` y `seed-*.xi`: controles de crecimiento,
  aislamiento, compacidad, igualdad de entradas y semillas.

La gramática probada combina los signos de dos señales y tiene
**un máximo de cuatro relaciones materializables**. Todavía no permite
la invención universal de reglas ni identifica automáticamente si el
crecimiento es espurio. La siguiente fase debe añadir selección basada
en utilidad, poda y recuperación de hipótesis, sin introducir motores
paralelos ni otros lenguajes para la inteligencia.

## Evidencia reproducible

[GitHub Actions E005, 3 semillas y 9 agentes/control](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40279710145):
**12 generaciones × 200 experiencias por agente**, es decir, 21.600
ejemplos de entrenamiento en toda la campaña. Después se evaluaron
240 muestras de magnitudes no vistas por cada agente.

| Semilla | Modelo con relaciones nuevas | Lineal con los mismos ejemplos | Entrenado con ruido, evaluado en XOR |
|---|---:|---:|---:|
| 19 | 240/240 | 118/240 | 133/240 |
| 42 | 240/240 | 114/240 | 114/240 |
| 91 | 240/240 | 119/240 | 121/240 |

Después del entrenamiento, la entidad con semilla 42 conserva cuatro
relaciones en un archivo RVPC2 de **5.642 bytes, 22 excepciones lógicas**
y **cero qubits activos**. Antes de eliminar el lote temporal ocupaba
18.673 bytes y 540 excepciones: **69,8 % menos bytes** para el mismo
problema controlado y las mismas 12 generaciones.

La validación incluye controles adversos, captura de un artefacto
RVPC2 reutilizable, rechazo de reentrenamiento de un lote consumido,
conservación exacta del archivo durante evaluación y rollback tanto
para un archivo nuevo como para un destino existente.

[Arquitectura, limitaciones, protocolo y corrección del control negativo](docs/AI_E005_RELATIONS.md).

## Ejecutar y continuar

Se utiliza REVERSE-PC integrado en el commit
`6d4de14a2dfbce4b8a7f1cb50e29d11b9073fe98` y su dependencia
Mundo X comprobada en
`e2778d962af22f6f1a0794058dd4685fc2573966`. Tras compilar
el intérprete XI original, situarse en el repositorio BBY Q:

```sh
reverse_pc init blank.rvp
reverse_pc run ai/xi/e005/birth.xi blank.rvp born.rvp
reverse_pc run ai/xi/e005/seed-42.xi born.rvp entity.rvp
reverse_pc run ai/xi/e005/feed-xor.xi entity.rvp observations.rvp
reverse_pc run ai/xi/e005/learn.xi observations.rvp generation1.rvp
reverse_pc run ai/xi/e005/audit-clean.xi generation1.rvp clean.rvp
reverse_pc run ai/xi/e005/eval-xor.xi generation1.rvp tested.rvp
# Para continuar, usar generation1.rvp como entrada de feed-xor.xi
```

No es necesario conservar `observations.rvp` para que la entidad
recuerde: `generation1.rvp` contiene sus relaciones. No mezclar
directamente un estado E004 y uno E005, pues tienen esquemas diferentes.

## E004 y laboratorio anterior

La [E004](docs/AI_E004_OWN_LANGUAGE.md) se conserva en `ai/xi/`:
8.000 experiencias sintéticas, 227/240 aciertos para su tarea lineal,
sin pérdida de la lógica ni necesidad de modelos externos.

El laboratorio óptico histórico Galaxy Watch4 Classic sigue separado
en `app/`, `ROADMAP.md` y `docs/RECEPTOR_OPTICO.md`.

## Dependencia temporal declarada

**Todo el algoritmo de aprendizaje E005 está escrito en XI.** El
intérprete actual de REVERSE-PC todavía utiliza un **bootstrap C++**
preexistente: no se ha logrado aún compilación nativa autoalojada.
MX (`.mx`) continúa siendo la futura fuente canónica; XI es un
dialecto de runtime propio que debe converger hacia MX. No confundir
este experimento de aprendizaje simbólico en CPU clásica con
ventaja cuántica, conciencia ni inteligencia general.
