# BBY Q X05 — P09 y P10

Este incremento parte de **X04**. Añade generación y reparación acotadas de programas XI y conecta peticiones explícitas con ejecución nativa y comprobación. **P07 y P08 permanecen pendientes**.

La interpretación, elección del algoritmo, emisión del código, diagnóstico y veredicto se ejecutan en XI. Node construye las fuentes offline, transporta bytes, fija identidades SHA256, llama al runtime y administra archivos temporales. No se añadió C++, Python de inferencia, Java de aplicación, pesos de otros modelos ni respuestas de enseñanza.

## P09: programación probada

```text
Escribe en XI un programa que sume 8 y 13.
Escribe en XI un programa que multiplique -17 por 9.
Escribe en XI un programa que sume los enteros de 3 a 17.
Escribe en XI un programa que calcule el factorial de 7.
Escribe en XI un programa que calcule el máximo común divisor de 84 y 30.
Escribe en XI un programa que ordene la lista 8, -2, 5, 8, 0.
Escribe en XI una prueba que detecte una división entre cero.
```

No se devuelve únicamente el resultado precalculado. Se emiten fuentes XI ejecutables: operaciones, bucles de suma y factorial, Euclides para MCD, ordenación por intercambios sobre memoria temporal y una rama que detecta el divisor cero. Las fuentes se compilan a RXE y se ejecutan sobre un RVPC2 aislado.

La salida de la cápsula para un borrador es un JSON con `language`, `status`, `source` y `repair`. Los saltos del código están escapados dentro de la cadena JSON para respetar el adaptador RXE existente. El coordinador exporta un `program.xi` con saltos reales. Así se conserva el contrato actual de texto: **no se modificó P12**.

Gramáticas de operaciones: `sume A y B`, `reste A y B`, `multiplique A por B`, `divida A entre B`, `calcule el resto de A entre B`. Los operandos son enteros escritos en cifras, con valor absoluto máximo 1.000.000. La división entera trunca hacia cero, y el resto conserva la semántica del runtime XI. La división y el resto por cero se rechazan antes de generar código.

Las otras familias admiten:

- Suma de enteros de `A a B`, con `A <= B` y hasta 1.000 términos.
- Factorial de un entero de cero a doce.
- MCD de dos enteros, excepto `(0,0)`; el resultado es no negativo.
- Listas de uno a dieciséis enteros, entre −32.768 y 32.767; se conservan los repetidos.
- Una prueba de divisor cero con un salto condicional que evita ejecutar la división inválida.

Los prefijos alternativos son `Genera en XI un programa que ...` y `Crea un programa que ...`. La generación sola prepara un borrador y no ejecuta una herramienta.

## Diagnóstico y reparación

```text
Corrige en XI para sumar 18 y 29: set r0 18; sub r0 29; print r0; halt
Corrige en XI para multiplicar 17 por 6: set r0 17; mul r0 6; print r2; halt
Detecta el error: set r0 3; add r0 4; resultado esperado 8.
```

La reparación interpreta un programa aritmético canónico con `set`, operación, `print` y `halt`, separado por punto y coma. Admite una operación incorrecta, registro de destino incorrecto, registro inicial incorrecto, registro de impresión incorrecto, impresión ausente o segundo operando sustituido por cero. Usa registros `r0..r3`. Se rechazan varias faltas simultáneas, operandos iniciales distintos de los declarados, instrucciones adicionales y estructuras fuera de esa gramática.

Se reutiliza el diagnóstico original `qd/diagnose.xi`: se cambian sus direcciones temporales, etiquetas y salida para enlazarlo; sus decisiones no se sustituyen por JavaScript. Para operandos no negativos de cero a noventa y nueve se reutiliza el emisor original `qd/compose.xi`. Se comprobó igualdad byte por byte con la fuente producida por ese emisor original en las cinco operaciones.

En el ejemplo del resultado esperado ocho, el análisis devuelve siete y señala que deben revisarse tanto el código como la expectativa. No inventa un arreglo para hacer coincidir una expectativa equivocada. Ese análisis estático se identifica como tal. La reparación prepara código corregido; para acreditar su ejecución se requiere el ciclo nativo posterior.

No se implementó edición general de proyectos, interpretación libre de cualquier código XI, creación arbitraria de funciones, reparación de múltiples errores ni aprendizaje autónomo de algoritmos nuevos.

## P10: petición, autorización, ejecución y observación

Para generar y ejecutar en un mismo pedido:

```text
Crea y ejecuta un programa en XI que multiplique 12 por 7.
Crea y ejecuta un programa en XI que ordene la lista 9, 2, -4, 2.
```

Para un programa ya preparado: `Ejecuta y verifica el programa XI.`

El flujo es: BBY Q interpreta la solicitud en XI; los roles originales `qdu-plan.xi` y `qdu-dispatch.xi` autorizan un envío de un solo uso; el anfitrión compila el código emitido y ejecuta el RXE en una memoria temporal; w4U compara las salidas observadas con la especificación; BBY Q entrega el resultado del veredicto nativo.

La revisión usa la fórmula de suma de progresión para el programa que suma con bucle; MCD binario para el programa que usa Euclides; y orden más multiplicidades para la lista que se ordena por intercambios. Se comprueba identidad de la tarea, intento, SHA256 completo, estado de ejecución, cantidad y representación de salidas. Una bandera de éxito del anfitrión por sí sola no produce un veredicto positivo.

Las nuevas peticiones del escritorio incluyen:

