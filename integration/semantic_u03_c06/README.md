# BBY Q U03 C06 — Aprendizaje semántico en XI (sin APK)

**Base:** C05 PR #91, commit fbe772600e24f4cf782b8592c119138277d9886e.

C06 introduce un **modelo de decisión semántica entrenable por supervisión en XI
nativo**, que aprende a distinguir tres tipos de instrucciones dentro de un
dominio pequeño: prohibir la acción, realizar una acción excluyendo un tema, o
hacer una solicitud afirmativa.

Ejemplos mínimos:

| Entrada | Etiqueta de evaluación |
| --- | --- |
| no definas Prisma | prohibir la acción |
| define Prisma no Brisa | ejecutar definiendo Prisma, excluir Brisa |
| define Prisma | acción afirmativa |

**Diferencia respecto a C05:** C05 solo creaba spans y relaciones candidatas.
En C06, los pesos de la cabeza clasificadora se actualizan en el intérprete
REVERSE-PC/XI, mediante operaciones nativas `c06_train` y
`c06_predict`. El clasificador NO ejecuta un algoritmo
de aprendizaje en Python ni recibe etiquetas durante inferencia.

## Arquitectura

- **Fuente XI nueva:** `ai/xi/c06/semantic-head.xi`. Implementa una
  cabeza lineal multiclase de 3 salidas y 8 características, con
  actualización perceptrón supervisada ejecutada por XI. Los pesos residen
  solo en un banco nativo RVPC2 nuevo, nunca en la memoria personal de U02.
- **Datos y etiquetas:** `dataset.py` construye en el dominio
  de gramática explícito de C05 muestras de entrenamiento y prueba con
  plantillas y entidades **completamente disjuntas entre particiones**.
  La etiqueta procede del autor de la plantilla, no de lo que C05 cree que
  significa. Los nombres desconocidos obligan a usar composición en lugar
  de memorizar un listado de entidades.
- **Características:** `features.py` extrae de C05
  únicamente eventos, posiciones, negaciones y distancias de palabras;
  no utiliza `event.polarity`, `negation.kind`,
  decisiones aprendidas, etiquetas ni ninguna información futura.
- **Controles de ablación:** se entrenan tres clasificadores XI con el
  mismo número de pesos, presupuestos y entrenamiento: (1) C05 con relaciones
  de orden; (2) C05 eliminando esas relaciones; (3) representación superficial
  sin orden de palabras, con un pequeño conjunto de indicadores textuales.
- **Selección:** los datos de validación seleccionan la época de cada
  candidato; la prueba reservada se crea y ejecuta **una sola vez**, después
  de congelar la selección. No se usan sus etiquetas para ajustar pesos.
- **Persistencia:** el checkpoint del modelo C06 elegido se guarda en
  `build/c06/semantic-trained.rvp` como nuevo RVPC2 nativo
  reproducible, con SHA-256 y manifiesto de entrenamiento. Las imágenes
  anteriores de C1, VQC3, QRL3 y QMemory no se modifican.
- **Interfaz actual:** no se sustituye el clasificador de intención congelado
  de U02 ni se cambia automáticamente la generación de respuestas. Este
  módulo sirve de cabeza semántica **experimental** que podrá competir o
  cooperar con C1 en siguientes ciclos cuando se demuestre que mejora la
  conversación completa.

## Conjunto de evaluación

| Partición | Ejemplos | Uso autorizado |
| --- | ---: | --- |
| Entrenamiento | 360 | SGD nativo, actualización de pesos |
| Validación | 90 | elección de época, no gradientes |
| Test reservado | 120 | una sola evaluación, al final |

El test usa plantillas inéditas y nombres que no aparecen en entrenamiento
ni validación. Se registran SHA-256 de corpus por partición y matrices de
confusión completas para las tres variantes, de modo que una disminución
no pueda ocultarse con porcentajes agregados.

## Ejecución y evidencia

Linux/runner GitHub, con REVERSE-PC 08c363e6c6855c14026c86046af7183a45f45a98,
Mundo X e2778d962af22f6f1a0794058dd4685fc2573966, Python 3.12:

    bash deps/reverse-pc/scripts/build-xi-session.sh deps/mundo-x deps/reverse-pc/build
    python3 -m unittest integration.semantic_u03_c06.test_semantics -v
    python3 -m integration.semantic_u03_c06.train --epochs 6 --out build/c06/training-report.json
    python3 -m integration.codifier_u03_c05.conformance

La CI vuelve a comprobar 159 archivos protegidos, entrenamiento XI,
reapertura desde checkpoint RVPC2, aislamiento de particiones, ausencia de
etiquetas en inferencia, ablations y diferencias estadísticas honestas.

## Límites de la prueba

- Los ejemplos son sintéticos, pero el conjunto reservado está separado en
  plantillas y entidades. Un resultado alto evalúa **esta tarea de semántica
  acotada**, no conversación general.
- La estructura de C05 todavía depende de un analizador lingüístico en
  Python y sus reglas de spans. XI aprende la relación entre esas
  características y la etiqueta, no el parser completo.
- El modelo es un clasificador lineal entrenado con la lógica XI original;
  no se debe llamar un circuito cuántico nuevo de 1000 cúbits ni demostrar
  "ventaja cuántica".
- Si los datos muestran empate con una ablación, se informa; no se inventa
  una contribución.
- Nada de esto predice automáticamente mejoras en los siete errores antiguos
  del generador C1. Corregirlos necesita aprendizaje de conversación y
  validación de end-to-end por separado.
- No se han fusionado PRs antiguas ni generado APK. El modelo nuevo es
  candidato, no reemplazo de la versión estable.
