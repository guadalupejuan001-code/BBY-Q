# Siguiente ciclo

## Verificación completada

El run 40711150887 y su job 122896463149 terminaron con success: 6.365 comprobaciones y checkpoint idéntico. No repetir esta campaña sin nueva evidencia. Evidencia:
https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40711150887

La revisión de ingeniería probada es `6a48224e63d1a23d6bfc4866902749875650d6e8`. Los commits posteriores que solo guardan notas usan `[skip ci]` para no repetir una campaña idéntica. Resolver los HEAD actuales y comprobar que ningún cambio posterior altera el código probado. No equiparar una marca de ESTADO.json con la actividad real del runner.

Al comenzar otra activación, comprobar cualquier trabajo posterior y conservar la evidencia ya registrada. El acceso al runner quedó verificado mediante el evento pull_request; no se utilizó el comando gh pendiente anterior.

## Objetivo de inteligencia tras validar el runner

Diagnosticar y ampliar la composición de una respuesta con **dos hechos de predicados diferentes sobre el mismo referente**, a partir de memoria XI/Ether, en español e inglés.

1. Confirmar si la revisión vigente ya permite esa composición. Medir el comportamiento inicial y dejar transcripciones; no suponer una puntuación de partida.
2. Preparar sujetos de enseñanza y 24 sujetos independientes de examen, sin compartir nombres. Separar los ficheros y las respuestas esperadas del proceso de aprendizaje.
3. Enseñar hechos y patrones de expresión mediante la ruta nativa. Si hace falta ingeniería, implementar la composición y selección de evidencia en XI/Ether, conservando el transporte existente.
4. Examinar 48 consultas ES/EN: cada respuesta debe expresar los dos hechos respaldados del mismo sujeto. Añadir controles con un hecho desconocido, negación y cambio de referente; no rellenar la respuesta con hechos inventados.
5. Comparar antes/después, comprobar persistencia tras reiniciar y ejecutar las regresiones pertinentes de la base vigente. Para E022, conservar las 6.365 comprobaciones de referencia y sus checkpoints.

Criterio de aceptación: 48/48 consultas nuevas correctas sobre los dos hechos, controles sin invención ni mezcla de sujetos, persistencia verificada y ninguna pérdida en las regresiones. Si el diagnóstico demuestra que ya lo resuelve, seleccionar otra debilidad demostrada en lugar de repetir esta enseñanza.

## Requisito pendiente de W4u e integración

Los árboles inspeccionados de REVERSE-PC (`main` cf7854fc0499801c3206fea38043806060b9ed5d y `feature/workbench-native-20261027` 09adc1290f8492ddccee362ef3906aef264ba48f) no identificaron una versión de W4u. La documentación publicada de la aplicación BBY Q describe E016, mientras BBY-Q publica E022.

Localizar una revisión, ruta, configuración y pruebas verificables de W4u antes de atribuirle coordinación o mover checkpoints a REVERSE-PC. No suponer que un checkpoint mencionado en una conversación está publicado. Esta comprobación no autoriza sustituir un estado más reciente ni borrar memorias de la aplicación.

Actualizar ESTADO.json, este archivo y el registro también ante fallo. Reintentar solo si cambió la evidencia, el acceso o la hipótesis.
