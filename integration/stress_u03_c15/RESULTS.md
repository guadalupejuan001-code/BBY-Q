# BBY Q U03 C15 — Resultados reales de estrés nativo XI y SQLite-WAL

**Estado:** [CI original XI aprobada #42456400116](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42456400116) · [artefacto JSON completo #13608230586](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42456400116/artifacts/13608230586) · [PR #101](https://github.com/guadalupejuan001-code/BBY-Q/pull/101) en borrador.  
**Base exacta:** [C14 PR #100](https://github.com/guadalupejuan001-code/BBY-Q/pull/100), commit `e774b1b3694a1a2dfaa505b054888b80db495db1`. Checkpoints originales y **159 activos históricos SHA-256 intactos**.

## Resultado y decisión

**C15 validó experimentalmente estrés nativo XI + SQLite-WAL sobre dos bancos originales**: U02 congelado y C12 entrenado pero no promovido. Cada nivel usó los mismos contratos originales U02, nuevas entradas sintéticas de C15 y sus seis motores C1/VQC/QRL/QMemory/Entity/QChat. **Ninguna optimización ni nuevo modelo se promocionó**, no se fusionó una PR y no se creó APK.

Se ejecutaron dos campañas: [primera CI #42455939599](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42455939599) y la campaña reforzada [CI #42456400116](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42456400116). La segunda **corrigió un vacío de cobertura del protocolo**: la primera muestreaba mientras el primer escritor calculaba, pero podía no ver un commit nuevo; ahora cada lector debe incluir una instantánea **posterior al primer commit real**, con revisión mayor.

## Throughput observado — Segunda campaña, Linux GitHub Actions

| Escritores / Lectores | U02 frozen (tareas/s) | C12 conjunto no promovido (tareas/s) | Latencia mediana de escritor U02 / C12 |
|---|---:|---:|---:|
| 1 / 1 | **0,3993** | 0,3975 | 2.447,637 / 2.459,957 ms |
| 2 / 2 | **0,4211** | 0,4079 | 3.615,444 / 3.734,619 ms |
| 4 / 2 | **0,4203** | 0,4138 | 6.140,165 / 6.203,864 ms |
| 6 / 3 | **0,4168** | 0,4102 | 8.626,676 / 8.713,702 ms |

Primer ensayo, para contraste: U02 **0,3774 / 0,3713 / 0,3941 / 0,3952** y C12 **0,3856 / 0,3956 / 0,4015 / 0,3974** tareas/s respectivamente para los niveles 1/2/4/6. Las diferencias entre runs son observaciones del runner Linux, no una mejora estable del modelo entrenado.

**Límite observado, no capacidad máxima:** subir de 1 a 6 escritores aumentó la mediana de latencia de ~2,45 s a ~8,6–8,7 s por petición, mientras el throughput permaneció alrededor de 0,4 tareas/segundo. Es compatible con el bloqueo/serialización de escrituras de la autoridad única SQLite, pero esta campaña de un solo host y ocho entradas nuevas **no demuestra ningún máximo universal**. La latencia p95 en seis escritores fue **14.391,362 ms** frozen y **14.611,739 ms** conjunto (nearest-rank p95, equivalente al máximo observado por ser muestra de seis).

## Lectores coherentes y checkpoints

- **13 misiones concurrentes completadas por brazo** distribuidas en 1+2+4+6, es decir 26 peticiones nativas XI de carga con seis motores trazados, y **26 replays exactos sin doble revisión**.
- 1/2/2/3 lectores por nivel con 8 snapshots cada uno: **64 por brazo, 128 en total**. Cada snapshot validó SHA-256 de los siete bancos, metadata U02 y C1; las revisiones fueron no decrecientes.
- Un lector de cada grupo **debía comprobar una revisión estrictamente posterior al commit**: **16 snapshots post-commit verificados**, además de 112 anteriores/al comienzo. Este nuevo criterio aprobó en CI #42456400116.
- SQLite `PRAGMA integrity_check=ok`, `journal_mode=WAL`, auditoría C09 original y sincronía C1/U02 aprobados tras cada nivel. No hubo pérdidas de recibos ni tareas, ni resultados de inferencia sin los seis motores trazados.
- Los snapshots se toman antes y después de *al menos el primer commit*, pero no prueban lectura continua de todas las revisiones bajo una campaña más extensa.

## Fallos, muerte abrupta y reinicio auténtico del host

| Escenario por brazo | U02 frozen | C12 conjunto |
|---|---|---|
| Cortar después de paso XI 1 | Rollback exacto | Rollback exacto |
| Cortar después de paso XI 2 | Rollback exacto | Rollback exacto |
| Cortar después de paso XI 3 | Rollback exacto | Rollback exacto |
| Matar subprocess con WAL **sin COMMIT** | Estado/7 bancos recuperados | Estado/7 bancos recuperados |
| Matar host **después de COMMIT XI** | Recibo conservado y replay | Recibo conservado y replay |
| Dos peticiones con mismo ID y payload | Un único recibo/tarea | Un único recibo/tarea |
| Mismo ID, distinto payload | Rechazado sin cambiar estado | Rechazado sin cambiar estado |

Los tres puntos de `fail_after` ejecutan las **operaciones originales U02 en una copia descartable** y comprueban integridad de bancos, historial, rollback y reinicio. Las muertes abruptas usaron códigos de salida intencionados **73** (cambio SQLite-WAL no confirmado) y **74** (después del commit de un recibo XI real). **No representan un apagón eléctrico dentro del intérprete XI, ni validan pérdida física de energía o Android.**

## CPU, RSS, I/O y saturación

Las mediciones son sumas del **proceso de GitHub Actions** por nivel de carga, no coste exclusivo de un motor ni de cada escritor.

| Métrica sobre niveles 1+2+4+6 | U02 frozen | C12 conjunto |
|---|---:|---:|
| CPU Python acumulada en niveles | **9.960,734 ms** | 9.553,515 ms |
| CPU procesos XI hijos finalizados (aproximada) | **27.719,504 ms** | 28.154,386 ms |
| I/O de escritura observada (`/proc/self/io`) | **1.696.534.528 bytes** | 1.698.156.544 bytes |
| Máximo RSS Python acumulativo del proceso compartido | **666.656 KiB** | 666.656 KiB |

Los picos RSS son acumulativos durante la campaña; el mismo proceso ejecuta ambos brazos, por lo que **no prueban igualdad de memoria ni ahorros de RAM**. `read_bytes=0` bajo Linux puede explicarse por caché de página y no significa ausencia de lecturas. Las escrituras observadas incluyen serialización, SQLite y actividad del host, **no son una cifra de desgaste SSD físico**.

## Comparación C13 sin promoción

Se ejecutaron tres parejas de solicitudes U02 sin caché vs C13 cacheada, **sólo en serie**. Los tres recibos y snapshots coincidieron exactamente. Esta comparación no incluye el coste completo de autenticar el alcance de caché y no se utiliza para atribuir ganancia; la caché experimental C13 emplea instrumentación de ámbito global y **no es segura para concurrencia multi-hilo sin rediseño**. No fue promocionada. C12 tampoco superó la exactitud U02 congelada en las validaciones anteriores.

## Restricciones y decisiones

- **159/159 archivos históricos protegidos** no modificados; todos los bancos originales y el checkpoint inicial U02 permanecen intactos.
- **BBY Q → w4U → QdU** sigue siendo el orden de responsabilidad; ninguna nueva fuente de memoria autoritativa.
- C15 confirma integridad en **hasta 6 escritores y 3 lectores**, **no** máximos teóricos de concurrencia ni seguridad a escala arbitraria.
- **Sin promoción** de modelos C12 ni caché C13, **sin fusiones automáticas y sin APK**.
- Todos los experimentos son de software XI/Ether sobre GitHub/Linux con observaciones sintéticas, no ventaja cuántica de hardware físico ni pruebas Android.

**Siguiente C16 — Integración Android y REVERSE-PC:** analizar la integración de los prototipos sin comprometer fuentes/checkpoints protegidos, preparar diagnóstico de JNI/servicios nativos y validaciones reales de compatibilidad Android, sin compilar APK antes de la etapa autorizada. [Panel C00–C17](../../docs/BBY_Q_U03_PANEL.md) · [Estado](../../docs/BBY_Q_U03_ESTADO.json) · [Continuidad C16](../../docs/BBY_Q_U03_SIGUIENTE.md).
