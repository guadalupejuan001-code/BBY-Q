# E017 — Aprendizaje durante el diálogo y fundamentos de conversación abierta

Continúa el checkpoint E016 auténtico sobre el código
`af1f9bff0e95cf78f0e03b5c289f7bd4dcdb9aa3`. Toda interpretación,
aprendizaje y deducción nueva se ejecutan en XI. REVERSE-PC permanece en
`6d4de14a2dfbce4b8a7f1cb50e29d11b9073fe98` y Mundo X en
`e2778d962af22f6f1a0794058dd4685fc2573966`. No hay modelo externo ni
integración con REVERSE OS.

Esta etapa inicia la ampliación hacia conversaciones menos rígidas.
**No alcanza conversación abierta general**: aprende construcciones
supervisadas, vocabulario, alias y afirmaciones, y razona dentro de dos
familias diseñadas. La salida es texto.

## Diagnóstico y cambios

E016 rechazaba las nuevas paráfrasis, las enseñanzas de vocabulario y las
peticiones de explicación del diagnóstico de 18 turnos. Cuatro controles
anteriores funcionaban. Los registros antes/después están versionados;
una negación sin evidencia debe continuar produciendo abstención.

| Necesidad | Implementación comprobable |
|---|---|
| Más formas de preguntar y enseñar | 39 construcciones inducidas desde ejemplos y etiquetas semánticas |
| Nuevas palabras durante el diálogo | Léxico adicional con identidades de 16 bits; referencia directa a conceptos antiguos |
| Dos nombres para un concepto | Alias aprendidos, compartidos por ES/EN, con detección de colisiones |
| Conocimiento de una conversación | Enseñanza explícita positiva/negativa; consultas ordinarias no asignan conceptos |
| Corregir una enseñanza | Retirar la evidencia del diálogo sin borrar la base anterior |
| Deducir sobre entidades nuevas | Grafo unificado de evidencia anterior y enseñada |
| Ampliar el razonamiento | Calibración supervisada entre transitividad y herencia de propiedades |
| Pedir el fundamento | Búsqueda de nuevo sobre la evidencia actual y camino con relaciones |
| Reinicios y errores de guardado | Mismo RVPC2, respuesta tras guardar; reversión del candidato completo |

La gramática sí se amplía, porque limitarse a añadir palabras no permitía
interpretar nuevas formas de frase. El aprendiz recibe el texto y los
conceptos semánticos esperados; descubre qué posiciones corresponden a
sujeto, predicado y objeto. Repetir una demostración no habilita una
construcción. Debe haber variación suficiente para separar sus papeles.
El intérprete es genérico para esas construcciones: no contiene un caso
distinto para cada entidad del examen.

Las formas de saludo, confirmación, desconocimiento y aclaración son
lecciones de texto fijo. La construcción de cláusulas usa las identidades,
nombres y formas nominales aprendidas. No se presenta como redacción libre.

## Ejemplo real de la prueba

```text
Usuario: aprende que neral es mamífero
BBY Q:   Aprendí esa afirmación del diálogo.

Usuario: neral es organismo?
BBY Q:   Según lo aprendido: Neral es un organismo. [neral --es--> mamífero --es--> vertebrado --es--> organismo]

Usuario: por qué?
BBY Q:   La evidencia guardada es: Neral es un organismo. [neral --es--> mamífero --es--> vertebrado --es--> organismo]

Usuario: michi significa gato
BBY Q:   Aprendí ese nombre para el mismo concepto.

Usuario: qué es michi?
BBY Q:   Un gato es un mamífero.
```

`neral` es un nombre de prueba, no un hecho científico incorporado al
modelo publicado. La entrada de enseñanza es una afirmación del usuario;
el prefijo de respuesta indica esa procedencia.

También se comprueban `explícame qué es un gato`,
`quisiera saber qué es neurona`, `is it true that cat is mammal?`,
`learn that ...`, `explain why ...`, `... means ...` y
`forget that ...`, dentro de las construcciones enseñadas.
El idioma de salida se selecciona con `--language es|en`; no se afirma
traducción general de términos nuevos sin un nombre enseñado.

## Enseñanza, contradicciones y razonamiento

