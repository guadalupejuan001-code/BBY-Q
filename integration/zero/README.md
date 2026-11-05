# BBY Q 0

BBY Q 0 amplía la aplicación con un espacio de trabajo simbólico persistente.
Conserva E01/E02, los agentes cuánticos, las lecciones X10, el historial y la
identidad de instalación. El nombre nuevo no certifica inteligencia artificial
general: la edición implementa algoritmos simbólicos y una gramática definidos.

## Capacidades implementadas

- Hechos y reglas persistentes que se aplican a sujetos y relaciones nuevos.
- Reglas con una o dos premisas, tres variables y evidencia negativa explícita.
- Deducción hasta un punto fijo, con testigos de los hechos y reglas utilizados.
- Detección de contradicciones y aclaración de antecedentes ambiguos.
- Retirada/corrección de conocimiento y recálculo de sus consecuencias.
- Rutas por un grafo dirigido de nombres arbitrarios; ya no dependen de las siete
  posiciones de la misión E02. El planificador usa búsqueda en anchura en XI.
- Aritmética con paréntesis, precedencia, signos y división controlada en XI.
- Tareas con varios pasos y herramientas; un paso exitoso posterior no oculta
  una pregunta anterior sin resolver.
- Evaluación explícita, aprendizaje de fiabilidad y crédito de submisiones E02
  verificables dentro de la misma transacción.

Todos los algoritmos de inferencia, unificación, búsqueda, cálculo, resolución
de referencias y actualización de fiabilidad se ejecutan en el intérprete XI
propio. El generador de fuentes solo trabaja al construir; Java/Python codifican
palabras y registros, transportan datos, manejan almacenamiento o presentan
resultados. El perfil numérico usa XI directamente, pues RXE v1 no lo codifica.

La nueva capacidad de transferencia procede de variables y reglas reutilizables;
no se presenta como entrenamiento de un modelo fundacional. Los pesos E02
se conservan. Aprender hechos/reglas y recibir una evaluación son operaciones
explícitas; la evaluación no modifica la verdad de una prueba ni crea hechos.

## Cooperación con lo anterior

El motor recibe los campos `requiere` declarados en las lecciones X10 como
relaciones. Cada campo se conserva como un término; no se inventan dependencias
adicionales separando su texto. Las definiciones y consultas anteriores siguen
disponibles. `recupera CLAVE` obtiene un bit del estado real de QMemory y
`observa NOMBRE muestra SEMILLA` clasifica una muestra sintética de 1.000 valores
con VQC3. XI proyecta esos resultados como premisas temporales para las reglas.

`consulta TEXTO` llama a las capacidades existentes desde la misma tarea,
incluidos QChat100, los agentes y las misiones E02. La aplicación invoca los
especialistas cuando sus entradas corresponden a su entrenamiento. No convierte
un plan de grafo arbitrario en una supuesta decisión del actor E02 de siete
posiciones. Los objetivos simbólicos no requieren que todos los circuitos se
ejecuten sin una función aplicable.

Una evaluación positiva de una tarea padre puede acreditar sus submisiones E02
pendientes. Los objetivos de esas submisiones siguen siendo verificados por E02.
Una evaluación negativa no castiga indiscriminadamente a todos sus hijos. Los
comprobantes y los hashes impiden repetir aprendizaje o usar evidencia alterada.

## Uso en el chat

```text
recuerda que ana es humana
aprende regla: si $x es humana entonces $x es mortal
¿ana es mortal?
```

```text
resuelve:
nara tiene bobina
bobina requiere energia
si $x tiene $y y $y requiere $z entonces $x necesita $z
¿nara necesita energia?
calcula (17 + 25) * 3
```

Los hechos y reglas sin `recuerda`/`aprende` dentro de `resuelve:` son temporales.
Las preguntas `por que ana es mortal`, `quien es mortal?` y `que sabes de ana`
consultan la misma evidencia. Los nombres de varias palabras usan guion bajo.
La gramática no realiza una comprensión abierta de cualquier frase española.

```text
resuelve:
casa conecta parque
parque conecta biblioteca
biblioteca conecta trabajo
ruta desde casa hasta trabajo
```

```text
memoria guarda faro 1
resuelve:
recupera faro
observa senal muestra 1763814988
si faro es uno y senal es clase0 entonces proyecto es autorizado
¿proyecto es autorizado?
```

La observación anterior es sintética; no representa sensores del teléfono.
La etiqueta supervisada de la muestra no se utiliza como premisa de inferencia.

```text
recuerda que ana no es mortal
¿ana es mortal?
olvida regla: si $x es humana entonces $x es mortal
¿ana es mortal?
```

El conflicto se muestra hasta retirar/corregir una de sus fuentes. `corrige que`
reemplaza las versiones explícitas de ese hecho; no anula reglas de forma oculta.
`correcto`/`incorrecto` o «Evaluar última tarea» evalúan la tarea correspondiente.

## Pruebas y límites

El protocolo se registró en `118eb2ac` antes de implementar el motor. La primera
prueba reservada obtuvo 120/120. Tras ampliar el control de resultados comunes,
una comprobación detectó que se perdía el estado de error aritmético: se corrigió
y se reservaron nombres y grafos nuevos en `zero-reserved-common-outcomes-v2`.
La revisión completa obtuvo 120/120 en seis familias: cadenas, uniones de
relaciones, contradicciones, rutas, aritmética y tareas mixtas tras reiniciar.

Son pruebas generadas de composición dentro de la gramática, no un examen de
AGI ni una medida de conocimiento del mundo. Los circuitos cuánticos siguen
ejecutándose mediante simulación clásica y no se afirma ventaja cuántica.

La ventana actual admite 1.024 hechos de trabajo, 256 reglas y 128 términos por
paso, con hasta 64 pasos por solicitud. Los especialistas reciben su carga
completa aunque exceda la ventana de términos. La búsqueda tiene un presupuesto
explícito; agotarlo produce un resultado inconcluso, nunca un falso «no existe».
Las pruebas móviles comprueban el conjunto nuevo y todas las pruebas anteriores.

```sh
node integration/zero/build.mjs
python3 integration/zero/verify.py
python3 integration/zero/evaluate.py
```

Las pruebas reservadas publicadas ya fueron abiertas. Una evolución posterior
necesita nuevas tareas y evidencias para medir sus cambios.
