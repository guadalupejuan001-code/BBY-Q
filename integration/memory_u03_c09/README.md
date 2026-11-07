# BBY Q U03 C09 — Memoria unificada verificable (sin APK)

**Base:** C08 / PR #94 (`747036aa33b3496e7db9b77af2c4121c0b3d55c3`).

## Objetivo y arquitectura inamovible

BBY Q sigue siendo la entidad central; su coordinación establecida es
**BBY Q → w4U → QdU**. C09 **no crea otra IA, coordinador ni memoria principal**:
la única autoridad de persistencia sigue siendo la **misma SQLite U02**,
con el banco nativo de lenguaje C1 y QMemory, VQC3, QRL3, voz y E02.

C09 implementa una **vista indexada, de solo lectura**, de fuentes
autenticadas desde la misma transacción SQLite. No escribe nuevas tablas,
no modifica esquemas, no materializa nuevos checkpoints y no modifica
el binario compacto XI ni su decodificación.

Archivo: `integration/memory_u03_c09/view.py`.

### Qué une sin confundir procedencias

| Fuente existente | Representación y límites |
|---|---|
| Diccionario C1 | Nombre canónico, ID nativo y display. Un símbolo no demuestra que un hecho sea verdadero |
| QMemory | Asociación, slot y etiqueta de supervisión explícita conservados. Es información aportada, no lectura cuántica fresca ni verdad externa |
| Observaciones VQC | Hash SHA-256 del input, tipo y banco; los 1.000 valores externos no se exponen por defecto |
| Proyecciones VQC | Clase derivada, fuente y versión. Se marca **stale** si cambió input o versión del readout; no se reutiliza como hecho actual |
| Tareas nativas | ID, hash de frame y vinculación a feedback. No inventa inferencias del contenido de cada tarea |
| Recibos C1/U02 | Exige que la copia legacy/unificada coincida. La firma es integridad del contenido, no autenticación de emisor |
| Checkpoints archivados | Se auditan hash de imagen y metadatos sin reabrir ni publicar el estado |

Cada lectura utiliza `BEGIN` de lectura en modo WAL, comprueba
identidad del modelo, SHA-256 de metadata, los siete bancos y los
links de receipts, y confirma la **misma revisión** para todo el informe.
Un escritor concurrente puede publicar otra revisión, pero no
mezclar parcialmente sus filas con las de la lectura.

### Conflictos y pérdida de información

`reconcile()` compara un dato registrado con aseveraciones
aportadas como overlay. Aunque una aseveración tenga hash válido,
**no es una fuente externa autenticada**. Si los valores discrepan,
se devuelve `conflict_unresolved`: nunca sobrescribir ni
entrenar automáticamente con la contradicción.

Si U02 y C1 están desincronizados por un cliente legacy externo,
C09 informa `C1_synchronized_with_U02=False`;
**no inventa una fusión**. Si hay proyecciones VQC caducadas por
entrenamiento o cambio de muestra, quedan visibles como obsoletas.
La consulta desconocida produce ausencia de evidencia.

### Uso experimental

    from integration.memory_u03_c09.session import MemorySession
    from integration.memory_u03_c09.view import external_claim

    with MemorySession("build/c09/synthetic.sqlite") as bbyq:
        print(bbyq.inspect_memory("Faro Azul"))
        print(bbyq.compare_memory("Faro Azul",overlay=[
            external_claim("Faro Azul","valor",0,"laboratorio:sin-autenticacion")
        ]))

Esta interfaz es exclusivamente observacional. El cálculo nativo, entrenamiento
C06/C07, ajustes propuestos C08, respuestas del usuario y SQLite originales
mantienen su autoridad previa.

## Verificaciones

    python3 -m unittest integration.memory_u03_c09.test_view -v
    python3 -m integration.memory_u03_c09.verify_panel
    python3 -m integration.memory_u03_c09.conformance
    python3 -m integration.memory_u03_c09.benchmark --samples 3

La CI host compila XI/Ether con versiones fijadas de REVERSE-PC y Mundo X,
repite las verificaciones C1/U02 y comprueba:
- reversión tras fallo en lectura y corrupción de cualquier banco,
- coincidencia de IDs, hashes, tareas, feedback y recibos legacy,
- **SQLite WAL consistente con un escritor concurrente**, sin nuevas tablas,
- asociaciones QMemory y vocabulario C1 tipados sin prometer veracidad,
- revisión desactualizada de VQC marcada sin reproducir una lectura incorrecta,
- contradicción sin publicar conocimiento y sin saltar la confirmación,
- **respuestas, historial y hashes U02/C09 idénticos** con tareas XI reales,
- recuperación de un estado generado por C09 usando el lector U02 original,
- 159 archivos protegidos sin modificaciones y cero APK.

La vista añade costo por hashing de snapshots; puede ser más lenta
que consultar el SHA que SQLite ya tiene almacenado. C09 busca
**trazabilidad y consistencia**, no prometer FPS ni aceleración
cuántica.

## Panel persistente de secuencias

[Panel C00–C17](../../docs/BBY_Q_U03_PANEL.md),
[estado estructurado](../../docs/BBY_Q_U03_ESTADO.json),
[siguiente ciclo y criterio de aceptación](../../docs/BBY_Q_U03_SIGUIENTE.md).

Los ciclos previos son ramas experimentales con PRs verificadas por CI,
no cambios automáticamente instalados en la aplicación. C08 fue
ingeniería probada **sin actualización de pesos ni mejora demostrada**.

**C09 no genera APK. C10 es la siguiente etapa de razonamiento y
planificación; no se inicia hasta verificar C09.**

## Cierre de C09: evidencia final

[RESULTS.md](RESULTS.md) documenta las pruebas de GitHub, la comparación exacta de
U02 y C09 y los límites. La CI nativa [#42391026706](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42391026706)
aprobó la auditoría de **siete bancos nativos**, 159 archivos protegidos,
WAL concurrente, contradicciones y proyecciones VQC obsoletas, sin APK.

El coste medio de una vista SHA completa fue **50,995 ms**, frente a
**10,474 ms** del snapshot U02 simple, en tres muestras sintéticas.
La vista C09 agrega verificación, **no acelera la inferencia XI**.

[Panel de secuencias actualizado](../../docs/BBY_Q_U03_PANEL.md):
C09 validado, **C10 siguiente**, sin modificación de la rama principal.
