# BBY Q — QML/QRL experimental en XI nativo (ciclos 01-04)

## Objetivo y contrato
Todos los **motores** de calculo, optimizacion, entrenamiento, inferencia, politica y control son archivos `.xi` del lenguaje original del autor. Se usa el interprete ya existente de REVERSE-PC / Mundo X; no se introduce ningun modelo Python, JavaScript, PyTorch, Qiskit ni pesos externos para aprender. Los scripts shell de CI solamente compilan el interprete existente, ejecutan programas XI y comparan sus resultados.

**Hasta C04 no sustituía** las rutas conversacionales E005-E034, P01-P06 o X09/X10, C05–C07 agregan un subcomando a `bbyq.mjs` sin cambiar pesos/checkpoints historicos. Es laboratorio independiente y optativo en `ai/xi/qml_qrl/`, con su estado RVPC2.

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

## Ciclos C05–C07: motores ampliados y acceso operativo

**C05: VQC2 entrelazado.** `vqc2-*.xi` usa dos bits de entrada, dos cúbits y un
circuito `X(x0) X(x1) · H(2) · CX(2,3) · H(2) T(2)^k H(2)`.
La capa H/CX prepara estados de Bell; el observable clasificador es la paridad
`Z₂Z₃` y no la medida de un cúbit. El modelo selecciona `k=0..7` en XI
minimizando Brier Q10000 con penalización de profundidad. Hay 4 ejemplos de
entrenamiento y 4 de holdout sintéticos, para XOR y XNOR de forma independiente.
La inferencia consulta Born/expectación nativas y deshace cada operador.

**C06: QRL2 secuencial.** Dos decisiones por episodio sobre la paridad de un
par Bell: `0=I`, `1=X`. La tabla persistente de 16 valores Q está indexada
por objetivo, etapa, paridad y acción. En XI se entrena con actualización
TD de objetivo Bellman, recompensa terminal, descuento `gamma=0.9` y costo de
acciones. Las decisiones se ejecutan contra el simulador de dos cúbits y
se comprueban con `expect Z:4 Z:5`, `expect X:4 X:5` y `probz`.
Es un MDP determinista, **no** QRL cuántico profundo ni aprendizaje de
recompensas físicas medidas. El feedback se calcula con transiciones en XI.

**C07: conexión CLI.** `bbyq.mjs quantum` ofrece transporte al intérprete
XI y persistencia RVPC2 aislada. JavaScript únicamente gestiona archivos,
validación de argumentos y salida JSON; la lógica de aprendizaje, clasificación
y política permanece enteramente en XI. Los entrenamientos usan reemplazo
atómico del estado solo tras una ejecución correcta.

```sh
R=/ruta/al/reverse_pc
S=/ruta/a/mi-estado-qml-qrl
node bbyq.mjs quantum --runtime="$R" --state="$S" init
node bbyq.mjs quantum --runtime="$R" --state="$S" train-xor
node bbyq.mjs quantum --runtime="$R" --state="$S" eval
node bbyq.mjs quantum --runtime="$R" --state="$S" classify 0 1
node bbyq.mjs quantum --runtime="$R" --state="$S" train-agent
node bbyq.mjs quantum --runtime="$R" --state="$S" plan 1 0
node bbyq.mjs quantum --runtime="$R" --state="$S" status
```

El conjunto inverso se selecciona con `train-xnor`. `eval`, `classify` y
`plan` no modifican la memoria `memory.rvp`.

La verificación está en `.github/workflows/bbyq-qml-qrl-next.yml`: construye
el intérprete original fijado, comprueba Bell y sus marginales, cuatro
objetivos del agente, ambos holdouts, aprendizaje retenido y rollback.

### Límites que se mantienen

- No hay APK conversacional en esta ampliación. La carpeta `app/` corresponde a
  `WatchOptics`, no a un empaquetador de X10 para Android.
