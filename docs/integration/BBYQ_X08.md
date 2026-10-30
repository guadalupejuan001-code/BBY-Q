# BBY Q X08 — currículo unificado, lenguaje y persistencia

X08 continúa el agente X07 de REVERSE 2.9.0. Conserva la lógica del agente y añade operaciones de lenguaje y lectura, unifica las dos familias de entrenamiento de Babilonia y publica sesiones mediante versiones inmutables. P13 y P14 quedan excluidos por instrucción del operador. No se genera otra APK.

## Contenido incorporado

| Contenido | Resultado |
|---|---|
| F001/F002 y F003 del agente X07 | 224 conceptos anteriores conservados |
| F003 de la otra rama | 64 conceptos/variantes conservados |
| F004 del entrenamiento en dos mitades | 64 conceptos añadidos |
| F004 de la segunda mitad ampliada | 128 conceptos añadidos |
| Total reconciliado | 480 conceptos, 960 relaciones `es/requiere` |
| Diferencias entre definiciones | Diez variantes atribuidas; claves alternativas terminadas en `[f003-b]` |
| Libro original normalizado | 122 páginas, 225.418 bytes, correspondencia con los 1.171 fragmentos previos |

Los conceptos canónicos de X07 no se sustituyen por versiones antiguas. La migración preserva las correcciones personales y resuelve las consultas contra la clave actual del banco, incluso si la posición de un concepto cambió. El índice del currículo identifica fuentes; no demuestra comprensión semántica general. Las lecciones aprendidas después siguen disponibles por su clave exacta.

El libro se almacena una sola vez, con un diccionario compartido de 3.499 bytes y 150.437 bytes de secuencias comprimidas. XI materializa únicamente la página consultada. El códec conserva los bytes UTF-8 y los fragmentos originales se pueden reconstruir mediante `integration/x08/data/fragments.jsonl`. La reducción del contenido persistente del libro es de 225.418 a 153.936 bytes; no se presenta como una aceleración general del agente.

## Operaciones nuevas

```text
traduce al ingles: yo tengo tres coches
traduce al español: my car is red
corrige: yo es amable y ellos es nuevos
enseña traducción: planeta violeta | violet planet

resume en 2 frases:
Primera frase. Segunda frase. Tercera frase.

compara:
A: La ciudad tiene agua y parques.
B: El pueblo comparte agua y parques.

redacta correo:
destinatario: Alma
asunto: Entrega 79
contenido: El prototipo llegará el jueves. No incluye sensores.
firma: Nilo

lee pagina 67
consulta: nomasir caballo
Por que perdio Nomasir la apuesta del caballo
@book status
@language status
```

La traducción combina frases enseñadas con coincidencia por palabras completas; indica cobertura parcial cuando conserva vocabulario desconocido. No es un traductor general. La corrección aplica reglas explícitas. El resumen es extractivo y conserva las primeras frases solicitadas, incluida la negación y los decimales. La comparación conserva tokens UTF-8 y sus dígitos, normaliza mayúsculas ASCII y evalúa palabras de al menos cuatro bytes. Muestra los textos y coincidencias léxicas; palabras coincidentes no implican significados iguales. El correo se compone exclusivamente con los cuatro campos del usuario.

La inteligencia nueva y el descodificador se ejecutan en XI. JavaScript prepara datos y fuentes fuera de línea, transmite bytes, invoca roles nativos y gestiona archivos. No consulta otro modelo para contestar ni ajusta pesos neuronales.

## Estado, límites y publicación

- Banco de conocimiento: esquema 2, hasta 4.096 posiciones lógicas; memoria temporal X07 trasladada a `9110000000004000000`. Los ejecutores X07 antiguos rechazan el esquema nuevo. La migración produce otro archivo y conserva la sesión anterior.
- La capacidad lógica no elimina el presupuesto físico de Inverse Memory: lecciones largas pueden agotarlo antes de ocupar todos los huecos. Se comprueba el llenado con registros cortos sintéticos, separado de los 480 conceptos naturales.
- Diccionario bilingüe: 204 entradas/reglas iniciales; hasta 2.048; campos de hasta 120 bytes. Traducción/corrección: hasta 1.024 bytes y presupuesto de 10.000 candidatos.
- Texto v2: hasta 16.384 bytes. Resumen de hasta ocho frases; comparación de hasta 1.024 bytes por texto, doce coincidencias y presupuesto de 12.000 comparaciones de bytes. Un límite de comparación se señala como resultado incompleto.
- Los módulos anteriores conservan sus gramáticas y sus límites. El transporte amplio no convierte automáticamente todas las operaciones antiguas en operaciones de texto largo.
- Las afirmaciones normales ya no se archivan automáticamente por E029. `recuerda que`, `@ctx add`, la enseñanza y los datos personales admitidos siguen siendo entradas explícitas de sus módulos.
- Un turno nuevo cancela solicitudes antiguas de herramientas antes de interpretar la petición. Las variantes de «escribe y ejecuta en XI» se normalizan en XI y conservan el ejecutor y el verificador W4u originales.

El programa X07 estaba cerca del límite de instrucciones RXE. X08 utiliza dos roles nativos fijados por hash, `front.rxe` y `code.rxe`, que operan secuencialmente sobre un único estado. La decisión de continuar al segundo rol la publica XI. No se ofrece una cápsula incompleta que al iniciarse pierda el libro.

