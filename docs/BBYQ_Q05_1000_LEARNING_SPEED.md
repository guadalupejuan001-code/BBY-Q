# Q05 — Medir a qué velocidad aprenden VQC1000 y QRL1000 (XI)

Esta prueba responde a la solicitud del propietario de **medir el entrenamiento de los dos agentes cuánticos a 1.000 cúbits cada uno**, no un registro GHZ independiente. Usa las políticas existentes `agents1000-infer.xi`, `agents1000-reward.xi` y `agents1000-update.xi`.

## Qué se mide

En una sesión RVPC2 nueva con **2.000 cúbits simulados**, VQC1000 y QRL1000 reciben, cada uno, un conjunto de N características distintas entre 0..999, con etiquetas binarias equilibradas 50/50, asignadas en orden pseudoaleatorio de semilla publicada. Las etiquetas son arbitrarias y no contienen reglas generalizables entre características individuales.

Cada episodio llama a la ruta de entrenamiento real:

1. XI crea la entrada de 1.000 dimensiones.
2. XI ejecuta el circuito GHZ de **1.000 cúbits del agente** y calcula una probabilidad de Born.
3. XI obtiene la recompensa del entorno de un paso y modifica el bit de fase correspondiente si hay error.
4. Se guarda RVPC2, y el banco experimental mide tiempo real total por actualización, mediana, percentil 95 y tasa de ejemplos por segundo.

Se repite la evaluación en hitos 0, 8, 16, 32, 64, 128, etc. sobre un grupo fijo de posiciones entrenables y otro de posiciones reservadas. Al final se prueba una colección de **24 combinaciones de 2–5 características conocidas** que jamás se presentaron como combinaciones durante el entrenamiento.

## Interpretación

El entrenamiento de un solo ejemplo puede cambiar un parámetro binario de 0 a 1 y corregir directamente la etiqueta. **Es aprendizaje de una tabla/paridad binaria**, no equivalente al aprendizaje abierto de una red variacional cuántica universal. Si alcanza 100% en ejemplos ya vistos, eso prueba una actualización de parámetros, no inteligencia general.

En las características reservadas, las etiquetas se asignan **independientemente y sin información predictiva**. No sería científicamente válido exigir generalización superior al azar. En cambio, las combinaciones nuevas de características conocidas sí comprueban la composición de paridades: un modelo clásico de XOR puede hacer lo mismo.

La recompensa de QRL1000 pertenece a un **bandido contextual de un paso** y no representa todavía una secuencia de decisiones con crédito temporal. No se usa hardware cuántico ni se demuestra superioridad computacional sobre aprendizaje clásico; el circuito es Clifford y la simulación de estabilizadores es eficiente.

Los tiempos incluyen las invocaciones del intérprete XI, las mediciones del simulador, el transporte JavaScript y la persistencia RVPC2, sin atribuir cada milisegundo exclusivamente al aprendizaje cuántico.

## Repetición

```sh
node integration/qml_qrl/tests/agents1000-learning-speed.mjs /ruta/reverse_pc /ruta/nueva-evidencia 128
```

Se producen `summary.json`, `results.json` con series de épocas y muestras, y una copia del checkpoint `agents/memory.rvp`.

GitHub Actions ejecuta dos pruebas independientes, con **128 y 800 episodios por agente**; el ejecutor local permite escoger un número par entre 16 y 1.000. El máximo teórico de 1.000 parámetros por agente no obliga a entrenarlos todos; en pruebas con características no vistas se mantiene una muestra separada hasta completar todo el espacio.

El diseño experimental preserva modelos previos VQC2/QRL2 y solo modifica la nueva sesión de laboratorio.

## Interpretación de los dos tamaños de entrenamiento

El ensayo corto mide la velocidad del aprendizaje inicial. El ensayo de 800 episodios entrena el 80 % de los 1.000 parámetros binarios de cada motor y reserva 200 dimensiones sin entrenamiento. Se publican mediciones de rendimiento individuales para ambos tamaños, sin extrapolar linealmente un resultado al otro. La CI no entrena una política variacional continua de 1.000 cúbits.
