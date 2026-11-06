# BBY Q U03 C00 — Resultado medido de la primera campaña aprobada

**Ejecución:** [CI C00 #42271172197](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42271172197)  
**Artefacto íntegro:** [BBYQ-U03-C00-native-audit](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42271172197/artifacts/13530915301)  
**Base U02 preservada:** ae3afcf52500954ce8849d9bf7c8f0286f5b172b  
**GitHub runner:** Linux Azure, Intel Xeon Platinum 8573C, 4 CPU lógicas, Python 3.12.16.  
**Muestras:** 2 por escenario, procesos aislados y bases SQLite temporales.

## Validación e integridad

- Seis tests unitarios de instrumentación: aprobados.
- CI nativa: aprobada tras corregir la profundidad del checkout Git.
- C1 frozen release + U02 release + readout + gradientes + integración y rollback + migración U01: aprobados.
- 159 archivos de fuentes y checkpoints protegidos: **SHA-256 sin cambios antes/después**.
- Cero APK nuevas; ninguna construcción o instalación Android.
- Los 200/200 casos de cooperación y 1024/1024 clasificaciones son evidencia **heredada y verificada**; la campaña C00 no los reentrenó ni repitió como benchmark de velocidad.

## Línea base de latencia y recursos (mediana, 2 observaciones)

| Operación | Pared (ms) | CPU nativa observada (ms) | Paquetes XI EXEC | Fuente enviada a XI | Escrituras Python/kernel | Pico RSS Python* |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Inicialización | 623 | — | 0 | — | 74,5 MiB | 110,5 MiB |
| Aritmética | 1.679 | 985 | 30 | 2,1 MiB | 97,9 MiB | 148,8 MiB |
| Pregunta de texto | 1.901 | 1.600 | 28 | 1,2 MiB | 29,5 MiB | 118,7 MiB |
| Misión cooperativa | 2.419 | 1.585 | 48 | 2,5 MiB | 123,9 MiB | 141,3 MiB |
| Feedback / aprendizaje | 3.681 | 2.515 | 113 | 4,4 MiB | 159,2 MiB | 143,0 MiB |
| Replay del mismo ID | 8,1 | — | 0 | 0 | 0 | 133,7 MiB |

*El pico RSS Python corresponde al proceso y puede incluir preparación previa de cada caso; no es la memoria incremental del turno. La memoria máxima observada por proceso XI en los escenarios con EXEC fue aproximadamente 73 MiB. No se suman picos de diferentes procesos para atribuir simultaneidad. Las lecturas de CPU e I/O Linux son observacionales, no un perfilado exclusivo del hardware Android.

## Causas de costo sugeridas por la evidencia

1. **Muchos paquetes nativos:** la misión produjo 48 operaciones XI EXEC; feedback 113. Esos paquetes reenviaron 2,5/4,4 MiB de texto de programas. Priorizar precarga/cache de instrucciones ya analizadas y reutilización segura de sesión.
2. **Persistencia intensa:** aproximadamente 124 MiB de escritura del proceso anfitrión para una misión y 159 MiB para feedback, con 5 y 7 llamadas SAVE respectivamente (primera muestra). Investigar snapshots diferenciales y publicación atomicamente versionada sin dañar rollback.
3. **Percepción repetida:** la misión nativa invocó dos conjuntos VQC (vqc_sample, select_agent, forward, u2_apply). Comparar exactitud de estado y revisión antes de compartir resultados.
4. **Repetición idempotente:** la misma petición y mismo ID devolvió un recibo en ~8 ms, sin ejecutar XI ni escribir nuevos datos. Preservar este comportamiento.
5. **Aprendizaje:** feedback incurrió en numerosas llamadas a QChat100, además de actualizaciones de percepción, memoria y política. Medir costos por banco con intervalos exclusivos antes de rediseñar su distribución.

## Límites y advertencias

- Son solo 2 observaciones por caso; el p95 de rango cercano equivale al máximo y no constituye una caracterización estadística sólida.
- La latencia es de un runner de GitHub; no demuestra rendimiento en el Galaxy A16 ni Android real.
- Una misma ejecución XI puede invocar varias subrutinas; las duraciones etiquetadas por subrutina se solapan y no deben sumarse.
- La métrica de bytes reenviados es tamaño del programa fuente enviado a XI, no tráfico de red ni datos del usuario.
- Los bytes escritos pueden depender del sistema de archivos, WAL, sincronización y entorno de CI.
- Los números no prueban por sí mismos qué optimización dará una aceleración; son la base para diseñar y falsar hipótesis C01.
- Esta campaña no modifica ni mejora aún rendimiento, comprensión semántica o aprendizaje.

## Veredicto de C00

**Aprobado:** medición y auditoría reproducibles, checkpoints intactos, migración nativa comprobada, ninguna APK.  
**Próximo trabajo C01:** optimizar primero transporte XI y persistencia sin sacrificar exactitud, utilizando estas medidas como referencia.
