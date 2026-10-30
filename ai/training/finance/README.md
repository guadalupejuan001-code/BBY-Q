# BBY Q — entrenamiento económico F001 + F002

Objetivo del operador: comprender «farmear dinero», generación de ingresos, negocios y sus proyectos; preparar progresivamente capacidades antes de usar fondos reales. No se habilita trading, compras o transferencias.

## Qué incorpora esta campaña

F001: 80 conceptos y 160 afirmaciones en el archivo contextual del agente XI/Ether E034. Su CI original 40995126415 aprobó 488 comprobaciones, incluyendo 320 respuestas exactas. Artefacto 12951241161; commit 9c70d68c7438c15185655741a82f4a52860695a1.

F002 continúa esa copia exacta, conserva los 160 hechos y añade otros 160: 160 conceptos y 320 afirmaciones en total. Añade conocimientos de monetización de REVERSE, BBY Q, renderizadores, XI, Ether y Laplace; costes, márgenes, caja, riesgos, experimentos comerciales y evaluación de predicciones.

La ruta E034 confundía «oye que es ingreso» con una afirmación. Se añade normalización acotada escrita y ejecutada en XI: muletillas, interrogación, acentos de vocales, once prefijos de consulta y once expresiones de intención económica. No es gramática aprendida autónomamente. Las expresiones económicas se convierten en consultas educativas, nunca en órdenes de operación.

BBY Q sigue siendo el agente; no se añade otra IA, otra memoria principal ni un servicio externo. Se conserva BBY Q → w4U → QdU. No se sustituye el agente E038/X04 de REVERSE ni se toca la memoria del operador: esta es una cápsula candidata E034/F001/F002 independiente del despliegue Android.

## Datos versus aprendizaje demostrado

- 7.600 ejemplos preparados: 4.752 de F001 y 2.848 adicionales de F002.
- 1.024 escenarios numéricos de evaluación: 512 de cada campaña. Son datos de examen, no una puntuación del modelo.
- Lo que se incorpora realmente en este ciclo son los 320 hechos estructurados acumulados. El corpus conversacional/numérico amplio no se cuenta como consumido.
- La evaluación comprueba recuperación, consultas compuestas, seguimiento, variantes diseñadas, retención y reapertura. No demuestra conversación abierta ni rentabilidad financiera.

## Reproducir

Con el artefacto original F001 extraído en `prior-f001` y su ejecutor XI:

```sh
node ai/training/finance/train-f002.mjs export evidence/corpus-f002
node ai/training/finance/train-f002.mjs train prior-f001/runtime/reverse_pc prior-f001 evidence/f002
```

El script comprueba hashes del checkpoint y de la cápsula antes de trabajar. Construye `query-normalizer.xi`, lo enlaza al código XI E034 recuperado sin reemplazarlo y entrena sobre una copia. JavaScript solo prepara datos, emite fuentes XI y transporta/examina mensajes; no decide respuestas en producción. El bootstrap original no se modifica.

Salidas: `results.json`, `transcripts.jsonl`, `BBY-Q-F002.rxe`, `finance-f002.rvp.gz`, corpus y fuente XI completa. La cápsula final incluye su semilla entrenada. No es una APK ni debe reemplazar automáticamente el checkpoint personal de una versión posterior.

La CI reproduce F001 y F002 y conserva las regresiones históricas E025/W4u. Las cifras definitivas de cada ejecución solo se publican cuando termina; una ejecución incompleta no se suma a los resultados aceptados.

## Límites y procedencia

Se heredan 255 bytes por entrada y 512 entradas contextuales; esta campaña ocupa 320. La normalización acepta hasta cuatro muletillas iniciales. Son límites explícitos del ABI y de esta gramática, no una declaración de capacidad ilimitada.

Los ejemplos numéricos son ficticios, se separan por escenario y no contienen saldos, claves, biometría ni datos bancarios del usuario. Las plantillas aritméticas se comparten entre entrenamiento y examen: no presentar ese corte como generalización a familias desconocidas. Las definiciones son redacción educativa original; `sources.json` conserva referencias SBA/Investor.gov y el origen de las convenciones del operador.
