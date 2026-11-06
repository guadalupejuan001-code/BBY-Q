# U02: una sesión para BBY Q y corrección de su lectura VQC

La entrada principal nativa es ahora `./bbyq`. C1, las herramientas simbólicas,
QMemory, VQC3, QRL3, el coordinador E02 y QChat100 participan en la misma
sesión SQLite, con un historial, tareas verificables y una transacción para
los cambios de estado y de parámetros.

Esta entrega integra el núcleo nativo. La interfaz Android instalada conserva
su versión anterior; no se compila, instala ni genera una APK con estos cambios.

## Ejecutar

Requiere Python 3, Node 24 para preparar las herramientas Zero y el runtime
original XI compilado con las revisiones fijadas en `release/manifest.json`.
El workflow `bbyq-unified.yml` prepara ese mismo runtime y solo ejecuta pruebas
nativas. No usa Gradle ni produce APK.

```bash
./bbyq --database build/unified/personal.sqlite init
./bbyq --database build/unified/personal.sqlite turn --id tarea-1 \
  'guarda la regla Faro Azul con valor 1 observa Nara con muestra 88113 y resuelve desde 3'
./bbyq --database build/unified/personal.sqlite turn --id explicación-1 \
  'explica la última tarea'
./bbyq --database build/unified/personal.sqlite turn --id aprendizaje-1 \
  'aprende de la última tarea'
```

La primera petición escribe una asociación cuántica, clasifica 1000 valores,
recupera esa asociación, calcula el objetivo, propone un movimiento y lo
expresa con la voz aprendida. Cada resultado incluye las llamadas nativas
que intervinieron y una referencia a la tarea guardada. No se sustituye la
decisión de QRL por una dirección calculada en Python.

Los hechos, cálculos y reglas de C1 entran por el mismo comando:

```bash
./bbyq turn --id cálculo-1 'calcula 7 + 3'
./bbyq turn --id regla-1 'si alguien es clase cero entonces es alerta'
./bbyq turn --id consulta-1 'dime si observación Nara es alerta'
```

La premisa `observación Nara es clase cero` procede de VQC3. El resultado
conserva su probabilidad y la identidad de los datos: es una predicción
del modelo. La conclusión de C1 depende de esa premisa. Las correcciones de
una observación retiran su clasificación anterior sin borrar otros hechos.
Tras actualizar el clasificador o aprender de feedback verificado, las
consultas recalculan las premisas VQC anteriores antes de razonar. Los recibos
históricos conservan la decisión que realmente se tomó.

Para datos reales, `turn --payload sensores.json 'observa Brisa Nueva'`
recibe `{"observations":[...]}` con **exactamente 1000 números finitos**.
El canal tipado conserva los 1000 valores completos, incluidos los últimos;
no los reduce a la capacidad de tokens del lector. Después se usa
`'resuelve Brisa Nueva usando la regla Faro Azul desde 3'`.
Las muestras con semilla son ejemplos sintéticos declarados, no sensores reales.

## Qué se comparte

| Componente | Aporte al mismo ciclo |
| --- | --- |
| C1 | Codificación de 100 cúbits, intención aprendida, lenguaje y herramientas XI |
| QMemory | Asociación binaria persistente por nombre; 4 cúbits por asociación |
| VQC3 | Clasificación de las 1000 observaciones; registro de 1000 cúbits |
| E02 | Premisas, objetivo, confianza, propuesta y verificación de voz |
| QRL3 | Propuesta de movimiento con su política de 1000 cúbits |
| QChat100 | Descripción aprendida del movimiento realmente propuesto |

Cada banco conserva su representación nativa. VQC3 y QRL3 mantienen el
backend original sin MPS: 1000 cúbits por agente en 250 grupos de cuatro;
esta entrega conserva esa topología. Todos los bancos se publican en una sola
base SQLite bajo `BEGIN IMMEDIATE`, junto con diccionarios, historial, tareas,
supervisión y recibos. Un fallo posterior a una escritura o a los gradientes
revierte la operación completa. Repetir el mismo identificador y entrada
devuelve el recibo original; reutilizarlo con otra entrada se rechaza.

Se puede indicar una base C1 existente con `--database`. Se conservan sus
hechos, nombres, diccionario e historial. Los clientes antiguos que escriban
esa misma base siguen siendo compatibles: la entrada unificada importa sus
cambios de lenguaje y conserva los bancos cuánticos. Los antiguos comandos
`node bbyq.mjs ...` quedan como compatibilidad histórica; la ruta unificada
documentada es `./bbyq`.

## Aprendizaje y comprobación

El lector de intención continúa el entrenamiento de C1 con SGD nativo,
repetición de las capacidades anteriores y los contratos cuánticos nuevos.
No se reemplaza una intención incorrecta por la regla del adaptador: una
discrepancia produce una abstención sin cambios parciales.

El feedback explícito usa la tarea original, sus observaciones y su regla
original, aunque el usuario haya corregido luego esa memoria. La supervisión
queda en tablas distintas del estado de inferencia. Los ejemplos sintéticos
tienen un verificador nativo; para datos externos se aceptan etiquetas
`{"labels":{"class":0,"rule":1}}` **solo al dar feedback**. Una valoración
sin etiquetas suficientes actualiza el coordinador, la expresión de la acción
y el lector; no inventa una etiqueta para VQC o QMemory.