- Históricamente, hasta C07, `quantum` solo era un subcomando de laboratorio. La integración conversacional explícita se añade en C08–C10.
- El simulador no expone actualmente observables Born a registros XI, por lo
  que el entrenamiento usa el modelo matemático tabulado, y la prueba cuántica
  es independiente de la actualización.
- Ninguna ventaja cuántica, generalización lingüística ni ejecución sobre
  hardware cuántico real queda demostrada por estos problemas sintéticos.

## Ciclos C08–C10: integración real con la conversación X10

**C08: intención nativa XI.** `ai/xi/qml_qrl/conversation-route.xi` interpreta
una gramática acotada en español e inglés, distingue órdenes de consulta,
entrenamiento y planificación, y rechaza parámetros inválidos o frases compuestas.
Las rutas abiertas son `quantum ...`, `cuantico ...`, `cuántico ...`
y `bby q quantum ...`; también se admiten órdenes sin prefijo al invocar
explícitamente `--module=quantum`. El filtro previo en JavaScript solo evita
ejecuciones nativas para mensajes claramente ajenos; **XI decide el comando**
y el sentido de sus dos argumentos binarios.

**C09: transacción de sesión completa.** La ejecución entra al mismo
`bbyq.mjs turn` y `ai/personal/x10/session.mjs` que la conversación general.
El puente `integration/qml_qrl/conversation.mjs` reutiliza los motores
QML/QRL XI existentes, conserva una memoria RVPC2 en la tabla SQLite
`quantum_state` (aparte del estado X09 y de E034) y comprueba su SHA-256.
Los resultados de aprendizaje se publican **dentro de la misma transacción**
que el comprobante X10; un fallo antes del COMMIT hace rollback del aprendizaje.
Un identificador repetido con idéntico mensaje reproduce su recibo, sin
reentrenar. Una solicitud contradictoria se rechaza.

**C10: suite de prueba.** `integration/qml_qrl/tests/native-chat.mjs` utiliza
sesiones sintéticas de X10 y el intérprete nativo XI; verifica ambos motores,
probabilidades y correlaciones Bell, consultas sin mutación, roles X10
existentes, restricciones de aprendizaje, múltiples pasos QRL, replay,
rollback, CLI real y preservación de estados X09/E034.
La CI se encuentra en `.github/workflows/bbyq-qml-qrl-conversation.yml`.

### Utilización desde una sesión conversacional existente de X10

Requiere un build X10 válido, Node 24 y su ejecutor `reverse_pc`
correspondiente (el antiguo entrenamiento X09 se preserva).
Para conversar con los motores conectados:

```sh
node bbyq.mjs --build /ruta/build-x10 turn /ruta/sesion-x10 q001 "quantum estado"
node bbyq.mjs --build /ruta/build-x10 turn /ruta/sesion-x10 q002 "quantum entrena xor"
node bbyq.mjs --build /ruta/build-x10 turn /ruta/sesion-x10 q003 "quantum clasifica 0 1"
node bbyq.mjs --build /ruta/build-x10 turn /ruta/sesion-x10 q004 "quantum evalúa"
node bbyq.mjs --build /ruta/build-x10 turn /ruta/sesion-x10 q005 "quantum entrena agente"
node bbyq.mjs --build /ruta/build-x10 turn /ruta/sesion-x10 q006 "quantum planea 1 0"
```

Cada solicitud debe usar un `REQUEST_ID` nuevo. Un mismo identificador
repetido con mensaje idéntico devuelve el resultado previo, sin entrenar.

También funciona el modo explícito `--module=quantum` y órdenes sin prefijo:

```sh
node bbyq.mjs --build /ruta/build-x10 turn /ruta/sesion-x10 q007 --module=quantum "clasifica 0 1"
```

**Límites:** la integración de chat ejecuta **comandos de laboratorio**
y describe sus resultados. **No** entrena lenguaje natural usando QML/QRL,
ni utiliza automáticamente sus políticas para producir cualquier respuesta
ordinaria. Las pruebas sintéticas no demuestran ventaja cuántica ni aprendizaje
a escala general. No se genera ni se valida una APK Android en C08–C10.
