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
- `docs/evidence/experiment001-local.json`: resultados de una ejecución local del algoritmo, **no** resultados de REVERSE-PC nativo. CI mide ambos por separado y conserva artefactos.

La comparación inicial solo se refiere a un problema controlado, no a superioridad sobre modelos generales ni a aceleración cuántica. Los resultados negativos —especialmente el olvido tras adaptarse— se conservan.
