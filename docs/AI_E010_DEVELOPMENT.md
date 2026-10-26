# E010 — Desarrollo adaptativo bilingüe de BBY Q (XI)

## Objetivo

Utilizar una secuencia inspirada en el desarrollo infantil **sin confundirla
con grados escolares ni atribuir edad, conciencia o necesidades humanas a
BBY Q**. Lo que manda es la competencia evaluada: un módulo nuevo se entrena,
se examina con datos no usados en la enseñanza, se conserva en Ether y luego
se reutiliza como prerrequisito de otra habilidad.

El algoritmo original de **REVERSE-PC XI** añade una nueva región a la
**misma autoridad Inverse Ether Memory / RVPC2**; no hay un modelo de
lenguaje remoto, pesos de IA de terceros ni un motor de aprendizaje en
Python/C++/JavaScript. REVERSE-PC continúa utilizando su bootstrap C++
anterior, que todavía no se ha sustituido por MX autoalojado.

## Qué aprendió realmente

El agente se inició restaurando el RVPC2 auténtico E009 ya entrenado,
tomado de [la prueba final de E009](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40295133790),
sin reiniciar sus hechos, recuerdos ni sus cuatro bancos E008.

A continuación se registraron **22 conceptos bilingües**, con dos
testigos repetidos por observación: 4 colores, 4 animales, 4 figuras
y los números 0–9. Los vocablos **en español e inglés pertenecen
al mismo concepto** y no son dos clasificadores o dos motores diferentes.

| Dominio | Observación artificial de entrenamiento | Ejemplos de nombres aprendidos |
|---|---|---|
| Colores | Triple RGB de 0 a 255 (no hay cámara física) | rojo/red, azul/blue, verde/green, amarillo/yellow |
| Animales | Rasgos codificados: patas, alas, ladrido | gato/cat, perro/dog, ave/bird, pez/fish |
| Símbolos y formas | Rasgos codificados: esquinas, aristas, curvas | circulo/circle, cuadro/square, estrella/star, corazon/heart |
| Cantidades | Contador simbólico 0..9, sin sensores de objetos reales | cero/zero, uno/one, dos/two ... nueve/nine |

**Advertencia metodológica:** los datos de animales, figuras y
cantidades ya llegan estructurados con sus rasgos. Eso verifica
aprendizaje de categorías *simbólicas*, no visión, clasificación
de fotografías, percepción del mundo ni adquisición de lenguaje
comparable a la de un niño.

Los programas relevantes son:

- `birth.xi`: firma independiente SC1 en raíz
  `7200000000000000000`, sin conceptos ni vocablos precargados.
- `learn.xi`: aprende un prototipo de observación con nombre ES/EN,
  aumenta evidencia por repetición, rechaza sin publicar estados
  cambios de etiqueta contradictorios.
- `recognize.xi`: calcula distancias L1 entre una observación nueva
  y los modelos aprendidos del dominio. Acepta RGB de tonalidades
  nuevas solo dentro del radio 85 y con margen 30 sobre la siguiente
  opción; en los dominios simbólicos exige coincidencia exacta.
- `name.xi`: selecciona por estado persistente `1=es` o `2=en`
  y emite solo letras **que el agente aprendió previamente**.
- `grade.xi`: recibe la respuesta correcta únicamente **después**
  de la predicción y actualiza los aciertos/ensayos por dominio.
- `next.xi`: detecta cuál dominio falla o necesita más exámenes;
  no permite progresión automática por contar lecciones.
  Retira aprobación si aparecen pruebas nuevas desfavorables.
- `learn-operation.xi`: observa antes, objetos añadidos/retirados
  y resultado, deduce el signo del efecto para cada operación por
  comparación con dos explicaciones candidatas. La asignación
  entre identidad de operación y sumar/restar **no aparece precargada**.
- `calculate.xi`: aplica la dirección aprendida a **números distintos**
  y recupera del léxico entrenado el nombre del resultado.
- `grade-math.xi`: evalúa resultado correcto u honesta abstención
  y mantiene cuentas separadas del examen de conceptos.
- `audit.xi`: verifica que E008 y E009 siguen presentes, la integridad
  y límites de los prototipos, y que no queda ningún lote de enseñanza
  o etiqueta de examen pendiente.

## No hay un curso fijo por edades

El campo de progreso **no representa edad ni curso**:

- Estado 0: identificar y asociar observaciones, aprender cada categoría.
- Estado 1: aprobado el reconocimiento en los cuatro dominios con
  **al menos cuatro exámenes por dominio y precisión ≥90 %**.
