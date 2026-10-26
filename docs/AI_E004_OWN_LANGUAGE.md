# BBY Q E004 — aprendizaje en lenguaje propio XI (provisional hacia MX)

## Regla de autoría

No hay código nuevo de entrenamiento en Python, C++, JS, bibliotecas neuronales o modelos ajenos.
Los tres programas de IA son **fuente XI ejecutable** que utiliza exclusivamente
las instrucciones del perfil programable de REVERSE-PC `#!reverse-pc-machine-v1`:
`set, mov, add, sub, mul, div, mod, cmp, label, j*, load8, store8, print`.

El **lenguaje canónico de la familia Mundo X es MX**. XI es el dialecto de
runtime que la especificación MX v1 identifica como temporal. Este experimento
no se presenta engañosamente como un programa compilado por el frontend `.mx`
actual: ese frontend sólo compone circuitos, todavía sin control de flujo ni
memoria condicional. El paso posterior es incorporar estas semánticas en MX
sin bifurcar su autoridad de lenguaje.

## Dependencias propias fijadas

- REVERSE-PC `feature/xi-programmable-machine-20261026`, commit
  `8e451dd6f2f9a24dc91d1a017252c204cac7fcff` (PR #16, aún sujeta a CI).
- REVERSE-PC mantiene Mundo X en
  `e2778d962af22f6f1a0794058dd4685fc2573966`.
- El runtime compilado de estas dependencias **todavía usa un bootstrap C++**.
  No se ha migrado la ejecución completa a MX autoalojado; afirmar que no
  hay C++ en el binario sería falso. **El entrenamiento y el modelo sí están
  programados exclusivamente en XI**, sin ruta oculta de aprendizaje nativa,
  librería externa ni pesos precargados.

## Una sola autoridad del agente

Los programas reciben y producen un único archivo **RVPC2**. La escritura
ocurre dentro de la transacción de `QuantumRuntime`; un error hace rollback.
Todos los pesos, identificador y generación se guardan como bytes
deterministas de Inverse Ether Memory, sin duplicados de estado.

| Coordenada lógica | Significado |
|---|---|
| `7000000000000000000..+2` | Firma `66,81,4` de BBY-Q-XI |
| `+16` | Época/generación duradera, 0..250 |
| `+64` | Relación `bias` |
| `+65` | Relación `signal` |
| `+66` | Relación `pressure` |
| `+67` | Relación `action` |

Pesos con signo `[-120,120]` codificados como `peso+128` en un byte.
Cada nueva ejecución de `learn.xi` retoma los pesos y número de época
anteriores, procesa **400 nuevas experiencias** de una secuencia
determinista distinta, y publica el siguiente estado. El operador aprende
de sus propios errores, no de un archivo de pesos descargado.

**No usar E003 sobre este estado.** La firma 4 separa el esquema XI de la
firma 3 de E003 (prototipo C++), y no hay conversión implícita entre ellos.

## Experimento reproducible

Los programas son:

1. `ai/xi/birth.xi`: rechaza nacimiento repetido; inicializa cuatro
   relaciones a cero y firma de estado; sin qubits automáticos.
2. `ai/xi/learn.xi`: entorno controlado genera pares de señales,
   acción y consecuencia; el agente predice **antes** de ver consecuencia.
   Sólo si se equivocó modifica las cuatro relaciones con pasos enteros.
   Las relaciones se guardan con la generación en una transacción atómica.
3. `ai/xi/holdout.xi`: 240 experiencias sobre señales `x` impares;
   entrenamiento utiliza `x` pares, garantizando disjunción. Mide
   aciertos del agente, baseline congelado (predicción constante 1) y
   control negativo XOR/paridad. Nunca ejecuta `store8`; rechaza
   la sesión si no supera el baseline o no alcanza 190/240.

La regla del mundo lineal es `3*x - 2*p + 25*a >= 0`, y se calcula **sólo
después de la predicción**, como devolución del entorno. El agente no
almacena sus coeficientes ni tiene acceso a ellos durante inferencia. El
modelo dispone de las cuatro relaciones: `bias + ws*(x/10) +
wp*(p/10) + wa*a`. La equivalencia es un problema controlado de
generalización por interpolación, **no** aprendizaje general ni conciencia.

La prueba negativa XOR usa la paridad de los signos de ambas señales;
la clase de hipótesis del agente no representa de modo general ese operador.

## Ejecutar con el runtime propio existente

En una instalación con REVERSE-PC fijado y compilado, estando en BBY Q:

```sh
reverse_pc init /tmp/bbyq-blank.rvp
reverse_pc run ai/xi/birth.xi /tmp/bbyq-blank.rvp /tmp/bbyq-born.rvp
reverse_pc run ai/xi/learn.xi /tmp/bbyq-born.rvp /tmp/bbyq-epoch1.rvp
reverse_pc run ai/xi/holdout.xi /tmp/bbyq-epoch1.rvp /tmp/bbyq-observed.rvp
reverse_pc run ai/xi/learn.xi /tmp/bbyq-epoch1.rvp /tmp/bbyq-epoch2.rvp
reverse_pc run ai/xi/holdout.xi /tmp/bbyq-epoch2.rvp /tmp/bbyq-observed2.rvp
```

En la salida del holdout se imprimen, en orden:
`r13` (aciertos aprendidos), `r15` (baseline), `r12` (XOR),
`r0` (240 casos). El workflow compara snapshots después de cada
evaluación para demostrar ausencia de modificaciones.

## Criterios científicos y límites

No convertir éxito de CI en afirmación de superioridad comercial ni cuántica.
El usuario ejecuta una IA simbólica ajustable en su lenguaje; el test
sintético es una evidencia limitada, con coeficientes conocidos para
el banco de pruebas. No hay 1000 qubits en el aprendizaje: éste usa
memoria lógica determinista, normalmente **0 qubits**.

Pendiente: seleccionar acciones por objetivo propio, interacción con datos
reales, detección de cambio de contexto y recuperación sin etiquetas,
construcción/retirada automática de relaciones, múltiples semillas,
competidores clásicos en condiciones idénticas, MX fuente auténtica y
bootstrap autónomo. Se reportarán resultados adversos si aparecen.
