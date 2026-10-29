# E034: composición de relaciones tipadas en XI/Ether

BBY Q sigue siendo la inteligencia principal. Este candidato conserva el modelo E033 y aprende ocho formas adicionales desde dieciséis ejemplos, con código fijo durante las lecciones. Las demostraciones no contienen hechos del examen.

Las relaciones funcionales 1 (apertura) y 5 (ubicación) pertenecen al tipo taller; 2 es ubicación de libreta, 3 cita y 4 baliza. El nombre internado es texto compartido, no identidad semántica entre tipos. Una consulta compuesta induce el literal del marco desde dos ejemplos y declara explícitamente los IDs 1 y 5. El operador XI consulta ambos índices, comprueba ambas evidencias antes de imprimir y conserva las dos fuentes. Se abstiene si falta una propiedad o existe conflicto; correcciones mantienen el diario anterior.

La referencia conserva únicamente dos bytes: ID internado y tipo, en el encabezado E033, 8400000000000000012..0013, antes libres. No copia texto ni respuestas. Cuatro formas de seguimiento se implementan explícitamente: «¿Y dónde está ese taller?», «¿Y qué día abre ese taller?» y sus dos formas inglesas. Son ingeniería de interfaz gramatical, no aprendizaje de pronombres arbitrarios. Una entidad de otro tipo, entrada no reconocida o consulta fallida invalida el antecedente. El estado de referencia no representa fecha de ocurrencia.

Mantiene la región 840... E033 y sus diccionarios, hechos y diario, añade marcos 23..30 sin migrar ni borrar los anteriores. Los límites continúan siendo 32 marcos, 96 entidades/valores y 255 eventos. El modelo limpio se guarda inmediatamente después de enseñar, antes de los 72 hechos reservados. E033/E032 y sus checkpoints se conservan.

Aceptación fijada antes de ejecutar: 48 respuestas compuestas exactas con fuentes, 96 seguimientos, 24 controles de nombres iguales/tipos distintos, abstención atómica ante falta/conflicto, conservación íntegra de memoria previa al enseñar y prueba de capacidades históricas. Casos de examen trama[a-x], valores y combinaciones diferentes de tutora/tutorb y teachera/teacherb. Se compara E033 original y el operador E033 con los mismos marcos aprendidos para separar la contribución del nuevo operador.

Ejecutor exclusivo: workflow existente bbyq-e029.yml/native-e029, ubuntu-latest; mismo grupo de concurrencia, pins y límites. Los scripts Python solo compilan, transportan datos, invocan XI y verifican resultados; no eligen respuestas.

Estado: candidato pendiente de CI nueva. No despliegue Android, no Transformer, no cambio de SOVENGI ni coordinación autónoma de repositorio atribuida a W4u.
