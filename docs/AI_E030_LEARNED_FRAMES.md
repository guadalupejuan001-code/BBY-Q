# E030 — formas de consulta aprendidas en XI

Objetivo: aprender una forma de pregunta doble ES y otra EN mediante ejemplos,
con un programa idéntico antes y después. E029/main aporta hechos naturales y
respuestas con procedencia; se conserva esa ruta completa. E026/E027 combinado
permanece preservado en PR #33; este candidato no fusiona su política factual.

## Contrato
- El docente explícito entrega consulta cruda, sujeto supervisado, idioma e
  intención 1 (definición y requisito). No entrega plantilla, posiciones,
  prefijo, sufijo, respuesta ni hechos de examen al aprendiz de gramática.
- `learn.xi` encuentra una única ocurrencia del sujeto con límites de palabra,
  deriva los lados literales y exige otro sujeto distinto con ambos lados
  idénticos antes de activar. Un duplicado no cuenta; un ejemplo incompatible
  falla sin publicar el destino. El registro activo no se puede reenseñar.
- `normalize.xi` interpreta las reglas RVPC2 y reescribe solo una consulta de
  un sujeto al objetivo canónico que E028 ya sabe resolver. E029/E028 selecciona
  evidencia, polaridad, cita y respuesta; no se añaden respuestas al anfitrión.
- Conserva el principio de dos testigos y roles de `grammar/learn-pattern.xi`.
  La gramática histórica depende de IDs léxicos y E022 está sellado; este
  módulo usa bytes para entidades archivadas E028 no presentes en el léxico,
  en una región independiente sin modificar esos modelos anteriores.

Región nueva: T=9200000000000000000. T+0 esquema. Buzón T+16..1023 se borra.
Ocho registros desde T+1024 con paso 256: testigos, idioma, longitudes,
primer sujeto, prefijo/sufijo y segundo sujeto. El examinador compara memoria
lógica, núcleo y bindings antes/después de enseñar, fuera de T..T+3071.

## Límites
Un solo sujeto ASCII minúsculo alfanumérico de 1..31 bytes. Lados de 1..80
bytes; solo letras minúsculas, cifras y espacios en las demostraciones.
La intención de dos relaciones está supervisada y fijada, no se descubre una
semántica o gramática universal. Un aprendiz separado XI requiere una sesión
docente explícita; los mensajes normales no pueden activar el aprendizaje.
Hasta ocho reglas; dos coincidencias con capturas incompatibles se rechazan.

## Aceptación y evaluación
Dos sujetos docentes, 24 sujetos diferentes reservados para 48 preguntas ES/EN.
Medir antes, después y ablación usando E029 sobre la memoria aprendida.
Hash de cápsula fijo, cambios de enseñanza solo en la región declarada,
reinicio de proceso por turno, ausencia/negación/mezcla de sujetos,
conservación del archivo y de hechos E025. Reejecutar también E029, E028,
E027, E025 sobre la cápsula candidata y W4u. No declarar el criterio cumplido
antes de obtener CI real. Semilla E025 preservada; estados docentes/examen
son desechables y no reemplazan el conocimiento publicado.

## Reproducir en el ejecutor configurado
```sh
python3 ai/releases/e030/regression.py deps/reverse/build/reverse_pc evidence/e029
python3 ai/releases/e030/test.py deps/reverse/build/reverse_pc evidence/e029 evidence/e030-learning
```
El workflow E029 existente ejecuta además todas las regresiones y conserva
cápsulas, estado anterior, checkpoint aprendido, transcripciones e informes.
Mismo runner y dependencias fijadas; no se añade ejecutor o programación.
No se instala en Android ni se atribuye coordinación autónoma de ingeniería a W4u.

## Resultados nativos verificados
CI [40781527990](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40781527990), código
`0061bcda177fc31f609939860ed9d0a75e222d50`, completada con éxito.
181 comprobaciones nuevas: **0/48 → 48/48** después de aprender, frente a 0/48
de E029 sobre la misma memoria aprendida. Dos sujetos docentes distintos;
24 sujetos reservados y reinicio nativo por turno. Cápsula antes/después:
`c9a33a322f58ac6d93f18ff3c59678ef637ac9612bb71845e122e8f5c9de43f9`.
Comparación del núcleo, bindings y memoria fuera de la región nueva aprobada.

Pasaron además E025 original 31, E025 sobre el candidato 31, E029 285,
E028 464, E027 429 y W4u 21. Los examinadores conservan etiquetas de versión
heredadas; la ruta y hash registrados en CI identifican la cápsula realmente usada.
Las regresiones amplias se ejecutaron antes de enseñar; las 181 comprobaciones
incluyen controles de conservación después de enseñar.

[Artefacto con cápsulas, checkpoints y transcripciones](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40781527990/artifacts/12857507917).
Checkpoint aprendido experimental:
`5a0d469fc70248a2afc7a6a319a9a854d6498fa7682d9351e543f0d701ae7cf6`.
Contiene hechos sintéticos del examen: no se publica como conocimiento real
ni reemplaza la semilla E025. El artefacto caduca el 26 de enero de 2027;
SIGUIENTE exige exportar la región aprendida de forma durable antes de esa fecha.
PR #33 conserva el candidato E026+E027. La política común entre sus hechos
y las fuentes E029 sigue pendiente, sin promoción ni despliegue Android.
