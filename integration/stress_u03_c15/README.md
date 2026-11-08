# BBY Q U03 C15 — Estrés, concurrencia y recuperación WAL

**Base exacta:** [C14 PR #100](https://github.com/guadalupejuan001-code/BBY-Q/pull/100), commit `e774b1b3694a1a2dfaa505b054888b80db495db1`. C00–C14 y los **159 archivos históricos protegidos** son inmutables. La cadena **BBY Q → w4U → QdU** permanece igual. Nada se fusiona automáticamente; ningún APK se crea.

## Diseño predefinido y controles

- **U02 `frozen`**: ejecuta las misiones XI originales sin feedback nuevo.
- **C12 conjunto entrenado pero no promocionado**: recibe exclusivamente los 2 feedback nativos XI originales de C12, antes de todas las pruebas; se auditan seis regiones nativas de pesos/ángulos como en C11–C14.
- **C13 caché autenticada experimental, no promocionada**: 3 parejas de peticiones separadas desde U02 frozen para comprobar recibo/snapshot idéntico; **sólo secuencial**, porque la instrumentación de caché C13 usa un parche global no seguro para hilos. Las latencias medidas sin coste de autenticación de esta rama NO justifican promocionar la caché.

Se usan ocho nuevas tareas XI sintéticas, separadas de C11–C14 (nombres, semillas y reglas); ambos valores de regla y todas las posiciones 0–6 están representados. No se introducen etiquetas de clase del oráculo en inferencia.

## Experimentos nativos XI/SQLite-WAL

1. **Estrés progresivo:** matrices predefinidas de **1, 2, 4 y 6 escritores** simultáneos, con **1, 2, 2 y 3 lectores** respectivamente por brazo. Los participantes sincronizan el inicio mediante barrera. Cada escritor abre su **propia sesión original U02** y realiza una misión XI con seis motores reales; los lectores abren conexiones SQLite `mode=ro` y ejecutan **8 instantáneas WAL cada uno** durante la carga.
2. **Lectura coherente:** cada instantánea autentica los **7 bancos XI**, SHA de metadatos U02 y el marcador de sincronización C1/SQLite; los lectores deben observar revisiones no decrecientes. La última de las ocho muestras se realiza **después de que al menos una escritura nativa haya confirmado su commit**, verificando un aumento real de revisión; los lectores no se cuentan como throughput de escritor. La auditoría oficial C09 se repite al final de cada nivel, seguida de `PRAGMA integrity_check`.
3. **Replays sin doble trabajo:** tras completar cada nivel, se reabre U02, se comprueban las tareas y todos los recibos, y se repiten **todas** las solicitudes con el mismo ID. El estado y las huellas tienen que permanecer idénticos.
4. **Fallos inyectados:** cortar la petición en los pasos 1, 2 y 3 del contrato original U02 (`fail_after`). Cada corte debe revertir los cambios en bancos, historial, recibo y snapshot, también después de reiniciar la sesión.
5. **Muerte del proceso:** dos subprocessos separados se matan con `os._exit`: uno con una transacción SQLite-WAL deliberadamente no confirmada, otro inmediatamente después de **un commit XI real**. Se comprueba la recuperación de los siete bancos y el replay; **la primera prueba NO simula una caída dentro del intérprete XI** ni un corte eléctrico.
6. **Colisiones de ID:** dos peticiones simultáneas con el mismo ID/payload deben crear **sólo una tarea y un recibo persistidos**. Reutilizar el mismo ID con distinto contenido debe rechazarse sin cambiar el snapshot.
7. **Observabilidad:** duración y throughput por nivel de carga, mediana/p95 de escritura y arranque, CPU Python y procesos XI finalizados (aproximada), pico RSS acumulado e I/O Linux del proceso, tamaños SHA, WAL e integridad. No se atribuyen contadores globales a una sola solicitud ni se inventa un máximo de capacidad.

**Regla de promoción:** ninguna variante ni caché se activa por llegar al final de esta campaña. Medir estabilidad y seguridad no demuestra ventaja de exactitud ni ventaja física cuántica. El control U02 `frozen` sigue siendo la referencia.

## CI y reproducción

```bash
bash deps/reverse-pc/scripts/build-xi-session.sh deps/mundo-x deps/reverse-pc/build
python3 -m unittest integration.stress_u03_c15.test_campaign -v
python3 -m integration.stress_u03_c15.verify_panel
python3 -m integration.stress_u03_c15.campaign --out build/c15/stress.json
```

Dependencias fijas: `REVERSE-PC@08c363e6c6855c14026c86046af7183a45f45a98` y `mundo-X@e2778d962af22f6f1a0794058dd4685fc2573966`. La CI verifica C1/U02, gradientes, rollback, fuentes históricas y el panel C00–C17 antes de los ensayos. El resultado JSON completo se publica como artefacto de GitHub Actions. **La campaña usa exclusivamente archivos SQLite temporales**; no ejecuta dispositivos Android ni instala nada.

[Informe medido](RESULTS.md) · [Panel C00–C17](../../docs/BBY_Q_U03_PANEL.md) · [Estado](../../docs/BBY_Q_U03_ESTADO.json) · [Siguiente C16](../../docs/BBY_Q_U03_SIGUIENTE.md).

## Resultado observado

[RESULTS.md](RESULTS.md) contiene el perfil real de las dos campañas, incluida [CI #42456400116 aprobada](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42456400116). Los lectores verificaron 128 snapshots autenticados en total, 16 después de un commit real. El throughput se mantuvo alrededor de 0,4 tareas XI/segundo con 1–6 escritores y latencias crecientes. Recuperación y colisiones pasaron; no se promovió modelo ni caché, ni se generó APK. Siguiente C16.
