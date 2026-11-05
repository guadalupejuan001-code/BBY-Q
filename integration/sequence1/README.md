# C1: codificador secuencial experimental

C1 corrige la pérdida de información anterior al circuito QChat. Conserva el
UTF-8 original y entrega cuadros ordenados con identificadores exactos. Los
modelos E01/E02/Zero y el generador activo de la app permanecen intactos.

**Estado: experimento guardado; no aprobado para sustituir el generador.**

## Representación

Cada palabra nueva obtiene un identificador distinto. Las claves del diccionario
usan NFC y minúsculas; conservan tildes y ñ. La versión original del texto y sus
posiciones en bytes se conservan aparte, por lo que las equivalencias de
mayúsculas o composición Unicode no destruyen el texto original.

El mismo registro Clifford simulado de 100 cúbits se reutiliza por cuadro:

| Campo | Bits |
| --- | ---: |
| Palabra | 20 |
| Palabra anterior | 20 |
| Posición | 16 |
| Sección | 2 |
| Último token de salida | 7 |
| Penúltimo token de salida | 7 |
| Posición de salida | 6 |
| Longitud UTF-8 del token | 16 |
| Reserva | 6 |

XI comprueba que las mediciones recuperan todos los campos y obtiene claves
enteras sin hash para palabras, pares ordenados, posición y prefijo de salida.
El almacenamiento original permite reconstruir el texto; las características
del lector no pretenden preservar espacios o mayúsculas por sí solas.

Los límites son 256 tokens de entrada, 64 de contexto, 64 de salida y 16384 bytes
por texto. Se rechazan excesos explícitamente. El diccionario tiene 2^20 plazas;
debe guardarse junto al checkpoint si se añade aprendizaje personal.

## Entrenamiento y resultado

Las predicciones y el SGD de los dos lectores se ejecutan en XI. Python prepara
ejemplos, transporta bytes y calcula métricas. El circuito Clifford es fijo; el
aprendizaje está en el lector clásico. No se demuestra ventaja cuántica ni AGI.

El ciclo válido final usa `protocol-cycle3.json`. Se ejecutaron 20 épocas de cada
lector: 83400 actualizaciones de texto y 13140 de intención. La selección
prioriza la capacidad más débil de validación y conserva la época 10 de ambos.

| Capacidad de validación | Correctas | Total |
| --- | ---: | ---: |
| Respuestas conocidas | 60 | 67 |
| Uso del contexto | 20 | 20 |
| Rechazo de temas desconocidos | 16 | 16 |
| Negación | 18 | 20 |
| Contrastes de orden | 8 | 18 |
| Texto completo | 122 | 141 |
| Clasificación de intención | 156 | 169 |

La media de intención (92,3 %) oculta fallos: consultas de nombres y rutas
obtuvieron 0/1, y aritmética 4/12. Esas muestras pequeñas tampoco permiten
afirmar una capacidad estable. Se conserva la exigencia de superar el 90 % en
cada grupo; no se promueve el modelo por su promedio.

Los controles nativos en los 18 contrastes de validación dieron 8/18 completos,
5/18 al retirar pares/posiciones y 0/18 al borrar las características medidas.
Esto comprueba dependencia del lector respecto a esas características; no
atribuye una ventaja al circuito sobre una implementación clásica equivalente.

El vocabulario de salida sigue siendo pequeño (80 tokens). Conservar un nombre
nuevo en la entrada todavía no permite generarlo o guardarlo como un hecho.
El adaptador de herramientas y la evaluación final de 200 tareas quedan
pendientes; esa evaluación final no se abrió ni se ejecutó en esta fase.

## Verificación

```bash
python3 integration/sequence1/verify_curriculum.py
python3 integration/sequence1/verify_codec.py
python3 integration/sequence1/verify_experiment.py
```

La primera prueba rechaza etiquetas contradictorias, ejemplos de orden mal
formados y solapamientos entre particiones. La segunda ejecuta 2048 cuadros,
200 pares de contraste, límites, caché y 400 actualizaciones de aprendizaje con
reapertura. La tercera verifica las identidades del modelo/diccionario/fuente,
las condiciones de promoción y 15 predicciones nativas tras recargar los bancos.

Android añade cuatro pruebas: 128 casos de paridad Python/Java/XI, 64 cuadros
completos, aprendizaje/reapertura de palabras antes confundidas y límites con
tildes. Las pruebas originales siguen ejecutándose.

## Ejecutar el experimento

Con REVERSE-PC compilado y las dependencias fijadas del proyecto:

```bash
python3 integration/sequence1/cli.py 'no definas memoria'
python3 integration/sequence1/cli.py 'repítelo' --previous 'define para mí memoria'
python3 integration/sequence1/cli.py 'Recuerda que mi nave se llama Neral.' --head intent
```

El tercer comando clasifica una intención; no ejecuta la enseñanza de un hecho.
Los checkpoints comprimidos se guardan en partes verificadas, reconstruidas por
`artifacts.py`. `model-binding.json` impide mezclar otra fuente o diccionario.

Para reproducir el entrenamiento final en un directorio nuevo:

```bash
python3 integration/sequence1/train.py build/sequence1/reproduction --protocol integration/sequence1/protocol-cycle3.json
```

## Siguiente etapa

1. Mejorar la lectura de posición y alcance de negaciones; debe resolver los
   contrastes sin depender del tema presente al final de la frase.
2. Equilibrar el muestreo del SGD por intención sin duplicar las cachés; ampliar
   la validación de las familias que hoy tienen una sola formulación.
3. Conectar argumentos exactos con las herramientas XI existentes, con una
   transacción y una prueba verificable por tarea completa.
4. Congelar candidatos que superen todos los grupos y ejecutar después las
   200 tareas nuevas. Una etiqueta de intención correcta no cuenta como tarea
   resuelta.

Los ciclos preliminares A/B se descartaron como evidencia de orden: un error de
preparación incluía una tupla con la respuesta del segundo tema. También se
corrigió la agrupación de intención, que debía usar la etiqueta esperada. Esos
errores no se trasladaron al ciclo C ni modificaron los modelos de la app.
