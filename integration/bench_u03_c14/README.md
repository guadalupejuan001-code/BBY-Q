# BBY Q U03 C14 — Medición nativa XI y ablaciones ampliadas

**Base exacta:** C13 [PR #99](https://github.com/guadalupejuan001-code/BBY-Q/pull/99), commit `5e88433895218ad90ee18f7380c49a69a51bc07e`. C13 demostró sólo reducciones del 2,08–2,95 % en distintas ejecuciones, **bajo el umbral 3 %**, y no promovió su caché. C12 tampoco mejoró la exactitud. Estas decisiones permanecen congeladas.

## Qué comprueba C14

1. **Perfil nativo XI reproducible:** todas las llamadas `XiSession.execute` se miden por paquete con el banco original, y se les asigna exactamente un propietario: **C1, VQC, QRL, QMemory, Entity, QChat** o categoría `XI-transport` / `XI-mixed`. Se exige que los intervalos no se solapen y que la suma de categorías iguale la duración de todos los paquetes. **Es tiempo exclusivo por paquete ejecutado en el host, no tiempo exclusivo interno por compuerta ni por core de CPU**; un paquete con varias operaciones NO se atribuye completo a cada operación.
2. **Matriz predeclarada e inédita:** 6 misiones XI completamente nuevas y distintas de C11/C12/C13, con ambos valores de regla y varias posiciones (0, 1, 2, 4, 5, 6). Dos repeticiones por ruta: **12 mediciones por ruta** × tres rutas: U02 `frozen`, C12 entrenado **no promocionado**, y la caché C13 opt-in **no promocionada** sobre los mismos bancos congelados. Alternar orden y contabilizar la autenticación de la caché.
3. **Recibos originales:** cada misión usa `Session.turn` nativo de U02 sobre una copia SQLite fresca; se comprueba contra el código no instrumentado de C13. Se compara respuesta, identidad del recibo y snapshot exacto en U02 vs caché; no se ocultan rechazos. Nunca pasan etiquetas de validación a inferencia.
4. **Ablaciones extendidas:** cinco condiciones U02 originales (normal, sin QMemory, sin VQC, sin QRL, sin QChat/voz) en 4 misiones nuevas y ambos estados `frozen`/C12 entrenado: **40 ejecuciones nativas**, con diferencias de clase, regla, acción, soporte, voz y coste. Se generan las etiquetas sintéticas del oráculo original XI **después de ejecutar todas las condiciones**.
5. **Interferencia:** secuencia A→B→A con reglas distintas en una sesión real U02 por brazo; no se presupone estabilidad.
6. **Concurrencia real:** dos peticiones `Session.turn` en **conexiones SQLite separadas** que escriben en una misma base descartable por brazo, con WAL, registro de ambas tareas, C1 sincronizado y replay sin doble ejecución. No se presenta como paralelismo cuántico, aceleración ni prueba masiva de carga.
7. **CPU/RAM/I/O/SQLite:** tiempos de copia SQLite, apertura/autenticación, `Session.turn`, auditoría C09 y cierre; CPU Python y del proceso nativo (observación `/proc` aproximada), pico RSS acumulativo, lecturas/escrituras I/O observadas, número de sentencias SQLite y bytes de fuente XI. Las trazas SQL cuentan sentencias, **no** sus tiempos exclusivos.

Todos los experimentos usan el simulador XI/Ether de **REVERSE-PC fijado**, no hardware cuántico físico ni Android. El C14 es una campaña de diagnóstico: sólo se puede proponer una optimización si supera controles repetibles y preserva exactitud y bancos; esta rama no despliega sustitutos al runtime original.

## Reproducción en GitHub

```bash
bash deps/reverse-pc/scripts/build-xi-session.sh deps/mundo-x deps/reverse-pc/build
python3 -m unittest integration.bench_u03_c14.test_campaign -v
python3 -m integration.bench_u03_c14.verify_panel
python3 -m integration.bench_u03_c14.campaign --repeats 2 --out build/c14/benchmark.json
```

Dependencias fijadas: `REVERSE-PC@08c363e6c6855c14026c86046af7183a45f45a98`; `mundo-X@e2778d962af22f6f1a0794058dd4685fc2573966`.

Evidencia en artefactos GitHub Actions: JSON completo con métricas, controles y huellas, regresiones C1/U02 y panel C00–C17. **159 archivos históricos protegidos con SHA-256**, ninguna autoridad nueva de memoria, ninguna fusión ni APK.

[RESULTS.md](RESULTS.md) · [Panel C00–C17](../../docs/BBY_Q_U03_PANEL.md) · [Estado JSON](../../docs/BBY_Q_U03_ESTADO.json) · [Continuidad C15](../../docs/BBY_Q_U03_SIGUIENTE.md).
