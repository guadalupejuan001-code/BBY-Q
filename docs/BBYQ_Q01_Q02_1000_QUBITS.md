# BBY Q Q01–Q02 — 1.000 cúbits reales del simulador XI/Ether

## Por qué antes mencionamos 4–8 cúbits

Los ciclos de entrenamiento **VQC2 y QRL2** utilizan actualmente un circuito de dos cúbits (pares Bell) y una pequeña tabla Q/optimización discreta. La propuesta de iniciar VQC3 con tres o cuatro cúbits y avanzar a 4–8 era una **estrategia prudente de entrenamiento**, no el límite máximo del intérprete XI/Ether.

El REVERSE-PC original distingue capacidad de *registro de estabilizadores* y capacidad para **circuitos universales no Clifford**. Según los contratos originales, admite 4.096 cúbits activos por runtime y componentes de hasta 1.024 cúbits; las operaciones densas y los estados no Clifford complejos tienen límites mucho menores. No existe aquí un vector denso genérico de 2^1000 amplitudes.

## Lo que se implementó

- `q1000-birth.xi` crea en **XI** un registro **GHZ de 1.000 cúbits entrelazados**, direcciones `100..1099`. Usa una H y 999 CX, representación **Clifford/estabilizadores**. No usa un multiplicador de amplitudes denso.
- Los cúbits `2,3` y `4,5` de VQC2 y QRL2 permanecen independientes del registro GHZ. Esto produce hasta **1.004 cúbits activos** cuando ambos agentes consultan sus circuitos. Se refiere a un componente GHZ de 1.000, no a que VQC2 y QRL2 entrenen cada uno una política de 1.000 cúbits.
- `q1000-audit.xi` verifica huella, correlación Z del primer/último cúbit, correlación Z del primero/intermedio, correlación X de extremos esperada 0 y probabilidades Z=1 de 0,5 en extremos. El host verifica además `active_qubits` y `largest_component=1000`.
- `q1000-overflow.xi` prueba que extender el mismo componente desde 1.000 hasta 1.025 cúbits se rechaza de manera atómica, conforme al límite de 1.024. El checkpoint original no se reemplaza.
- `q1000-uncompute.xi` deshace H/CX en estado de **prueba desechable**, comprueba que las probabilidades de 1 regresan a 0 y no modifica el RVPC2 almacenado.
- `enable-1000` permite anexar el registro a una sesión previa de VQC2/QRL2, tras verificar que solo se emplearon sus cuatro cúbits reservados y que no existe ya un registro GHZ. Guarda por reemplazo atómico cuando todas las validaciones concluyen.
- `init-1000` inicializa de cero una sesión de laboratorio VQC2/QRL2 más el GHZ-1000. `audit-1000` comprueba un estado ya existente sin cambiarlo.

## Uso desde la raíz de BBY Q

```sh
# Crear laboratorio con componente GHZ de 1000 qubits
node bbyq.mjs quantum --runtime=/ruta/reverse_pc --state=/ruta/quantum-1000 init-1000

# Auditar la correlación nativa
node bbyq.mjs quantum --runtime=/ruta/reverse_pc --state=/ruta/quantum-1000 audit-1000

# Entrenar VQC2/QRL2 en esa misma memoria aislada
node bbyq.mjs quantum --runtime=/ruta/reverse_pc --state=/ruta/quantum-1000 train-xor
node bbyq.mjs quantum --runtime=/ruta/reverse_pc --state=/ruta/quantum-1000 train-agent
node bbyq.mjs quantum --runtime=/ruta/reverse_pc --state=/ruta/quantum-1000 classify 0 1
node bbyq.mjs quantum --runtime=/ruta/reverse_pc --state=/ruta/quantum-1000 plan 1 0

# O anexarlo a una sesión de laboratorio VQC2/QRL2 previa
node bbyq.mjs quantum --runtime=/ruta/reverse_pc --state=/ruta/quantum-anterior enable-1000
```

El workflow publica además dos estados RVPC2 de ejemplo: una sesión con VQC2 y QRL2 ya entrenados más el componente GHZ de 1.000 cúbits, y otra sesión GHZ recién inicializada con VQC2/QRL2 aún sin entrenar.

Las consultas y los fallos no deben alterar la huella original. El entrenamiento normal sí modifica la parte Ether de parámetros VQC2/QRL2.

## Próximos pasos Q03–Q04

1. Diseñar VQC3 con compuertas parametrizadas, calcular la factibilidad por tipo de circuito y separar *anchura lógica* del *número de cúbits activos en el aprendizaje*.
2. Desarrollar QRL3 con más estados y recompensas observadas; conectar mediciones verificables con las actualizaciones en XI, sin fingir que las tablas Q clásicas son una política cuántica entrenable.
3. Medir dispersión de costes, semillas, memoria, tiempo y generalización; comparar con métodos clásicos equivalentes.

**Veredicto técnico:** alcanzar un GHZ de 1.000 cúbits simulados NO demuestra que un agente variacional universal de 1.000 cúbits sea eficiente o que exista ventaja cuántica. Solo demuestra las operaciones del circuito concretamente ensayado, si la CI concluye satisfactoriamente.
