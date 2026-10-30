# F002 — conocimiento económico y consultas del operador en XI

## Resultado local verificado

Código: `5a567e6c5ab6dbfa9faf0ad6382251597d21b4fe`.
Se ejecutó el runtime original recuperado del artefacto F001 `12951241161` en Linux x86-64. Las tres fuentes nuevas coinciden byte por byte con los blobs Git: `extension.mjs` = `02f6ae25306d746d9a331eebc972b610715aea27`, `build-normalizer.mjs` = `df0179f478e023344c38ffc1d35f110cffb48e31`, `train-f002.mjs` = `e46be9035d54e8859f06a9bc5e5872b9a6d3151c`.

**899 comprobaciones aprobadas en una ejecución completa.** Un intento anterior se interrumpió por el límite de tiempo del entorno y NO se cuenta como una prueba aprobada. El intento aceptado partió otra vez del F001 original.

| Medida | Resultado |
|---|---:|
| Conceptos nuevos incorporados | 80 |
| Conceptos acumulados F001 + F002 | 160 |
| Nuevos hechos contextuales incorporados | 160 |
| Hechos contextuales acumulados | 320 |
| Respuestas sobre hechos anteriores conservadas | 160/160 |
| Consultas nuevas de definición, requisito, composición y seguimiento | 320/320 |
| Variantes diseñadas de consulta e intención | 239/239 |
| Controles negativos y de rutas no modificadas | 11/11 |
| Ejemplos preparados acumulados | 7.600 |
| Escenarios numéricos de examen preparados | 1.024 |

Las restantes comprobaciones incluyen ingestión, conteo del archivo, reapertura, semilla empaquetada y conservación de hashes. No sumar las categorías a las 899 como si fueran pruebas adicionales. El corpus aritmético NO ha sido aprendido ni evaluado como capacidad del agente. La exactitud sobre hechos enseñados NO demuestra razonamiento económico abierto.

## Fallo corregido

Antes, E034/F001 respondía `Registré esa afirmación.` a `oye que es ingreso`, `pz que es beneficio` y `mira que es farmear dinero`. Era contaminación del archivo contextual por una mala clasificación de consultas.

F002 añade un prefijo de interpretación ejecutado en XI. Solo compromete la entrada normalizada si coincide con una forma de consulta diseñada. Las demás entradas y comandos explícitos llegan intactos al motor anterior. Se comprueba que las consultas de la batería no aumenten los 320 registros.

Las muletillas y correspondencias están diseñadas; no afirmar que se descubrieron por aprendizaje autónomo. JavaScript emite el programa, prepara el currículo y verifica salidas; el agente consulta y responde en XI/Ether sin otro modelo.

## Respuestas reales del candidato

```text
Operador: pz quiero farmear dinero
BBY Q: farmear dinero requiere medir ingresos costes tiempo y posibles perdidas [#001].

Operador: pz como monetizo reverse
BBY Q: monetizar reverse requiere identificar comprador utilidad precio y coste de entrega [#007].

Operador: pz como valido laplace
BBY Q: validar laplace requiere conservar fallos y aciertos fuera de datos usados para ajustarlo [#307].

Tras crear un estado nuevo desde la cápsula entrenada:
Operador: ¿Oye, qué es economía unitaria?
BBY Q: economia unitaria es analisis de ingresos y costes atribuibles a una unidad de negocio [#160].
```

## Artefactos e identidad

- Checkpoint sin comprimir: 1.541.164 bytes; gzip: 209.653 bytes.
- SHA-256 checkpoint: `80e10341872a93d5a9ca648958c7b1ebd38212209503f9cb558d6d1e7e5b0215`.
- SHA-256 cápsula entrenada: `02edd2efc162e61a98b55d24b17301a6a2d909e32109401afd8c9ad9b62b5e41`.
- SHA-256 fuente XI enlazada: `912a58e3ed1cc40c1a770cb0a4afeff95af7d9771840d06f47990d867b5c1d6e`.

El campo `source_sha` de esta cápsula contiene los primeros 40 caracteres del digest de la fuente XI, no un nuevo commit Git. La procedencia Git completa se registra arriba.

La ingestión de los 160 hechos nuevos tomó 32.954 ms en esta ejecución; no es un rendimiento Android ni una comparación causal entre lenguajes. No se midió aceleración cuántica.

## Alcance de integración

Se conserva BBY Q → w4U → QdU. No se modifica REVERSE, la APK, el agente E038/X04, memorias privadas, cuentas ni permisos financieros. F002 es una cápsula candidata basada en E034/F001 con su semilla entrenada; no debe reemplazar automáticamente un modelo posterior. No ejecuta compras, trading ni transferencias.

Falta enseñar y medir razonamiento numérico/económico, conversación abierta y migración al agente más reciente de la APK. El volumen del corpus no sustituye esas pruebas. Fuentes educativas y procedimientos de reproducción: `ai/training/finance/README.md`. Resultado estructurado: `docs/evidence/f002-local-results.json`.

La CI añadida reproduce la campaña. Este informe acredita la ejecución local, no presupone el resultado de ninguna CI todavía en curso.
