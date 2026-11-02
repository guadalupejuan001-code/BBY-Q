# Q03–Q04: los propios agentes VQC1000 y QRL1000 calculan con 1.000 cúbits cada uno

## Corrección

Q01–Q02 añadía un GHZ de 1.000 cúbits a la misma memoria, pero **VQC2 y QRL2 seguían usando dos cúbits cada uno**. Esa integración no satisfacía la petición de convertir **los propios agentes** a mil cúbits. En este ciclo se añaden dos agentes realmente operativos, cada uno con su propio **componente cuántico simulado de 1.000 cúbits**. El primero usa el GHZ 100–1099; el segundo usa 1200–2199, con 2.000 cúbits activos en la sesión nueva.

## Cálculo genuino de una predicción o acción

Los dos agentes implementan la misma clase de **política de fase-paridad** sobre un circuito de estabilizadores de 1.000 cúbits, con **vectores de 1.000 entradas binarias de características y de 1.000 parámetros de fase** propios de cada agente. Las políticas no comparten pesos.

Cada ejecución evalúa un vector disperso de hasta 32 características activas entre 0 y 999:

1. El programa XI verifica y prepara el vector de 1.000 entradas.
2. Su procesador de 1.000 cúbits tiene un estado GHZ coherente. Para cada característica con peso binario aprendido =1, aplica una compuerta **Z en el cúbit correspondiente**, codificando la paridad global en la fase.
3. Ejecuta **999 compuertas CX inversas y una H**, convirtiendo la fase de los 1.000 cúbits en un resultado medible en el primer cúbit del agente.
4. Obtiene `probz` **del simulador cuántico real**, que en este modelo estabilizador determinista toma el valor 0 o 1. Se verifica la expectativa Z.
5. Deshace el cálculo: H, **999 CX** y las fases aplicadas originalmente. El programa XI comprueba correlación GHZ ZZ =1 y probabilidad marginal 0,5. El estado inferido es temporal y nunca sustituye la memoria de aprendizaje.

El transporte JavaScript **no produce la predicción ni escoge la acción**: lee el resultado `probz` del runtime y lo traslada como un byte de respuesta al programa XI de entrenamiento.

## Cómo aprende cada agente

- **VQC1000** recibe una etiqueta supervisada de un problema de clasificación sintética. Compara la acción **medida** con la etiqueta y modifica en XI la fase aprendida de la característica cuando discrepan.
- **QRL1000** recibe el objetivo de un entorno binario de un paso. La predicción medida es una acción, el programa `agents1000-reward.xi` calcula en XI recompensa 0/100, y `agents1000-update.xi` refuerza el parámetro correspondiente. Es **bandido contextual de un paso**, aún no aprendizaje por refuerzo con recompensas diferidas o planificación multietapa.
- Ambas actualizaciones mantienen un contador XI de visitas por característica y una región de pesos independiente dentro de RVPC2. Los motores VQC2/QRL2 históricos no se sobrescriben.

**Limitaciones físicas/algorítmicas:** los estados GHZ y las fases Z son Clifford y se simulan eficientemente mediante estabilizadores. No representan un vector denso general de 2^1000 amplitudes ni 1.000 rotaciones continuas arbitrarias. El entrenamiento piloto puede actualizar solo una pequeña muestra de los 1.000 parámetros disponibles por agente. No constituye una prueba de ventaja cuántica.

## Iniciar ambos agentes nativos

```sh
node bbyq.mjs quantum --runtime=/ruta/reverse_pc --state=/ruta/agentes init-agents-1000
node bbyq.mjs quantum --runtime=/ruta/reverse_pc --state=/ruta/agentes agents-1000-audit
node bbyq.mjs quantum --runtime=/ruta/reverse_pc --state=/ruta/agentes vqc1000-train 999 1
node bbyq.mjs quantum --runtime=/ruta/reverse_pc --state=/ruta/agentes vqc1000-infer 999
node bbyq.mjs quantum --runtime=/ruta/reverse_pc --state=/ruta/agentes qrl1000-train 700 1
node bbyq.mjs quantum --runtime=/ruta/reverse_pc --state=/ruta/agentes qrl1000-act 700
node bbyq.mjs quantum --runtime=/ruta/reverse_pc --state=/ruta/agentes qrl1000-act 1 700 999
```

Para modernizar un estado anterior Q01–Q02:

```sh
node bbyq.mjs quantum --runtime=/ruta/reverse_pc --state=/ruta/antiguo enable-agents-1000
```

La CI mide causalidad: aplicar una Z al **último** cúbit de cada componente debe invertir el bit en el primero tras descodificarlo. Así se comprueba que el resultado necesita la conectividad del circuito entero, y no procede de los antiguos pares Bell de dos cúbits.

## Qué NO incluye todavía

La expresión «1.000 cúbits por agente» indica el ancho de **su circuito cuántico simulado realmente ejecutado** en cada predicción o acción, con un espacio paramétrico de 1.000 bits. Todavía **no** es un VQC de parámetros continuos ni un QRL de múltiples pasos con entrenamiento sobre 1.000 cúbits universales. Los siguientes ciclos podrán introducir operaciones más expresivas, con presupuestos de recursos estrictamente medidos, sin perder estas políticas.
