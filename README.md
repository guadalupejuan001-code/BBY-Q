# BBY Q — investigación de inteligencia artificial evolutiva

**Estado:** ETAPA 1 implementada como prototipo reproducible; aprendizaje de ETAPA 2 bajo prueba. No hay conciencia, vida biológica, simulación cuántica obligatoria ni modelo conversacional preentrenado.

BBY Q investiga si un medio lógico de **reglas, relaciones, diferencias y transformaciones** puede sustentar una entidad computacional que conserve experiencias, formule hipótesis, prediga consecuencias y modifique sus representaciones. Se reutiliza el motor real de REVERSE-PC para persistir **una sola autoridad de estado** en Inverse Ether Memory. Los mecanismos semánticos y de aprendizaje, todavía ausentes en Ether, se investigan en este repositorio; no se atribuyen al motor original.

## Recuperación del laboratorio previo

El código histórico del Galaxy Watch4 permanece intacto en `app/` por ahora, claramente **fuera del núcleo de IA**. También se preservó antes de estos cambios mediante la rama [`archive/watch4-optics-20261025`](https://github.com/guadalupejuan001-code/BBY-Q/tree/archive/watch4-optics-20261025), commit `a5cde7b06d5b3f80714560048d34285c2b435173`. `ROADMAP.md` y `docs/RECEPTOR_OPTICO.md` pertenecen al trabajo anterior. No se incluyen permisos de sensores en la inteligencia.

## Iniciar y probar

Python 3.11+ sin dependencias de IA. Para **persistencia real**, compilar el ejecutable XI `reverse_pc` de REVERSE-PC en el commit `063d871c27de2d4f10904ec5c3e1363c2fe16d86`, utilizando su dependencia Mundo X fijada a `e2778d962af22f6f1a0794058dd4685fc2573966` y su script de integración verificada.

```bash
# En un checkout de REVERSE-PC fijado en ese commit:
bash scripts/setup-ether.sh
cmake -S . -B build -DCMAKE_BUILD_TYPE=Release -DBUILD_TESTING=OFF
cmake --build build --target reverse_pc --parallel 2

# En el checkout de BBY Q, usar el ejecutable construido:
export PYTHONPATH=ai
export BBYQ_REVERSE_PC=/ruta/REVERSE-PC/build/reverse_pc
python -m bbyq --state /tmp/bbyq.rvp birth
python -m bbyq --state /tmp/bbyq.rvp predict --signal 0.5 --pressure -0.2 --action 1
python -m bbyq --state /tmp/bbyq.rvp step --signal 0.5 --pressure -0.2 --action 1 --outcome 0
python -m bbyq --state /tmp/bbyq.rvp inspect
# Nuevo proceso: comprobar mismo identificador, experiencia y pesos
python -m bbyq --state /tmp/bbyq.rvp inspect
```

Si no está compilado REVERSE-PC, las pruebas del algoritmo pueden ejecutarse aisladamente y se identifican como tales; **no sustituyen** la prueba de persistencia nativa.

```bash
PYTHONPATH=ai python -m unittest discover -s ai/tests -v
PYTHONPATH=ai python -m bbyq experiment --seed 42 --runs 5 --train 400 --test 240 --output /tmp/experiment.json
# Con REVERSE-PC compilado: persiste el modelo entrenado en su RVPC2
PYTHONPATH=ai python -m bbyq --state /tmp/aprendida.rvp experiment --persist --output /tmp/experiment-native.json
```

## Componentes y evidencia

- `ai/bbyq/model.py`: representación explicable mediante relaciones ponderadas, predicción y actualización por error; implementada en BBY Q, sin pesos externos.
- `ai/bbyq/world.py`: entorno oculto para el agente; observaciones y consecuencias separadas de la hipótesis.
- `ai/bbyq/store.py`: bytes diferenciales sobre el InverseMemory real a través de XI; RVPC2, atomicidad y recuperación son responsabilidad de REVERSE-PC.
- `ai/bbyq/experiment.py`: holdout, controles sin entrenamiento y mayoría, paridad no lineal y cambio de régimen con prueba de retención.
- `ai/tests/`, `.github/workflows/bbyq-ai.yml`: pruebas locales y pruebas nativas obligatorias en CI.
- `docs/AI_AUDIT.md`, `docs/AI_ARCHITECTURE.md`, `docs/AI_EXPERIMENTS.md`: auditoría, contrato técnico, protocolo y límites.
- `docs/evidence/experiment001-local.json`: resultados locales del algoritmo; `docs/evidence/native-benchmark-run-40266295038.json`: ejecución CI del REVERSE-PC real con latencia, memoria y sobrecostes medidos.

La comparación inicial solo se refiere a un problema controlado, no a superioridad sobre modelos generales ni a aceleración cuántica. Los resultados negativos —especialmente el olvido tras adaptarse— se conservan.


## E002 — aprendizaje con recuperación contextual

Nueva hipótesis en `ai/bbyq/context.py`: BBY Q reconoce cambios por evidencia de error, conserva representaciones anteriores y puede recuperar una hipótesis archivada **sin que el entorno le indique su identidad**. El cambio de estado y las experiencias se persisten en el **mismo** Inverse Ether Memory/RVPC2; no hay bases de datos paralelas ni un modelo externo de IA. La aritmética de aprendizaje es código propio de BBY Q y todavía se ejecuta en Python, no en la ALU XI.

```bash
PYTHONPATH=ai python -m bbyq experiment --contextual --seed 42 --runs 5 --train 400 --test 240 --recovery 36 --output experiment002.json
# Interacción persistentemente contextual por defecto:
PYTHONPATH=ai python -m bbyq --state /tmp/bbyq.rvp step --signal 0.5 --pressure -0.2 --action 1 --outcome 0
# Comparar con el aprendiz anterior:
PYTHONPATH=ai python -m bbyq --state /tmp/legacy.rvp step --single-model --signal 0.5 --pressure -0.2 --action 1 --outcome 0
```

La campaña local E002 (5 semillas) midió 95,00 % en el contexto original tras regresar y 67,33 % con modelo único; hubo recuperación real del contexto archivado en las cinco ejecuciones. La prueba ampliada (25 semillas) obtuvo 95,05 % frente a 60,75 %. No implica conciencia, semántica general ni superioridad cuántica. Véase [protocolo, límites y controles negativos](docs/AI_E002_CONTEXT.md). La verificación de persistencia nativa para E002 se ejecuta separadamente en CI.


## BQL2 — compacidad del estado lógico

El codec propio `ai/bbyq/compact.py` detecta fragmentos ASCII repetidos y
los representa como referencias acotadas a posiciones ya observadas. Convierte
JSON canónico de BBY Q en una proyección reversible y guarda sus bytes en
las mismas direcciones de **Inverse Ether Memory**, bajo XI/RVPC2. No
introduce otro motor, modelos preentrenados ni qubits automáticos.

El encabezado de longitud distingue BQL2 de snapshots JSON anteriores,
que siguen siendo legibles. Las pruebas cubren recuperación exacta,
datos corruptos, límites de descompresión y migración nativa de V1 a BQL2.
El codec solo busca ahorro de espacio: tiempo de CPU e I/O deben medirse;
una mejora en bytes no implica aceleración.
