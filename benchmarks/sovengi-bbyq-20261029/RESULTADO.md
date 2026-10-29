# SOVENGI frente a BBY Q: prueba real de inferencia

Ejecución terminada: 2026-10-29T01:12:43.941Z. [CI](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40798417876), completed/success. [Evidencias originales](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40798417876/artifacts/12864548932).

## Resultado

| Medición | BBY Q E032 | SOVENGI, configuración habitual |
| --- | ---: | ---: |
| Consultas de calidad completadas | 32/32 | 32/32 |
| Errores técnicos, 44 consultas por brazo | 0 | 0 |
| Aciertos semánticos completos | 20/32 | 2/32 |
| Respuestas parciales adicionales | 0 | 2 |
| Posesión temporal | 8/8 | 0/8 |
| Memoria cotidiana, días y ubicaciones | 1/8 | 1/8 |
| Composición de clase y requisito | 8/8 | 0/8 |
| Preguntas abiertas y saludos | 3/8 | 1/8 |
| Mediana de las 12 consultas repetidas | 160,81 ms | 1.140,65 ms |
| Mediana de las 32 consultas iniciales | 161,55 ms | 1.354,90 ms |
| Pico RSS muestreado del árbol de procesos | 45,50 MiB | 995,11 MiB |

En las consultas repetidas, BBY Q tarda 7,09 veces menos y el pico RSS observado es 21,87 veces menor. Son costes de los dos productos bajo este protocolo, no de operaciones equivalentes ni una medición causal del lenguaje de programación. Los fallos semánticos también están incluidos en los tiempos.

## Condiciones y conservación

Mismo runner ubuntu-latest, CPU AMD EPYC 7763, un CPU lógico por worker (afinidad 0), Torch 2.8.0+cpu con un hilo. Versiones: SOVENGI 58345eec2cb6a05d3fb0491e3a2f3d914cd1a48c; BBY Q E032 código ca501af7e3306cea28eaf41f0f6d9e1db825eeda, cápsula d2c5e4ebb2b0c3b7af74abc881d6f8c1a5ff2e106f621d0ceba5cb312b525048, checkpoint f1c2ace6a8d35643c0ae68103f3cb0aa33a0325c9fea004f00fd5e38d60ffb56. Examinador a96ede4c1a4f3223967c14f1bfa80d41c333da17.

Las 35 identidades SOVENGI participaron realmente durante la secuencia de consultas; no simultáneamente. La configuración habitual genera hasta cuatro candidatos y selecciona uno. Los 1.417.104.076 bytes de pesos mantienen sus hashes antes y después. BBY Q mantiene cápsula y checkpoint originales. No se entrenó, fusionó, desplegó ni modificó ningún modelo. Los HEAD main remotos permanecen sin cambios.

El protocolo se congeló antes de generar: SHA256 81303a9d8de748031f16555c6175fe20a16db01df05aa06c5863feebe13d66a7. Las copias de sesión son desechables. BBY Q recibe los hechos como turnos y conserva su estado nativo; SOVENGI recibe los mismos hechos originales en su historial mediante el producto común, sin respuestas de referencia. En BBY Q la ingesta se mide aparte del turno final; en SOVENGI la preparación del contexto forma parte de esa consulta. La primera carga de modelos es perezosa; los 12 tiempos repetidos se miden después de las 32 preguntas iniciales. La rotación puede cambiar los modelos residentes.

RSS se muestrea cada 10 ms sobre worker y descendientes, incluyendo adaptador de prueba e inferencia, excluyendo el driver; puede contar páginas compartidas dos veces. No es la RAM mínima ni una medición de energía o Android. BBY Q no cargó páginas @lex en esta batería.

## Respuestas que explican el resultado

- Ante una posesión pasada, BBY Q afirma el pasado y se abstiene sobre el presente; distingue previsión y contradicción. SOVENGI genera respuestas ajenas o repetitivas en estas ocho consultas.
- Sobre el taller Brisalto, SOVENGI responde correctamente jueves; BBY Q no reconoce la relación abre/día. Ambas fallan otras preguntas de días y ubicaciones. SOVENGI pierde las dos correcciones: contesta martes en lugar de viernes y sábado en lugar de domingo.
- BBY Q compone clase y requisito con referencias. SOVENGI no completa ninguna de las ocho consultas de este grupo.
- Los tres aciertos abiertos de BBY Q son dos saludos y reconocer un color favorito desconocido. No explica lluvia o hielo, no parafrasea, no ordena los pasos del té y no traduce good morning.
- SOVENGI saluda correctamente en español; sus dos parciales son una ubicación sin el color de la caja y una paráfrasis mal formada. No se cuentan como aciertos completos.

La revisión es de Codex, no de un panel humano independiente. Se fijaron criterios semánticos antes de generar y no se ajustaron modelos ni prompts con los resultados. La señal es/en de BBY Q es explícita; SOVENGI conserva su prompt de producto, habitualmente español: los casos ingleses no aíslan por sí solos competencia lingüística. Las categorías contienen dominios específicos y no acreditan una superioridad general ni son porcentajes de inteligencia.

## Lectura del resultado

BBY Q obtiene mayor precisión y menor coste observado en este conjunto, con un dominio más restringido y respuestas breves. SOVENGI intenta generación más libre y coordina varios modelos, pero su mayor capacidad de representación no se traduce aquí en mejores respuestas. Ninguno demuestra conversación abierta fiable. El siguiente desarrollo de BBY Q debe ampliar relaciones y lenguaje útil manteniendo la precisión; esta evaluación no implementa cambios.

## Archivos

results.json conserva métricas y condiciones; machine-results.json el informe original sin revisión; responses.json las salidas de consola originales de las 88 consultas; review.json los 32 pares, criterios y decisiones caso por caso. El artefacto guarda además respuestas completas con las trazas SOVENGI, preparación y errores. Esta rama solo añade el examinador y evidencias; no fusionar su workflow temporal sobre main.
