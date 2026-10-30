# F003 — El hombre más rico de Babilonia

Solicitud: descargar un PDF gratuito del libro y enseñar sus principios a BBY Q. Se mantiene BBY Q → w4U → QdU; no se reemplaza el agente posterior de REVERSE ni se modifica memoria personal, cuentas, permisos o APK.

## Fuente

- George S. Clason, *The Richest Man in Babylon*. Original inglés, 122 páginas.
- PDF: https://cpcglobal.org/publications/The%20Richest%20Man%20in%20Babylon.pdf
- SHA-256: `76b620d86a163a1934aebeea997f75c1c685d0ecd877f4a0854f0ab3e0e29b69`.
- La página 2 declara dominio público y permite distribución gratuita. Se conserva ese aviso. El texto indica 1926; el PDF fue creado en 2009. No se copia una traducción comercial al español.
- Referencia sobre dominio público estadounidense: https://copyright.gov/what-is-copyright/
- Las lecciones españolas son paráfrasis educativas propias. Cada una identifica páginas y origen: 56 del libro, 3 aplicaciones modernas separadas, 5 distinciones críticas.

## Qué se enseña y qué no

64 conceptos con 2 propiedades cada uno: 128 hechos estructurados nuevos. El candidato parte de los 320 hechos F001/F002 y debe terminar con 448; ningún resultado se considera aprobado hasta que termina la ejecución y existe `results.json` con `completed: true`.

El libro enseña principios mediante relatos: reservar parte de los ingresos, controlar gastos, reinvertir, proteger capital, buscar consejo pertinente, mejorar habilidades, actuar ante oportunidades comprendidas y organizar deudas. Sus proporciones y ejemplos se atribuyen al relato, no se convierten en órdenes personales o promesas de rentabilidad.

La adquisición ejecutada usa el archivo contextual persistente XI/Ether del candidato E034/F001/F002. No es ajuste de pesos neuronales ni ingestión literal del libro completo. El ejecutable XI se conserva byte por byte; cambia el estado aprendido. JavaScript prepara datos y comprueba respuestas; no sustituye la inferencia por respuestas del anfitrión.

Hay además 448 diálogos preparados y 128 escenarios numéricos reservados. No se cuentan como aprendidos. Los exámenes de recuperación comprueban formas de pregunta diseñadas sobre hechos enseñados, no generalización semántica a cualquier conversación.

## Fallos hallados y tratamiento

El primer lector de cápsula suponía un encabezado de longitud fija; F002 tiene otro desplazamiento. El transporte ahora localiza RXE1 y valida cotas sin modificar la cápsula original.

La segunda ejecución guardó 128 hechos y conservó los 320 anteriores, pero no recuperaba 11 definiciones. El lector XI E028 omite valores mayores de 80 bytes, aunque `@ctx add` acepta registros más largos. Se reformularon esas 11 definiciones y se añadió validación previa de valor, sujeto, registro y mensaje. El límite del lector NO fue ampliado ni se presenta como límite físico de Ether. Los intentos fallidos no se suman como campañas aprobadas.

## Reproducir

Node 22.16.0; runtime Linux x86-64 original, sin reconstruirlo. SHA-256 del runtime: `ef0c3a709121b8fd3cf4c996808ecfef8b60a7065d3f9c802280c58dc9370d84`.

El paquete F002 debe contener `modelo/BBY-Q-F002.rxe`, `modelo/finance-f002.rvp.gz`, `datos/hechos-nativos.jsonl`. El entrenador comprueba los hashes exactos de app y estado antes de trabajar sobre copias.

```sh
node ai/training/babylon/train-f003.mjs export evidence/corpus-f003
node ai/training/babylon/train-f003.mjs train RUNTIME F002_PACKAGE BOOK.pdf evidence/f003
```

La CI recupera la ejecución F002 aprobada `40996666892` y el artefacto `BBYQ-F001-economic-learning`; no usa estados personales posteriores. Dependencias de Actions fijadas por commit. El PDF se vuelve a verificar por hash.

Salidas: `BBY-Q-F003.rxe`, `finance-f003.rvp.gz`, código XI sin cambios, `results.json`, `transcripts.jsonl` y corpus. Se examinan adquisición, retención de 320 hechos, definiciones y requisitos nuevos, composición de dos propiedades, seguimiento, variantes del operador, ausencia de evidencia y reapertura de semilla. Cuatro preguntas abiertas exploratorias se conservan con sus respuestas aunque fallen; no elevan la puntuación.

## Límites explícitos

255 bytes por mensaje; 224 por registro; 80 por valor recuperable; 512 entradas contextuales, de las cuales este currículo ocupa 448. Son restricciones del candidato actual, no capacidades infinitas ni limitaciones universales del lenguaje. Falta aritmética económica abierta y migración comprobada al agente de la APK.

No se ejecutan compras, inversiones, transferencias ni conexiones financieras. Una campaña aprobada acredita las pruebas indicadas, no autonomía para administrar dinero.
