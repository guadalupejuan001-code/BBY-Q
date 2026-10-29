# E033: relaciones compartidas en estados mínimos

BBY Q continúa siendo la IA principal. Aprendizaje, análisis de frases, diccionarios, índices, caché, correcciones y respuestas se ejecutan en XI sobre Ether/RVPC2. Python solo enlaza fuentes, transporta ejemplos etiquetados y examina resultados; no selecciona respuestas. No hay motor externo, sustitución por SOVENGI ni Transformer añadido.

## Arquitectura

Región decimal exacta 8500000000000000000, longitud73728; ceros implícitos no materializados. Se conserva íntegra la memoria E032 anterior. Hasta32 marcos de256bytes, aprendidos desde dos ejemplos que cambian sus roles; después se descarta el primer ejemplo y quedan los literales y etiquetas necesarios. Intenciones: afirmación, pregunta, corrección explícita. Relaciones funcionales identificadas por ID1..16; sin ramificar el intérprete por cada verbo.

Dos diccionarios compartidos y direccionados por hash con comparación completa de bytes: entidades de hasta48bytes y valores de hasta80bytes, con96 elementos por diccionario y127 posiciones. Se comparten textos repetidos. Tabla de256 posiciones,8bytes por clave entidad/relación. Diario apendicular de255 eventos,8bytes cada uno: IDs de entidad, relación, valor, marco y enlace a la evidencia previa. El marco y los roles permiten reconstruir la afirmación normalizada mediante @rel source N, sin duplicar el texto de la frase. La normalización conserva UTF-8 y baja solo mayúsculas ASCII; no preserva el uso original de mayúsculas.

La consulta usa el índice, emite el valor con referencia [#rNNN] y reutiliza una caché de última clave. Toda nueva evidencia invalida esa caché; preguntas desconocidas no crean hechos. Afirmaciones iguales son idempotentes. Dos valores incompatibles para una relación funcional producen abstención; solo la construcción aprendida de corrección explícita publica una revisión como vigente, conservando el diario. Los límites se comprueban antes de publicar para evitar cadenas huérfanas o pérdidas por capacidad.

## Enseñanza y aceptación

22 construcciones y44 ejemplos supervisados: apertura de taller, ubicación de libreta, día de cita, ES/EN y una relación ficticia adicional. No es extracción general de prosa; una relación por turno dentro de marcos aprendidos, ni comprensión abierta de todos los verbos. Las categorías temporales E032 continúan separadas; esta etapa no implementa fechas absolutas ni orden general de eventos.

Examen independiente:24 entidades reservadas,4 relaciones,168 preguntas ES/EN; comparar E032 con los mismos hechos y preguntas. Verificar deduplicación, colisiones de hash, ausencia de estados nuevos por consultas, invalidación de caché, reconstrucción de procedencia, UTF-8, múltiples palabras y rechazo atómico al llenar diccionarios/diario. Conservar144 respuestas temporales, E027/E028/E029 completos, E025 y W4u. Medir crecimiento real de archivo/gzip frente al archivo textual nativo; registrar diferencias de representación y no atribuir a compactación una aceleración no medida.

Las32 preguntas de comparación anteriores se incluyen como diagnóstico de desarrollo, nunca como nueva prueba reservada. El modelo se guarda antes de ingresar hechos de examen. E032 y todos los checkpoints previos permanecen disponibles. Resultados pendientes de CI; no declarar capacidad aprobada antes de su ejecución.
