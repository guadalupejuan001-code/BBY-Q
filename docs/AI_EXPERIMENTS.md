# BBY Q — experimento E001 y protocolo de falsación

## Pregunta

¿Una entidad que solo recibe dos señales, ejecuta una de dos acciones y observa un resultado puede adquirir una representación que prediga **casos nuevos** mejor que una versión congelada, usando sus propias experiencias y sin respuestas precargadas?

## Condiciones verificables

- Mundo: `RelationalWorld(seed)` con cuatro coeficientes y sesgo ocultos; política de acciones de exploración equilibrada. Coeficientes no se importan al agente.
- Modelo: relaciones observables + gradiente logístico en línea. No hay pesos iniciales, modelos remotos ni llamadas a LLM.
- Entrenamiento: 400 experiencias/semilla. Test: 240 observaciones nuevas por semilla, otro RNG y comprobación de intersección vacía. Acción de evaluación balanceada entre -1 y +1. Cinco semillas consecutivas 42–46.
- Referencias: mismo modelo sin aprendizaje (`learn=False`), predicción antes de entrenar y mayoría de resultados del entrenamiento. Mismo holdout para todas.
- Control negativo: dinámica XOR/paridad con las mismas observaciones; la clase lineal debe mostrar una limitación.
- Cambio de régimen: se invierten resultados; se evalúa sin entrenamiento en la nueva regla, después de adaptación y finalmente en la **regla antigua**. La adaptación ocurre sobre **una copia aislada**, no destruye el agente principal.
- Evaluación: llama solo `predict()` y `world.step()`, nunca `experience()`; un test verifica que no muta el estado.

## Ejecutar

```sh
PYTHONPATH=ai python -m unittest discover -s ai/tests -v
PYTHONPATH=ai python -m bbyq experiment --seed 42 --runs 5 --train 400 --test 240 --output experiment.json
# Con REVERSE-PC compilado y revisionado, ejecutar adicionalmente:
BBYQ_REVERSE_PC=/path/reverse_pc PYTHONPATH=ai \
  python -m bbyq --state learned.rvp experiment --persist --output experiment-native.json
BBYQ_REVERSE_PC=/path/reverse_pc PYTHONPATH=ai \
  python ai/bench/native_benchmark.py
```

## Resultado local inicial: algoritmo en Python

El JSON bruto de 5 ejecuciones se conserva en `docs/evidence/experiment001-local.json`, incluye promedios, resultados **de cada semilla**, errores, tiempos y tamaño de memoria Python `tracemalloc`. El proyecto no redondea a una supuesta ventaja cuántica.

| Medida | Media local |
|---|---:|
| Predicción inicial / control congelado | 45,25 % |
| Mayoría entrenada | 59,25 % |
| BBY Q después de 400 experiencias | 95,17 % |
| Control XOR/paridad negativo | 48,92 % |
| Regla invertida antes de adaptar | 4,83 % |
| Regla invertida tras adaptar | 96,58 % |
| **Regla antigua después de adaptar** | **3,42 %** |

Estas cifras son reproducibles a nivel de salidas para misma semilla, versión y algoritmo. Los microsegundos y el pico de `tracemalloc` del JSON dependen del entorno; no son RSS nativo. El benchmark nativo de latencia por XI y tamaño RVPC2 se ejecuta en CI después de compilar el REVERSE-PC fijado. Su evidencia sin filtrar se publica como artefacto CI y se conserva en `docs/evidence/native-benchmark-run-40266295038.json`.

## Interpretación que puede fallar

El 95 % no implica razonamiento, conversación, causalidad general ni transferencia abierta: la dinámica positiva fue generada desde una familia compatible con los rasgos del predictor. Tampoco se ha encontrado una ventaja sobre aprendizaje logístico estándar: **ese método es la referencia interna utilizada**. El negativo de paridad demuestra límite representacional. La retención bajo inversión demuestra olvido extremo; la siguiente investigación debe medirlo tras cualquier mecanismo nuevo. Un modelo convencional con contexto o memoria múltiple podría superar claramente esta propuesta.

**Criterio Etapa 1:** suite native-integrated completa y continuidad `RVPC2` tras proceso nuevo, con rollback y corrupción detectada.
**Criterio inicial Etapa 2:** mejora de precisión del agente frente al congelado y mayoría en holdout, con negativos publicados. **No** reclamar Etapa 3 o adaptación sin olvido.

