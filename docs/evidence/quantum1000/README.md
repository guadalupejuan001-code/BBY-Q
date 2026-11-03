# VQC3 / QRL3: 1.000 cúbits conectados por agente

[Resultados, curvas y tiempos reales](RESULTS.md) · [Checkpoints y hashes](CHECKPOINTS.json).
El modelo combinado utiliza CZ y conserva 1.000 episodios nuevos por agente.

Esta revisión elimina la separación fija de los agentes anteriores en grupos
de cuatro. Cada agente prepara **un registro de 1.000 cúbits** y aplica CZ
a los 999 pares de vecinos de una cadena. Los cruces 3→4, 7→8, 499→500 y todos
los demás límites anteriores ahora forman parte del mismo circuito.
También se conserva la variante conectada con CNOT, seleccionable mediante
`--entangler cnot`; la variante por defecto utiliza CZ.

El circuito, los observables, las pérdidas y las actualizaciones están escritos
en XI en [`ai/xi/quantum1000`](../../../ai/xi/quantum1000). REVERSE-PC incorpora
una representación MPS en QuantumRuntime/InfiniteCore; no se utiliza qsim.
Cada forward ejecuta 2.000 RY, 999 CZ/CNOT y 2.000 observaciones X/Z. Las 1.000
mediciones Z influyen en la salida y las 1.000 X permiten calcular todos los
gradientes de ángulos, mediante la identidad exacta `d<Z>/dθ = -<X>` para la
última RY de cada sitio. Se entrenan los 1.000 ángulos por paso, además de los
1.000 pesos y el sesgo de salida. El recorte del logit anula sus gradientes en
la región saturada.

## Representación y límites

Los tensores del MPS están conectados y representan un único estado de 1.000
cúbits. La dimensión virtual dos del circuito probado describe los enlaces
de la representación, **no grupos de dos ni de cuatro cúbits independientes**.
No se truncan enlaces ni se descartan coeficientes. El error numérico procede
de la aritmética binaria64.

La eficiencia depende de la profundidad y del entrelazamiento del circuito.
El backend actual permite hasta 64 valores por enlace y falla si se agota ese
presupuesto; nunca reduce el número de cúbits para continuar. El circuito
validado es una cadena con una pasada de CZ/CNOT y rotaciones locales, no un
circuito arbitrario de profundidad ilimitada. Esto no demuestra ventaja
cuántica, capacidad general de `2^1000` ni hardware cuántico físico.

En la capa CZ, cada observación local depende del sitio y sus vecinos: el
agente combina las 1.000 observaciones, pero no se afirma que cada medición
individual tenga una dependencia causal de los 1.000 datos. El estado sí
presenta entrelazamiento en los 999 cortes, sin particiones independientes.
La variante CNOT permite además propagar la influencia de una entrada del
primer sitio hasta una observación del último; esa prueba se identifica como
CNOT en el informe de validación.

Las tareas de prueba lineal y navegación conservan cuatro variables latentes
codificadas en los 1.000 sitios. Esa dimensión de entrada del problema no es
un límite de cuatro cúbits. El clasificador también admite 1.000 valores de
entrada mediante la interfaz externa.

## Validación y conservación

La validación ejecuta ambos agentes con el intérprete XI real. Comprueba la
conectividad, los 999 cortes entrelazados de cada registro, la influencia del
primer cúbit sobre una medición del último en modo CNOT y derivadas del score completo,
incluidas posiciones que antes pertenecían a grupos diferentes. Guarda y
restaura tanto el estado entrelazado como el entrenamiento. Doce episodios
reales ya bastan para comprobar que los 1.000 ángulos y los 1.000 pesos cambian
en cada agente; esto es una comprobación de participación, no un umbral de
precisión o éxito.

El código histórico en `ai/xi/quantum3` y todos sus checkpoints se conservan.
Los nuevos programas utilizan el identificador de modelo 174; los históricos
usaban 173. Un checkpoint antiguo requiere migración explícita. La migración
conserva ángulos, pesos y sesgos, guarda los contadores históricos en un informe
y empieza los contadores de entrenamiento de la nueva topología en cero.
Conservar coeficientes no garantiza conservar su rendimiento en otro circuito.

## Ejecución reproducible

REVERSE-PC: [`4e201ec515da268612ab9e06eba090988814fda6`](https://github.com/guadalupejuan001-code/REVERSE-PC/commit/4e201ec515da268612ab9e06eba090988814fda6).
Ether/Mundo X: `e2778d962af22f6f1a0794058dd4685fc2573966`.

```sh
bash REVERSE-PC/scripts/build-xi-session.sh mundo-X REVERSE-PC/build
python BBY-Q/integration/quantum1000/validate.py --runtime REVERSE-PC --output validation-connected
python BBY-Q/integration/quantum1000/campaign.py --runtime REVERSE-PC --agent vqc --task linear --episodes 1000 --eval-size 32 --seed 173 --step-budget 10000000 --output vqc-connected
python BBY-Q/integration/quantum1000/campaign.py --runtime REVERSE-PC --agent qrl --task line_easy --episodes 1000 --eval-size 32 --seed 173 --step-budget 10000000 --output qrl-connected
python BBY-Q/integration/quantum1000/cli.py --runtime REVERSE-PC --state modelo-conectado.rvp info
```

La evaluación final usa una semilla nueva después de seleccionar la
arquitectura, con 64 casos IID y 64 OOD. Se reproduce mediante
`integration/quantum1000/evaluate.py --runtime REVERSE-PC --trained FINAL.rvp --initial INICIAL.rvp --agent qrl --task line_easy --samples 64 --seed 20261103 --output evaluacion-nueva.json`.
Para el clasificador, cambiar a `--agent vqc --task linear`.

Para conservar los coeficientes de un modelo histórico en una copia conectada:

```sh
python BBY-Q/integration/quantum1000/migrate.py --runtime REVERSE-PC --input modelo-anterior.rvp --output modelo-migrado.rvp --report migracion.json
```

Los comandos rechazan rutas de salida que ya existen. Los checkpoints de
campaña, diarios y manifiestos se guardan antes de continuar. La separación
entre semillas de entrenamiento y evaluación se comprueba explícitamente.
La CI ejecuta 100 episodios de cada agente y publica sus checkpoints y pruebas;
no impone una precisión mínima que oculte resultados de aprendizaje negativos.
