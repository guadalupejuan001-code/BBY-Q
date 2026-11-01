# C15 — Aprender de resultados reales de respuestas, sin inventar evaluaciones

## Decisión

Se conectan las características conversacionales de **C14** con un **agente XI independiente de aprendizaje por recompensas**. Una calificación explícita se aplica solamente a la ruta que **produjo realmente** una respuesta X10 anterior, cuya identidad se conserva en un comprobante `requestId`. Las decisiones aprendidas se publican solo como observaciones; NO modifican el texto ni el enrutamiento automático X10.

Este ciclo implementa la fórmula terminal de una actualización TD / bandido contextual:

`Q(contexto,ruta) ← Q + trunc[(100 × recompensa − Q)/2]`.

El cálculo se ejecuta exclusivamente en `ai/xi/cognitive15/update.xi` sobre la memoria Ether RVPC2; no hay pesos aprendidos en JavaScript, Python ni modelos externos. La elección `observe.xi` solo usa los valores Q si hay **al menos tres respuestas de esa misma ruta calificadas** en el contexto y su Q llega a **7000/10000**; en otro caso regresa a la recomendación supervisada C14. Los contextos ambiguos o protegidos nunca admiten el reemplazo.

**Distinción técnica esencial:** este agente usa aprendizaje clásico por recompensa programado en XI, coherente con la idea de QRL, pero no reutiliza el agente Bell de dos cúbits QRL2 ni usa mediciones cuánticas para recompensar. QML/VQC2 conserva sus experimentos independientes. No se afirma ventaja cuántica ni mejora ya demostrada de calidad conversacional.

## Uso: evaluación basada en una respuesta ejecutada

Con un build X10 verificado y una sesión previamente inicializada:

```sh
# 1. X10/P04 ejecuta su respuesta real y guarda su procedencia en el comprobante.
node bbyq.mjs --build /ruta/build-x10 turn /ruta/sesion poema001 \
    --module=p04 --shadow-c15 "escribe un poema sobre una estrella"

# 2. Tras leer la respuesta, el evaluador asigna 0 a 100 al resultado observado.
node bbyq.mjs --build /ruta/build-x10 turn /ruta/sesion nota001 \
    --module=c15 --rl-feedback=poema001,90 "calificación"

# 3. Se puede consultar nuevamente el agente con un nuevo ID de turno.
node bbyq.mjs --build /ruta/build-x10 turn /ruta/sesion poema002 \
    --module=p04 --shadow-c15 "escribe un poema sobre una estrella"

node bbyq.mjs --build /ruta/build-x10 status /ruta/sesion
```

Cada turno de aprendizaje necesita otro **ID nuevo**. La calificación no puede inventar una respuesta, cambiar el motor que respondió, adjudicar el resultado a una ruta hipotética ni evaluarlo por segunda vez. Para analizar otros motores hay que generar primero una respuesta válida y explícita mediante la ruta correspondiente. El evaluador humano determina la recompensa; un resultado numérico de Q no constituye una confianza estadística calibrada.

## Protección de la memoria

- Tabla SQLite `c15_policy` separada, con memoria RVPC2 comprimida y hash SHA-256. La observación sin recompensa no crea aprendizaje persistente.
- Tabla `c15_feedback` con una fila única por `target_id`, contexto, ruta realmente aplicada, recompensa, hash de respuesta y hash de política.
- La transacción X10 y los recibos permiten rollback ante fallos, repetición idempotente y rechazo de una segunda nota para el mismo resultado.
- `c15_shadow.actual_action` se obtiene de la extensión X10 realmente ejecutada. Solo P04, P03, P05 y determinadas rutas X09/X10 con procedencia reconocible son puntuables. Los demás motores se abstienen.
- Ni C14 supervisado ni la memoria C12, ni los checkpoints antiguos X09/E034, ni los motores QML/QRL2 son reentrenados por C15.

## Limitaciones y siguiente prueba

La CI puede simular evaluaciones humanas para comprobar matemáticamente la actualización, sin afirmar que esas puntuaciones representan calidad real de las respuestas. Para adoptar automáticamente las recomendaciones hace falta una **evaluación independiente de respuestas completas** (corrección factual, fidelidad a contexto, seguridad, latencia, coherencia) sobre solicitudes fuera del entrenamiento, con el X09 restaurado y un procedimiento para detectar recompensas equivocadas.

Hasta cumplirlo, C15 permanece deliberadamente en `--shadow-c15`; la ruta ejecutada sigue siendo la misma que habría elegido X10.
