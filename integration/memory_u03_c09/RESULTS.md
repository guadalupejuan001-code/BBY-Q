# BBY Q U03 C09 — Resultado verificable

**PR:** [#95](https://github.com/guadalupejuan001-code/BBY-Q/pull/95). Base exacta: C08, commit 747036aa33b3496e7db9b77af2c4121c0b3d55c3.

**CI nativa aprobada:** [GitHub Actions #42391026706](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42391026706).  
**Evidencia JSON:** [Artefacto C09](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42391026706/artifacts/13581347382).

## Arquitectura probada

La memoria principal de BBY Q **sigue siendo SQLite U02**, la misma que conserva los bancos nativos C1, QMemory, VQC3, QRL3, QChat100 y E02. C09 añade únicamente una **vista de lectura autenticada**, sin nuevas tablas, autoridades de memoria, modelos ni formatos RVPC2. Se conserva la cadena BBY Q → w4U → QdU.

Se auditó la procedencia y coherencia de las asociaciones QMemory supervisadas, identificadores de vocabulario C1, muestras VQC, proyecciones VQC con revisión, tareas, feedback, recibos históricos y checkpoints archivados. Un símbolo del diccionario no equivale a un hecho, una clasificación VQC no equivale a verdad y el hash de una aseveración externa no autentica al emisor.

## Resultados funcionales

| Comprobación | Resultado |
|---|---|
| Compatibilidad nativa U02 / C09, salida e historial | Idénticos |
| SHA-256 de los siete bancos existentes | Idénticos |
| Regresión original XI, C1/U02, feedback y migración U01 | Aprobada |
| Recuperación de memoria y tarea nativa | Aprobada |
| Repetición idempotente, rollback y reinicio U02 | Aprobados |
| Proyección VQC antigua después del aprendizaje | Señalada como obsoleta |
| Contradicción de valor, sin reescritura ni entrenamiento | Detectada y conservada |
| WAL coherente mientras otro cliente escribe | Aprobado |
| Checksum de banco/recibo/archivo corrupto | Rechazado |
| Fuentes/checkpoints protegidos | 159 intactos |
| Nuevas autoridades de memoria | 0 |
| APK construidas | 0 |

La conformance nativa de prueba observó seis entradas de memoria tipadas y verificó los siete bancos de estado. Todas las lecturas se hicieron en una transacción SQLite consistente; no hubo escrituras nuevas.

## Costo de auditoría

Medianas de **tres muestras** en un runner Linux, sobre una base sintética:

| Operación | Tiempo |
|---|---:|
| Snapshot original U02 (consulta hashes registrados) | **10,474 ms** |
| Vista C09 completa (recalcula hashes y verifica relaciones) | **50,995 ms** |
| Vista C09 filtrada (misma auditoría, menos registros visibles) | **50,855 ms** |

La vista C09 es aproximadamente **4,9 veces más lenta** en esta muestra, porque comprueba el contenido nativo completo en lugar de devolver solo los hashes almacenados. No es una aceleración: es una mejora de verificabilidad y consistencia. El filtro mantiene la comprobación de integridad completa.

## Límites y siguientes trabajos

No se acreditó memoria conversacional general, aprendizaje nuevo, ventaja cuántica ni autenticación de fuentes externas. C08 sigue sin una mejora demostrada de pesos. No se mezclaron los modelos experimentales C06–C08 como una nueva autoridad de memoria.

**C10** debe conectar razonamiento y planificación con este índice de procedencia, validando sus dependencias sin aceptar proyecciones caducadas ni comprometer el estado nativo. Ninguna APK hasta los ciclos finales.

[Panel de secuencias C00–C17](../../docs/BBY_Q_U03_PANEL.md) · [Estado estructurado](../../docs/BBY_Q_U03_ESTADO.json) · [Siguiente etapa](../../docs/BBY_Q_U03_SIGUIENTE.md)