`io.mjs` transforma un archivo de entrada inmutable en otro archivo nuevo. Para una conversación mutable con varios clientes, utilizar `session.mjs`: un bloqueo de proceso protege lectura, ejecución y publicación; el estado y el recibo se escriben antes de actualizar `HEAD.json`. Las solicitudes tienen identificador, revisión y protección contra repetición con contenido distinto. Una interrupción sin confirmación devuelve estado desconocido y se consulta repitiendo el mismo identificador. Los archivos inmutables huérfanos no se ejecutan automáticamente.

El importador X03 también rechaza un segundo escritor sobre el mismo estado con `E_BUSY`. Sus primitivas de bajo nivel y el CLI nativo suelto no deben usarse para modificar una sesión compartida por fuera del contrato de sesiones.

## Ejecutar y reconstruir

Requisitos del paquete reproducible: Linux x86-64, Node 24.22.1 y `flock`. Se conserva el ejecutor original, SHA-256 `ef0c3a709121b8fd3cf4c996808ecfef8b60a7065d3f9c802280c58dc9370d84`; no se modifica C++.

Con las fuentes de esta rama y los activos nativos de la entrega:

```bash
node ai/personal/x08/session.mjs init RUNTIME X08_NATIVE MI_SESION
node ai/personal/x08/session.mjs turn RUNTIME X08_NATIVE MI_SESION turno-001 'consulta: nomasir caballo'
node ai/personal/x08/session.mjs turn RUNTIME X08_NATIVE MI_SESION turno-002 'traduce al ingles: yo tengo tres coches'
```

`initialize` comprueba el modelo comprimido y lo restaura en una versión propia. Para migrar un estado X07, usar un destino nuevo:

```bash
node ai/personal/x08/migrate.mjs RUNTIME X08_NATIVE ANTERIOR_X07.rvp NUEVO_X08.rvp
node ai/personal/x08/session.mjs init RUNTIME X08_NATIVE MI_SESION NUEVO_X08.rvp
```

La entrega es autocontenida. `node integration/x08/prepare.mjs NUEVO_DIRECTORIO` verifica y restaura el modelo X08 y su base X07 desde `integration/x08/release/`. La base canónica de entrenamiento conserva el hash de la entrega original, con el archivo personal vacío; no se publica una sesión del usuario ni su historial. `integration/x08/package.mjs` rechaza estados distintos de esas semillas fijadas. Las fuentes X07 provienen del commit `03c255fc920979f4d6b928f05ebd930d01fff1b5` de REVERSE-PC. Ya no se necesita descargar el ZIP de otra conversación.

Para reconstruir desde los datos reconciliados y ejecutar las pruebas en serie:

```bash
bash integration/x08/check.sh RUNTIME X07_NATIVE NUEVO_DIRECTORIO
```

Los resultados finales por módulo se guardan en `docs/evidence/x08`. La prueba de reconstrucción del códec ejecuta todas las páginas en XI y compara sus hashes con el texto original. La retención de hechos compara datos; sus comprobaciones no se cuentan como problemas independientes de razonamiento. Las 2.049 comprobaciones históricas no se vuelven a atribuir a X08: esta revisión publica las regresiones que efectivamente vuelve a ejecutar.

## Integración futura de REVERSE

El paquete nativo incluye modelo comprimido, ambos roles, contratos y fases de migración. El consumidor debe aplicar primero el rol de entrada, leer la marca nativa de consumo y ejecutar el segundo rol cuando corresponda; debe publicar solo tras completar el turno y su limpieza. La implementación de referencia de ese contrato está en `ai/personal/x08/transport.mjs`. Adaptarlo, compilar Android y probar el teléfono pertenece a P13, excluido de este ciclo. P14 también queda excluido.

REVERSE incorpora ahora una entrada nativa en `integration/bbyq-x08/run.mjs`, fijada a la revisión publicada de BBY-Q. Ejecuta este mismo contrato y sus sesiones persistentes, con verificación del código, modelo y archivos preparados. Su integración Android sigue fuera del alcance; la versión del APK anterior se conserva identificada como tal.

## Cierre de la entrega nativa

El constructor publica cada fase mediante un archivo candidato distinto y comprueba las 480 claves y sus 960 relaciones antes de publicar el manifiesto. La primera reconstrucción del cierre detectó 479 conceptos aunque el registro de llamadas declaraba 480; su resultado se conserva como fallo preliminar. La comprobación final impide presentar un modelo incompleto como reconstrucción aprobada. El empaquetado también exige la identidad exacta del modelo canónico.

`integration/x08/verify-rebuild.mjs` compara modelo y ambos roles byte por byte. La CI `.github/workflows/bbyq-x08.yml` restaura la entrega, ejecuta sus pruebas, reconstruye desde X07 y vuelve a ejecutar las seis baterías. Las ejecuciones remotas se consideran pendientes hasta observar su resultado; no se atribuyen resultados históricos a una revisión nueva.

Los límites y capacidades generales aún pendientes se conservan en [PENDIENTES-X08.txt](PENDIENTES-X08.txt).
