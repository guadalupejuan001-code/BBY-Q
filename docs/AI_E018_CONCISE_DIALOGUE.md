# E018 — Continuar el aprendizaje y responder con brevedad

Continúa el checkpoint E017 auténtico. La base de código es
`d082096bfce81be9d90266d3f813a7a71733ac7d`; REVERSE-PC permanece en
`6d4de14a2dfbce4b8a7f1cb50e29d11b9073fe98` y Mundo X en
`e2778d962af22f6f1a0794058dd4685fc2573966`.
Toda interpretación, aprendizaje, deducción y composición se ejecutan en XI,
en el mismo RVPC2. No se añade un modelo externo ni integración con REVERSE OS.

## Qué aprende esta ronda

Se aplican **50 demostraciones semánticamente etiquetadas** para inducir
25 construcciones nuevas, sin repetir las 39 anteriores. El estado llega
a **64 construcciones y 533 entradas léxicas**, con nueve formas nuevas y
dos identidades funcionales adicionales. Dos fragmentos supervisados
enseñan las conjunciones «y» y «and».

Las nuevas formas incluyen «háblame de…», «qué significa…»,
«qué es el significado de…», «me puedes decir…», «dime si…»,
«tell me whether…», «could you tell me…», preguntas con «por favor/please»
y enseñanza positiva, negativa y retirada con artículos.
«Si/if/whether» forma preguntas de verificación; no implementa razonamiento
condicional general. «Qué significa» consulta la clasificación conocida;
no convierte al modelo en un diccionario abierto.

El aprendiz de construcciones sigue recibiendo texto y etiquetas de
sujeto/predicado/objeto, y descubre sus posiciones. La preferencia de brevedad
es una **configuración explícita**, separada del aprendizaje de gramática.
No se presenta como una capacidad de redacción aprendida autónomamente.

## Respuestas comprobadas

```text
Usuario: gato es organismo?
BBY Q:   Un gato es un organismo.

Usuario: por qué?
BBY Q:   La evidencia guardada es: Un gato es un organismo. [gato --es--> mamífero --es--> vertebrado --es--> organismo]

Usuario: aprende que el neral es un mamífero
BBY Q:   Aprendí esa afirmación del diálogo.

Usuario: háblame de neral
BBY Q:   Según lo aprendido: Neral es un mamífero, un vertebrado, un animal y un organismo.

Usuario: qué estudia filosofía?
BBY Q:   Filosofía estudia conciencia y conocimiento.

Usuario: qué es algoquenoexiste?
BBY Q:   No tengo información suficiente para responder.
```

«Neral» es un nombre reservado para las pruebas. No está en el checkpoint
publicado. Las afirmaciones del diálogo siguen distinguiéndose con
«Según lo aprendido»; la brevedad no elimina esa indicación de procedencia.

## Presentación y prudencia

Una consulta normal presenta el resultado sin adjuntar automáticamente
el camino. «¿Por qué?» o «explain why…» repite la búsqueda sobre la evidencia
vigente y muestra el fundamento disponible. La búsqueda, validación de
testigos, excepciones y límites se conservan. No se trunca texto a un número
de palabras ni se dejan de examinar resultados para contestar antes.

Si una pregunta produce varios objetos para el mismo sujeto/predicado,
se enumeran todos con comas y la conjunción supervisada. Así se evita
repetir cuatro veces «Neral es…» sin perder sus cuatro clasificaciones.
La API `--compact` conserva exactamente su protocolo anterior, con pruebas.

Los textos de falta de información, evidencia insuficiente, contradicción,
ambigüedad y falta de antecedente conservan sus bytes anteriores. Abstenerse
ante información insuficiente no garantiza que toda respuesta del sistema
sea verdadera: las afirmaciones enseñadas por una persona siguen siendo
supuestos, y la gramática y el conocimiento son limitados.

## Ambigüedad descubierta y corregida

La nueva pregunta «qué significa X» competía con el patrón genérico
«alias significa referente». El selector ahora prefiere una construcción
que satisface más restricciones literales frente a otra más genérica.
Se cuentan las restricciones realmente aprendidas, sin una regla especial
para una pregunta concreta ni decisiones de lenguaje en Python.

Dos interpretaciones de igual especificidad que asignan papeles semánticos
distintos siguen produciendo aclaración. Un control enseña un orden
contradictorio con dos demostraciones y comprueba esa abstención.
Se verifican también el caso de definición más específico y la enseñanza
normal de un alias, para que la corrección no desactive esta última.

## Preservación y estado publicado

El checkpoint ocupa **298.808 bytes**. Conserva núcleo, enlaces, léxico,
construcciones, superficies y hechos aprendidos anteriormente. Solo se
actualizan los contadores declarados, la preferencia y las nuevas regiones
de registros. No se repite el currículo anterior ni se publican entidades
o afirmaciones de los diálogos del examen.

No se añaden afirmaciones sobre el mundo en esta etapa. Permanecen los
185 hechos anteriores y las 12 afirmaciones didácticas ficticias de E017.
Las dos familias de deducción son las ya calibradas: transitividad y
herencia de propiedades. Los nuevos enunciados del examen se suministran
como supuestos separados y se retiran antes de publicar el estado.

