# F002 — auditoría final de datos preparados

Esta auditoría no modifica el agente, el checkpoint ni las 899 comprobaciones de la ejecución local. Se efectuó al consolidar los dos corpus educativos para la entrega.

- Registros originales preparados F001 + F002: **7.600**.
- Preguntas iniciales distintas en el conjunto consolidado: **7.520**.
- Preguntas iniciales repetidas entre corpus: **80**. Se conserva la primera versión de F001, más extensa; las variantes F002 se guardan por separado para auditoría. No se afirma que sus respuestas fueran idénticas.
- Escenarios numéricos de examen: **1.024**, sin preguntas iniciales duplicadas ni coincidencias exactas con el conjunto de entrenamiento.
- Hechos nativos acumulados: **320**, sin textos repetidos.

La deduplicación es por texto exacto de la primera pregunta: no prueba diversidad semántica ni independencia de plantillas. Las familias numéricas comparten plantillas entre entrenamiento y examen. Este corpus ampliado sigue **sin ser consumido por el agente nativo**; la adquisición demostrada continúa siendo la de los 320 hechos contextuales.

## Identidad de los archivos consolidados

| Archivo | Bytes | SHA-256 |
|---|---:|---|
| conversaciones.train.jsonl | 3416698 | ca4bb993de126fc1a3e556801b1c5a12d68bfaf1a762425b5be2104f37a0dbc0 |
| aritmetica.eval.jsonl | 486830 | 6711b8f5e51303b7b8672ef15aff79f111e3e2be6a58d8ade72b7bb5d80c3379 |
| hechos-nativos.jsonl | 53835 | 4ec8fdfc7adc6d990261ece64799347243ce322d08e49a81514b6400348c42e4 |
| duplicados-excluidos.jsonl | 55061 | 274af119ed184b161bda0e0ab38b7222d0b4bb0c390c247aefcbe3d1e73f459a |

La entrega incluye `fuentes/consolidate.mjs` para repetir esta auditoría, los corpus originales, la cápsula XI entrenada, el checkpoint comprimido, transcripciones, fuentes y el ejecutor Linux original. No es una APK ni una actualización automática de REVERSE. El código nativo probado sigue siendo `5a567e6c5ab6dbfa9faf0ad6382251597d21b4fe`; este documento no implica una nueva ejecución de entrenamiento.