```text
Abre la calculadora.
Por favor, abre la calculadora.
Quiero abrir la calculadora.
Necesito que abras la calculadora.
Pon la calculadora a pantalla completa.
Por favor, abre el explorador de archivos.
Muéstrame el explorador de archivos.
Quiero ver mis archivos.
Organiza las ventanas abiertas.
Por favor, ejecuta el programa 1.
Quiero ejecutar el programa 7.
```

También se admiten `minimiza`, `restaura` y `cierra la calculadora`. Los programas se identifican por los números uno a dieciséis del catálogo observado. La petición se convierte en un objetivo tipado del **W4u existente**; ese motor conserva las comprobaciones de conexión, capacidades, presencia y ambigüedad de ventanas, planes de hasta dos pasos y confirmaciones observadas.

Se exige coincidencia completa de las formas admitidas. Negaciones, citas, órdenes adicionales, condiciones y números de programa fuera del catálogo no producen una acción. Un mensaje nuevo limpia la petición anterior e invalida un paso anterior todavía pendiente. La cápsula, sin observaciones de un anfitrión conectado, no puede abrir ventanas ni afirmar que lo hizo.

La prueba de escritorio usa las funciones originales de `desktop.js`, `bbyq-control.js` y `programs.js`, con XI real y un RXE que incrementa un byte de estado nativo. El DOM, el dibujo y la persistencia Android son fixtures de prueba. **No demuestra una ejecución en el teléfono.** Tampoco habilita búsquedas web, navegación, cuentas bancarias u otras herramientas arbitrarias.

## Uso del coordinador nativo

Desde la raíz del paquete, con el runtime existente:

```sh
reverse_pc app-init BBY-Q.rxe inicial.rvp
node BBY-Q/ai/personal/x05/run.mjs /ruta/reverse_pc . inicial.rvp borrador.rvp 'Escribe en XI un programa que sume los enteros de 3 a 17.'
node BBY-Q/ai/personal/x05/run.mjs /ruta/reverse_pc . borrador.rvp ejecutado.rvp 'Ejecuta y verifica el programa XI.'
```

El primer comando de conversación exporta `borrador.rvp.files/program.xi`. El segundo exporta fuente, RXE, traza de las fases y estado despachado para inspección. La respuesta de éxito la produce `result.xi` después de que `review.xi` acepte lo observado.

El coordinador conserva la entrada y exige un destino nuevo. Compila y ejecuta únicamente la fuente extraída de la tarea emitida por la cápsula fijada; verifica hashes de la cápsula y de los roles. Usa un directorio privado, RVPC2 aislado y el presupuesto original de un millón de instrucciones. No interpreta el lenguaje de la petición ni decide el resultado matemático.

Este coordinador es un anfitrión de programas nativos. Las operaciones de ventanas requieren el anfitrión de escritorio REVERSE y observaciones frescas. No abre ventanas del teléfono desde la terminal ni reemplaza el puente Android.

Un intento solicitado pasa por preparado, solicitado, despachado y verificado o rechazado. Despachar de nuevo el mismo estado se rechaza. Un estado despachado sin confirmación queda sin verificar y no se reejecuta automáticamente. El transporte conserva un estado despachado antes de compilar/ejecutar. La propiedad de un solo uso corresponde a ese estado y ese intento; no es una garantía global entre copias deliberadamente bifurcadas de un archivo RVPC2. Todas las ejecuciones de esta entrega son programas locales aislados, sin efectos sobre proyectos del usuario.

## Memoria y migración

| Región | Contenido |
| --- | --- |
| `9090000000000000000`, 8.192 bytes reservados | Propiedad `85`, esquema `1`, estado de la tarea, identidad y parámetros |
| `B+64` | Hasta dieciséis parámetros enteros con signo |
| `B+256` | Identidad de la observación y resultado tipado del anfitrión |
| `B+512` | Hasta dieciséis salidas observadas con signo |
| `B+1024` | Fuente XI, hasta 4.096 bytes |
| `B+6144` | Fuente original de una reparación, hasta 512 bytes |
| `B+100000`, 8.192 bytes | Trabajo temporal, borrado al finalizar |

La región original QdU `846...` y sus campos w4U de autorización se usan de forma temporal y se restauran. Si están ocupados por datos previos, el coordinador se detiene antes de sobrescribirlos. Las regiones anteriores de hechos, memoria personal, documentos y razonamiento se conservan.

```sh
node BBY-Q/ai/personal/x05/migrate.mjs /ruta/reverse_pc . memoria-anterior.rvp nueva-x05.rvp
```

El migrador ejecuta las fases necesarias X02, X03, X04 y X05, cada una con su presupuesto nativo original, sobre una copia privada. Publica únicamente al completar todas las fases. Repetirlo es idéntico byte por byte. `model.rvp` es una **semilla limpia**, no debe sustituir una memoria personal usada.

## Validación y límites de la entrega

Los protocolos congelados, fuentes de prueba, resultados y transcripciones están incluidos. Cubren generación, ejecución RXE, ocho reparaciones con fallo previo y acierto posterior, valores nuevos, límites reales de listas y números, permiso ausente, repetición de tickets, recibos alterados, fuente o generación cambiada, conservación de datos y migración. También se comprueba la compatibilidad de X01–X04 y del W4u original.

La semilla crece 49 bytes porque añade la propiedad de un esquema inicialmente vacío. La implementación ocupa código adicional en la cápsula y los roles XI; sus tamaños y hashes se declaran aparte. Los programas y datos de tareas aumentan la memoria usada. No es una puntuación de inteligencia ni una comparación directa con ChatGPT o Claude.

Esta entrega contiene código y una cápsula RXE. **No contiene una APK nueva y no modifica una instalación Android.** La integración de estos archivos, el coordinador y sus formatos en la APK sigue siendo parte de P13. No se publicaron cambios remotos.