La preferencia vive en `U+3`, con `U=7800000000000000000`:
0 conserva la presentación histórica y 1 activa brevedad. El modo nativo
de configuración `open-style` acepta la preferencia en `U+316`; requiere
ambas conjunciones antes de habilitarla y rechaza valores inválidos.
Los checkpoints anteriores, cuya preferencia es 0, conservan sus respuestas.

## Pruebas y mediciones

La campaña E018 aprueba **3.905 verificaciones**:

- 60 diálogos de 12 turnos: **720 turnos** con referentes y alias que no
  aparecen en las demostraciones de sintaxis. Se examinan las 25 formas.
- Deducciones nuevas sin enseñar su consecuencia, nombres compartidos
  ES/EN, negación, retirada y pérdida del antecedente tras una duda.
- 1.522 consultas anteriores en respuesta breve y las mismas 1.522 con
  exactamente la salida compacta anterior.
- Repetición insuficiente, conflicto de interpretaciones, configuración
  inválida, incertidumbre, contradicciones y corrección de hechos anteriores.
- Cantidades, continuidad, aritmética, clientes públicos, reinicio,
  restablecimiento del episodio y rollback ante un guardado fallido.

La aplicación de este currículo a un runtime ya compilado tardó **1,41 s**.
No incluye diseñar los módulos, compilar ni ejecutar los exámenes.
La regresión E017 se registra por separado en
`docs/evidence/e018-e017-regression.json`.
Aprueba sus **4.376 verificaciones** y recupera exactamente el mismo núcleo,
memoria lógica y enlaces del checkpoint E017. Su contador de asignaciones
MXIM2 cambia por las escrituras temporales del selector; por eso difiere la
huella del archivo serializado, aunque el estado lógico es idéntico.

El benchmark intercalado usa el mismo checkpoint E018 y compara código E017,
E018 con presentación histórica y E018 breve. Tiene 40 repeticiones por
tarea, ocho tareas y semilla 180627: 960 turnos medidos, con guardado antes
de confirmar cada respuesta. Entre las dos variantes E018 solo cambia la
preferencia. Los oráculos permanecen fuera del proceso nativo.

| Tarea, mediana Linux | E017 completo | E018 completo | E018 breve |
|---|---:|---:|---:|
| Recuperación directa | 13,51 ms | 13,29 ms | 13,71 ms |
| Deducción anterior | 13,56 ms | 13,61 ms | 13,82 ms |
| Varios resultados | 16,22 ms | 16,36 ms | 15,03 ms |
| Definición de concepto nuevo | 30,18 ms | 29,60 ms | 27,56 ms |
| Deducción de concepto nuevo | 19,85 ms | 19,85 ms | 17,77 ms |
| Explicación explícita | 21,60 ms | 21,65 ms | 22,01 ms |
| Falta de información | 13,12 ms | 12,97 ms | 12,97 ms |

En el ejemplo de deducción nueva, la respuesta normal pasa de 106 a
43 bytes UTF-8; su explicación explícita mantiene los 111 bytes.
La definición nueva pasa de 110 a 84 bytes conservando sus cuatro objetos.
La respuesta de desconocimiento mantiene sus 48 bytes.

Esta medición muestra menos texto y ahorro de tiempo en algunos casos,
con pequeñas diferencias y costes en otros. No demuestra una aceleración
general del aprendizaje ni ventaja cuántica. La RAM residente medida de la
sesión breve fue **6,63 MiB**, distinta del pico de arranque de 13,25 MiB.
No se midió Android ni consumo de batería.

Los resultados, diagnóstico antes/después y benchmark están en
`docs/evidence/e018-*.json`. El manifiesto fija las huellas de los datos,
el padre y el checkpoint. La CI vuelve a entrenar y compara el estado lógico
completo con la versión publicada.

## Uso y reproducción

Usar con el código E018 o posterior y el adaptador del runtime fijado:

```bash
base64 -d ai/checkpoints/BBYQ_E018_Concise_Dialogue_ES_EN.rvp.gz.b64 | gzip -dc > bbyq.rvp
python3 ai/native/session_client.py /ruta/bbyq_session bbyq.rvp --language es
```

Cada línea es un turno. `--language en` selecciona inglés; `--compact`
selecciona el protocolo anterior. También se puede usar la CLI de un turno:

```bash
bash ai/xi/knowledge/text.sh /ruta/reverse_pc bbyq.rvp 'gato es organismo?' es
bash ai/xi/knowledge/text.sh /ruta/reverse_pc bbyq.rvp 'por qué?' es
```

Para continuar el entrenamiento desde el padre auténtico:

```bash
base64 -d ai/checkpoints/BBYQ_E017_Open_Learning_ES_EN.rvp.gz.b64 | gzip -dc > parent.rvp
python3 ai/xi/open/tests/native-e018.py /ruta/reverse_pc /ruta/bbyq_session parent.rvp --out evidence/e018 --dialogs 60
```

Se mantienen 255 bytes y 15 palabras por entrada, 64 nodos de búsqueda,
32 nodos de prueba y ocho resultados. Las 64 construcciones actuales
ocupan la capacidad de esta versión; ampliarla requiere desarrollo adicional.
La salida sigue siendo texto y la conversación sigue acotada.