## Validación con el REVERSE-PC real (GitHub Actions)

Fuente: [run 40266295038](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40266295038), artefacto `bbyq-native-evidence`. La suite nativa pasó 13/13 pruebas, incluidos reinicio en nuevo proceso, rollback, detección de corrupción y persistencia del agente aprendido. Datos del benchmark `BBYQ-NATIVE-B001`:

- 24 pasos con `reverse_pc run` real; latencia mediana **16,99 ms**, p95 nearest-rank **28,57 ms** por transacción y restauración asociada. Se conservan las 24 duraciones crudas en el JSON.
- Archivo RVPC2 final: **169.131 bytes**; **7.322 overrides lógicos**, revisión de memoria 68.998. No es tamaño del JSON sin compresión ni memoria RSS.
- Pico máximo RSS de los procesos hijos observado por Python (Linux): **15.884 KiB**. No aísla asignaciones del almacén, incluye el ejecutable y el costo del proceso.
- Estadísticas nativas: **0 qubits activos, 0 enlaces cuánticos, 0 reglas Ether globales**. Es uso clásico de InverseMemory, no aceleración cuántica.
- La campaña aprendida conservada bajo RVPC2 utilizó **10.736 overrides** y un archivo de **245.195 bytes**; fue restaurada y comparada con el estado previo.

Son medidas de **una ejecución** en un runner compartido, no una distribución de plataformas. Esta versión aún no demuestra ahorro frente a SQLite ni frente a un archivo JSON clásico. Hay un sobrecoste claro de almacenamiento y procesos; el siguiente ensayo debe comparar alternativas bajo igual semántica de persistencia, aislamiento y rollback.


## E002: el agente reconoce un régimen previamente aprendido

La evaluación independiente de E002 enfrenta el sistema contextual a un
modelo único con idéntica experiencia y holdout. No se informa al agente
qué régimen está activo. La recuperación ocurre por contradicciones de
alta confianza; se verifica el evento `recalled`, no solo la precisión.
Para las cinco semillas 42–46, tras A (400), B invertido (400) y retorno
a A (36), el sistema contextual promedió 95,00 % contra 67,33 % del
control de modelo único sobre 240 observaciones nuevas por semilla.
El régimen B alcanzó 93,92 % de precisión antes del regreso; los cinco
ensayos terminaron con exactamente dos contextos y dos transiciones.

En 25 semillas adicionales (1–25; holdout de 160), la recuperación de A
promedió 95,05 % frente a 60,75 %, con 25/25 eventos `recalled`.
E002 no mostró solución general de paridad/XOR; el control local en
25 semillas promedió alrededor de 55,76 %. No sustituir estas pruebas
locales por afirmaciones de persistencia: el workflow compila y ejecuta
REVERSE-PC real y publica el estado E002 en RVPC2 y su inspección.
Ver [diseño y límites E002](AI_E002_CONTEXT.md).


## Benchmark de transporte BQL2 (nativo, misma máquina)

Se midieron siete pares intercalados A/B y B/A de 24 transacciones reales
en la misma revisión compilada de REVERSE-PC; los archivos persistentes
de cada prueba contienen estados lógicos **idénticos**. La mediana de
las siete medianas por condición fue de 12,9517515 ms (JSON) y
9,755009 ms (BQL2), un 24,68 % menos en esta carga. Los tamaños
RVPC2 fueron 171.748 bytes y 57.093 bytes respectivamente (66,76 %
menos); los overrides lógicos 7.438 y 2.349. La condición BQL2 tuvo
un valor atípico p95 de **122,351 ms** en uno de los siete ciclos,
registrado sin eliminarlo. Son medidas integradas de codec + Python
+ proceso XI + escrituras y no tiempos aislados del codec.

Para la entidad contextual E002 completa: sin codec, RVPC2 de
380.972 bytes y 16.746 excepciones; con BQL2, 109.836 bytes y 4.731
excepciones, sin alterar 95,00 % de precisión al recuperar el contexto.
Cero qubits en ambas condiciones. Artefactos:
[runner comparativo](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40269377678),
[runner E002 original](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40268336713)
y [runner BQL2](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40269083155).
Resumen con todas las parejas y outlier en
[evidence/codec-paired-ab01.json](evidence/codec-paired-ab01.json).
