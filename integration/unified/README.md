# U01: una sesión para BBY Q

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

Cada banco conserva su representación nativa. Todos se publican en una sola
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

```bash
python3 -m integration.unified.verify_release
python3 -m integration.unified.verify
python3 -m integration.unified.evaluate --count 200 --workers 4
```

La evidencia completa se conserva en `release/`: validación del lector,
comprobaciones de estado y 200 tareas reservadas que atraviesan todos los
componentes, con nombres, semillas, reglas y posiciones nuevas. Los controles
alteran memoria, circuito VQC, parámetros QRL y observables de voz para
comprobar que esos componentes afectan al resultado. No se aprende con el test.

| Comprobación | Resultado |
| --- | ---: |
| Invariantes de integración, persistencia y aprendizaje | 8/8 |
| Intenciones del lector completo | 488/490 |
| Contratos cuánticos y sus negaciones | 139/139 |
| Tareas finales con todos los componentes ejecutados | 200/200 |
| Decisiones finales correctas | **191/200** |

**Persisten nueve errores de clasificación de VQC3 en la reserva final.**
No se presentan las 200 ejecuciones como 200 aciertos. Un diagnóstico
anterior e independiente también dio 191/200; ambos se conservan completos.
Una continuación con 2048 muestras de entrenamiento nuevas se descartó:
la validación independiente pasó de 241/256 a 242/256, pero empeoró la
calibración. Ninguna muestra de las reservas se usó para entrenar. Las ocho
comprobaciones de integración y el exit code `--integration-only` comprueban
la conexión y la integridad; la precisión se informa por separado. La prueba
de predicciones, sin esa opción, devuelve error mientras queden fallos.

El dominio cooperativo sigue siendo acotado: reglas binarias, objetivo 0 o 6
y una posición entre 0 y 6; la memoria admite 250 asociaciones. Los comandos
admitidos tienen una gramática declarada. Los dos errores anteriores del
lector de intención y las limitaciones del generador de texto no desaparecen
por conectar los componentes. Los circuitos se ejecutan en el simulador
nativo; esto no demuestra ventaja cuántica, conversación general ni un
gradiente conjunto de extremo a extremo.
