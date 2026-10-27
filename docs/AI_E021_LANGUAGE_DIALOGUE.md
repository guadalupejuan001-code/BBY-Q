# E021 — Campaña de lenguaje y diálogo acotado en XI

Continúa el E020 identificado por SHA-256
`9fdf0b3f5300ea63607f6c0656d09c3ad1bfb7dbf96a167e775c48c35ae4fafc`.
No repite el currículo antiguo, no incorpora pesos de otro modelo y no integra
REVERSE OS. Aprendizaje, interpretación, búsqueda de evidencia, contexto y
respuesta siguen dentro de XI sobre el mismo RVPC2.

## Qué se entrenó realmente

El currículo original añade 128 construcciones: 224 contando las 96 antiguas.
Los **96 registros anteriores** permanecen en su banco independiente,
conservados byte por byte; los **128 nuevos** ocupan otro banco. Se enseñan
109 entradas léxicas adicionales, 648 entradas en los registros K+U. Esa cuenta
es comparable con las 539 de E019/E020; excluye los nombres originales de E010.
Contando también esos nombres y eliminando duplicados hay 674 formas distintas.
El pequeño léxico de operadores E020 se conserva aparte.

Hay 256 presentaciones iniciales de texto con papeles S/P/O supervisados.
El algoritmo XI intersecta posibilidades literales y variables, y exige
variación para promover marcos con argumentos. La semántica de consultar,
enseñar, explicar o retomar está diseñada; se aprende qué formas la invocan
y dónde están sus argumentos. Los ejemplos sintácticos no afirman su contenido
como verdadero: una frase combinada sobre dos conceptos cualesquiera no añade
un hecho al mundo del agente.

Después se consumen **2.119.224 secuencias distintas de conceptos**, con sus
etiquetas S/P/O, en 4.192 lotes de entrenamiento. Cada secuencia completa entra
al runtime; XI contrasta todos sus tokens con los papeles y literales inducidos.
Los primeros ejemplos variados ya permiten inducir los marcos; el volumen posterior es
consolidación y comprobación masiva, no millones de significados adicionales.
No se presenta como descubrimiento de una gramática universal.

El producto cartesiano tiene 128 sujetos, cuatro predicados y 128 objetos para
cada una de 32 construcciones ternarias (2.097.152 secuencias). Las 96 restantes
aportan 22.072 secuencias de preguntas de propiedad, definiciones, contexto,
recuperación de temas y actos sociales. No se inflan los marcos sin argumentos
con miles de repeticiones. El corpus se genera de forma determinista y se
publican SHA-256 de las secuencias codificadas y de sus frases de superficie.
El flujo masivo usa **tokens de conceptos**, no tokenización de millones de
párrafos originales. Las presentaciones iniciales y los exámenes conversacionales
sí entran como bytes de texto y se interpretan en XI.

Se ejecutan 4.840 comprobaciones estructuradas de validación: **4.816 usan
combinaciones fuera del entrenamiento**, con sujetos/objetos reservados y
predicados diferentes. Las otras **24 son revisiones de marcos literales**;
no pueden demostrar transferencia a argumentos nuevos porque no tienen
argumentos. Estas dos cantidades permanecen separadas en la evidencia.
Un lote incorrecto se rechaza entero sin modificar el estado de origen.

## Composición más allá de una frase completa

El diagnóstico de desarrollo mostró que añadir marcos exactos dejaba sin
resolver reformulaciones nuevas. Por eso se añade una vía compositiva diseñada
en XI y habilitada por diez lecciones de señales: dos grafías interrogativas,
seis conceptos de veto global y dos vetos inmediatamente anteriores a la
interrogación.
Las grafías e identidades se aprenden en datos; no están en el código del parser.

Una construcción completa reconocida siempre gana. Si no existe, una señal
interrogativa aprendida puede delimitar una cláusula que contiene exactamente
un sujeto y un predicado conocidos, más palabras funcionales conocidas. El
preámbulo puede tener palabras nuevas; un contenido desconocido dentro de la
cláusula, varios sujetos o predicados, negación, enseñanza o referencias
ambiguas impiden esta vía. Un `por/para` inmediatamente anterior a `qué` requiere
otra interpretación y también se rechaza en esta vía. La numeración de una
pregunta se permite antes de la señal, nunca como sujeto factual.

