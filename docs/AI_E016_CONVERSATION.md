# E016 — Componer frases y sostener diálogos cortos

Continúa el checkpoint E015 auténtico, sin repetir el currículo anterior.
Base de código: `c0e6b9f3df68f1d614ac00f68a615265d656c08b`.
El runtime REVERSE-PC permanece en
`6d4de14a2dfbce4b8a7f1cb50e29d11b9073fe98`, y Mundo X en
`e2778d962af22f6f1a0794058dd4685fc2573966`.

## Comportamiento comprobado

```text
Usuario: hola
BBY Q:   Hola. Soy BBY Q.
Usuario: ana tiene dos manzanas.
BBY Q:   Ana tiene dos manzanas.
Usuario: ella recibe tres más
BBY Q:   Ana tiene cinco manzanas.
Usuario: ¿cuántas tiene ella?
BBY Q:   Ana tiene cinco manzanas.
Usuario: ¿qué es un gato?
BBY Q:   Un gato es un mamífero.
Usuario: ¿y un perro?
BBY Q:   Un perro es un mamífero.
```

La preferencia de salida puede ser inglés sobre la misma autoridad:
`how many apples does she have?` → `Ana has five apples.`.
Idioma de entrada e idioma de salida son independientes; no se afirma
detección automática del idioma preferido.

La superficie conversacional añade saludos, presentación, una respuesta
de estado del software, preguntas naturales con artículos, «háblame de» /
«tell me about», frases de cantidades, seguimiento de persona/objeto y
continuaciones de preguntas factuales. Los datos siguen siendo las cuentas
y el conocimiento acotado anteriores. No añade un modelo de terceros.

## Aprendizaje y mecanismos diseñados

| Elemento | Qué se enseña o programa |
|---|---|
| Orden de las frases de cantidades | XI induce cuatro posiciones desde cuatro demostraciones ES/EN etiquetadas con actor, objeto, verbo y número |
| Habilitación del orden | Requiere variar persona, objeto y cantidad; repetir ejemplos o variar solo parte no basta |
| Singular, plural, «un/una/one», artículos | 58 frases nominales supervisadas; el plural requiere dos cantidades distintas |
| Vocabulario nuevo | 43 entradas al final del léxico existente; 471 en total |
| Persona, objeto y compatibilidad de pronombres | 21 etiquetas de papel conversacional, explícitas y supervisadas |
| Marcadores funcionales | 26 asociaciones supervisadas; la gramática que los usa está programada |
| Saludos, presentación, desconocimiento y prefijos | 16 textos fijos enseñados; no son generación libre |
| Cuentas, aritmética, hechos y deducción | Capacidades E010–E015 anteriores, conservadas |
| Construcción de texto y continuidad | Nuevos módulos XI; Python solo enseña, transporta y examina |

El profesor de orden recibe una respuesta de ejemplo y las identidades
semánticas que aparecen en ella. No proporciona un vector de posiciones.
En un control independiente, enseñar orden verbo/persona/cantidad/objeto
cambia la salida a `Tiene Eva siete libros.` con el mismo ejecutable.
La frase de cada cuenta se construye con la cantidad vigente, no con una
respuesta del examen guardada en el estado.

Las preguntas factuales reutilizan el grafo y la cadena de evidencia reales.
Por ejemplo, una deducción puede responder:

```text
Un gato es un organismo. [gato -> mamífero -> vertebrado -> organismo]
```

Los artículos se añaden para las categorías que recibieron esa enseñanza.
Las demás relaciones conservan los nombres compartidos. Los guiones bajos
de nombres técnicos se muestran como espacios. Todavía no hay un sistema
general de concordancia, flexión o redacción de explicaciones abiertas.

## Referentes, dudas y persistencia

La conversación conserva una referencia de cuenta (persona y objeto), una
referencia factual (sujeto y predicado) y el tema del último turno apoyado.
Estos descriptores viven dentro del RVPC2 original.

- `ella/she/her` y `él/he/him` solo se resuelven cuando el último tema es una
  cuenta con una persona compatible. No se infieren identidades ni género
  de una persona real.
- Una frase con pronombre y otro nombre propio se rechaza por ambigüedad
  en esta gramática. No se implementó resolución general de correferencias.
- `¿y las peras?` cambia el objeto, mientras `¿y Luis?` cambia la persona
  dentro del mismo dominio de cuentas.
- Tras una pregunta factual, `¿y un perro?` conserva el predicado de esa
  pregunta y consulta el nuevo sujeto.
- Una referencia sin antecedente produce una petición de aclaración. Una
  palabra desconocida o una pregunta fuera del alcance no crea conocimiento.
- Un turno fallido invalida el tema para posteriores elipsis. No borra
  las cuentas ya guardadas ni sustituye los hechos anteriores.
- Se puede continuar después de cerrar y volver a abrir el proceso.
  Reiniciar el episodio borra también los descriptores de conversación.

Una cuenta admite `recibe tres`, `ella recibe tres más` o
`how many does she have?` dentro de su contexto. «Tiene dos más» se rechaza:
el efecto aprendido de «tiene» es asignación y no se reinterpretó como suma.
Una interrogación no puede convertirse en una asignación silenciosa.

