# Comprobación numérica auxiliar de los circuitos VQC3/QRL3

**La comparación entre agentes completos está pendiente.** Este adaptador
qsim no ejecuta episodios QRL, actualizaciones de política, campañas de
entrenamiento, planificación ni persistencia recuperable. Los tiempos de
este experimento no miden aprendizaje y no determinan qué sistema completo
es más rápido. Su cobertura se detalla en
[PRIOR_ART.md](../../docs/evidence/quantum3/PRIOR_ART.md).

Este experimento compara el mismo circuito de 1.000 cables, las mismas entradas,
ángulos y pesos, en una CPU con afinidad a un núcleo. Compara XI/REVERSE-PC con
el núcleo público qsim Basic en precisión binaria64. No modifica los agentes.

qsim representa normalmente un statevector completo. El adaptador de esta
carpeta explota **la misma factorización exacta del circuito del proyecto**:
250 estados independientes de cuatro cúbits por agente. Mantiene ambos registros
asignados y evalúa todos los bloques del agente seleccionado. Es código nuevo
de referencia: no documenta un agente QRL histórico de 1.000 cúbits de qsim.

Dependencias fijadas:

- qsim: `50cac4b3fa331450b70387735479a00e223b8d25`,
  [repositorio y licencia Apache-2.0](https://github.com/quantumlib/qsim).
- REVERSE-PC: `59ac79386bc427620a10227489eb7f7be12c55c7`.
- Mundo X/Ether: `e2778d962af22f6f1a0794058dd4685fc2573966`.

```sh
bash REVERSE-PC/scripts/build-xi-session.sh mundo-X REVERSE-PC/build
python3 BBY-Q/benchmarks/quantum3-reference/run.py --runtime REVERSE-PC --mundo-x mundo-X --qsim qsim --checkpoint modelo-entregado.rvp --output resultados
```

Sin `--checkpoint`, se usan parámetros no nulos reproducibles para la CI.
Con ese argumento, se copian los parámetros del modelo únicamente a sesiones
de prueba; se comprueba el hash del archivo original antes y después.

El orden es qsim/XI/XI/qsim. Se guardan los tiempos individuales, las entradas,
todos los observables, los cuatro gradientes seleccionados y la comprobación
de una actualización SGD de VQC contra el cálculo externo. El aprendizaje del
producto sigue escrito en XI; el cálculo SGD C++ es exclusivamente un oráculo.
Se exige un error absoluto inferior a 1e-10 y uso efectivo de 1.000 cúbits.

Los tiempos miden el forward del modelo congelado. La preparación de entradas
se excluye de ambos cronómetros nativos; el tiempo de transporte de XI se
conserva por separado. El adaptador qsim está compilado en C++ y XI ejecuta
instrucciones de una máquina genérica con almacenamiento Ether. La comparación
muestra el coste de esas rutas concretas, no el de entrenar Super Mario ni una
ventaja del lenguaje C++ para cualquier aplicación.

La memoria principal es **VmHWM de Linux del ejecutable después de exec**,
excluyendo el orquestador Python para ambos. Para XI se compila una envoltura
que incluye su fuente fijada sin cambios y adapta únicamente el informe RSS
de `getrusage`; sus tiempos CPU permanecen intactos. Se evita así arrastrar
el máximo de memoria previo a exec del hijo de Python. La CI valida exactitud
y ejecución, sin imponer un resultado de velocidad o memoria dependiente del hardware.