Esta generalización está restringida a consultas de propiedad. Nunca escribe
hechos o vocabulario y no adivina el significado de palabras nuevas del
contenido. Admitir un preámbulo nuevo no equivale a comprender su intención
completa. Por ejemplo:

```text
Usuario: aprende que neral es clasea
BBY Q:   Aprendí esa afirmación del diálogo.
Usuario: por curiosidad qué requiere neral
BBY Q:   Según lo aprendido: Neral requiere agua.
Usuario: I was wondering what neral requires
BBY Q:   From the taught statements: Neral requires water.
```

El idioma de salida se configura en el cliente; no se detecta automáticamente.
Las relaciones de clase y requisitos didácticos vienen del padre. Las frases
compuestas y los nombres nuevos del examen no se publican en el conocimiento.

## Diálogo y contexto

Se enseñan ocho respuestas ES/EN de cortesía, estado funcional, capacidades,
límites y petición de aclaración. Son fragmentos supervisados, no generación
libre de prosa ni afirmaciones de sentimientos o conciencia.

La memoria conserva los **ocho últimos sujetos factuales apoyados**, con su
último modo de pregunta, predicado y objeto. `volvamos a X` busca ese sujeto;
`retoma el tema anterior` selecciona el segundo tema más reciente. Se restaura
la pregunta, no una respuesta: se vuelve a buscar evidencia. Una retirada,
una excepción negativa o una contradicción cambia la respuesta al retomarla.
Los alias comparten la identidad, los temas más antiguos se expulsan y una
referencia que falta pide aclaración. El contexto persiste entre procesos;
`reset-episode.xi` borra las referencias y conserva los hechos aprendidos.
Esto no es resolución general de correferencias entre personajes.

## Exámenes y comparación reproducible

El examen principal transfiere todas las construcciones a ocho diálogos con
nombres nuevos y al predicado `requiere/requires`, ausente de las secuencias
masivas. Además evalúa expulsión de temas, cortesía entre preguntas, cambios de
evidencia, contradicciones, reinicio, borrado de contexto y rollback al fallar
el guardado. Los controles de aprendizaje prueban que repetir una demostración
no induce sus variables; invertir la supervisión S/O en una copia experimental
cambia su interpretación con el mismo código y la misma frase.

Se comparan checkpoints E017, E018, E019, E020 y E021 con el mismo runtime,
fuente de inferencia, entradas, preparación y examinador. Varía el estado
aprendido. Las 128 sondas de marcos nuevos incluyen sujetos y predicados
reservados. Se ignora una prueba añadida espontáneamente al puntuar respuestas
no explicativas, para no penalizar la mayor verbosidad de E017.

Las 16 reformulaciones iniciales se etiquetan como **diagnóstico de desarrollo**:
se usaron para detectar la carencia, por lo que no se presentan como examen
ciego después de la corrección. Un archivo independiente del currículo fija
12 consultas con preámbulos nuevos y 12 controles de abstención. También se
miden 32 consultas antiguas compartidas y seis operadores E020. Las puntuaciones
son de estas tareas concretas, no porcentajes de inteligencia o lenguaje general.

| Estado | Construcciones | Registro léxico K+U | Marcos nuevos | Preguntas con preámbulos nuevos | Mediana 32 consultas comunes | Estado guardado |
|---|---:|---:|---:|---:|---:|---:|
| E017 | 39 | 524 | 0/128 | 0/12 | 14,03 ms | 279.677 B |
| E018 | 64 | 533 | 0/128 | 0/12 | 14,78 ms | 298.808 B |
| E019 | 96 | 539 | 0/128 | 0/12 | 17,81 ms | 319.274 B |
| E020 | 96 | 539 | 0/128 | 0/12 | 19,69 ms | 325.721 B |
| E021 | 224 | 648 | 128/128 | 12/12 | 20,22 ms | 465.830 B |

