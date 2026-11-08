# BBY Q U03 C12 — XI, capacidad y interferencia entre bloques

**Base exacta:** PR #97 C11, commit `4bf3a7aebe3f18bb8b7616264362e2f612faba30`. Esta rama usa exclusivamente el simulador XI/Ether, U02 y sus snapshots históricos. No crea otro motor de entrenamiento ni autoridad de memoria.

## Protocolo previamente fijado

Se usan identidades, semillas y reglas sintéticas **distintas de C11**: 2 muestras para entrenamiento y 4 para validación, luego 6 pruebas inéditas y 6 tareas de carga. Las muestras evalúan las siete posiciones permitidas en U02 y ambos valores de regla; la respuesta de VQC se compara con un generador XI **separado y consultado después** de la inferencia. Es un oráculo sintético, no un hecho externo.

Los brazos parten de la misma base U02: uno `frozen` ejecuta entradas sin feedback y otro `joint-verified` pide el feedback original de U02 en muestras de entrenamiento. Los seis grupos nativos VQC, QRL, QMemory, Entity, QChat y readout se miden con hashes de pesos/ángulos reales, además del banco y contador C1. La validación decide la elegibilidad; el conjunto de prueba no participa en selección ni entrenamiento.

**Capacidad observada:** seis misiones nuevas en la MISMA sesión nativa, con reglas y observaciones distintas. No confundimos seis misiones con capacidad máxima.

**Interferencia:** secuencia A → B → A (dos reglas/semillas); se compara el primer resultado A con el último A después de B, en cada brazo. Cambios y fallos se registran, no se descartan.

**Sincronización:** comprobación C1/U02 en cada paso, integridad de los siete bancos, rutas nativas de seis motores y huellas de parámetros antes/después. Las ablationes utilizan exactamente los modos U02 `memory-erased`, `vqc-ablated`, `qrl-ablated`, `voice-ablated` sobre copias.

**Coste:** tiempos de pared Linux que incluyen copias/arranque XI más tiempos por paso y entrenamiento separados; no representan latencia Android. No se afirma ventaja cuántica física, ganancia de exactitud ni generalización sin medirlas.

## Reproducir en CI

```bash
bash deps/reverse-pc/scripts/build-xi-session.sh deps/mundo-x deps/reverse-pc/build
python3 -m unittest integration.blocks_u03_c12.test_campaign -v
python3 -m integration.blocks_u03_c12.campaign --out build/c12/campaign.json
python3 -m integration.blocks_u03_c12.verify_panel
```

La compilación depende de las revisiones fijas de REVERSE-PC y mundo-X usadas en C11. El informe JSON contiene observaciones individuales (incluidos rechazos), medidas, ablaciones, hashes y copia SQLite **sintética y desechable**. No fusionar ni instalar; no generar APK. La cadena de agencia es **BBY Q → w4U → QdU**.

[Panel completo C00–C17](../../docs/BBY_Q_U03_PANEL.md) · [Estado](../../docs/BBY_Q_U03_ESTADO.json) · [Continuidad](../../docs/BBY_Q_U03_SIGUIENTE.md).

## Cierre de campaña nativa

[RESULTS.md](RESULTS.md) registra los resultados de [CI aprobada #42441627503](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42441627503): 6/6 regiones de pesos nativos cambiaron en el brazo conjunto; validación 4/4 y test 6/6 empataron con el congelado, sin beneficio de exactitud ni promoción. Carga 6/6 y A→B→A sin diferencias en las condiciones medidas. **Siguiente C13**, sin fusión ni APK.
