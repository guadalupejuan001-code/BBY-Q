# Continuidad de F003

## Alcance actual

Fuente inglesa gratuita con aviso de dominio público, lecciones españolas originales y adquisición contextual en la copia congelada E034/F001/F002. No es el agente posterior de la APK ni se deben sobrescribir sus estados. BBY Q → w4U → QdU se conserva.

El número de hechos o de comprobaciones solo se acredita con el `results.json` final y sus transcripciones. Descargar el PDF y preparar ejemplos no basta. No sumar intentos fallidos como ejecuciones completas.

## Hallazgos de compatibilidad

1. La cabecera de la cápsula F002 no tiene el desplazamiento fijo que se había supuesto. Se localiza RXE1 y se validan límites antes de extraer el ejecutable.
2. El archivo acepta registros de hasta 224 bytes, pero el lector relacional E028 omite valores mayores de 80. Once definiciones se redujeron y el entrenador rechaza valores incompatibles antes de enseñar. No se amplió el motor.
3. E028 elimina artículos iniciales `el`, `la` y `the` en preguntas, pero no en los registros introducidos con `@ctx add`. Se conserva `surface_term` y se usa un sujeto canónico compatible al enseñar. El título se puede preguntar con o sin `el`. El sujeto recuperable admite 48 bytes, no 80.

Son contratos actuales de implementación, no límites físicos de XI/Ether. Una ampliación debe cambiar de forma consistente almacenamiento, consulta, foco, semilla y pruebas, no solo quitar una comparación.

## Próxima prioridad propuesta

Enseñar y medir aplicaciones numéricas en XI: porcentajes, ingresos menos costes y distribución narrativa 10/70/20, con casos nuevos y datos faltantes. Los 128 escenarios numéricos F003 están reservados, no aprendidos. No deben mezclarse con entrenamiento para luego presentarlos como examen independiente.

Después: conversación de varios turnos con cifras corregidas; distinguir preguntas abiertas de afirmaciones para no contaminar la memoria; revisar capacidad de archivo (448 de 512 entradas ocupadas); ampliar el lector si hace falta sin perder regresiones; migrar conocimiento al agente actual de REVERSE conservando su memoria.

No habilitar transacciones como consecuencia de aprobar recuperación textual. No cambiar la APK hasta probar integración y versión de agente. No fusionar automáticamente esta rama por la mera existencia de un artefacto.
