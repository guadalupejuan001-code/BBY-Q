# E032 — aprendizaje de formas temporales y separación de evidencias
Se añade un aprendiz y un intérprete propios XI, sobre la cápsula E031 exacta.
El código no enumera conjugaciones. El docente transporta frases completas,
sujeto/objeto supervisados, idioma, intención, polaridad y etiqueta temporal.
XI localiza ambos referentes e induce prefijo, parte intermedia y sufijo;
otro ejemplo debe variar ambos referentes antes de activar el patrón.
Se retoma el principio de dos testigos de grammar/learn-pattern.xi, preservando
los modelos sellados anteriores y usando otra región del mismo RVPC2.

Hay 48 formas ES/EN, 96 ejemplos independientes de los 24 sujetos de examen.
Incluyen tenía/tiene/tendrá y had/has/will have, negaciones, preguntas y
marcadores ayer/hoy/mañana, yesterday/today/tomorrow, variantes acentuadas.
Son datos docentes; no casos del intérprete. La enseñanza no recibe respuestas,
eventos del examen ni plantillas con huecos: solo texto y roles/etiquetas.

Los hechos se indexan por sujeto, objeto y categoría temporal. Evidencia de
pasado no afirma presente/futuro. Lo futuro siempre queda como previsión
no confirmada. Dos afirmaciones opuestas en el mismo momento producen
abstención, conservando las otras categorías y los registros anteriores.

Región: 8650000000000000000; marcos desde +4096, 64 registros de 256 bytes;
hechos desde +65536, 256 de 80 bytes. Buzón/scratch +16..4095 se borra.
Se mantienen el diccionario externo E031, contexto E029 y patrones E030.
No se vuelve a importar el diccionario ni se cuentan sus entradas como
aprendizaje temporal. La fuente enlazada de E031 se recompila y reempaqueta
exactamente antes de enlazar el candidato.

## Alcance
Primera capacidad acotada para posesión, entidades/objetos de un token ASCII,
tres categorías temporales relativas. No hay fechas, desplazamiento del
reloj, orden de eventos dentro de una categoría, aspecto perfecto/progresivo,
condicional/subjuntivo o conjugación general. Una previsión no es un hecho
observado y una afirmación del usuario no es verificación externa.
Las pruebas entre idiomas mantienen el mismo identificador del referente
(piano, radio, taxi, hotel); no demuestran traducción general.

## Reproducir en el runner configurado
```sh
python3 ai/releases/e032/build.py deps/reverse/build/reverse_pc prior evidence/temporal
python3 ai/releases/e032/test.py deps/reverse/build/reverse_pc prior evidence/temporal
python3 ai/releases/e031/regression.py deps/reverse/build/reverse_pc evidence/temporal-compat evidence/candidate-regression
```
Descargar el artefacto E031 run 40793126384 a prior. CI E029 existente:
mismo runner y pins, sin nuevo ejecutor. En temporal-compat/dictionary.rxe
se copia temporal.rxe para reutilizar el examinador histórico E025/W4u.
E032 test también prueba el CLI de diccionario E031 sobre la cápsula nueva.

Aceptar solo con comparación real antes/después y con E031 sobre la misma
memoria, 144/144 preguntas reservadas, controles de aislamiento y conflicto,
código idéntico entre enseñanza/examen, memoria anterior intacta durante
enseñanza, persistencia y regresiones. No declarar resultados antes de CI.