Se continúan los parámetros de VQC3, QRL3, QMemory, E02, QChat y el lector
en el mismo commit. El crédito de QRL se omite cuando falló una premisa o no
hubo movimiento. El entrenamiento de memoria usa una copia temporal y
publica solo ángulos y contador, conservando las asociaciones del usuario.
El modelo de texto congelado y las versiones anteriores se conservan.

U02 conserva los ángulos y pesos originales de VQC3 y QRL3. La corrección
añade una lectura de correlaciones Pauli X/Z del estado cuántico real,
deshace algebraicamente la codificación conocida y obtiene estadísticas de
los 1000 valores codificados. Una lectura solo de Z perdía información de
fase. El decodificador no lee los sensores originales, las variables ocultas
del entorno, su semilla ni la etiqueta. Se conservan 19 posiciones de
coeficientes. Una selección por covarianza calculada en XI con el conjunto
de entrenamiento retiene dos estadísticas y su sesgo; el logit anterior
queda como comparación. El ajuste usa Adam y pasos de Newton con gradientes,
curvatura y resolución Cholesky nativos, sobre 2048 ejemplos nuevos con ruido
0,1 y 0,6. Las etiquetas solo entran por el canal de entrenamiento.

Se conservan las fuentes exactas del entrenamiento y la validación, con 512
ejemplos independientes por nivel de ruido. Las reservas antiguas, los nueve
errores y las pruebas finales permanecen fuera del entrenamiento. Las pruebas
numéricas comparan fases y todas las estadísticas con un cálculo independiente,
comprueban los últimos cúbits y contrastan los gradientes con diferencias
finitas. También fuerzan etiquetas falsas y borran los sensores originales
manteniendo el estado cuántico: la inferencia debe permanecer idéntica.

Las sesiones U01 identificadas se actualizan en una transacción: se incorpora
solo la nueva región de lectura, sin reemplazar el aprendizaje personal de
los motores, y se archiva el banco VQC anterior. Nombres, asociaciones,
diccionarios, tareas y recibos se conservan. Una identidad desconocida se
rechaza; un fallo inyectado después de las escrituras revierte la migración.

```bash
python3 -m integration.unified.verify_release
python3 -m integration.unified.verify_perception
python3 -m integration.unified.verify
python3 -m integration.unified.verify_upgrade
python3 -m integration.unified.evaluate --count 200 --workers 4 --seed 2026110705 --output build/unified/regression.json
python3 -m integration.unified.evaluate --count 200 --workers 4 --seed 2026110602 --output build/unified/opened-regression.json
python3 -m integration.unified.evaluate --count 200 --workers 4 --seed 2026110603
python3 -m integration.unified.evaluate_perception --count 1024 --seed 2026110603
```

La evidencia completa se conserva en `release/`: validación del lector,
comprobaciones de estado, tres series de 200 tareas y una reserva independiente
de 1024 clasificaciones con datos numéricos externos al modelo. Los controles
alteran memoria, circuito VQC, parámetros QRL y observables de voz para
comprobar que esos componentes afectan al resultado. No se aprende con el test.

| Comprobación | Resultado |
| --- | ---: |
| Invariantes de integración, persistencia y aprendizaje | 9/9 |
| Decodificación, aislamiento, gradientes y optimizador nativos | 7/7 |
| Migración de sesiones U01 reales y rollback | 5/5 |
| Intenciones del lector completo | 488/490 |
| Contratos cuánticos y sus negaciones | 139/139 |
| Validación del clasificador, ruido 0,1 | 512/512 |
| Validación del clasificador, ruido 0,6 | 512/512 |
| Regresión original, incluidos los nueve fallos | **200/200** |
| Regresión de la primera prueba nueva | **200/200** |
| Reserva final nueva con todos los componentes | **200/200** |
| Reserva independiente de 1000 entradas por clasificación | **1024/1024** |
| Misma reserva con el clasificador anterior | 976/1024 |
| Misma reserva anulando las nuevas observaciones X | 747/1024 |

**Corregidos los nueve errores originales de VQC3.** Se conserva la reserva
U01 de 191/200 en `u01-reserved.json.gz`, junto con cada comparación antes y
después. La primera selección U02 detenía el ajuste al alcanzar el mínimo de
validación: dio 199/200 en otra prueba y 1023/1024 en la clasificación tipada.
Ambas pruebas se conservan completas en `first-reserved.json.gz` y
`first-classification-test.json.gz`.

El ajuste final completa 115 épocas Adam y 30 pasos Newton sobre los mismos
2048 ejemplos de entrenamiento, y elige por calibración en la validación.
Corrige también el fallo adicional de las 200 tareas abiertas; estas pasan a
ser regresión. La reserva final usa otra semilla, declarada antes de abrirla:
2026110603. Ninguna etiqueta de esas pruebas se usa para ajustar el modelo.
Las tres series conservan todos los resultados, sus parámetros identificados
y controles causales. La CI exige aciertos reales y ejecuta las pruebas sin
`--integration-only`; no basta con llamar a todos los motores.

El dominio cooperativo sigue siendo acotado: reglas binarias, objetivo 0 o 6
y una posición entre 0 y 6; la memoria admite 250 asociaciones. Los comandos
admitidos tienen una gramática declarada. Los dos errores anteriores del
lector de intención y las limitaciones del generador de texto no desaparecen
por conectar los componentes. Los circuitos se ejecutan en el simulador
nativo; esto no demuestra ventaja cuántica, conversación general ni un
gradiente conjunto de extremo a extremo.
