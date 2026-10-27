# E020 — Millones de experiencias estructuradas, estado pequeño

Continúa el E019 auténtico (`aa8be33d964af55d9976f46745775113d6996630cbbfad3bb5c2b4d75833e9d0`).
REVERSE-PC permanece en `6d4de14a2dfbce4b8a7f1cb50e29d11b9073fe98`
y Mundo X en `e2778d962af22f6f1a0794058dd4685fc2573966`. No cambia el
bootstrap ni el formato de bytes del transporte. Toda selección de hipótesis, aprendizaje,
validación, promoción e inferencia del agente se ejecuta en XI.

## Qué significa «millones» en esta campaña

Se consumen **2.097.152 ejemplos sintéticos distintos**: ocho conceptos
numéricos opacos, cada uno con una cuadrícula de 512 × 512 pares. Es un
currículo de aritmética estructurada con consecuencias etiquetadas, no un
corpus abierto de conversaciones ni millones de afirmaciones sobre el mundo.

El profesor genera `a=0..511`, `b=1..512`. Normalmente la entrada es `(a,b)`;
para división exacta es `(a*b,b)`. Los resultados de resta incluyen negativos,
lo que distingue resta de distancia absoluta. Todos los triples de entrada
`(concepto,X,Y)` son distintos: la transformación de división es inyectiva
porque `b` es distinto de cero. No se suma repetición para alcanzar la cifra.

El orden canónico del corpus es concepto, `a`, `b`. Cada fila de la huella
contiene concepto `u8`, X `u32`, Y `u16` y consecuencia `i32`, little-endian:
**23.068.672 bytes** antes de cualquier empaquetado. SHA-256:
`85b5b9f36b9c1961c7c97610c789a352b4abc9ae264ced3b59c7f9d7eec536a3`.
El generador versionado reproduce ese flujo sin descargar pesos ni datos.

## Qué se diseña y qué se aprende

Las ocho primitivas candidatas están implementadas explícitamente en XI:
restar, sumar, multiplicar, dividir exactamente, calcular resto, mínimo,
máximo y distancia absoluta. Esta versión **no descubre sus algoritmos**.

El agente recibe solo la identidad opaca del concepto, operandos y consecuencia.
Evalúa candidatos, conserva los compatibles y exige variación de entradas.
La correspondencia entre concepto y primitiva no se suministra al aprendiz.
Después, veinte nombres de operador ES/EN se asocian por supervisión a esas
identidades, sin introducir una tabla de nombres a primitivas en el ejecutable.

| Concepto opaco | Nombres de ejemplo | Primitiva identificada |
|---|---|---|
| 1 | minimo / minimum | Mínimo |
| 2 | por / times / multiplica / multiply | Producto |
| 3 | distancia / distance | Distancia absoluta |
| 4 | suma / add | Suma |
| 5 | resto / remainder / modulo / mod | Resto |
| 6 | resta / subtract | Resta |
| 7 | maximo / maximum | Máximo |
| 8 | dividido / divided | División exacta |

La prueba contrafactual cambia las consecuencias del concepto 2 en una copia
experimental: el mismo código y el mismo nombre «por» pasan a producir el
mínimo aprendido. Esa copia no se publica. Otro control repite un único par:
aunque encaje una primitiva, la falta de variación impide promocionarla.

## Por qué cabe en la misma memoria

La región nueva es `M=7900000000000000000`. Conserva máscaras de candidatos,
identidad identificada, contadores y un primer par de entrada por concepto
como testigo de diversidad. No conserva filas completas del corpus.

| Región relativa a M | Contenido |
|---|---|
| +0..15 | Firma, versión, promoción, léxico y contadores globales |
| +16..31 | Cabecera temporal; se borra al terminar |
| +128..639 | Ocho registros de concepto de 64 posiciones lógicas |
| +1000..2023 | Hasta 32 nombres de operador, registros de 32 posiciones |
| +10000..20239 | Lote temporal máximo de 1.024 filas de diez bytes |

Se ejecutan **2.048 transacciones de aprendizaje**, cada una con 1.024
observaciones. El concepto está en la cabecera del lote; cada fila aporta
solo los diez bytes de operandos y consecuencia. Un bucle XI consume todas
las filas, contrasta sus consecuencias y borra el lote antes del commit.
Un error revierte también las filas correctas anteriores del mismo lote.

La entrada al CLI es transporte `store8`, equivalente al adaptador anterior.
Python genera estímulos y consecuencias, pero no decide el modelo del agente
ni interpreta sus consultas. Las etiquetas de evaluación textual permanecen
fuera del proceso nativo.

La sesión conversacional conserva su guardado por respuesta. La campaña
estructurada confirma por lote; no se presentan esos dos modos como si
tuvieran la misma frecuencia de persistencia ni el mismo coste por ejemplo.
Cada lote respeta el límite original de un millón de pasos XI por ejecución.

## Datos nuevos, promoción e integridad

Tras entrenar se procesan **2.048 validaciones independientes**: 256 por
concepto, con `a=700..955` y `b=1100..1865`. No se adaptan las máscaras durante
esta validación. La promoción exige una única primitiva, entradas variadas,
al menos 256 observaciones de aprendizaje y 256 de validación por concepto.
Una consecuencia errónea, un concepto inválido o un lote excesivo revierte
la transacción. El modelo promocionado rechaza más lotes improvisados.

