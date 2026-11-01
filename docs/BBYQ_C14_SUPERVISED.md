# C14 — Entrenamiento supervisado de elección de rutas en XI (experimento)

## Pregunta

¿Puede BBY Q recomendar mejor la ruta X10/P05/P03/P04 si recibe características más finas que los 18 contextos de C12?

Este ciclo **no** declara una mejora de las respuestas conversacionales ni activa la política. Solo entrena una **clasificación de rutas** en modo laboratorio y la compara con un control con las mismas etiquetas basado únicamente en la intención P01.

## Diseño experimental

- El motor XI de características ai/xi/cognitive14/features.xi examina texto normalizado por P01 XI y distingue ocho clases: genérica, recuerdo, lógica, creación, contradicción, ejecución, explicación y guardada. Reserva la bandera de memoria P05. Existen 9 × 8 × 2 = 144 contextos posibles.
- Entrenamiento en XI mediante birth.xi, train-batch.xi y decide.xi. Se conservan contadores de 16 bits para cuatro rutas. Las 800 etiquetas se publican como pares contexto-ruta sin acceso a las etiquetas de prueba.
- Decisión conservadora: mínimo tres observaciones y pureza mínima del 70%. En contextos mixtos/protegidos, el sistema se abstiene (elige X10).
- Comparador: mayorías aprendidas con idénticos ejemplos, pero solo 18 contextos P01. Es un control de clasificación, no una medida real de calidad de X10.

## Datos

integration/c14/corpus.mjs construye **1.000 ejemplos sintéticos** con 40 plantillas escritas manualmente y sustituciones deterministas de nombres de temas. Se reservan 800 para entrenar y 200 para probar. El entrenamiento tiene 25 temas y ocho plantillas por clase; el holdout tiene otros 25 temas y otras dos plantillas por clase, evitando la repetición literal de plantillas y temas.

No son conversaciones reales ni muestras de usuarios. No se prueba capacidad lingüística abierta. Se añaden casos adversarios de enseñanza explícita, órdenes mezcladas y preguntas sobre memoria para comprobar abstención.

## Ejecución

Con el intérprete original REVERSE-PC y Node 24:

    node integration/c14/bench.mjs /ruta/a/reverse_pc /directorio/nuevo/resultado

El resultado contiene report.json, corpus-manifest.json y trained.rvp. Se informan matriz de confusión, exactitud por clase, abstenciones, comparación de baselines, y hashes SHA-256; las inferencias no alteran el estado entrenado.

## Próxima puerta de integración

Aunque C14 supere al comparador en la prueba sintética, **NO reemplaza automáticamente las rutas X10** ni modifica el entrenamiento histórico C12 o X09. La integración en sesiones reales requiere primero comprobación con entrenamiento X09 completo y evaluación de respuestas reales.

VQC2/QRL2 cuánticos de los ciclos C05–C10 no participan en esta política supervisada. Su ventaja cuántica no se afirma.
