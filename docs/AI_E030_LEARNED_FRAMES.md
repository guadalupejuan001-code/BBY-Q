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
