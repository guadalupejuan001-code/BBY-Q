# BBY Q U03 C11 — Aprendizaje conjunto XI, supervisión verificada y ablaciones

**Base exacta:** C10 / PR #96, commit `147cfe804d413110400a7da528d286529f749fa9`.  
**Autoridad original:** BBY Q → w4U → QdU. No sustituir los motores, sus checkpoints, XI/Ether, ni el sistema original U02.

## Qué incorpora C11

C11 coordina una campaña de aprendizaje **sobre la ruta conjunta que U02 ya tiene implementada**. No crea un algoritmo de entrenamiento artificial en Python ni finge que todos los agentes aprendieron simplemente porque se ejecutó un procedimiento. El aprendizaje verdadero depende del feedback verificado original, que entrena de forma transaccional **Entity, VQC3, QRL3, QMemory, QChat100 y C1 router**.

El nuevo componente aporta:

- **Fuente común certificada:** crea una base U02 **sintética y temporal**, registra una misión original y la etiqueta de la regla aportada, y conserva un snapshot SHA-256 de los siete bancos.
- **Tres condiciones con el mismo checkpoint inicial:** `joint-verified` (feedback XI con clase y regla verificadas), `outcome-only` (solo resultado escalar explícito, sin etiqueta de clase/regla, por lo que VQC/QRL/QMemory no reciben esa supervisión) y `frozen` (sin entrenamiento).
- **Deltas de parámetros nativos:** lectura real por XI de las regiones de pesos VQC/QRL, ángulos QMemory, parámetros Entity y QChat, más identidad del readout VQC. A diferencia de un hash del RVPC2 completo, se excluyen los contadores de optimización y la metadata. El lector C1 se comprueba por su banco original y su registro `updates.router`, sin afirmar un cambio de pesos no medido.
- **Fallos atómicos y replay:** las transacciones de feedback inyectadas con fallo deben revertir todo banco y recibo. Un replay de la misma solicitud no debe reentrenar; una segunda solicitud de feedback debe rechazarse.
- **Validación independiente:** tres muestras nuevas, sin repetir la semilla ni los nombres del entrenamiento; un test reservado de cuatro muestras se abre solamente después de la decisión de promoción. Las predicciones se producen en el U02 original antes de revelar las etiquetas del generador XI, que se obtienen en otra sesión nativa independiente.
- **Ablaciones reales de inferencia U02:** `memory-erased`, `vqc-ablated`, `qrl-ablated`, `voice-ablated` y misión normal. Cada condición se ejecuta sobre un clon nuevo; no se altera el candidato entrenado.
- **Promoción controlada:** la variante conjunta solo es candidata si mejora estrictamente sobre `frozen` en clasificación de validación, no empeora premisas/reglas/salida y existe un delta de parámetros. Si no, se conserva la versión original y se documenta honestamente.

## Qué se mide

Se registran, sin descartar fallos, las clases nativas, supervisión QMemory, soporte de misión, voz fiel/terminada, acción simulada QRL, traza de XI, identidad de banco y porcentaje de acierto de clase frente a etiquetas sintéticas. El valor de `native_action=1` es una observación del plan QRL, **no se trata automáticamente como recompensa ni como acción físicamente correcta**.

Las etiquetas de evaluación del generador XI solo se calculan **después de todas las inferencias**, jamás se pasan como payload a esas pruebas. Los nombres, las semillas y las consultas de entrenamiento/validación/test son disjuntos. La variante `outcome-only` no es una ablación de un solo componente, porque su supervisión es más débil; las ablaciones nativas individuales se reportan aparte.

La campaña publica un archivo `build/c11/joint-candidate.sqlite` que contiene solo datos sintéticos y snapshots de laboratorio. **No se fusiona automáticamente** a la memoria real de usuarios ni se instala en Android.

## Reproducción

```bash
bash deps/reverse-pc/scripts/build-xi-session.sh deps/mundo-x deps/reverse-pc/build
python3 -m unittest integration.joint_u03_c11.test_campaign -v
python3 -m integration.joint_u03_c11.campaign --out build/c11/campaign.json
python3 -m integration.joint_u03_c11.verify_panel
```

CI: `.github/workflows/bbyq-u03-c11-joint.yml`, con compilación XI/Ether host, regresiones completas C1/U02, comparación C10 y SHA-256 de los 159 archivos protegidos.

## Límites y seguridad

- **Los resultados no prueban IA general ni ventaja cuántica.** Son episodios y semillas sintéticos de contratos existentes; la capacidad conversacional libre queda fuera.
- No se añaden nuevos agentes o autoridades de conocimiento. La memoria principal sigue siendo U02 SQLite con los bancos originales.
- Los pesos se entrenan por código XI nativo, no por un modelo clásico externo. No se afirma aprendizaje si únicamente cambia un contador o una imagen serializada.
- La evaluación sin feedback puede alcanzar ya el máximo: la selección conjunta no debe promoverse por simple ejecución de `train`.
- Cada evaluación se realiza en una copia temporal y descarta sus propios estados, preservando checkpoints anteriores.
- Ninguna APK, Gradle, implementación Android ni cambio automático a `main`.

[Panel C00–C17](../../docs/BBY_Q_U03_PANEL.md) · [Estado JSON](../../docs/BBY_Q_U03_ESTADO.json) · [Siguiente C12](../../docs/BBY_Q_U03_SIGUIENTE.md).