Solo las construcciones explícitas de enseñanza modifican el conocimiento:
`aprende que`, `recuerda que`, `learn that`, alias y retirada.
Una interrogación que se parezca a una orden no puede enseñar ni borrar.
Se resuelven de nuevo las palabras después de cada alta para que
`aprende que mismo es mismo` use una única identidad.
Una palabra que necesitaría dos papeles incompatibles en la misma lección
se rechaza antes de crear conceptos.

Las afirmaciones positivas y negativas se guardan por separado. Si se
enseñan ambas para el mismo triple, se pide una corrección y no se elige
una por su orden temporal. Esto también protege los hechos anteriores:
enseñar `gato no es mamífero` bloquea la respuesta contradictoria en las
dos superficies, sin cambiar ningún byte de la evidencia antigua.
`olvida que gato es mamífero` retira las polaridades añadidas por diálogo
y permite recuperar la evidencia original.

La calibración de reglas recibe consecuencias observadas con dos testigos
distintos. Selecciona entre **dos familias ya implementadas**, no inventa
reglas arbitrarias:

- Transitividad del mismo predicado: S→A y A→O permiten S→O.
- Herencia: S es A, y A tiene una relación P con O, permiten S P O.

El currículo nuevo incluye **12 afirmaciones didácticas ficticias**
identificadas en `reasoning-v1.psv`. Son cuatro tríos de ejemplos con
nombres artificiales, no conocimientos objetivos nuevos. Calibran
`requiere/requires` como herencia y `alcanza/reaches` como transitividad.
La prueba separada enseña al mismo predicado otra familia y obtiene el
comportamiento correspondiente con el mismo programa.

Repetir un testigo no basta. Un caso compatible con ambas familias no
autoriza escoger una. Las deducciones vuelven a verificar los testigos;
retirar o contradecir una premisa invalida la regla hasta restaurarla.
Las excepciones negativas directas o intermedias impiden atravesar una
ruta que no está respaldada.

Las preguntas de propiedades también pueden recoger resultados inferidos.
Un resultado singular muestra su camino real. Una lista con varios
resultados no recibe un único camino como si justificara todos.
`por qué` consulta de nuevo la memoria vigente, y no reutiliza una
conclusión guardada como evidencia. Un cambio de tema, una enseñanza o un
reinicio de episodio invalida ese antecedente.

## Gramática de las respuestas

Se reutilizan los artículos y las formas nominales de E016. En inglés se
enseñan seis bases verbales para negaciones como `does not require`.
Si un predicado nuevo carece de esa forma supervisada, se utiliza la
construcción metalingüística enseñada `It is false that ...`, en lugar
de inventar una flexión. Falta un sistema general de conjugación,
concordancia, discurso libre y resolución de referentes.

## Estado y límites

La región E017 comienza en `7800000000000000000`, dentro del mismo RVPC2.
El núcleo, enlaces y **todos los bytes lógicos del padre fuera de esta
región son idénticos** en el checkpoint publicado. Se conservan las 471
entradas léxicas y los 185 hechos anteriores. No se repite su entrenamiento.

El checkpoint nuevo tiene **279.677 bytes**, con **524 entradas léxicas**
totales y 12 afirmaciones didácticas de esta etapa. No incluye las entidades,
alias, cuentas ni afirmaciones reservadas para el examen.

| Recurso | Límite de esta implementación |
|---|---:|
| Entrada | 255 bytes y 15 palabras |
| Entradas léxicas adicionales | 2.048 |
| Afirmaciones registradas adicionales | 1.024 |
| Construcciones | 64 |
| Identidades de conceptos | 16 bits; 65.534 como máximo |
| Nodos por búsqueda / camino | 64 / 32 |
| Resultados por consulta | 8 |

La saturación devuelve un mensaje de límite, no una negación falsa.
No es vocabulario ilimitado ni razonamiento general.
El reinicio del episodio conserva lo enseñado y borra las referencias de
conversación; no reinicia el aprendizaje.

## Verificación

La campaña local aprueba **4.376 verificaciones**:

- 80 diálogos nuevos de ocho turnos: **640 turnos**, con conceptos y alias
  que no aparecen en las demostraciones de construcciones.
- 1.522 casos anteriores con la superficie conversacional y los mismos
  1.522 con la salida compacta exacta, además de cantidades y aritmética.
