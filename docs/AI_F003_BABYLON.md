# F003 — Babilonia: conocimiento persistente en XI/Ether

## Entrega

Solicitud: descargar un PDF gratuito de El hombre más rico de Babilonia y entrenar BBY Q.

Se descargó el original inglés de George S. Clason, en un PDF de 122 páginas. La página 2 declara dominio público y libre distribución. Las lecciones son redacción educativa original en español, no una traducción comercial ni una traducción completa.

Fuente: https://cpcglobal.org/publications/The%20Richest%20Man%20in%20Babylon.pdf
Corroboración de la obra original: https://commons.wikimedia.org/wiki/File:The_Richest_Man_In_Babylon.pdf
PDF SHA-256: `76b620d86a163a1934aebeea997f75c1c685d0ecd877f4a0854f0ab3e0e29b69`.
Descarga GitHub Actions 40999971672: completada con éxito; artefacto 12952972230.

## Incorporación comprobada

64 conceptos nuevos: 48 derivados del libro y 16 aplicaciones modernas etiquetadas por separado. Cada ficha conserva fuente y páginas. Se incorporaron 128 hechos nativos a F002: total 224 conceptos y 448 hechos persistentes.

Temas: ahorro, presupuesto, reinversión, protección del capital, las cinco leyes del oro, capacidad de ganar, préstamos, vivienda, futuro y deudas. Las aplicaciones modernas incluyen REVERSE, XI, Ether, Laplace y BBY Q. El reparto 10/20/70 de Dabasir se atribuye al relato, no se impone como regla universal.

Esta enseñanza utiliza el archivo contextual del agente XI/Ether: no es ajuste de pesos neuronales ni lectura autónoma del PDF. Los 256 ejemplos de diálogo preparados NO se cuentan como aprendizaje conversacional consumido. Node prepara, transporta y verifica; el agente guarda y responde en XI/Ether.

## Resultados locales completos

Código ejecutado: `14088c1288998a8859be65b81141e6a10021b964`. Entorno Linux x86-64, Node 22.16.0, ejecutor original de F002.

| Prueba | Resultado |
|---|---:|
| Aserciones contadas en la campaña | 923 aprobadas |
| Respuestas exactas a nuevos hechos antes de enseñarlos | 0/128 |
| Hechos nuevos incorporados | 128/128 |
| Respuestas antiguas conservadas | 320/320 |
| Consultas nuevas de definición y requisito | 128/128 |
| Consultas compuestas | 64/64 |
| Seguimientos compatibles | 64/64 |
| Variantes de consulta del operador | 64/64 |
| Recuperación desde una nueva instancia de la cápsula | 128/128 |
| Casos de longitud del lector | 8/8 |

Las filas son partes de la campaña; no deben sumarse otra vez a las 923. Las pruebas abiertas fallidas NO se cuentan como aprobadas. La recuperación de hechos enseñados no demuestra razonamiento abierto ni rentabilidad.

## Fallo descubierto y corregido

El archivo admitía hechos de 224 bytes, pero el lector de relaciones descartaba valores de más de 80 bytes. Esto afectaba a 19 hechos de esta campaña. Con el mismo estado ya enseñado, el lector antiguo recuperó 0/19 y el corregido 19/19.

Se cambiaron exactamente dos comparaciones en XI, sin modificar el host. El lector ahora admite los valores que caben en el registro; permanecen los límites de 224 bytes por hecho, 255 bytes por entrada y 512 entradas contextuales. Los valores se emiten directamente desde su posición y longitud en el archivo. Se verificó que desensamblar y recompilar la base sin cambios reproduce un binario idéntico. También se conservó la detección de contradicciones entre valores largos.

El primer intento local y la CI inicial 41000575377 fallaron en «siete remedios»; no se cuentan como campañas aprobadas. La ejecución corregida se inició nuevamente desde F002.

## Respuestas reales

Entrada: `oye que es pagarte primero`
Salida: `pagarte primero es reservar para tu futuro una parte de lo que ganas segun el libro [#328].`

Entrada: `que es quinta ley del oro`
Salida: `quinta ley del oro es la advertencia contra rendimientos imposibles y consejos de embaucadores [#376].`

Entrada: `que es plan de dabasir y que requiere`
Salida: `plan de dabasir es el reparto del relato de diez por ciento para ahorro veinte para deuda y setenta para vivir [#400]. plan de dabasir requiere registrar ingresos deudas y pagos para comprobar el avance [#401].`

Entrada: `que es babilonia aplicada a reverse`
Salida: `babilonia aplicada a reverse es una propuesta educativa de convertir funciones utiles de reverse en ofertas comprobables [#432].`

Los identificadores #NNN son registros del agente, no páginas del libro. Las páginas están en el corpus.

## Limitación importante: conversación abierta

Se probaron ocho tareas abiertas, en estados desechables, sin enseñar sus respuestas. Ninguna quedó resuelta: siete devolvieron «No tengo información suficiente para responder.» y una devolvió «Registré esa afirmación.», aumentando su copia de 448 a 449 hechos.

Entre los casos fallidos están calcular el 10% de 1000, aplicar numéricamente el plan de Dabasir, reconocer el caso del fabricante de ladrillos y las joyas, adaptar la regla cuando faltan alimentos, comparar vivienda, cuestionar una promesa de duplicar dinero y aplicar el libro a REVERSE. La petición de invertir dinero tampoco se convirtió en una operación; respondió que no tenía información suficiente.

La frase «Entonces comprar casa siempre es mejor que alquilar» fue guardada como afirmación en la copia de prueba. Es un fallo de interpretación pendiente. Las copias de prueba NO se incorporaron a la semilla publicada; se verificó su hash sin cambios.

Por tanto, esta campaña acredita adquisición y recuperación de conocimiento bajo gramática compatible. No acredita administración de dinero ni resolución de casos nuevos.

## Artefactos

Cápsula F003 SHA-256: `2458e999acbb72dcaf81219b44b7187244df7abaa22a465f59fc8ffcefc6300b`.
Checkpoint SHA-256: `dfdf19b32905a11b4ff43f0106bc298434941796001c6b1e05d25d6dc8ed7883`.
Checkpoint: 1.873.946 bytes; gzip: 252.034 bytes.
Fuente XI corregida SHA-256: `72b4ab38bd4b6cf589d6eb3fbe5fdbe8bfd73e6363dfa4a6ddfdf4b2089e86a2`.
Ejecutor SHA-256: `ef0c3a709121b8fd3cf4c996808ecfef8b60a7065d3f9c802280c58dc9370d84`.

La entrega descargable contiene PDF, cápsula, estado, base F002, ejecutor, fuentes, corpus, transcripciones, resultados y un script de reproducción. No requiere otro modelo ni una compilación nueva del host.

## Alcance

PR #46 abierta, sin fusionar. No se actualizó la APK ni se reemplazó el agente más reciente de REVERSE, ni se tocó la memoria del operador. No se habilitaron cuentas, trading, pagos o transferencias. Se conserva BBY Q → w4U → QdU.

Quedan 64 entradas libres de las 512 actuales. No se declara memoria ilimitada. La reproducción corregida en GitHub Actions 41001114852 estaba en curso al escribir este informe; no se presupone su aprobación. Los resultados numéricos publicados arriba corresponden a la ejecución local completa.
