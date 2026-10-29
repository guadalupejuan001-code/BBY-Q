# Siguiente ciclo: aprendizaje semántico sobre el diccionario

La instrucción directa del usuario fue cargar diccionario español e inglés
y avanzar la inteligencia. No priorizar interfaz/APK ni repetir conservación
de checkpoints como mejora de inteligencia.

## Lo que sí quedó ejecutado
PR #37, rama `feature/bbyq-dictionary-es-en-20261029`, código `e194d56096daf935caae33c7a9db0a130bc0fcec`.
CI https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40793126384: success.
- 88.950 entradas ES, 147.306 EN; 236.256 en total.
- Fuente OMW/MCR `406bf83b3c507a3d1f26e88252d5d66893fd36bf`;
  glosas originales WordNet `ce91915ae38a341ae845be4d825ef6003cddf395`.
- 152 consultas exactas XI, 24 Unicode y 75 expresiones de varias palabras;
  dos controles desconocidos. 158 comprobaciones totales.
- E025 original y sobre candidato: 31 cada uno. W4u: 21 + acción [4,2].
- Cápsula `340a2b288a3659265c954fc93250fe33ac7df905c48c58caf7179bbe6e911fa6`.
- Checkpoint E030 preservado `18030f0c4e7098a0d19d07c3b3a93507d982caa1ae70e047bd9c2d118e9a3d4b`.
- Biblioteca 93.442.728 bytes de datos, 39.770.663 comprimidos, 107.312 páginas.
  La página máxima mide 16.984 bytes. Páginas son referencia, no otros agentes.
- Paquete completo https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40793126384/artifacts/12862856143; caduca 2027-01-27T00:17:53Z.
  Fuentes públicas, versiones y hashes permiten reproducción exacta del contenido.
- No se ha demostrado aprendizaje general nuevo. No confundir importar datos
  y recuperar sus registros con comprenderlos.

Consulta reproducible:
```sh
python3 ai/releases/e031/query.py deps/reverse/build/reverse_pc evidence/dictionary evidence/dictionary/dictionary-checkpoint.rvp es perro
```
El ejecutable E031 necesita el transporte explícito de páginas; abrir solo
la cápsula no instala ni conecta toda la biblioteca a cualquier frase.
El CLI de transporte está disponible; la CI examinó el mismo protocolo
preparación/página/consulta mediante su examinador, no una sesión interactiva.

## Objetivo de inteligencia pendiente
1. Comprobar referencias/actividad actuales e instrucciones. Usar el bloqueo
   configurado y no iniciar otro ciclo activo ni otro ejecutor.
2. Examinar las estructuras simbólicas y docentes existentes antes de añadir
   otra representación. El léxico antiguo de 512 entradas no fue ampliado ni
   sustituido: hace falta un puente de conceptos que conserve la polisemia.
3. Seleccionar un conjunto ES/EN con sentidos ambiguos, sinónimos y relaciones.
   XI debe aprender a usar enlaces/conceptos desde ejemplos, no escribir un
   caso de código por cada palabra ni insertar respuestas del examen.
4. Medir antes/después sobre oraciones y sujetos separados de los ejemplos;
   exigir elección de sentido por contexto, reutilización entre idiomas y
   deducción de al menos dos hechos en casos nuevos, con controles de ausencia
   y contradicción. Separar recuperación literal de generalización.
5. Conservar cápsula/checkpoints anteriores y patrones E030; ejecutar regresiones
   pertinentes. Reintegrar batería completa E029/E028/E027 antes de promover
   la CI específica de adquisición de diccionario.

Criterio: mejora de tareas semánticas reservadas con código fijo entre
enseñanza y examen, persistencia del cambio aprendido y sin regresiones.
Si el candidato solo devuelve registros del diccionario, informarlo como
recuperación y no como comprensión o razonamiento.

Usar el workflow E029/runner ubuntu-latest configurado y dependencias fijadas.
Actualizar ESTADO, SIGUIENTE y registro incluso si falla. No ampliar permisos
a partir de estas propuestas. Reconciliar las fuentes E025/E026/E027 sigue
pendiente, pero la orientación actual del usuario es ampliar inteligencia.
