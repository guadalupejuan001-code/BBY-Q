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

La ejecución nativa comprobó 800 ejemplos de entrenamiento y 200 ejemplos separados, con 200/200 rutas sintéticas correctas, frente a 100/200 del comparador P01 de 18 contextos. Estos resultados solo miden la clasificación del corpus descrito, **no una mejora en la precisión de respuestas reales**.

El estado aprendido se conserva en ai/xi/cognitive14/supervised-seed.xi como 13 celdas no nulas y dos bytes de recuento, además del estado RVPC2 de evidencia. La CI comprueba que cada byte de peso reconstruido por XI coincide con el del entrenamiento real y que los contadores suman 800. No se transfieren pesos externos.

### Observación optativa en una sesión X10

Una sesión X10 correctamente construida puede pedir un diagnóstico en paralelo:

    node bbyq.mjs --build /ruta/build-x10 turn /ruta/sesion c14-1 --shadow-c14 "Escribe un poema sobre el faro."

El recibo conserva intacto el campo response y añade c14_shadow con suggested_route, semantic_class, support, training_purity_percent y applied:false. No se guarda el modelo supervisado en las lecciones X09 ni se reemplaza el anterior C12. Si C14 no puede evaluar un texto largo o falla, el diálogo X10 continúa y su recibo explica la limitación.

**C14 jamás ejecuta automáticamente la ruta sugerida.** Para introducir decisiones reales necesitamos primero pruebas en conversaciones nuevas, respuestas completas y verificación de los paquetes originales X09; esta evaluación sigue pendiente.

VQC2/QRL2 cuánticos de los ciclos C05–C10 no participan en esta política supervisada. Su ventaja cuántica no se afirma.
