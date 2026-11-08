# BBY Q U03 C13 — Optimización global: coste real y caché autenticada

**Base exacta:** [C12 PR #98](https://github.com/guadalupejuan001-code/BBY-Q/pull/98), commit `d31d60bb0ee356b004e9e1e2d819aa361ef3a9db`. Trabajar sobre rama y PR borrador **C13 → C12**, no fusionar ni generar APK.

## Hipótesis y límite de la optimización

C12 midió ~2,17–2,20 segundos por misión sintética en Linux, incluidos inicialización de sesión y copia SQLite. Ese dato NO permite atribuir el coste a un circuito concreto sin instrumentación. C13 separa las etapas antes de recomendar una estrategia.

**Candidato técnico:** caché autenticada de bytes de los checkpoints y manifiestos inmutables **en el proceso de laboratorio**. El U02 original revalida y descomprime `read_models`, `entity_models`, `router_model`, `perception_model` y recalcula `source_identity` por sesión. La caché comprueba las fuentes en el primer acceso y su integridad al final del alcance mediante los 159 hashes SHA-256. Devuelve copias de los diccionarios para evitar mutaciones entre consumidores.

Se prohíbe cachear inferencias, respuestas, estados del usuario, encabezados de QRL, gradientes, transacciones, sesiones XI o resultados de `Session.turn`. C13 no modifica ningún archivo original del runtime U02/XI. Si la fuente cambia mientras opera la caché, la ejecución falla al cerrar su ámbito.

## Protocolo reproducible

1. Crear una base U02 original sintética e independiente; copiarla en un control `u02-frozen` y un `c12-joint-experimental` entrenado **solo** mediante los dos feedback originales XI de C12.
2. Evaluar **cuatro casos nuevos, prefijados y distintos de C11/C12**, con 3 repeticiones por caso y brazo (12 observaciones por ruta, 24 por brazo). Alternar el orden de las rutas para mitigar el efecto del caché de página Linux y de la carga del runner.
3. Comparar `original-c12` vs `cached-release-c13`. Cada observación recibe un clon SQLite fresco: mismas solicitudes, ID, bancos, XI, clasificación, memoria, acción y voz. Exigir identidad de **recibo, salida nativa y snapshot posterior**; no premiar simplemente menor duración.
4. Perfilar el tiempo por etapa: backup SQLite, autenticación+arranque U02, ejecución XI con todos los motores, auditoría C09 y cierre. Separar CPU Python, RSS máximo, I/O observado y telemetría de `XiSession` (ejecuciones, bytes enviados, CPU e I/O nativo, pico RSS). Las duraciones de paquetes XI **se solapan** si hay varias llamadas por paquete; nunca se suman como tiempos exclusivos por componente.
5. Repetir cuatro ablaciones originales U02 y normal sobre dos entradas nuevas por brazo; exigir resultados originales idénticos, sin reentrenar durante pruebas.
6. Validar las seis regiones de parámetros antes y después del conjunto de pruebas, el banco C1 sincronizado, las siete huellas U02, ninguna modificación de SQLite fuente, identidad de los 159 archivos, sin APK.

**Puerta de decisión:** recomendar un uso experimental opt-in de la caché solo si todos los recibos y parámetros coinciden y la mediana observada es al menos un **3 % inferior en ambos brazos**. Una ganancia aislada en un solo runner no acredita mejora general; si no se cumple, no recomendar. En ningún caso promover el modelo entrenado C12: sigue sin ventaja predictiva frente a `frozen`.

## Reproducir

```bash
bash deps/reverse-pc/scripts/build-xi-session.sh deps/mundo-x deps/reverse-pc/build
python3 -m unittest integration.optimize_u03_c13.test_campaign -v
python3 -m integration.optimize_u03_c13.verify_panel
python3 -m integration.optimize_u03_c13.campaign --repeats 3 --out build/c13/benchmark.json
```

CI: `.github/workflows/bbyq-u03-c13-optimize.yml`, dependencias nativas REVERSE-PC/mundo-X **fijadas a los mismos SHA que C12**. Se guardarán JSON con resultados sin censurar, informes, hashes y panel C00–C17.

**Resultado medido:** [CI #42443472416 aprobada](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42443472416), [RESULTS.md](RESULTS.md). Observado 2,77 % U02 y 2,95 % C12 de reducción de latencia end-to-end incluyendo autenticación; ambos bajo umbral 3 %, por tanto la caché no se habilita como solución general. Todos los recibos, snapshots y ablaciones fueron idénticos. El simulador XI es software, no hardware cuántico físico ni Android.

[Panel permanente C00–C17](../../docs/BBY_Q_U03_PANEL.md) · [Estado JSON](../../docs/BBY_Q_U03_ESTADO.json) · [Siguiente secuencia](../../docs/BBY_Q_U03_SIGUIENTE.md).
