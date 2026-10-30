# F004 — Libro en dos etapas nativas

## Resultado local completado

Se ejecutó A (páginas 1–61), se comprobó y guardó su estado, y después B (páginas 62–122), sin borrar lo anterior. La campaña registra 4.816 comprobaciones aprobadas. No son 4.816 pruebas de comprensión: incluyen ingestión, recuperación, conteos, aislamiento y persistencia.

| Medida | A | B |
|---|---:|---:|
| Páginas incorporadas en la etapa | 1–61 | 62–122 |
| Fragmentos nuevos del texto | 562 | 609 |
| Conceptos nuevos en español | 32 | 32 |
| Hechos nuevos en español | 64 | 64 |
| Registros acumulados | 1074 | 1747 |
| Hechos estructurados recuperados correctamente | 512/512 | 576/576 |
| Registros añadidos recuperados, acumulados | 626/626 | 1299/1299 |
| Páginas completas reconstruidas, acumuladas | 61/61 | 122/122 |
| Páginas recuperadas tras restaurar | 61/61 | 122/122 |
| Variantes del operador correctas | 32/32 | 64/64 |

El estado final conserva los 448 hechos anteriores y añade 128 hechos españoles y 1.171 fragmentos del texto inglés. Total: 576 hechos estructurados y 1.171 fragmentos = 1.747 registros. Quedan 2.349 de 4.096 espacios.

Se conserva todo el texto extraído de las 122 páginas, normalizado en espacios y controles C0, incluidos preliminares y pies de página. No se enseña el contenido de imágenes. Las 64 lecciones españolas son síntesis originales, no una traducción completa ni todas las conclusiones posibles del libro.

## Naturaleza del aprendizaje

Adquisición contextual persistente en XI/Ether; no ajuste de pesos neuronales ni lectura autónoma de PDF. Node emite XI, entrega entradas y verifica salidas; no responde en lugar del agente. El ejecutor original no cambia. El comando nativo `@libro pagina 62` reconstruye la página desde los registros de BBY Q.

Respuesta real:

- Entrada: `oye que es babilonia comprador alternativo`.
- Salida: `babilonia comprador alternativo es la posibilidad de vender los metales a otros aunque el rey no los compre [#1088].`

## Memoria, entrega y restauración

La capacidad pasó de 512 a 4.096 registros. Se ajustaron identificadores, marcador de ausencia y tabla temporal de búsqueda, que antes podía solaparse con metadatos. Se mantienen 224 bytes por registro y 255 bytes por entrada; no es memoria ilimitada.

Checkpoint A: 5.046.330 bytes; gzip 666.419 bytes. Cápsula A: 5.655.711 bytes, con estado incluido.

Checkpoint B: 8.514.330 bytes; gzip 1.120.208 bytes. Motor B: 2.483.327 bytes. El motor y el checkpoint se entregan separados porque incrustarlos excede el límite de 8 MiB del empaquetador. No se recorta el libro ni se modifica el host.

**B requiere el checkpoint adjunto.** Ejecutar solo `app-init` devuelve la semilla F003 de 448 hechos. La entrega incluye `consultar.sh`, que restaura el estado completo en un directorio local separado y verifica su hash. Se comprobaron 122 páginas después de restaurar ese checkpoint. El nombre heredado `pages_reconstructed_from_fresh_seed` del JSON significa restauración externa en B, no inclusión del conocimiento en la cápsula del motor.

## Límites observados

Ocho tareas abiertas: ninguna resuelta. Siete respuestas de información insuficiente y una entrada guardada como afirmación en una copia desechable. Fallaron, entre otras, el 10 % de 1.000, la aplicación numérica del plan de Dabasir y un caso de joyas reformulado. La copia que guardó una afirmación incorrecta se descartó; el checkpoint publicado conserva su hash.

La búsqueda general `@ctx find` y el borrado `@ctx clear` en el archivo completo superaron el presupuesto de instrucciones en los casos examinados. Se conservan como pruebas negativas, no como controles aprobados. La lectura por página y las preguntas estructuradas sí fueron comprobadas.

No se acredita razonamiento económico abierto, rentabilidad, administración de fondos, ejecución Android ni aceleración cuántica. No se actualiza la APK ni se sustituye el agente más reciente de REVERSE; no se habilitan pagos, cuentas, trading o transferencias.

## Procedencia y reproducción

Código de entrenamiento verificado byte por byte contra el commit `d46accc62f0d151e135d9b6a2997a711ba31b7b5`. Las revisiones posteriores del examinador de límites se documentan por separado. Reproducción: `ai/training/babylon-halves/README.md` y `.github/workflows/bbyq-babylon-halves.yml`.

Hubo intentos interrumpidos por límites de instrucciones, salida y tamaño de cápsula. Se reanudaron estados nativos conservados y transcripciones verificadas con la misma fuente XI. No se presenta el trabajo como una única ejecución ininterrumpida; los tiempos del JSON de continuación no son tiempos totales de toda la sesión.

La primera CI F004 falló por ausencia de pdftotext; se corrigió reutilizando el texto fuente de hash verificado. Los resultados de este informe son locales. Una repetición remota no se declara aprobada mientras no termine.

## Identidad

- PDF: `76b620d86a163a1934aebeea997f75c1c685d0ecd877f4a0854f0ab3e0e29b69`.
- XI ejecutado: `be932dd4a0b9721c57d2653d6c8e0921d9b5b558e5fcfff67115dae5f558691a`.
- Runtime: `ef0c3a709121b8fd3cf4c996808ecfef8b60a7065d3f9c802280c58dc9370d84`.
- Checkpoint A: `aa34602b6ae8ee4556973ff980ab03f067ee59532315e39d4723001b1df60f3f`.
- Checkpoint B: `8808fc02b22a32c78eeacb616290b0c582effd4735072e6d656feb39232f6421`.
- Motor B: `23f53ebe68f504cf40d8d57948e9a76ed96915a9f6f2af9edef6f219048b0f62`.

Los artefactos descargables incluyen el PDF, texto, estados, código, runtime, transcripciones, resultados y lanzador. PR #46 permanece abierta y sin fusionar.
