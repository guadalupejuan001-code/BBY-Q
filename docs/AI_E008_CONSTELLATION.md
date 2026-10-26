# BBY Q E008 — Ether Constellation y diagnóstico de organismo

## Hipótesis refutable

E007 preservaba dos contextos, pero un nuevo entorno no cabía en la
memoria y un error de una sola dirección temporal podía corromper el
conocimiento. E008 pregunta si un mismo agente puede aprender cuatro
reglas, reconocerlas tras numerosos cambios, **abstenerse** cuando
ninguna encaja y **proponer qué examinar después**.

El experimento es de aprendizaje simbólico en CPU clásica: no presume
conciencia, vida biológica, hardware cuántico ni rendimiento superior
a un clasificador diseñado a mano.

## Tecnología autorizada

Toda la lógica de representación, entrenamiento y control, admisión,
memoria, detección de novedades, selección de contexto, curiosidad
operativa y autodiagnóstico está en programas **XI propios**
(`ai/xi/e006/` y `ai/xi/e008/`). El intérprete existente sigue
usando bootstrap C++ para ejecutarse; no se ha escrito un motor de IA
en Python/C++/JavaScript ni añadido un modelo externo. REVERSE-PC
`6d4de14a2dfbce4b8a7f1cb50e29d11b9073fe98` reutiliza
Mundo X fijado en `e2778d962af22f6f1a0794058dd4685fc2573966`.
MX es el lenguaje fuente canónico futuro, todavía no autoalojado.

## Memoria: una autoridad, cuatro hipótesis

Todo reside en **un solo archivo RVPC2** con Inverse Ether Memory.

- El estado E006 mantiene su firma `66,81,6`, la estructura de
  entrenamiento original y la transición transaccional.
- Banco 0..3: raíz lógica `7000000000000000700 + 64 × banco`.
  Cada banco guarda firma 88, cantidad de relaciones,
  tres pesos lineales, cuatro descriptores, cuatro pesos compuestos y
  checksum módulo 251. Los bancos admitidos permanecen sellados.
- `+610`: cantidad de bancos; `+611`: banco activo; `+612/+625`:
  contador duradero de consultas con acarreo de 16 bits;
  `+613`: abstención; `+614/+626`: contador de abstenciones;
  `+615`: signo/región con mayor contradicción; `+616`:
  razón de abstención; `+617/+618`: mejor/segundo número de aciertos.
- `+621`: acción epistémica (`0` utilizar, `1` preguntar,
  `2` investigar contradicción, `3` ampliar repertorio);
  `+622`: región de entrada para la siguiente prueba;
  `+624`: grado de desacuerdo, expresado en votos 0..2.
- `+2000..` guarda contadores temporales para las pruebas; `+10000..`
  guarda observaciones y consecuencias. **Se borran dentro de la misma
  transacción que confirma la evaluación.** Esto impide colisiones con
  los bancos de conocimiento en `+700..+924`.

El archivo no almacena 4 RVPC2 ni crea 4 autoridades del núcleo.
Un quinto banco se rechaza sin sobrescribir los cuatro existentes.
El checksum detecta corrupción accidental, no ofrece autenticación
criptográfica ni defensa contra un escritor con permisos sobre el
archivo.

## Nacimiento, aprendizaje, validación y recuperación

Cada una de cuatro reglas se entrena desde un nuevo estado sombra
sobre 12 épocas × 200 ejemplos con magnitudes pares. Después un
examinador independiente en XI usa 240 magnitudes impares y permite
archivar el candidato si supera **214/240** y la mejor etiqueta
constante por al menos **15/240**.

Reglas del banco de pruebas:

| Banco | Relación desconocida inicialmente por el aprendiz |
|---|---|
| 0 | XOR de los signos de dos señales |
| 1 | XNOR, su negación |
| 2 | AND de dos signos |
| 3 | OR de dos signos |

Durante el reconocimiento, para **cada ejemplo** E008 calcula las
cuatro predicciones antes de leer la consecuencia. Esas predicciones
se comparan contra la misma etiqueta de la realidad simulada. Se
exige un modelo con suficiente precisión y diferencia sobre los
competidores. Una comprobación local impide que una precisión global
alta esconda fracaso sistemático en uno de los cuatro signos posibles.

Hay dos puertas de selección:

- alta confianza: mejor al menos 208/240, margen de al menos 30/240;
- ruido: mejor al menos 156/240 y margen de al menos 18/240;
- ambas requieren que cada región conocida tenga no más de un 45 %
  de errores. La incertidumbre produce **abstención**, nunca una
  elección forzada.

Estos umbrales se ajustaron en la campaña de desarrollo; cualquier
campaña final con secuencia aleatoria separada deberá declararse
como comprobación independiente, no como una nueva oportunidad para
ajustarlos silenciosamente.

## Aprender qué experimentar después

