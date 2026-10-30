# BBY-Q X10: capacidad ampliada

X10 añade almacenamiento paginado a la entrega X09 integrada. Conserva los
programas y el estado entrenado originales; las lecciones editables se consultan
por clave y se materializa un solo registro de 640 bytes por operación.

| Recurso | X09 | X10 | Ampliación |
| --- | ---: | ---: | ---: |
| Lecciones editables | 4.096 registros | 1.048.576 registros | 256 veces |
| Comprobantes de operaciones por sesión | 4.096 | 1.048.576 | 256 veces |
| Entrada para repetición exacta y resumen extractivo | 16 KiB | 1 MiB | 64 veces |
| Salida de texto de esos módulos | Hasta 64 KiB de transporte | Hasta 1 MiB | 16 veces |

El millón es capacidad de almacenamiento. No representa un millón de lecciones
aprendidas ni un aumento de inteligencia. El diccionario original, la campaña,
el texto de Babilonia y el resto del aprendizaje de X09 siguen en sus módulos.

## Qué ejecuta cada parte

La validación completa de UTF-8, la selección de operaciones, el reconocimiento
de prefijos, la normalización de claves, la lectura de campos, las decisiones de
crear/corregir/borrar y la composición de las respuestas se ejecutan en XI.
`native.mjs` emite cuatro programas que el ejecutor original compila a RXE:
`validate`, `route`, `record` y `stream`.

Node.js transporta bytes y mantiene la persistencia con su módulo incorporado
`node:sqlite`. SQLite indexa claves binarias y guarda páginas opacas de Ether;
no interpreta las preguntas ni genera respuestas. No hay dependencias de npm.
Los datos del banco, la revisión, la memoria principal y el comprobante se
publican en una transacción con sincronización completa. Un error revierte los
cambios; repetir un identificador confirmado devuelve su comprobante original.

La memoria principal RVPC2 se conserva comprimida. Las modificaciones de
lecciones del currículo original se sincronizan mediante XI antes de ejecutar
un módulo X09 que consulte ese currículo. Las lecciones adicionales permanecen
en páginas independientes y no obligan a ampliar el archivo RVPC2 de 32 MiB ni
los presupuestos de instrucciones del ejecutor.

Los textos se validan por completo en páginas de 8 KiB, incluso si un resumen
termina antes de su último byte. Las secuencias UTF-8 que atraviesan páginas
conservan su estado. Una segunda pasada nativa produce el resultado sin truncar
el mensaje para adaptarlo al buzón anterior.

## Preparación y uso

Requisitos comprobados: Linux x86-64, Node.js 24.22.1 y la entrega original
`BBY-Q-X09-Entrenamientos-Integrados.zip`. El archivo se verifica con el hash
fijado por la preparación de X09. La entrega anterior no se modifica.

```sh
node bbyq.mjs prepare --archive /ruta/BBY-Q-X09-Entrenamientos-Integrados.zip
node bbyq.mjs init /ruta/sesion-x10
node bbyq.mjs turn /ruta/sesion-x10 operacion-001 '@learn status'
node bbyq.mjs status /ruta/sesion-x10
```

Para transferir una sesión X09 existente, incluidos sus identificadores de
reintento, a un directorio nuevo:

```sh
node bbyq.mjs upgrade-session /ruta/sesion-x09 /ruta/sesion-x10
```

La fuente queda disponible sin alteraciones. La sesión nueva conserva el estado
RVPC2 exacto que señalaba `HEAD.json` al iniciar la transferencia.

Para un texto grande, el archivo debe contener la instrucción y el contenido:

```text
repite exactamente:
Contenido que debe devolverse sin cambios.
```

```sh
node bbyq.mjs turn /ruta/sesion-x10 texto-001 --file /ruta/mensaje.txt
```

También se admiten `resume:` y `resume en N frases:`, con N entre 1 y 8,
seguidos por un salto de línea y el texto original. Los resúmenes son
extractivos; conservan fragmentos del texto proporcionado.

## Límites que permanecen

- La entrada de 1 MiB corresponde a repetición exacta y resumen extractivo.
  Las operaciones heredadas conservan su contrato de hasta 16 KiB y sus límites
  particulares. Un texto demasiado grande para ellas recibe un error explícito.
- Cada lección mantiene los campos del formato original: clave de 64 bytes,
  definición y requisito de 224 bytes cada uno, fuente y páginas de 32 bytes
  cada uno. Estos tamaños se cuentan en UTF-8.
- La importación del archivo de contexto original conserva su formato y sus
  límites. X10 no cambia las capacidades lingüísticas de los módulos antiguos.
- La capacidad nueva necesita espacio físico. Los registros y comprobantes se
  conservan hasta llegar al límite; X10 no elimina aprendizaje ni historial de
  forma automática para liberar espacio.
- Esta implementación usa el anfitrión Linux/Node. No está validada en Android.
  El anfitrión Android necesitará adaptar la persistencia y el ciclo de páginas
  antes de incorporar esta capacidad a una APK; recompilar una APK antigua por
  sí solo no instala el almacenamiento X10.

## Verificación reproducible

```sh
node integration/x10/check.mjs build/x10 build/x10-evidence --full-capacity
node integration/x10/tests/edge-cases.mjs build/x10 \
  build/x10-evidence/pristine build/x10-edge-evidence
node --test integration/x09/tests/initialization.test.mjs \
  integration/x09/tests/prepare.test.mjs \
  integration/x09/tests/retention/state.test.mjs \
  integration/x09/tests/retention/repository.test.mjs
```

El informe medido queda en `docs/evidence/x10-capacity/results.json`, junto con
las huellas de los archivos comprobados. La prueba de capacidad utiliza datos
sintéticos claramente marcados: llena el almacenamiento y después ejecuta
operaciones XI reales de inserción, consulta, borrado y reutilización. La prueba
de historial también distingue comprobantes sintéticos de turnos nativos reales.
No se presentan esas cargas como entrenamiento.

Resultado local: 51 comprobaciones aprobadas (17 grupos nativos, 5 pruebas
adicionales de persistencia y 29 pruebas de conservación del repositorio). Se
almacenaron realmente 1.048.576 registros y 1.048.576 comprobantes en dos bases
de prueba. La base de registros ocupó 890.310.656 bytes y la de comprobantes
284.033.024 bytes. Son tamaños de esas cargas sintéticas, no una estimación del
tamaño de cualquier entrenamiento futuro.

La prueba de texto recibió 1.048.576 bytes y devolvió los 1.048.556 bytes del
contenido después de retirar el prefijo de la instrucción. Procesó 128 páginas
y tardó aproximadamente 36,3 segundos en este anfitrión. Es una medición de
capacidad; no implica esa latencia ni rendimiento en un teléfono.
