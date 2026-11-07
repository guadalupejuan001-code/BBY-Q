# BBY Q U03 / C04 — Planificador de recursos XI (opt-in, sin APK)

**Base exacta:** C03 / [PR #89](https://github.com/guadalupejuan001-code/BBY-Q/pull/89), commit c4bd78d4d5fa17ea9268ffef602e2108d6bc025a.

El planificador U03-C04 prepara un grafo de dependencias a partir del **contrato ya reconocido por XI** y utiliza sesiones cuánticas de arranque diferido. Mantiene intactos los modelos, sus parámetros, el formato compacto XI/Ether, los cuatro bancos nativos VQC3/QRL3/QMemory/QChat100 y el estado transaccional de U02.

## Arquitectura y mejoras reales

La sesión original U02 crea **cuatro procesos XI** (`v3`, `memory`, `voice`, `entity`) en cada turno, aunque la petición sea solo una suma o la lectura del estado. También consulta de manera incondicional la identidad de readout V3 antes de saber si se necesitan observaciones.

C04 implementa estos cambios, aislados de U02:

1. **Plan de dependencias (DAG):** tras la interpretación aprendida XI, registra las etapas y sus dependencias nativas conservando *el orden original*. Nunca reemplaza la etiqueta de intención ni elige acciones diferentes. La ruta sin contrato también sigue el flujo original.
2. **Sesiones nativas diferidas:** se crea un descriptor ligero por banco pero el proceso XI original se abre únicamente cuando U02 realmente intenta ejecutar, guardar o leer ese banco. Los bancos no usados nunca se arrancan.
3. **Lectura VQC diferida:** la consulta de la versión del readout nativo se hace cuando una operación requiere la percepción. Las consultas de texto, cálculo, reglas, estado y cancelación no necesitan leer un banco V3.
4. **Paralelismo seguro:** solo los hashes SHA-256 de bancos inmutables, que se recuperan mediante una consulta SQLite serial en el hilo principal, se ejecutan en hasta cuatro trabajadores independientes. Se comparan todas las firmas **antes** de abrir cualquier cálculo XI.
5. **Control de aislamiento:** la ruta utiliza el bytecode original de `Session.turn` con globals aislados por sesión, sin modificar el código verificado por el manifiesto U02, sin cambiar la topología cuántica, sin cambiar la transacción original, sin escrituras por los trabajadores de hash.
6. **Telemetría separada:** el plan, el número de bancos iniciados/evitados y los verificadores de hashes se miden fuera de la respuesta del modelo. Los recibos históricos y checkpoints permanecen idénticos.

## Límite deliberado de paralelismo

**No se ejecutan dos circuitos cuánticos con estado en paralelo.** QRL, VQC, memoria y coordinación tienen dependencias y efectos internos en el simulador, aunque sus respuestas inmediatas parezcan independientes.

C03 ya demostró que omitir una segunda ejecución VQC cambió 32.155 bytes de su checkpoint. C04 no pierde esos estados: todo circuito requerido se ejecuta íntegramente, en su orden U02.

La representación de C04 muestra candidatos de ejecución y un orden topológico, pero *no* declara que XI haga trabajo cuántico concurrente. El paralelismo implementado y verificado es SHA-256 de snapshots inmutables; cualquier paralelismo nativo requerirá un modelo de autoridad compartida, commits ordenados y pruebas de identidad de todos los estados.

## Cómo probar

En Linux, con las revisiones fijadas de REVERSE-PC y Mundo X ya usadas en C03:

    bash deps/reverse-pc/scripts/build-xi-session.sh deps/mundo-x deps/reverse-pc/build
    python3 -m unittest integration.planner_u03_c04.test_planner -v
    python3 -m integration.planner_u03_c04.conformance
    python3 -m integration.planner_u03_c04.benchmark --samples 2 --out build/c04/benchmark.json

Ejemplo experimental:

    from integration.cache_u03_c03.session import archive_cache_scope
    from integration.planner_u03_c04.runtime import PlannedSession

    with archive_cache_scope() as models:
        with PlannedSession("build/c04/synthetic.sqlite", parallel_hash_workers=4) as bbyq:
            answer = bbyq.turn("math-1", "calcula 7 + 3")
            print(answer)
            print(bbyq.last_plan_stats)

**Sin cambios de producto:** `Session` U02 y `CachedSession` C03 siguen existiendo y funcionando igual. El código del planificador está en un directorio separado `integration/planner_u03_c04/` y debe activarse explícitamente.

## Conformance y criterios estrictos

- Comparación byte por byte de resultados, historial, checksums de bancos, rollback y reanudación con U02.
- Aritmética, texto, estado y cancelación deben evitar abrir los cuatro bancos cuánticos.
- `remember` y `recall` deben iniciar únicamente memoria nativa; `policy` inicia V3, voz y coordinador; una misión completa activa los cuatro.
- Feedback debe conservar todas las actualizaciones; leer hechos derivados de VQC tras aprendizaje abre el motor V3 cuando se requiere recalcular.
- Ningún circuito se omite sin haber probado equivalencia de estados: conteos `EXEC` de misión completa deben mantenerse.
- Los 159 archivos congelados se verifican SHA-256; no se modifica el formato de datos ni se genera APK.
- Medición A/B de procesos abiertos, ejecución XI y latencia en el mismo runner y con la misma caché C03 en ambos lados.

## Pros, contras y riesgo

**A favor:** menos procesos, memoria transitoria y arranques inútiles en tareas sencillas, sin rediseñar los modelos. Es reversible, acotado y protege todos los checkpoints.

**En contra:** el despacho en Python, los hilos para hash y la validación del grafo añaden trabajo extra; no todas las tareas ganarán rendimiento. Para una misión completa se activan los cuatro bancos, por lo que su beneficio puede ser pequeño o negativo. La planificación no concede poderes de inteligencia nuevos ni ventaja cuántica.

Las mediciones son de GitHub/Linux, no de Android físico. No se realiza APK, compilación Gradle ni activación en la aplicación instalada. Esta es una rama experimental con revisión antes de fusionar.

## Resultados reproducibles de C04

La campaña completa original/C03/C04 aprobó las pruebas de integridad y las
mediciones A/B en [GitHub Actions #42345963529](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42345963529).
Consulta [RESULTS.md](RESULTS.md) para cifras exactas, recursos, limitaciones,
regresiones de latencia y el experimento de consulta VQC diferida.

No se omite ninguna operación *con estado* de VQC/QRL/QMemory/voz. En tareas
que no necesitan VQC se evita exclusivamente su consulta read-only de versión,
lo que reduce un paquete nativo EXEC además de hasta cuatro procesos.
El paralelismo implementado sigue limitado a hashes independientes.