- Crecimiento con 280 entidades nuevas: **804 entradas léxicas**; consulta
  y persistencia de identidades superiores a 512.
- Repetición y variación insuficiente, construcciones contradictorias,
  papeles incompatibles, colisiones de nombres y palabra autorreferente.
- Contradicciones con hechos nuevos y anteriores, retirada y restauración,
  excepciones intermedias, testigos de reglas obsoletos y familias ambiguas.
- Límites de búsqueda, reinicio, caché de fuentes y reversión completa ante
  fallo de guardado o excepción XI tras modificar el candidato.

La aplicación del currículo nuevo tardó **2,92 segundos** en esta campaña.
Los razonamientos de los diálogos reservados tuvieron mediana **21,30 ms**
y p95 **28,96 ms**. Son mediciones de este currículo y estas tareas.

La regresión independiente de E016 también aprueba sus **4.668 verificaciones**
y reproduce exactamente el checkpoint E016 publicado. Sus resultados están
en `docs/evidence/e017-e016-regression.json`.

Los oráculos, etiquetas y generación de casos están fuera de la inferencia:
el proceso residente recibe únicamente texto y la preferencia de idioma.
Las pruebas verifican también que consultas y auditorías no cambien el
conocimiento, que el trabajo temporal quede limpio y que un error posterior
a actualizar vocabulario, hechos o referencia de explicación revierta tanto
el archivo como el candidato cargado.

El cliente de transporte ahora convierte una tubería cerrada en el error
nativo de arranque y no oculta ese diagnóstico durante el cierre.
La prueba de un escritor bloqueado conserva el bloqueo ajeno; no se añade
ninguna eliminación automática de bloqueos.

## Rendimiento medido

La comparación intercalada usa el mismo checkpoint E017 en código E016
compacto, E017 compacto y E017 conversacional, 40 repeticiones por caso y
semilla 160629. El guardado sigue ocurriendo antes de confirmar cada turno.

| Tarea Linux | E016 compacto | E017 compacto | E017 conversacional |
|---|---:|---:|---:|
| Recuperación directa, mediana | 9,16 ms | 12,03 ms | 13,44 ms |
| Deducción anterior, mediana | 9,24 ms | 12,17 ms | 13,27 ms |
| Consulta de cantidades, mediana | 10,17 ms | 12,88 ms | 15,00 ms |
| Aritmética, mediana | 8,40 ms | 11,16 ms | 12,69 ms |
| Consulta desconocida, mediana | 7,68 ms | 10,88 ms | 12,03 ms |

La RAM residente de la conversación medida fue **6,88 MiB**.
La ruta nueva es más lenta en estas tareas anteriores: añade resolución,
construcciones y comprobaciones; el runtime fijado interpreta el programa
en cada turno. Esta etapa no demuestra una ventaja cuántica ni una
aceleración del aprendizaje general. No se midió Android.

Las cifras completas están en `docs/evidence/e017-results.json` y
`docs/evidence/e017-performance.json`. Los tiempos de aplicar el currículo
no incluyen desarrollar los módulos, compilar el runtime ni ejecutar los
exámenes.

## Usar y reproducir

```bash
base64 -d ai/checkpoints/BBYQ_E017_Open_Learning_ES_EN.rvp.gz.b64 | gzip -dc > bbyq.rvp
python3 ai/native/session_client.py /ruta/bbyq_session bbyq.rvp --language es
```

Cada línea es un turno. `--compact` conserva la API anterior;
`--language en` elige la superficie inglesa. No se reutiliza la misma
copia de estado con dos escritores simultáneos.

Para entrenar de nuevo desde el padre exacto:

```bash
base64 -d ai/checkpoints/BBYQ_E016_Conversation_ES_EN.rvp.gz.b64 | gzip -dc > parent.rvp
python3 ai/xi/open/tests/native-open.py /ruta/reverse_pc /ruta/bbyq_session parent.rvp --out evidence/e017 --cases 80 --terms 280
```

El manifiesto fija las huellas del padre, checkpoint y datos. La CI vuelve
a entrenar y exige que el estado lógico resultante sea idéntico al
publicado, además de examinar los diálogos y las capacidades conservadas.
