# BBY Q — P04: composición de respuestas con XI/Ether

## Objetivo y límites

P04 implementa un módulo **acotado** de producción de lenguaje: poesía con versos variables, ficción breve con principio/progresión/cierre y explicaciones que reorganizan premisas explícitamente aportadas por el usuario. La decisión de ruta, la elección de frases, la copia de palabras originales y la salida se ejecutan dentro del programa **XI** compilado con el runtime de REVERSE-PC. JavaScript compone el **código XI durante la compilación**; no selecciona la respuesta en tiempo de consulta.

No se han añadido pesos neuronales ni un Transformer, y **no** se afirma generación abierta al nivel de ChatGPT. Las variantes textuales se crean combinando temas introducidos por la persona con distintos fragmentos y estructuras. Las respuestas imaginativas son ficción, no hechos confirmados.

## Arquitectura

- `ai/personal/p04/compose.mjs`: emisor del rol `compose.xi`, currículo de formatos acotados, cuatro variantes por etapa, validación de tema y construcción de respuestas. Datos fuente en UTF-8, límites de 768 bytes por petición y 80 bytes por tema. Entrada y salida nativas XI.
- `integration/x10/prepare.mjs`: genera, compila y registra por hash `compose.rxe` junto con los roles `validate`, `route`, `record`, `stream`, `intent` y `reason`.
- `ai/personal/x10/pages.mjs`: ejecuta el compositor sobre la memoria de trabajo nativa y devuelve tipo de composición, número de unidades y texto.
- `ai/personal/x10/session.mjs`: permite `module:'p04'` con recibo transaccional X10 y ruta automática únicamente para intenciones de creación o explicación identificadas por P01 y reconocidas nativamente por P04. Las peticiones no reconocidas siguen a X09/P03 según la ruta previa.
- `bbyq.mjs`: admite `--module=p04` para pruebas explícitas. Se conserva `--module=p03` y `--module=e034 --learn`.

## Gramática admitida

### Poesía de 2 a 6 versos

```text
Escribe un poema de cuatro versos sobre una guitarra.
Escribe un poema de 4 versos sobre la luna.
Crea un poema de tres versos sobre el mar.
Escribe un poema sobre una estrella.
```

Las formas `dos/tres/cuatro/cinco/seis` y los números `2..6` se interpretan en XI. Cada línea combina un inicio, el tema UTF-8 proporcionado y un cierre. Se seleccionan cuatro variantes por etapa según un resumen de bytes del tema. La última línea es un cierre aunque la longitud del poema cambie.

### Historias de 2 a 6 frases

```text
Escribe un cuento de tres frases sobre una estrella.
Crea una historia de cuatro frases sobre un bosque.
Inventa un cuento sobre una brújula.
```

Las frases siguen una secuencia de introducción, desarrollo y desenlace. El generador conserva el tema de la petición y no declara que sus acontecimientos sean datos del mundo real.

### Explicación con causa y efecto proporcionados

```text
Explica con datos:
hecho: el hielo flota
causa: tiene menor densidad que el agua líquida
efecto: permanece en la superficie
```

También se admiten `explica con estos datos:` y `explica:` en el mismo formato. Se emite una explicación condicional con las tres piezas de entrada y una advertencia de **no verificación independiente**. Este modo NO tiene licencia para inventar causas, efectos ni fuentes que el usuario no haya proporcionado.

Para `Explícame por qué el cielo es azul` sin premisas, P04 todavía no demuestra una respuesta fiable: la solicitud vuelve al motor anterior. Adquirir más conocimiento validado, comprensión abierta y generación explicativa más flexible son tareas posteriores.

## Seguridad, integridad y compatibilidad

1. **Sin aprendizaje implícito:** P04 escribe únicamente en su memoria de trabajo nativa, de la región `B+98304` hasta `B+102400`. No modifica el checkpoint X09/X10, las lecciones, el estado E034 ni los registros del usuario.
2. **Sintaxis delimitada:** los temas tienen límite de tamaño, no admiten controles ni saltos de línea. Los campos de explicación deben estar completos y en el orden declarado; las entradas parciales no generan afirmaciones.
3. **Identidad de la petición:** los recibos X10 distinguen `module:p04` para impedir que se reproduzca silenciosamente una petición de otro motor bajo el mismo identificador.
4. **No se anulan capacidades anteriores:** cuando XI no reconoce el formato, se usa la ruta anterior.
5. **Android no validado:** las pruebas son de runtime XI en Linux; una APK actualizada deberá integrar y probar estos activos de forma independiente.

## Validación reproducible

```bash
node --test integration/p01/tests/contracts.test.mjs integration/p02/tests/contracts.test.mjs integration/p03/tests/contracts.test.mjs integration/p04/tests/contracts.test.mjs
node integration/p04/tests/native.mjs /ruta/reverse_pc /ruta/evidencia-nativa-nueva
node integration/p04/tests/cli.mjs /ruta/reverse_pc /ruta/evidencia-cli-nueva
```

La primera batería ejecuta XI sobre temas y datos novedosos y compara formato, ausencia de escritura fuera de P04, límites y variaciones. La segunda ejecuta **el punto de entrada X10 real y la CLI** con una base de prueba sintética sin el ZIP X09 original; comprueba enrutamiento automático, modo explícito, replay, rollback y conservación del estado principal/E034.

**No** se atribuye a esta batería la restauración completa de X09 desde su paquete original, ni se confunden frases sintéticas con entrenamiento neuronal.

CI: [workflow P04](../../.github/workflows/bbyq-p04.yml).