E021 conserva 32/32 consultas compartidas, 6/6 operaciones E020 y 12/12
controles de abstención de la prueba compositiva. Las 16 reformulaciones de
desarrollo pasan de 0/16 a 7/16; las nueve restantes siguen fuera de alcance.
La campaña local aprueba **5.880 comprobaciones de consulta y controles**.
Las 1.024 consultas de marcos nuevos tienen mediana de 34,42 ms y p95 de
49,03 ms. Las doce consultas compositivas independientes tienen mediana de
56,15 ms. Son medidas de una ejecución local, incluido guardar antes de
confirmar; no demuestran una diferencia estadística de velocidad.

La fase masiva tarda **337,92 s** (6.271 secuencias/s); las presentaciones
iniciales tardan 12,34 s. Excluyen desarrollo, compilación y exámenes.
El proceso de transferencia informa 8.152 KiB residentes y 22.336 KiB de pico.
Los datos completos están en `docs/evidence/e021-results.json` y la comparación
en `docs/evidence/e021-comparisons.json`; la CI conserva la transcripción completa.

Se vuelven a examinar las 1.522 consultas anteriores en las dos superficies,
las construcciones E018/E019 con nuevos sujetos y las 1.024 consultas numéricas
E020 fuera de su cuadrícula. La CI reproduce la campaña completa y compara
núcleo, bytes lógicos y enlaces del checkpoint publicado. La revisión MXIM2
puede variar sin cambiar ese estado lógico.

## Estado compacto, reproducción y límites

La región nueva es `L=8000000000000000000`: cabecera y contadores, señales desde
L+1000, construcciones desde L+10000, y ocho descriptores de contexto en
L+128..255. Cada construcción conserva sus restricciones y testigos iniciales,
no todas las secuencias. Los lotes temporales L+100000..118431 y controles
L+16..63 quedan en cero. Los hechos, reglas, operadores y registros anteriores
se conservan. No se añaden afirmaciones del examen al estado publicado.

El estado publicado ocupa **465.830 bytes**, frente a 325.721 del padre
(+140.109 bytes). SHA-256:
`3246c34cb2d51037476f206020c55d8453a3060a4d2c511887c4b3fb3bdb4b1b`.
La auditoría informa 18.416 excepciones clásicas y cero enlaces cuánticos;
no se guarda el corpus completo.

El programa sigue siendo fuente XI textual; el modo `--compact` es el protocolo
de respuesta anterior. La compactación de regularidades sintéticas no demuestra
compresión universal ni estados globalmente mínimos. El adaptador nativo C++
no cambió; Python es currículo, transporte y examinador. No interpreta texto
por el agente durante la inferencia.

REVERSE-PC sigue fijado en `6d4de14a2dfbce4b8a7f1cb50e29d11b9073fe98` y Mundo X en
`e2778d962af22f6f1a0794058dd4685fc2573966`. Se mide Linux, sin qubits activos;
no se midió Android ni se afirma ventaja cuántica o aceleración general.
Persisten 255 bytes y 15 palabras por turno, ocho temas, 64 nodos de búsqueda,
32 de prueba y ocho resultados. No hay interpretación libre de párrafos largos,
generación abierta ni aprendizaje autónomo de cualquier algoritmo. Esta campaña
permite más diálogo acotado, **no alcanza conversación abierta general**.

```bash
python3 ai/xi/lingua/tests/native-language.py /ruta/reverse_pc --out evidence/e021-training --batch 512
python3 ai/xi/lingua/tests/native-e021.py /ruta/reverse_pc /ruta/bbyq_session evidence/e021-training/unsealed.rvp evidence/e021-training/training.json --out evidence/e021 --dialogs 8
base64 -d ai/checkpoints/BBYQ_E021_Language_Dialogue_ES_EN.rvp.gz.b64 | gzip -dc > bbyq.rvp
python3 ai/native/session_client.py /ruta/bbyq_session bbyq.rvp --language es
```