El checkpoint publicado añade solo la región M. **Todos los bytes lógicos,
enlaces y núcleo E019 anteriores son idénticos**. Se mantienen 539 entradas
en el registro lingüístico E012+E017 y 96 construcciones de diálogo; los
veinte nombres aritméticos nuevos pertenecen a un registro separado. No se
añaden afirmaciones sobre el mundo ni entidades del examen.

El frontal reserva los decimales sin resolver al dominio de
cantidades. Así `7 minimo 2` no enfrenta las dos interpretaciones lingüísticas
genéricas S/P/O y P/S/O sobre tres palabras desconocidas. La comprobación de
tipo está escrita en XI y no contiene respuestas ni nombres de operaciones.

## Resultado local y límites

La fase de 2.097.152 ejemplos tarda **120,09 s**, unos **17.463 ejemplos/s**,
incluyendo generación, transporte por archivos, ejecución y guardado de lotes.
El runtime ya estaba compilado. No incluye el desarrollo ni los exámenes
posteriores. Mide filas numéricas estructuradas, no turnos de conversación.

El RVPC2 pasa de **319.274 a 320.537 bytes** durante esa fase: **1.263 bytes
adicionales**. Tras asociar nombres y validar/promocionar ocupa **325.721 bytes**.
El ahorro se explica por las regularidades muy simples y la selección entre
ocho primitivas conocidas. No prueba compresión arbitraria de conocimiento
ni una representación matemáticamente mínima.

Los exámenes posteriores comprueban 1.024 consultas numéricas fuera de la
cuadrícula de entrenamiento, las veinte formas, mezcla ES/EN, cadenas y
continuidad de resultados. La regresión vuelve a comprobar las 1.522 consultas
anteriores en ambas superficies, referentes E019, capacidades E018, clientes,
reinicio, rollback y auditorías. La CI repite además toda la campaña de millones
y compara núcleo, memoria lógica y enlaces con el checkpoint publicado.

La campaña local final aprueba **4.744 verificaciones de consultas y controles**,
además de las 2.048 filas de validación estructurada. El diagnóstico fijo de
las veinte formas pasa de 0/20 a 20/20; no es una puntuación de inteligencia.
La mediana de las 1.024 consultas numéricas nuevas es 20,66 ms y su p95,
26,96 ms. El proceso nativo informa 7.448 KiB residentes y 24.340 KiB de pico
en esa sesión Linux. No es una comparación de velocidad con tareas anteriores;
Android no se ha medido.

La entrada textual conserva números **0..65.535 en cada paso**, hasta siete
operaciones y un intérprete de izquierda a derecha. Una suma/resta seguida
de producto, división o resto se rechaza para evitar un resultado contrario
a la precedencia habitual; falta implementar esa gramática. El entrenamiento usa X `u32`
y consecuencias `i32`; eso no amplía automáticamente la interfaz textual.
La división no exacta, división/resto por cero y resultados fuera del dominio
provocan abstención. No se devuelve un cociente truncado como división exacta.

Ejemplos del protocolo conversacional, con preferencia de salida ES/EN
seleccionada por el cliente:

```text
dos por tres                 -> El resultado es seis.
eight times nine             -> The result is 72.
ocho dividido dos            -> El resultado es cuatro.
tres por cuatro mas dos      -> El resultado es 14.
dividido dos                 -> El resultado es siete.
cinco dividido dos           -> No tengo información suficiente para responder.
```

Los resultados completos, diagnóstico y contadores nativos se publican en
`docs/evidence/e020-results.json` y `docs/evidence/e020-diagnostic.json`.
El manifiesto fija el corpus, el padre, las fuentes y la huella del estado.
La revisión MXIM2 puede depender de escrituras temporales; la reproducción
compara el estado lógico íntegro.

El adaptador y la CLI usan el mismo bloqueo de kernel sobre un archivo
estable `.writer`, liberado al cerrar el descriptor o morir el proceso.
No depende de borrar un directorio al terminar. Los directorios `.lock` de
clientes anteriores siguen causando rechazo y se preservan: no se decide
automáticamente que pertenezcan a un proceso muerto. La CLI necesita `flock`
en el anfitrión Linux. No se mezclan clientes antiguos y nuevos simultáneamente.

Siguen siendo datos y operaciones clásicas en Inverse Ether Memory: cero
qubits activos en esta carga. No se afirma aceleración cuántica ni comprensión
abierta del lenguaje. El código sigue siendo XI textual y no se integra REVERSE OS.

## Reproducción

```bash
python3 ai/xi/scale/tests/native-scale.py /ruta/reverse_pc --out evidence/e020-training --batch 1024
python3 ai/xi/scale/tests/native-e020.py /ruta/reverse_pc /ruta/bbyq_session evidence/e020-training/state.rvp evidence/e020-training/training.json --out evidence/e020
```

Para usar la versión publicada:

```bash
base64 -d ai/checkpoints/BBYQ_E020_Million_Arithmetic_ES_EN.rvp.gz.b64 | gzip -dc > bbyq.rvp
python3 ai/native/session_client.py /ruta/bbyq_session bbyq.rvp --language es
```