`plan-next.xi` no lee etiquetas del mundo:

- Con conocimiento compatible, decide **0: conservar y usar**.
- Si ningún modelo explica una región del espacio de entrada,
  propone **2: investigar la categoría con mayor sorpresa empírica**.
- Con incertidumbre distribuida o ruido, evalúa las predicciones
  de los cuatro modelos para los cuatro signos y elige una pregunta
  donde haya máximo desacuerdo entre hipótesis (**1: preguntar**).
- Si los cuatro modelos dan siempre la misma predicción,
  propone **3: ampliar la representación**, no inventa un resultado.

La política elige **el siguiente objetivo**. Todavía no crea nuevos
operadores generales ni puede ejecutar acciones físicas de manera
autónoma. Los generadores experimentales siguen siendo un entorno
externo simulado que escribe datos en el mismo RVPC2.

## Pruebas de desarrollo, no demostración universal

[CI de desarrollo E008](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40288674148),
cinco semillas 19,42,91,117,203:

- **20/20 modelos aceptados** tras generalizar en las tareas sintéticas
  (240/240 en el examen de desarrollo), 48.000 experiencias de
  entrenamiento en total.
- Secuencia de reconocimiento conocida
  `XOR → AND → XNOR → OR → XOR`: sin error en las cinco semillas.
- **5/5 NAND desconocidos** y **5/5 etiquetas aleatorias**
  rechazados sin afirmar una respuesta inexistente. NAND generó
  acción de investigación; el ruido, una consulta discriminante.
- **20/20 decisiones** con 15 % de ruido y **20/20** con 25 % de ruido
  conservaron la elección correcta, en el conjunto usado para
  calibrar la regla. No extrapolar ese 100 %.
- Rechazo de quinto banco, memoria dañada, consecuencia inválida,
  repetición de evaluación y pruebas de borrado de todos los
  buffers. Ningún caso adverso comprometió el estado original.
- Estado de cuatro hipótesis: alrededor de 6,7 KB RVPC2,
  **cero qubits activos**, cero enlaces cuánticos.

**Prueba independiente E008**:
[GitHub Actions — secuencias de evaluación separadas](https://github.com/guadalupejuan001-code/BBY-Q/actions/workflows/bbyq-e008-final.yml).
Usa distinta inicialización de los generadores para mundos conocidos,
NAND, ruido puro y una tercera causa no observable. Incluye una
campaña de longevidad con más de 255 consultas, cambiando las entradas
y verificando que el estado no se infle ni pierda archivos. Sus
resultados se documentan por separado cuando la ejecución concluye.

## ¿Se está creando un organismo?

Una entidad artificial no es biológicamente viva sólo por memorizar y
aprender. La palabra «organismo» es una **hipótesis de ingeniería**
en este proyecto, no un resultado científico confirmado.

| Propiedad funcional | Estado E008 |
|---|---|
| Identidad y continuidad en reinicio | Verificada en el esquema RVPC2 |
| Adquisición de regularidades y relaciones | Verificada sólo en mundos simbólicos acotados |
| Evaluación, rechazo y conservación de hipótesis | Verificada en pruebas controladas |
| Recuperación y selección entre cuatro contextos | Verificada en desarrollo |
| Detección de datos novedosos y abstención | Verificada para NAND y ruido del banco de pruebas |
| Planificación del siguiente experimento | Política XI limitada, todavía no exploración abierta |
| Autorregulación sostenida y metabolismo computacional | Parcial: presupuestos, transacciones y contadores, sin gestión autónoma de recursos |
| Causalidad en el mundo real y sensores propios | No demostrada |
| Invención abierta de gramáticas y metas | No demostrada |
| Autorreproducción, autoconstrucción o vida biológica | No implementada |

## Límites y falsificadores prioritarios

1. El repertorio de funciones de dos signos tiene tamaño muy pequeño:
   hasta una tabla clásica de cuatro entradas lo resolvería. No concluir
   creatividad abierta ni inteligencia general por aciertos perfectos.
2. Las etiquetas de examen conviven temporalmente en el mismo RVPC2
   que las hipótesis; XI fija predicciones antes de consultar feedback
   por inspección del programa, **no** por un aislamiento secreto
   resistente a ataques.
3. La fuente de observaciones es sintética; los dominios reales,
   señales ambiguas, nuevos sensores y efectos fuera de distribución
   no se han probado.
4. El contador de entrenamiento heredado de E006 todavía tiene
   límite de 250 generaciones. E008 resolvió el antiguo límite de
   255 *decisiones*, no todas las restricciones del sistema.
5. E008 elige qué estudiar, pero aún no diseña y ejecuta por sí solo
   una investigación física, un programa nuevo ni una arquitectura
   de aprendizaje nueva. El siguiente desarrollo debe conectar
   planes con experimentos auditables y medir ganancia informativa
   frente a preguntas seleccionadas al azar.
