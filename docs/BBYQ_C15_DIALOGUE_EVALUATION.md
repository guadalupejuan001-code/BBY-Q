# C15 — Medición de respuestas nuevas (no solo rutas)

Este ejercicio responde a la pregunta: «¿Elegir una ruta mediante aprendizaje por recompensa produce mejores respuestas de BBY Q?».

En la aplicación X10 se ejecutan realmente P03, P04 y P05 para **doce solicitudes nuevas redactadas para el ensayo**: cuatro solicitudes de creación, cuatro razonamientos con premisas autocontenidas y cuatro búsquedas de memoria conversacional. Cada solicitud se prueba por separado en la ruta automática X10 y en las tres rutas explícitas. Las respuestas y errores se guardan sin reescribirlos.

## Qué podemos medir

- Las tareas creativas se evalúan **solo** por número de versos/frases y aparición del tema. Esto no mide belleza literaria ni satisfacción del usuario.
- La lógica se evalúa mediante resultados y trazas de inferencia previstos por los enunciados. No prueba razonamiento abierto.
- La memoria se evalúa mediante coincidencia con una frase introducida previamente en la **misma sesión de prueba**; un caso debe reconocer que el tema solicitado no aparece.

Se calcula la fracción de respuestas que satisfacen los criterios limitados, sin convertirla en «inteligencia», «confianza» ni «calidad conversacional general». Los ejemplos no provienen de chats reales. El ejecutor usa X10 real y sus roles XI compilados, pero la memoria X09 del conjunto de pruebas es **sintética**, no la copia entrenada del propietario; por eso no se evalúa conocimiento histórico auténtico.

## Cómo comprobamos el aprendizaje por refuerzo

Se toma una solicitud de poema **reservada** y se registra la respuesta P04 y la recomendación C15 antes de entrenar. En una sesión separada se generan seis respuestas efectivas sobre tres temas de calibración: tres con P04 y tres con P03. Se asigna una recompensa **determinista** de 100 cuando la respuesta cumple la rúbrica y 0 cuando falla. El agente XI actualiza Q únicamente al recibir una calificación de una respuesta que realmente ocurrió; no aprende del mensaje del usuario sin autorización.

Después del aprendizaje se repite la solicitud reservada. Se comparan respuesta, recomendación y puntuación de la rúbrica. Si C15 termina recomendando P04 cuando X10 ya lo hacía, **eso no es una mejora de calidad**, sino una recuperación aprendida de la misma decisión. El informe lo indica explícitamente.

## Reproducción

Con Linux x86-64, Node 24, el REVERSE-PC fijado y las fuentes XI:

```sh
node integration/c15/tests/dialogue-eval.mjs /ruta/reverse_pc carpeta-nueva
```

Se generan `summary.json` y `dialogue-evaluation.json`, con solicitudes, respuestas producidas, reglas de calificación, tiempos, alternativas y evolución de las recomendaciones.

El experimento no activa ejecución automática de rutas ni modifica el algoritmo productivo C15.


## Resultados medidos (GitHub Actions, 1 noviembre 2026)

Ejecución reproducible: https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/41364467854

| Métrica | Resultado |
| --- | --- |
| Solicitudes nuevas redactadas para el ensayo | 12 |
| Respuestas automáticas nativas verificadas | 9 de 9 ejecutables |
| Solicitudes automáticas que llegaron a un X09 no restaurado | 3 de 12 |
| Motor explícito correcto (4 de cada dominio) | 12/12 por rúbrica limitada |
| Recomendaciones C15 coincidentes con ruta esperada | 2 de 12 |
| Recomendaciones admitidas en lugar de abstenerse | 6 de 12 |
| Recompensas ficticias explícitas, vinculadas a respuestas ejecutadas | 6 |
| Q de P04 tras tres resultados 100/100 de calibración | 8750/10000 |
| Nueva temática con la misma estructura y contexto 70 | C15-outcome-Q activo |
| Paráfrasis de poema con contexto distinto 6 | Continúa C14-supervised-prior |
| Mejora del contenido de respuesta reservada | 0; texto idéntico |

**Diagnóstico:** el aprendizaje Q **sí** se actualiza y recupera en la consulta de un ejemplo distinto del mismo contexto (70). Sin embargo, una paráfrasis («haz un poema de tres versos sobre un cometa») recibe el contexto **6**; las tres experiencias positivas se guardaron en el contexto **70**. El sistema no comparte crédito entre esas dos representaciones de una misma intención. Este es un problema observable de generalización y representación, no una demostración de que el código Q esté roto.

Las tres solicitudes automáticas no resueltas cayeron al fallback X09 del fixture, que no incluye la tabla `dirty_slots` ni el modelo histórico restaurado. La ejecución falló con `ERR_SQLITE_ERROR`. No se atribuye ese fallo, sin más, al X10 completo del propietario.

**Decisión técnica:** no activar selección autónoma. Antes de hacerlo hay que ampliar la equivalencia de formulaciones (P01/C14), ofrecer rutas nativas antes del fallback cuando la gramática lo pruebe, y volver a medir calidad en sesiones X09 auténticas y conversaciones recopiladas con autorización. Las evaluaciones actuales son un piloto con rúbricas objetivas limitadas, no un estudio de conversación humana.
