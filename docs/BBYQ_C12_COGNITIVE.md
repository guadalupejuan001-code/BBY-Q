# C12 — Política conversacional Q en XI (observación)

## Propósito

C11 valida primero las fuentes históricas. C12 inicia un entrenador de selección de rutas conversacionales sin desplazar todavía a la generación de respuestas X10. Las puntuaciones se calculan con un **bandido contextual**, no con un modelo general de lenguaje o un computador cuántico físico.

El contexto de aprendizaje es `2 * P01_intent + memory_reference`, donde P01 y P05 son programas XI nativos, con 18 contextos y cuatro acciones: 0 X10 tradicional, 1 P05 memoria, 2 P03 razonamiento, 3 P04 composición. Las recompensas son anotaciones **explícitas** de 0 a 100; la actualización `Q <- Q + trunc((recompensa_Q10000-Q)/2)` se ejecuta exclusivamente en `ai/xi/cognitive/policy-update.xi`.

El entrenamiento de circuitos QML/QRL de C05–C10 sigue siendo independiente. Este módulo estudia un posible uso conversacional de aprendizaje de políticas; **no** transfiere pesos del VQC de paridad ni afirma que el bandido mejore respuestas reales.

## Prueba en la sesión X10

Usa un build X10 completo compatible y una sesión previamente inicializada:

```sh
# Opt-in: añade metadatos cognitive_shadow; nunca sustituye la respuesta original
node bbyq.mjs --build /ruta/build-x10 turn /ruta/sesion id01 --shadow "Explícame qué es un estado cuántico."

# Inspecciona una recomendación, sin modificar el motor X10
node bbyq.mjs --build /ruta/build-x10 turn /ruta/sesion id02 --module=cognitive "Explícame un principio físico."

# Feedback intencional: el evaluador asigna a la acción 2 una recompensa de 90/100
node bbyq.mjs --build /ruta/build-x10 turn /ruta/sesion id03 --module=cognitive --policy-feedback=2,90 "Explícame un principio físico."

# La misma recomendación muestra Q aprendido (no una probabilidad calibrada)
node bbyq.mjs --build /ruta/build-x10 turn /ruta/sesion id04 --module=cognitive "Explícame un principio físico."
```

Los textos se clasifican mediante P01 y P05 en XI. El `cognitive_shadow` incluye el contexto, la ruta sugerida, puntuación Q, número de actualizaciones y `applied:false`. Una puntuación Q alta **no es** precisión lingüística ni confianza estadística.

## Integridad y límites

- `--shadow` es optativo y nunca cambia el texto de respuesta. El estado de aprendizaje se guarda en una tabla separada `cognitive_policy`, con hash SHA-256 y la misma transacción SQLite de X10.
- La única actualización de Q ocurre al enviar `--module=cognitive --policy-feedback=RUTA,NOTA`. Nunca se aprende de la conversación ordinaria sin autorización.
- El replay del mismo ID devuelve el recibo sin duplicar entrenamiento. Un fallo antes de commit revierte la nueva memoria.
- Las pruebas de integración cubren compatibilidad de X10, P01, P05, estado antiguo, retroalimentación, replay, anomalías y rollback.
- Todavía **no** se ha demostrado superioridad frente a X10 ni generalización sobre conversaciones nuevas. La selección de rutas continúa en modo observación, sin activación automática.
- C11 no puede dar por restaurado el entrenamiento real del X09 sin el paquete binario íntegro, como explica `docs/BBYQ_C11_INTEGRITY.md`.

La siguiente aceptación requiere evaluar pares nuevos de mensajes, respuestas reales e indicadores de corrección/latencia antes de permitir que la política proponga una ruta ejecutable.
