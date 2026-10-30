# BBY Q F004 — segunda mitad de Babilonia

## Resultado

Se incorporaron 128 lecciones originales en español y 256 hechos persistentes del tramo 62–122 del PDF de 122 páginas. El candidato parte de F003 PR47 y pasa de 448 a 704 hechos: 352 conceptos acumulados. Aprendizaje contextual en XI/Ether, no ajuste de pesos neuronales ni lectura autónoma del PDF por BBY Q.

F003 anterior había seleccionado lecciones de todo el libro; no constituía una primera mitad exhaustiva. Esta entrega trabaja los seis capítulos finales. El mapa de páginas acredita referencias al tramo, no memorización de todas las frases ni comprensión general del libro.

## Secuencia ejecutada

| Capítulo | Páginas PDF | Lecciones nuevas | Hechos nuevos | Acumulado |
|---|---:|---:|---:|---:|
| Las cinco leyes del oro | 62–72 | 24 | 48 | 496 |
| El prestamista de Babilonia | 73–83 | 24 | 48 | 544 |
| Las murallas de Babilonia | 84–87 | 8 | 16 | 560 |
| El comerciante de camellos | 88–97 | 16 | 32 | 592 |
| Las tablillas de barro | 98–106 | 24 | 48 | 640 |
| El hombre más afortunado | 107–122 | 32 | 64 | 704 |

Se guardó un checkpoint después de cada capítulo. Las definiciones resumen el relato y los requisitos son tareas pedagógicas originales; no son citas literales ni asesoramiento individual. Se incluyen circunstancias, errores, mecanismos de ingresos y límites de interpretación, sin presentar los desenlaces narrativos como garantías.

## Comprobaciones locales

1659 aserciones aprobadas en dos fases de ejecución enlazadas por el mismo checkpoint. Incluyen 448/448 hechos anteriores, 256/256 propiedades nuevas, 128/128 consultas compuestas, 128/128 seguimientos, 128/128 variantes diseñadas de pregunta, 256/256 respuestas después de abrir una instancia nueva y 4/4 controles de información desconocida. Las categorías son partes de la campaña, no deben sumarse de nuevo a 1659. Los controles de frontera y los hashes completan la campaña; no son pruebas de comprensión abierta.

La ejecución inicial completó 1621 aserciones y se detuvo al iniciar una prueba sintética porque su archivo no tenía la cabecera XI requerida. Se corrigió la cabecera, se auditaron las salidas anteriores y se completaron las 38 aserciones restantes desde el checkpoint idéntico. Las 3377 comprobaciones de auditoría del registro no se suman a las 1659. No se afirma una repetición ininterrumpida del arnés corregido ni una ejecución aprobada en GitHub Actions. El registro del intento interrumpido se conserva.

## Reparaciones nativas

Capacidad del archivo: 512 → 4096 hechos; bytes configurados: 114688 → 917504. Quedan 3392 entradas libres. No es memoria ilimitada.

Se corrigió la lectura de propiedades mayores de 80 bytes, sin ampliar el máximo de 224 bytes por hecho. Permanecen 255 bytes por entrada y 48 por sujeto. Se movió el área temporal de búsqueda para que no solape los metadatos ampliados. Se adaptaron los centinelas y la visualización/lectura de identificadores de cuatro dígitos. El ejecutor base no cambió.

Los índices 511, 512, 999, 1000 y 4095 pasaron inserción, recuperación, acceso directo, búsqueda y conservación tras buscar. Se comprobó el rechazo al exceder 4096. Son estados sintéticos dispersos, no una prueba llena con 4096 hechos naturales. También se comprobó detección de una contradicción en una copia desechable.

## Respuestas reales

Entrada: `que es estafa del caballo de nomasir`
Salida: `estafa del caballo de nomasir es una apuesta perdida ante viajeros asociados con el supuesto rival de ninive [#458].`

Entrada: `que es acuerdo de reparto de las tortas y que requiere`
Salida: `acuerdo de reparto de las tortas es la division del ingreso en mitad para costes y dos cuartos para panadero y vendedor [#672]. acuerdo de reparto de las tortas requiere distinguir ingreso bruto costes y parte recibida por cada participante [#673].`

Los identificadores #NNN son posiciones del archivo del agente, no páginas del libro.

## Limitaciones medidas

Seis preguntas abiertas no resueltas. Todas respondieron «No tengo información suficiente para responder.»: calcular el 10 % de 2000, repartir 1000 como Dabasir, explicar la pérdida de Nomasir con una pregunta causal, aplicar Mathon al préstamo a un amigo, explicar por qué el esfuerzo no bastó en el canal y cuestionar que todas las inversiones del libro sean seguras. No se añadieron hechos durante estas seis pruebas. No se cuentan como éxitos. La semilla publicada quedó intacta.

Se demuestra recuperación bajo gramática compatible, no razonamiento económico general, rentabilidad ni preparación para administrar fondos. La primera mitad sigue sin una comprobación exhaustiva de cobertura. No se modifica la APK, el agente posterior de REVERSE, la memoria del operador ni permisos de cuentas. Se conserva BBY Q → w4U → QdU.

## Identidad y entrega

Fuente: https://cpcglobal.org/publications/The%20Richest%20Man%20in%20Babylon.pdf
PDF SHA-256: 76b620d86a163a1934aebeea997f75c1c685d0ecd877f4a0854f0ab3e0e29b69
Cápsula F004 SHA-256: 24026731bfeabf297c9b5d8be636107bf86fb292fa24ad7b1078bafe15690f8c
Checkpoint SHA-256: f89605975dd00960eef82d840303f478e32dfb38548ed270cfd580775b95da2c
Checkpoint: 2621832 bytes; gzip: 347337 bytes.
Fuente XI SHA-256: d24d6948ecfc37d4e700e60a1a225cace13248529a4dc875f3d8a80bbeb17489
Ejecutor SHA-256: ef0c3a709121b8fd3cf4c996808ecfef8b60a7065d3f9c802280c58dc9370d84

El paquete incluye cápsula, estado, seis checkpoints intermedios, currículo, mapa de páginas, código XI, preparadores y arnés, transcripciones, resultados, intento interrumpido, script de continuación auditada, base F003 mínima y PDF fuente. Entorno local: Linux x86-64 / Node 22.16.0. No probado en Android.

Fuentes añadidas a la misma rama de la PR #47, sin fusionar. No se creó otra rama F003. La cápsula entrenada está en el paquete descargable; el repositorio conserva fuentes, currículo y evidencia, no una actualización automática de REVERSE.