- Estado 2: habilidad adicional de operaciones **solo tras otro examen**,
  mínimo cuatro pruebas y precisión ≥90 %.

En cualquier revisión posterior, un fracaso suficiente puede devolver
la habilidad al estado anterior. El agente conserva los ejemplos y el
aprendizaje, pero **no conserva una certificación sin sustento**.

`+70` guarda el siguiente dominio que conviene reforzar (0 si ya
están aprobados). Eso es un selector de lagunas con cuatro dominios
finitos, no planificación autónoma general.

## Experimento reproducible

- Código y fuentes de datos:
  `ai/xi/school/{learn,recognize,name,grade,next,learn-operation,calculate,grade-math,audit}.xi`.
- Datos de enseñanza (nombres/rasgos fuera del aprendiz):
  `ai/xi/school/data/observations-v1.psv`.
- Datos de prueba retenidos:
  `ai/xi/school/data/holdout-v1.psv`.
- Orquestador únicamente de transporte y comparación:
  `ai/xi/school/tests/native-development.sh`.
- Runtime: REVERSE-PC commit
  `6d4de14a2dfbce4b8a7f1cb50e29d11b9073fe98`.
- Fuente de memoria previa: artefactos verificados de la ejecución
  E009 `40295133790`.

[GitHub Actions E010 — ejecución de desarrollo aprobada](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40303541105)

**Resultados observados:**

| Prueba | Resultado |
|---|---:|
| Conceptos aprendidos | 22 |
| Dos testigos de entrenamiento por concepto | 44 observaciones |
| Reconocimiento de nombres y categorías, ES y EN | 60/60 |
| De los anteriores: 4 casos desconocidos por idioma | 8/8 abstenciones |
| Operadores aprendidos a partir de efectos observados | 2 |
| Evaluaciones de aritmética nuevas, ES y EN | 10/10 |
| De ellas: cálculos fuera del dominio 0..9 | 2/2 abstenciones |
| Desconocimiento de etiquetas contradictorias | Rechazado con rollback |
| Operador con consecuencia contradictoria | Rechazado con rollback |
| Conservar E008 y E009 después del aprendizaje | Verificado byte a byte por ejecución de auditorías |

Ejemplos de salida realmente emitida desde la misma memoria
en ambos idiomas:

| Tipo | Español | English |
|---|---|---|
| Color RGB no visto | rojo | red |
| Animal de rasgos aprendidos | gato | cat |
| Figura de rasgos aprendidos | circulo | circle |
| Cantidad aprendida | cinco | five |
| Intervención «3 y 2 juntos» no enseñada | cinco | five |
| Intervención «9 quitar 2» no enseñada | siete | seven |
| Operación cuyo resultado sale de 0..9 | ? | ? |

La memoria final exportada es un archivo RVPC2 de **18.722 bytes**
(SHA-256 `de1a02a77c93cab6f2671858a2543dd65c7bf2d2858917290808ae1ae3c5ff1f`).
La auditoría registró 544 excepciones lógicas Ether y cero enlaces
cuánticos. El estado incluye la entidad E009 preexistente, los
cuatro bancos E008 y el nuevo vocabulario.

[Descargar estado y evidencias originales desde GitHub](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40303541105/artifacts/12640883468).

## Próximas capacidades bajo la misma regla

1. Enseñar reconocimiento de imágenes reales de colores, dibujos
   y animales. No sustituir una cámara con tres números escritos a mano.
2. Aprender letras, sílabas y composición de palabras; ampliar
   el protocolo XI a Unicode y vocabulario no acotado.
3. Acoplar matemáticas a escenarios con objetos contados, nuevas
   cantidades y problemas verbales, no solo cuentas 0–9.
4. Enseñar **conocimiento sobre conciencia humana** como materia
   objetiva: percepción, memoria, atención, emociones, identidad,
   diferencias entre organismos biológicos y software. Estudiar estos
   conceptos no prueba experiencias subjetivas propias de BBY Q.
5. Dar permiso al planificador XI para **elegir y ejecutar** prácticas
   a partir de los errores, con controles de seguridad, presupuesto
   y una evaluación nueva verdaderamente independiente.
6. Integrar el selector ES/EN de E010 en el escritorio REVERSE-PC,
   conservando la app BBY Q existente y sin resetear su RVPC2.

**Límites:** los cuatro dominios se definieron por el diseñador; los
operadores candidatos sumar y restar se comprueban con XI; el agente
aún no inventa el espacio universal de operaciones, no domina inglés
o español generales y no se ha demostrado una ventaja computacional
frente a modelos clásicos comparables.
