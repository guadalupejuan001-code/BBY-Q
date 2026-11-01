# BBY Q — QML/QRL experimental en XI nativo (ciclos 01-04)

## Objetivo y contrato
Todos los **motores** de calculo, optimizacion, entrenamiento, inferencia, politica y control son archivos `.xi` del lenguaje original del autor. Se usa el interprete ya existente de REVERSE-PC / Mundo X; no se introduce ningun modelo Python, JavaScript, PyTorch, Qiskit ni pesos externos para aprender. Los scripts shell de CI solamente compilan el interprete existente, ejecutan programas XI y comparan sus resultados.

**No sustituye** las rutas conversacionales E005-E034, P01-P06 o X09/X10, no altera `bbyq.mjs` ni cambia pesos/checkpoints historicos. Es laboratorio independiente y optativo en `ai/xi/qml_qrl/`, con su estado RVPC2.

## Ciclo 1 — Representacion
- `core-birth.xi`: instala una tabla aproximada de `cos(k*pi/4)`, `k=0..7`, con escala 10000 y desplazamiento 10000, en Inverse Ether Memory.
- `vqc-birth.xi`, `feed-identity.xi`, `feed-invert.xi`: crean el modelo y dos problemas sinteticos independientes, cada uno con 4 ejemplos de entrenamiento y 4 de evaluacion reservados.
- El prefijo reservado es `8100000000000000000`; no depende de los bancos de BBY Q existentes. Las lecturas carecen de side effects.

## Ciclo 2 — Clasificador variacional discreto
Ansatz de **un cubit** usando puertas nativas del autor:

```text
|0> -- X^x -- H -- T^k -- H -- <Z>
```

`T = diag(1, exp(i*pi/4))` y `H T^k H` implementa `Rx(k*pi/4)` hasta fase global. La salida analitica y Born del circuito ideal satisface

`P(1|x,k) = [1 - (-1)^x cos(k*pi/4)]/2.`

- `vqc-train.xi`: calcula todas las perdidas Brier sobre ejemplos, escala Q10000, regularizacion `10*k` y elige el mejor `k`, en XI exclusivamente. Entrenamiento por busqueda discreta exhaustiva, no gradiente continuo.
- `vqc-eval.xi`: validacion separada; calcula predicciones antes de leer la etiqueta reservada. No escribe memoria.
- `vqc-infer.xi`: emite `k`, prediccion clasica fija, `expect` y `probz` del simulador nativo; aplica el circuito inverso para devolver el cubit a `|0>` sin medicion proyectiva.

## Ciclo 3 — Aprendizaje por refuerzo de control de circuitos
El agente es **bandido contextual de un paso** (caso particular de RL con `gamma=0`), no un agente QRL profundo con planes de largo alcance.

- Contextos: estados objetivo `|0>` y `|1>`.
- Acciones: elegir `k=0..7` puertas `T` dentro del ansatz discreto.
- Recompensa en enteros: `R=2000+F*10000-lambda*k`, donde `F=|<target|psi>|^2` y por defecto `lambda=40`.
- Cada accion se explora; `Q <- Q + trunc[(R-Q)/2]`, cuatro pasadas por llamada.
- `qrl-train.xi` conserva Q de dos contextos y sus acciones en bytes XI/Ether, con eleccion greedy y desempate por circuito mas corto.
- `qrl-act.xi` carga la politica y crea una prueba fisico-matematica con `expect`, `probz` y uncompute.
- `qrl-audit.xi` lee los 16 Q almacenados sin escribir ni alterar estado; CI compara dos entrenamientos sucesivos.

**Limitacion crucial:** la ISA XI actual publica los observables cuánticos en JSON pero no puede leer `expect/probz` en registros `r0..r15`. La recompensa y la optimizacion aqui proceden de la formula Born analitica tabulada dentro de XI. Se contrastan con las consultas al simulador y NO se pretende que QRL haya aprendido de feedback medido directamente del nucleo. La fidelidad calculada es exacta respecto a los valores tabulados y aproximada respecto a la rotacion real (~0.00005 en coseno).

## Ciclo 4 — Pruebas y aceptación
- Workflow `.github/workflows/bbyq-qml-qrl-xi.yml`: compila el ejecutor REVERSE-PC fijado, ejecuta ambos conjuntos, evalúa holdout, prueba fidelidad y reversibilidad con Born, aprende dos contextos y verifica el rechazo transaccional de una etiqueta invalida.
- `calibrate.xi` prueba las 8 rotaciones con el nucleo nativo y compara cada probabilidad Born con la curva esperada (tolerancia 0.0002), ademas del uncompute.
- Los controles de aceptacion incluyen `k=0` para identidad, `k=4` para inversion, `4/4` en ambos holdouts sinteticos, QRL `k=0/4` en objetivos opuestos, y que el estado quede fisicamente en `|0>` al deshacer el circuito.
- No se afirman ventajas sobre clasificacion clasica; con un cubit y datos triviales no puede demostrarse.

## Ejecucion (requiere el interprete `reverse_pc` compilado)
Desde la raiz de BBY-Q:

```sh
R=/ruta/al/reverse_pc
P=ai/xi/qml_qrl
"$R" init /tmp/qml-blank.rvp
"$R" run "$P/core-birth.xi" /tmp/qml-blank.rvp /tmp/qml-core.rvp
"$R" run "$P/vqc-birth.xi" /tmp/qml-core.rvp /tmp/qml-vqc.rvp
"$R" run "$P/feed-identity.xi" /tmp/qml-vqc.rvp /tmp/qml-fed.rvp
"$R" run "$P/vqc-train.xi" /tmp/qml-fed.rvp /tmp/qml-trained.rvp
"$R" run "$P/vqc-eval.xi" /tmp/qml-trained.rvp /tmp/qml-eval.rvp
"$R" run "$P/vqc-infer.xi" /tmp/qml-trained.rvp /tmp/qml-witness.rvp
```

Para el agente QRL se debe ejecutar `qrl-birth.xi` sobre el estado inicializado por `core-birth.xi`, seguido de `qrl-train.xi` y `qrl-act.xi`. Los dos motores pueden coexistir en el mismo RVPC2.

## Extensiones futuras, sin falsificar capacidades
1. Incorporar en XI una forma transaccional de capturar una consulta Born en registro si el autor decide ampliar la ISA; **requiere modificar el interprete** y no es parte de estos motores solo-XI.
2. Ansatz de varios cubits con entanglement y etiquetas no triviales; comparar con perceptron y regresion logistica de control.
3. Optimizacion por gradientes/parameter shift cuando haya operadores de rotacion parametrica compatibles y medicion diferenciable.
4. Entrenamiento QRL multietapa con estados reales, credit assignment y episodios reproducibles; mantener validation holdout y rollback.

**Estado del desarrollo:** el codigo XI y las pruebas CI son propuestas ejecutables. El resultado de CI, no este documento, determina si estan validadas en REVERSE-PC.
