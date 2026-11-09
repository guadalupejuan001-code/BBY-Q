# BBY Q U03 — C17: entrenamiento personal en Android

Base exacta: PR #104, `eefb0e26c3cbe2838f7701ce300389930d902a65`.
Rama de trabajo: `codex/bbyq-c17-personal-training-20261108`.
Se conserva BBY Q → w4U → QdU y los 159 originales. No hay fusión automática.

## Objetivo de esta entrega

Que el usuario pueda crear una sesión, enseñar con sus propios ejemplos, medir lo aprendido, activar un candidato validado en la conversación y exportar una copia evaluable. La guía ilustrada está dentro del APK y funciona sin conexión.

La memoria de hechos/reglas y el entrenamiento de parámetros se presentan por separado porque son operaciones distintas. Los ejercicios conjuntos ejecutan el aprendizaje XI original, con etiquetas después de la predicción. El texto libre no se anuncia como un entrenador universal de conversación.

## Panel completo

| Ciclo | Estado conservado o conectado en esta entrega |
|---|---|
| C00 Auditoría | Telemetría, hashes y comprobantes reales. |
| C01 Runtime | Ejecutor XI JNI original y transporte autenticado. |
| C02 Persistencia | Transacciones, sesiones guardadas y recuperación. |
| C03 Cachés | ArchiveMemo original en las sesiones. |
| C04 Planificador | Apertura selectiva de bancos y planificación original. |
| C05 Codificador | Marco auxiliar y lector C1 original. |
| C06 Semántica | Checkpoint original; análisis observacional. |
| C07 Metacognición | Evaluación explícita de evidencia tipada. |
| C08 Aprendizaje activo | Candidato original y petición de verificación; sin promoción global. |
| C09 Memoria | Misma autoridad SQLite para la conversación activa. |
| C10 Razonamiento | Inferencias y operaciones originales de reglas; herramientas de planificación. |
| C11 Aprendizaje conjunto | Flujo personal de predicción, corrección y aprendizaje XI; auditoría de parámetros. |
| C12 Entre bloques | Reutiliza el aprendizaje conjunto original y conserva sus laboratorios. |
| C13 Optimización | Laboratorio conservado; no se cambia la caché global por una etiqueta. |
| C14 Evaluación | Comparación de referencia/candidato y pruebas reservadas; laboratorios conservados. |
| C15 Concurrencia | Exclusión de operaciones, detección de cambios de la conversación y recuperación. |
| C16 Android | Los 16 controles anteriores y su reinicio externo se vuelven a ejecutar. |
| C17 Entrenamiento personal | Sesiones, guía con dibujos, enseñanza, validación, activación, restauración y exportación. |

## Condiciones de entrega

Estado al implementar: pruebas Android pendientes. La fuente de verdad final será el trabajo CI y `validation.json`, no la mera presencia de una pantalla.

- Los ejemplos deben llamar al ejecutor XI existente.
- Las correcciones no pueden filtrarse a la predicción que se evalúa.
- La sesión personal conserva una referencia anterior al aprendizaje.
- Activar exige una validación vigente y no puede sobrescribir conversaciones nuevas.
- Una repetición de la misma solicitud no debe duplicar aprendizaje.
- El paquete exportado debe contener un modelo real, su identidad y el registro de entrenamiento.
- El modelo activo y las sesiones deben sobrevivir a un cierre forzado.
- La guía y el espacio de entrenamiento deben mostrarse en un emulador Android.
- Los 159 archivos protegidos deben seguir siendo idénticos al punto de partida.

GPU-VIRTUAL/QSSD computacional no se anuncian como integrados; esta entrega no introduce modelos externos ni declara capacidades generales o mejoras no medidas.
