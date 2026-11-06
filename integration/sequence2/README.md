# C1: lectura y herramientas verificables, sin generar APK

Esta continuación conserva el experimento `sequence1` y los modelos
E01/E02/Zero/VQC3/QRL3 originales. La ruta nueva se ejecuta desde el código
fuente con el intérprete XI/Ether fijado del proyecto. No sustituye todavía el
chat instalado en Android, ni migra su estado a otra base de datos.

## Correcciones

- El texto sigue conservando UTF-8, posiciones, tildes, ñ, números y nombres
  nuevos. El registro Clifford simulado de 100 cúbits se reutiliza por cuadro.
- El lector incorpora una característica explícita del alcance de
  `define A no B` y otra de negación. Son reglas sintácticas acotadas de XI;
  los tokens de respuesta y sus gradientes siguen siendo aprendidos en XI.
- La intención recibe el mismo presupuesto de actualizaciones por clase,
  muestrea sin duplicar las cachés y pondera por separado la posición inicial.
  Las palabras de cortesía, artículos y puntuación no dominan ese lector; el
  texto y sus características exactas siguen conservados. El currículo añade
  variantes léxicas y usa los contratos propios como profesor, con argumentos
  de entrenamiento independientes de los evaluados.
- La primera palabra significativa mantiene su función aunque cambie la
  puntuación inicial. Una característica de soporte distingue términos del
  vocabulario de capacidades frente a entradas desconocidas; la decisión final
  sigue siendo aprendida.
- Un parser estructural de XI selecciona contratos completos de herramientas.
  La selección aprendida debe coincidir con el contrato. Un desacuerdo produce
  rechazo; no se modifica la etiqueta para convertirlo en un acierto.
- Las herramientas preservan argumentos exactos: calculadora, nombres,
  correcciones, evidencia negativa, reglas y rutas. La calculadora, la
  inferencia y la búsqueda de caminos reutilizan el núcleo Zero existente.
- Las respuestas con nombres nuevos salen de los hechos nativos recuperados,
  con sus cadenas originales; no se atribuyen al pequeño vocabulario generador.
- Una consulta que nombra un tema explícito deja de arrastrar otro tema del
  historial. Un seguimiento sin tema, como `repítelo`, conserva el contexto.
- Una transacción publica el checkpoint compacto, sus diccionarios y un solo
  resultado por petición. Un error en un paso posterior revierte todo el turno.
  Reintentos y solicitudes simultáneas con el mismo ID son idempotentes.

## Uso desde el proyecto

Con las dependencias del workflow `bbyq-c1-native.yml` preparadas:

```bash
node bbyq.mjs language build/mi-bbyq.sqlite t1 'Recuerda que mi nave se llama Niña Ámbar.'
node bbyq.mjs language build/mi-bbyq.sqlite t2 '¿Cómo se llama mi nave?'
node bbyq.mjs language build/mi-bbyq.sqlite t3 'Tengo 137 cajas con 24 piezas cada una. ¿Cuántas piezas tengo en total?'
```

La base nueva es independiente de la instalada en el teléfono. La identidad
del modelo, fuente y diccionario se comprueba al abrirla; no se reinicia
silenciosamente un estado incompatible o corrupto.

## Evidencia y selección

`release/validation.json` conserva cada predicción de los lectores y los
resultados por capacidad. `release/selection.json` identifica los checkpoints
elegidos por su peor grupo de validación, antes de abrir tareas reservadas.
Los pesos, vocabulario, fuente nativa y partes comprimidas tienen identidades
verificadas en `release/manifest.json`.

La continuación de texto conserva como candidato el punto de partida medido:
más épocas no obligan a aceptar un modelo peor. El entrenamiento de intención
puede reutilizar las características nativas de un checkpoint solo si coinciden
el conjunto ordenado de entradas, el diccionario y el programa de codificación.
La reutilización vuelve a comparar muestras con mediciones frescas del circuito;
no cambia los datos ni cuenta una caché repetida como una muestra nueva.

La evaluación reservada contiene 200 tareas completas de cinco familias:
aritmética, nombres/correcciones, inferencia, rutas y composición/negación.
Se abre una sola vez después de congelar un candidato que supere cada grupo de
validación, las herramientas, las transacciones y las tareas de desarrollo.
Su marcador y sus resultados identifican el código evaluado. No se utiliza
para seleccionar pesos. Una intención correcta sin resultado correcto no cuenta.
El lenguaje de los contratos es conocido por el profesor y el alumno: la
evaluación mide su aplicación a argumentos nuevos. No se presenta como una
prueba de comprensión de reformulaciones completamente desconocidas.

```bash
python3 integration/sequence2/verify_curriculum.py
python3 integration/sequence2/verify_codec.py
python3 integration/sequence2/verify_tools.py
python3 integration/sequence2/verify_release.py
python3 integration/sequence2/verify_workspace.py
python3 integration/sequence2/evaluate.py --workers 4
```

La reproducción de lectores parte de semillas congeladas y ejecuta el SGD en
XI. Es más costosa que verificar los checkpoints seleccionados:

```bash
python3 integration/sequence2/train.py build/sequence2/reproduction
```

## Alcance

El parser reconoce contratos declarados en `grammar.py`, con nombres de hasta
ocho tokens. Rechaza lo que no sabe traducir. Las expresiones usan binary64,
límites numéricos explícitos, precedencia y rechazo de división por cero; no son
aritmética decimal o entera de precisión arbitraria. Los límites generales del
codec permanecen explícitos y las entradas aceptadas no se truncan.

El mapa Clifford es fijo y el lector es clásico. La gramática, las reglas y la
planificación son algoritmos programados en XI. Estas pruebas no demuestran
comprensión libre del lenguaje, AGI ni ventaja cuántica. Los agentes VQC3/QRL3
conservan su implementación y sus 1.000 cúbits declarados por agente.

El workflow nuevo ejecuta pruebas nativas. El workflow Android tampoco genera
APK en las pull requests: la compilación exige una ejecución manual con la
opción `build_android`, desactivada por defecto. En esta corrección no se pide
esa ejecución y no se entrega una APK.
