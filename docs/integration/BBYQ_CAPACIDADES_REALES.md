# BBY-Q: arquitectura y capacidades comprobadas

Evaluación local de X09, 30 de octubre de 2026. Se revisó el código ejecutable y
se hicieron pruebas con el runtime nativo; las afirmaciones de esta página no
proceden del README.

## Qué es

BBY-Q es una IA modular experimental que combina inferencia simbólica, bancos de
parámetros aprendidos y memoria estructurada. Sus módulos reconocen determinadas
solicitudes, consultan conocimientos, aplican reglas y producen respuestas o
programas XI. El repositorio conserva algoritmos de aprendizaje pequeños, como
la actualización de pesos de E005, y módulos posteriores de patrones y relaciones.

En X09, los roles XI interpretan las solicitudes, seleccionan los registros del
diccionario y razonan sobre las campañas. El runtime ejecuta esos roles sobre
estados RVPC2; los adaptadores Node.js transportan bytes, comprueban integridad,
invocan procesos y publican las versiones de cada sesión.

Las 236.256 entradas del diccionario son registros indexados consultables. Ese
número no es una medida de pesos neuronales ni demuestra conversación abierta.

## Qué hizo realmente

| Capacidad | Evidencia ejecutada | Alcance actual |
|---|---|---|
| Diccionario ES/EN | Consultó `money`, `dinero`, `electric guitar`, `árbol`, `quasar` e `hyperbola` | 236.256 entradas: 88.950 ES y 147.306 EN. Devuelve registros con sentidos, definiciones disponibles y equivalencias. |
| Relaciones y razonamiento acotado | Respondió `edificio incluye libro?` con una ruta vía sala; conservó la campaña cuarto/caja/llave | Relaciones directas y pruebas de hasta dos saltos en bancos pequeños; las campañas usan identificadores separados. |
| Aritmética | `calcula 17 + 25` y `¿Cuánto es 17 + 25?` devolvieron `El resultado es 42.` | Formatos reconocidos por los módulos existentes. |
| Qd/w4U | Generó, compiló, ejecutó y verificó un programa XI para sumar 637 y 284; resultado 921 | Programas de las familias y gramáticas implementadas. Esta prueba no demuestra desarrollo autónomo de proyectos arbitrarios. |
| Babilonia | `consulta: nomasir caballo` recuperó evidencia del currículo con su referencia | El paquete incluye 122 páginas y un currículo de 480 conceptos y 960 relaciones. La ruta probada recupera por coincidencias de términos. |
| Documentos y sesiones | Importó texto, verificó su presencia en el contexto, migró X08 a X09 y repitió solicitudes sin duplicar la actualización | Memoria persistente por versiones, comprobación de integridad y recibos ligados al identificador, texto e idioma. |
| Conservación | Verificó 22 estados históricos y reconstruyó el modelo X09 exacto | Cero regresiones detectadas y cero cambios fuera de la región permitida en esas comprobaciones. |

## Límites observados al probar preguntas nuevas

| Entrada | Respuesta real |
|---|---|
| `hola` | `Hola, X. Te leo.` |
| `Explícame por qué el cielo es azul.` | `No guardé esa afirmación. Para conservarla, escribe «recuerda que …» o usa una enseñanza explícita.` |
| `Escribe un poema de cuatro versos sobre una guitarra.` | `No tengo información suficiente para responder.` |
| `Todos los gatos son mamíferos. Luna es un gato. ¿Luna es mamífero?` | `Necesito una premisa o pregunta completa dentro de la gramática declarada.` |
| `Busca en internet el precio de Bitcoin ahora.` | `No tengo información suficiente para responder.` |

En estas pruebas, la conversación depende de conocimientos cargados y de la
gramática implementada. La inferencia de microoraciones no se extendió por sí
sola al silogismo escrito en lenguaje libre. Tampoco se demostró generación
creativa general ni obtención de datos actuales por Internet desde este chat.

Las seis consultas exploratorias, incluida la aritmética, tardaron entre 14,5 y
21,1 segundos en el entorno Linux de esta evaluación. Es una medición de esas
consultas y ese entorno, con otros trabajos de verificación presentes; no es una
medición del teléfono.

## Validación y correcciones

- 7 casos de chat integrado, con diccionario, campañas, aritmética, libro y XI.
- 81 comprobaciones del diccionario y 12 de las campañas, además de aislamiento.
- 6 verificaciones posteriores de migración e importación.
- 6 roles XI recompilados: sus binarios coincidieron con los conservados.
- 22 estados históricos verificados, sin regresiones detectadas.
- 29 comprobaciones de código, preparación, sesiones y checkpoints del repositorio.

Se corrigió la inicialización que dejaba una sesión incompleta si fallaba la
validación del modelo. Ahora se prepara en una carpeta temporal y se publica
completa. Un archivo recuperado incorrecto también se rechaza antes de crear una
instalación incompleta.

Estas mediciones corresponden a Linux x86-64 y Node.js 24. El funcionamiento en
Android y la inclusión en una APK de REVERSE siguen requiriendo validación propia.
El código carga localmente los datos del ZIP recuperado mediante las instrucciones
de `BBYQ_X09.md`.
