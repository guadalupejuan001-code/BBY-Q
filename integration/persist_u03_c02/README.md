# BBY Q U03 C02 — Persistencia especulativa SQLite (opt-in, sin APK)

**Base:** C01 (PR #87, commit 06be3c7d52104ace67df9793c0747b0a51e31e58).
C00 conserva la línea base y los hashes de 159 archivos protegidos.

## Problema

U02 inicia BEGIN IMMEDIATE antes de ejecutar XI, guardar checkpoints y confirmar
la respuesta. En SQLite/WAL, esta transacción bloquea a otros escritores
durante casi todo el turno.

C02 no altera el formato RVPC2, codificador, gramática XI, algoritmos,
pesos ni la implementación estable. Es una ruta de persistencia opt-in.

## OptimisticSession

1. Inicialización original: la sesión U02 autentica los checkpoints y realiza
   las migraciones antiguas cuando corresponda.
2. Instantánea coherente: una conexión SQLite WAL captura PRAGMA data_version
   y crea una copia mediante Connection.backup. Una escritura concurrente
   durante la copia hace repetir el intento.
3. Ejecución privada: el original Session.turn opera sobre esa base temporal,
   incluyendo C1, QMemory, VQC3, QRL3, E02, QChat100, feedback y rollback.
4. Delta por clave primaria: se comparan las filas del estado inicial/final
   antes de iniciar la transacción de publicación. Se rechazan claves ambiguas
   y cambios de esquema; se conservan filas sin cambios.
5. Confirmación breve: BEGIN IMMEDIATE comprueba nuevamente data_version y
   publica solamente cambios de filas bajo un COMMIT atómico; cualquier
   excepción hace ROLLBACK.
6. Conflictos: si otro escritor confirmó un estado distinto, se desecha el
   cálculo anterior y se repite sobre el estado actualizado, con límite
   configurable de reintentos. No se sobrescriben resultados concurrentes.

Se conserva el orden por rowid de los recibos, la idempotencia por ID y el
formato original de estados persistentes.

## Uso experimental

    from integration.persist_u03_c02.optimistic import OptimisticSession

    with OptimisticSession("build/c02/private.sqlite", max_retries=3) as session:
        result = session.turn("turno-1", "calcula 7 + 3")
        print(result)
        print(session.last_metrics)

Esta ruta no debe habilitarse todavía sobre datos personales sin superar
pruebas adicionales de carga, recuperación y compatibilidad.

## Verificaciones

    python3 -m unittest integration.persist_u03_c02.test_optimistic -v
    python3 -m integration.persist_u03_c02.conformance
    python3 -m integration.persist_u03_c02.benchmark --samples 3 --out build/c02/comparison.json

El workflow .github/workflows/bbyq-u03-c02-persistence.yml recompila el
runtime nativo fijado de REVERSE-PC y Mundo X y repite las pruebas C1/U02,
readout, gradientes, migración U01, persistencia, concurrencia y rollback.

Pruebas nuevas: duplicados simultáneos, escritura externa entre cómputo y
COMMIT, retries agotados, rechazo de esquema/claves ambiguas, comparación
exacta de snapshots y respuestas U02/C02, restauración con Session original,
fallo inyectado y benchmark de latencia y retención del bloqueo de escritura.

Cada prueba crea bases SQLite sintéticas aisladas; no requiere información
personal ni instala Android.

## Pros y contras

Ventajas:
- La inferencia XI se realiza sin mantener bloqueada la escritura de SQLite.
- No se publican estados parciales y se detectan escritoras concurrentes.
- No se reemplaza la versión U02, el runtime original ni los pesos.
- Solo se actualizan filas realmente distintas en el COMMIT final.

Desventajas:
- Una copia completa de SQLite y la comparación de filas añaden trabajo,
  memoria, espacio temporal y E/S; la latencia total puede empeorar.
- Si hay conflictos frecuentes, hay que repetir el cálculo nativo.
- El disco lleno durante la etapa provisional aborta el turno sin publicarlo.
- No admite migraciones de esquema dentro del turno ni tablas sin clave
  primaria no ambigua: falla de forma explícita, sin continuar silenciosamente.
- Un mejor tiempo de bloqueo no implica menor latencia total, CPU o energía.
- PRAGMA data_version es válido solamente desde la misma conexión persistente.
- SQLite sigue manteniendo un solo escritor por COMMIT.
- C01 (pool XI) y C02 son opciones aisladas; no combinarlas durante estas
  pruebas multihilo hasta verificar su aislamiento.
- La duración del bloqueo antiguo se estima por traza SQL desde BEGIN y
  hasta antes del COMMIT; C02 incluye también su COMMIT.
- Los resultados del runner Linux no sustituyen pruebas físicas Android.

C02 permanece en una rama de laboratorio hasta validar ganancias medibles
bajo concurrencia y consumo real de memoria. No se promete aceleración.

**Cero APK, cero modificación de checkpoints, ningún entrenamiento global.**
