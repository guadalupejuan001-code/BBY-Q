# Autómata experimental de memoria cuántica en XI

El ciclo entrena puertas, valida, guarda checkpoints, prueba con datos nuevos y
se detiene al cumplir el criterio o agotar su presupuesto. Solo activa el
candidato si supera la prueba final. No modifica los agentes VQC3/QRL3,
QChat100, la conversación X10 ni la APK existente.

## Uso desde BBY Q

```sh
node bbyq.mjs quantum memory auto NUEVA_CAMPAÑA --runtime=REVERSE_PC
node bbyq.mjs quantum memory status NUEVA_CAMPAÑA
node bbyq.mjs quantum memory auto NUEVA_CAMPAÑA --runtime=REVERSE_PC --resume
node bbyq.mjs quantum memory demo NUEVA_CAMPAÑA --runtime=REVERSE_PC
```

El presupuesto predeterminado es ocho ciclos de diez actualizaciones por
modelo. `--max-cycles` y `--steps-per-cycle` permiten otro presupuesto finito.
La selección utiliza validación; los datos de prueba y las longitudes nuevas
se consultan después de detener el entrenamiento. Un fallo conserva el último
ciclo publicado; `--resume` exige idénticos parámetros, código y runtime. Una
solicitud ya completada devuelve sus resultados sin repetir el entrenamiento.
No es un proceso indefinido en segundo plano ni una tarea de calendario.

Para cargar el modelo experimental aceptado que acompaña al código:

```sh
node bbyq.mjs quantum memory prepare NUEVA_SESIÓN --runtime=REVERSE_PC
node bbyq.mjs quantum memory demo NUEVA_SESIÓN --runtime=REVERSE_PC
```

## Qué aprende

Son 1.000 cúbits simulados: 250 componentes de cuatro. Cada uno contiene una
memoria binaria, una entrada inicial, una corrección y un auxiliar de ruido.
No hay entrelazamiento global entre los 250 componentes y no se usa MPS.

Tres ángulos compartidos controlan el intercambio para escribir, corregir e
interactuar con distractores. El estado se inicializa una vez por secuencia,
no en cada entrada. La salida es fija: `(1 - <Z_memoria>)/2`. No hay pesos
entrenables en la salida. Los datos, etiquetas, puertas, pérdida y SGD están
implementados en XI; Python controla procesos, presupuestos y evidencias.
Se usan diferencias finitas centrales: el ángulo de ruido se repite y no
admite aplicar ingenuamente la regla de desplazamiento de una única puerta.

Cada episodio presenta 250 asociaciones binarias independientes en paralelo,
con correcciones opcionales y distractores. Los datos y etiquetas se generan
en XI. Las etiquetas solo se leen en el evaluador, nunca en el circuito de
consulta. El ensayo trabaja con símbolos binarios; no aprende lenguaje libre.

Las lecturas son esperanzas de Born analíticas, sin ruido de disparos. La
precisión se calcula con umbral 0,5; un 100 % de clases correctas no significa
probabilidad cuántica perfecta ni fidelidad 100 %. Las rotaciones y el
optimizador usan aritmética de punto flotante.

## Controles y alcance

Se compara con ángulos congelados, memoria borrada antes de consultar y un
modelo clásico recurrente entrenado con los mismos datos, tres parámetros y
salida fija. El control clásico tiene dos estados escalares por asociación;
no se presenta como una simulación analítica equivalente del circuito.

La barrera de ingeniería exige al menos 95 % de aciertos, una mejora de al
menos 15 puntos frente a los ángulos iniciales y como máximo 60 % al borrar la
memoria. Este criterio no acredita una ventaja frente a modelos clásicos.

La demostración guarda, cierra y recarga el proceso nativo entre enseñanza,
distractores, corrección y consulta. También borra los campos de datos y
etiquetas del caso consultado. Las consultas recuperan el estado cuántico;
no se reproduce el historial para reconstruirlo. Recordar nuevas entradas
cambia el estado; aprender los tres ángulos ocurre durante el entrenamiento.

Los resultados de tres semillas están en `release/evidence.json`. No se
afirman novedad científica, superioridad cuántica ni aprendizaje más rápido.
La comparación de tiempos es exploratoria en CPU compartida. El siguiente
paso hacia conversación necesita una representación de texto y tareas más
amplias, validadas por separado.
