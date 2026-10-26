# BBY Q E006 — Jurado XI: promoción, rechazo y conocimiento sellado

## Hipótesis y arquitectura

E005 demostró construcción de cuatro composiciones de signos, pero también
crecía con etiquetas aleatorias: **crecimiento no equivale a conocimiento útil**.

E006 añade un **Jurado de Validación** completamente escrito en XI. Hay una
sola autoridad persistente (REVERSE-PC / Inverse Ether Memory / RVPC2).
La representación candidata y las estadísticas de decisión son bytes del
mismo espacio; no existe motor de IA Python/C++, Transformer ni pesos de terceros.

Flujo:

1. `birth.xi`: firma nueva `66,81,6`, relaciones inicialmente ausentes.
2. `feed-xor.xi` o `feed-noise.xi`: mundo genera 200 consecuencias de
   entrenamiento por generación sobre magnitudes pares.
3. `learn.xi`: aprende en estado **sombra/no aprobado**. Construye
   composiciones después de errores, borra los datos ya consumidos y nunca
   conoce la fórmula de XOR.
4. `validate-feed-xor.xi` o `validate-feed-noise.xi`: un generador
   separado prepara **240 ejemplos nuevos de magnitudes impares**.
   Sus etiquetas residen temporalmente en el mismo archivo, sin acceso
   de la función que aprende.
5. `jury.xi`: para cada observación calcula ANTES de consultar su
   consecuencia dos predicciones: modelo con relaciones compuestas y
   modelo con esas relaciones ablatadas. Sólo después compara ambos
   aciertos con las etiquetas. Los pesos quedan inmutables en esta etapa.
6. Promoción si hay al menos una composición, si el modelo candidato
   acierta **205/240 o más** y supera por **30/240 o más** al modelo
   base sin composiciones. Si no, elimina descriptors, pesos de
   composición y evidencia espuria, dejando el resto de la identidad.
7. Juicio y eliminación de 240 etiquetas/observaciones se aplican en
   **una transacción XI**. Un fallo no publica un RVPC2 parcialmente modificado.
   La decisión sólo puede aplicarse una vez; `infer-grid.xi` usa
   las composiciones exclusivamente con flag de promoción activo.

El modelo aprobado se **sella**: `learn.xi` rechaza mutaciones cuando
`+31 == 1`. Esto conserva E006 sin deriva silenciosa; para aprender
otro contexto se necesita un futuro banco de sombra separado.

## Mapa lógico (base 7000000000000000000)

| Dirección relativa | Significado |
|---|---|
| +0..2 | Identidad BBY Q, esquema 6 |
| +3 | Perfil: permite o prohíbe crear relaciones |
| +16 | Generación de entrenamiento |
| +20 | Semilla |
| +30 | Descriptores compuestos presentes |
| +31 | Flag 0=sombra, 1=conocimiento aprobado y sellado |
| +32/+33 | Conteo acumulado de promociones/rechazos |
| +40/+41 | Generación autorizada del lote de entrenamiento/evaluación |
| +42/+43 | Tipo de mundo evaluador y último veredicto (1/2) |
| +64..66 | Hipótesis lineales base |
| +120..123 | Evidencia pendiente de crecimiento |
| +200..203 | Descriptores de composición |
| +220..223 | Pesos de composición |
| +10000..+12239 | Hasta 240 observaciones y etiquetas temporales |

Todo dato temporal vuelve al fondo Ether 0 después de consumir el lote.
No se crea un qubit por byte, no se activa entrelazamiento y no hay
dos bases de datos de conocimiento.

## Controles adversos

12 agentes (4 brazos por semilla, semillas 19/42/91). Cada brazo recibió
12 épocas × 200 experiencias = 2.400 experiencias; total **28.800
experiencias de entrenamiento**, más los 240 casos independientes por brazo.

| Semilla | XOR aprendido: candidato / ablatado | Veredicto | Ruido entrenado, ruido evaluado | Control lineal en XOR | XOR entrenado, ruido evaluado |
|---|---|---|---|---|---|
| 19 | 240/240 vs 106/240 | promover | 108/240, rechazar | 165/240, rechazar | 138/240, rechazar |
| 42 | 240/240 vs 133/240 | promover | 124/240, rechazar | 133/240, rechazar | 129/240, rechazar |
| 91 | 240/240 vs 119/240 | promover | 123/240, rechazar | 131/240, rechazar | 118/240, rechazar |

El modelo lineal no tiene descriptores y por ello no puede aprobarse.
El control adverso usa un mundo de validación distinto del entrenado,
para evitar que coincidencias de entrenamiento se publiquen como regla
general.

**CI verificó 12/12 decisiones** con
[GitHub Actions 40283557920](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40283557920);
tras cada decisión `audit-verdict.xi` comprobó la eliminación de
etiquetas en 240 direcciones. `infer-grid.xi` produjo la tabla de
predicciones sellada [0,1,1,0] en los tres modelos XOR aprobados;
los 9 controles quedaron sin promoción. Una segunda aplicación
del jurado y un intento de entrenar un modelo aprobado fueron
rechazados sin publicar archivos.

## Límites que quedan

- **No existe todavía memoria de múltiples contextos**; el sellado evita
  la deriva, pero también impide adaptar el mismo banco a un cambio
  de entorno. Próximo hito E007: archivo y recuperación reversible de
  hipótesis dentro del mismo RVPC2, por contraste de consecuencias
  observadas, sin etiquetas de contexto suministradas.
- El jurado decide por mejora del **conjunto** de cuatro relaciones,
  no mide aún qué descriptor individual se puede podar. Añadir
  ablación individual de manera independiente.
- La gramática de relaciones sigue fija a conjunciones de dos signos,
  sin evolución arbitraria del repertorio de operadores.
- La validación no es ciega criptográficamente: todo ocurre dentro de
  un RVPC2 y la separación consiste en código e instrucciones; el
  jurado lee consecuencia después de haber fijado las dos predicciones.
- 3 semillas y un entorno sintético no acreditan rendimiento en
  lenguaje natural, mundos externos, inteligencia general, conciencia
  ni ventaja cuántica.

**Lenguaje:** la lógica de agente E006 sólo está escrita en `.xi`,
dialecto de ejecución propio de REVERSE-PC. El futuro idioma fuente
canónico es MX; el compilador/intérprete usa por ahora un bootstrap C++
preexistente. No se añade C++/Python al sistema de aprendizaje.
