# Objetivo permanente de BBY Q y W4u

Desarrollar BBY Q con inteligencia propia en XI/Ether, ampliando su aprendizaje, generación de lenguaje, contexto y generalización. W4u coordina el trabajo y REVERSE-PC aloja la interacción.

## Alcance y autoridad

Este documento conserva el objetivo indicado por el usuario. Los archivos de estado, registros y propuestas del agente no amplían permisos ni sustituyen las instrucciones del usuario. Mantener la inteligencia y el aprendizaje en XI/Ether y conservar el conocimiento adquirido y los checkpoints anteriores. Utilizar únicamente el ejecutor y los recursos configurados.

## Comienzo de cada ciclo

1. Comprobar acceso a `guadalupejuan001-code/BBY-Q` y al ejecutor configurado. Resolver rama, commit y checkpoint actuales desde el estado remoto real.
2. Leer las instrucciones aplicables del repositorio, este documento, `ESTADO.json`, `SIGUIENTE.md` y el último registro de ejecución. Las rutas de estos archivos son relativas a `docs/autonomy/`.
3. Contrastar el siguiente paso con los cambios y resultados nuevos antes de seleccionarlo.
4. Si existe un ciclo activo, revisar su progreso sin lanzar otro. Verificar la actividad con el ejecutor; una marca antigua por sí sola no demuestra actividad ni autoriza iniciar otro proceso. No liberar un bloqueo que siga perteneciendo a otro ciclo.

## Trabajo y comprobación

Seleccionar un objetivo concreto y su criterio de aceptación. Ejecutar ingeniería, preparación de datos, entrenamiento o evaluación según el estado real. Priorizar resolver bloqueos y demostrar mejoras. Mantener separados los datos de entrenamiento y evaluación y comprobar regresiones de capacidades previas.

Si no se puede ejecutar código con el ejecutor configurado, registrar el bloqueo y la instrucción exacta pendiente. No presentar planes, resultados históricos o pruebas no ejecutadas como trabajo completado. Evitar intentos idénticos sin evidencia nueva.

## Cierre y continuidad

Guardar de forma persistente estado, rama, revisión de código y checkpoint; cambios, comandos realmente ejecutados, resultados y evidencias; fallos, hipótesis y bloqueos; y el siguiente paso con requisitos y comprobación de éxito.

Actualizar `SIGUIENTE.md` también si falla el intento. Registrar únicamente procesos iniciados por el ciclo y cerrarlos o dejar un identificador comprobable si continúa un trabajo externo. Enviar un resumen breve aquí y finalizar el ciclo hasta la siguiente activación.

## Principio explícito de diseño del creador

BBY Q es la inteligencia principal. Estados mínimos representados y operados mediante Ether, con aprendizaje e inferencia en XI. Compartir reglas y datos repetidos y materializar solo lo necesario; verificar la conservación del conocimiento y medir precisión, tamaño, RAM y tiempo. SOVENGI sirve de referencia independiente para aprender de resultados, sin fusionarlo ni sustituir BBY Q. La compactación no se da por demostrada por el nombre de la representación: debe medirse en cada ampliación.