Los errores de guardado y las excepciones XI posteriores a actualizar el
candidato conservan tanto el archivo como la cuenta y el referente cargados.
La respuesta se anuncia únicamente después del guardado atómico del
adaptador original. No se añadió otra autoridad persistente.

## Organización del estado

Región nueva: `7700000000000000000`.

| Posiciones relativas | Contenido |
|---|---|
| `+0..2` | Esquema |
| `+4..15` | Referencias y tema de conversación |
| `+16..255` | Trabajo temporal, limpio al finalizar |
| `+513..538` | Conceptos funcionales enseñados |
| `+1000`, `+1032` | Orden y dos testigos por idioma |
| `+2000..6095` | Textos supervisados de ocho actos en dos idiomas |
| `+10000+ID*4` | Papeles y compatibilidad de pronombres |
| `+100000+ID*224` | Formas nominales ES/EN y testigos de plural |

El estado publicado conserva el núcleo, enlaces y cada byte aprendido del
padre, con las únicas ampliaciones declaradas del léxico y la región nueva.
Contiene cero cuentas o referencias ficticias del examen.

## Pruebas y mediciones

La campaña local aprueba **4.668 verificaciones**:

- 120 diálogos de ocho turnos: **960 turnos** con Eva/Tom y libros/pelotas,
  separados de los ejemplos de orden Ana/Luis y manzanas/peras. Los nombres
  y formas nominales sí se enseñaron por separado.
- 384 consultas/acciones de concordancia y cantidades 0, 1, 2, 9, 10 y
  65535, en ambos idiomas; capacidad real de 16 cuentas.
- Los 1.522 casos factuales anteriores con la nueva superficie de frases y
  otros 1.522 con exactamente la salida compacta anterior.
- Enseñanza repetida, variación insuficiente, orden invertido, formas
  contradictorias, plural incompleto y corrupción detectada por auditoría.
- Ambigüedad, palabras desconocidas, negación fuera del alcance, preguntas
  con apariencia de acción, cambio de tema y pérdida del antecedente.
- Reinicio, rollback de cuenta y contexto, clientes públicos, protocolo
  compacto, compatibilidad del padre y caché de los módulos nuevos.

La regresión E015 independiente también aprueba sus 3.080 verificaciones
y reproduce exactamente el checkpoint E015 publicado.

La enseñanza/configuración de las 168 entradas de esta etapa tardó **2,12 s**
en la campaña local. Esa cifra mide aplicar estas lecciones acotadas a un
runtime ya compilado; no mide desarrollar un idioma, el programa ni las
comprobaciones completas.

| Medición Linux x86-64 | Resultado |
|---|---:|
| Acciones con elipsis de los diálogos nuevos, mediana / p95 | 12,26 / 15,31 ms |
| Pregunta explícita de cuenta, sesión intercalada | 11,03 ms |
| Deducción factual con frase y prueba, sesión intercalada | 9,24 ms |
| RAM residente en la sesión de conversación medida | 5,00 MiB |
| Estado RVPC2 publicado | 209.659 bytes |

La comparación usa exactamente el mismo checkpoint E016 para tres rutas,
40 repeticiones por caso y orden intercalado con semilla `160629`.
El protocolo compacto cuesta 2,5–6,9 % más que el código E015 en las cinco
tareas comparadas. La conversación realiza trabajo adicional y no se
presenta como una aceleración. Se conserva el guardado antes de cada
respuesta. La RAM residente se distingue del pico de arranque.

Los datos están en `docs/evidence/e016-results.json`,
`docs/evidence/e016-performance.json` y
`docs/evidence/e016-e015-regression.json`. No se midió Android, ventaja
cuántica ni una comparación de inteligencia general con modelos grandes.

## Usar y reproducir

```bash
base64 -d ai/checkpoints/BBYQ_E016_Conversation_ES_EN.rvp.gz.b64 | gzip -dc > bbyq.rvp
python3 ai/native/session_client.py /ruta/bbyq_session bbyq.rvp --language es
```

Cada línea es un turno de texto. `--language en` selecciona respuestas en
inglés. `--compact` conserva las salidas anteriores para integraciones y
comparaciones. Los checkpoints anteriores también conservan su protocolo
al usarse con el cliente nuevo; el anfitrión no analiza sus preguntas.

La CLI de un turno usa la misma ruta nativa:

```bash
bash ai/xi/knowledge/text.sh /ruta/reverse_pc bbyq.rvp 'ana tiene dos manzanas.' es
bash ai/xi/knowledge/text.sh /ruta/reverse_pc bbyq.rvp 'ella recibe tres más' es
```

Para reproducir desde el padre auténtico:

```bash
base64 -d ai/checkpoints/BBYQ_E015_Grammar_ES_EN.rvp.gz.b64 | gzip -dc > parent.rvp
python3 ai/xi/conversation/tests/native-conversation.py /ruta/reverse_pc /ruta/bbyq_session parent.rvp --out evidence/e016 --dialogs 120
```

Los límites siguen siendo 255 bytes y 15 palabras por entrada, cantidades
0–65535 y 16 cuentas por episodio. Puede mantener diálogos cortos dentro de
estas capacidades; no es conversación abierta sobre cualquier tema ni
generación neuronal de lenguaje. La salida es texto, sin síntesis de voz.
REVERSE OS permanece pospuesto.
