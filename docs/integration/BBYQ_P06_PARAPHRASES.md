# BBY Q — P06: generalización lingüística supervisada y verificable en XI

## Alcance de esta prioridad

P06 incorpora un **normalizador de intenciones y formas de expresión** que traduce distintas maneras de formular una petición a los formatos ya entendidos por P03 (razonamiento), P04 (producción de lenguaje) y P05 (recuperación conversacional). La decisión sobre qué reconocer y cómo transformar el mensaje ocurre **dentro de instrucciones nativas XI**.

La gramática de esta entrega se compila desde `ai/personal/p06/paraphrase.mjs` a `paraphrase.rxe`; no ejecuta clasificadores de texto en JavaScript durante la conversación, no incorpora un modelo neuronal y no reentrena pesos. Su catálogo es acotado y verificable: **144 prefijos de reformulación**, con espacios variables para temas y premisas que el programa no conoce de antemano. La ampliación es productiva dentro de esas estructuras, no generalización arbitraria a todas las formas del lenguaje.

## Reconocimiento y composición

### Recordar algo dicho anteriormente (P05)

Entrada original:

```text
¿Me recuerdas qué dije de Aurora?
```

P06 genera dentro de XI la consulta canónica:

```text
¿Qué dije de Aurora?
```

P05 sigue siendo responsable de seleccionar un turno **real** del historial y mostrar su procedencia. Esto también se aplica a variantes como «¿Qué te comenté de ...?» y «Recuérdame qué dije sobre ...». La traducción de «remind me what I said about ...» es una frase concreta admitida, **no** una capacidad de inglés general.

### Poemas y ficción (P04)

P06 reconoce variantes como «Hazme cuatro versos sobre ...», «¿Me escribes un poema sobre ...?» o «Cuéntame una historia sobre ...» y produce instrucciones equivalentes a `escribe un poema de 4 versos sobre ...` o `escribe un cuento sobre ...`. Los números **2 a 6**, tanto con dígitos como escritos, se combinan con distintas peticiones y con temas que no figuran en el código.

P06 no compone los versos ni inventa los acontecimientos: ese trabajo sigue en XI/P04, que comprueba de forma independiente el formato.

### Explicaciones aportadas por el usuario (P04)

La entrada:

```text
Explícame con los datos:
hecho: la lámpara se apagó
causa: faltó electricidad
efecto: quedó oscuro
```

se convierte en la forma `explica con datos:` con los mismos campos originales, para que el compositor P04 pueda elaborar la explicación sin añadir hechos o causas no proporcionados.

### Razonamientos (P03)

Una petición con prefacio como «Deduce a partir de estas premisas: ...» puede eliminar ese prefacio y trasladar las premisas intactas a P03. P03 verifica **por separado** que entiende todas las premisas y la conclusión buscada. Si existe una frase desconocida, no se le da por demostrada una inferencia parcial.

## Barreras de seguridad y persistencia

- **Solo lectura:** `paraphrase.rxe` utiliza memoria de trabajo reservada dentro de XI. No escribe lecciones, datos E034 ni el estado RVPC2 de X09/X10.
- **Dos verificaciones:** la normalización debe coincidir con una regla XI y la nueva entrada debe ser aceptada por P05, P04 o P03. Las frases no resueltas continúan al flujo X09 original o se abstienen en modo P06 explícito.
- **Aprendizaje separado:** peticiones de enseñanza/corrección P01 no se redirigen a P06. La opción `--learn` continúa reservada a E034.
- **Texto conservado:** si la reformulación produce una respuesta, el recibo incluye `paraphrase_canonical` para auditoría; el índice P05 registra la frase **original**, no una versión que el usuario nunca escribió.
- **Control de significado:** los tópicos con comillas, punto y coma, saltos de línea fuera de campos documentados o una segunda instrucción conectada por « y » se abstienen. Son falsos negativos deliberados para no descartar órdenes.
- **Integridad de solicitud:** se mantiene el sistema normal de `requestId`, digest, replay y rollback de X10. `--module=p06` conserva una etiqueta propia en el digest para evitar reproducir recibos de otro módulo.
- **Límites de evaluación:** entrada máxima de 512 bytes, salida canónica hasta 768 bytes y un tópico de hasta 80 bytes en peticiones de recuerdo, poesía y ficción. El motor XI y los módulos de destino conservan sus propios límites.
- **Compatibilidad:** X10 ejecuta las capacidades originales P01–P05 antes de evaluar la reformulación automática. Una compilación X10 anterior que no tenga `paraphrase.rxe` conserva su comportamiento sin intentar la capacidad nueva.

## Uso en una instalación X10 reconstruida

Normalmente, no se necesita especificar el módulo:

```bash
node bbyq.mjs --build build/x10 turn /ruta/sesion p06-auto "Hazme cuatro versos sobre la aurora."
```

El modo explícito permite comprobar P06 y obtener una abstención clara si la gramática no lo reconoce:

```bash
node bbyq.mjs --build build/x10 turn /ruta/sesion p06-test --module=p06 "¿Me recuerdas qué dije de Aurora?"
```

Los resultados de ambos comandos siguen siendo recibos X10 y no sobrescriben entrenamientos anteriores.

## Examen reproducible

```bash
node --test integration/p01/tests/contracts.test.mjs integration/p02/tests/contracts.test.mjs integration/p03/tests/contracts.test.mjs integration/p04/tests/contracts.test.mjs integration/p05/tests/contracts.test.mjs integration/p06/tests/contracts.test.mjs
node integration/p06/tests/native.mjs /ruta/reverse_pc /ruta/evidencia-nativa-nueva
node integration/p06/tests/cli.mjs /ruta/reverse_pc /ruta/evidencia-cli-nueva
```

La batería nativa ejecuta **cada regla**, más combinaciones con temas nuevos y controles de rechazo; la de sesión utiliza el transactor X10 real con una base **sintética** sin el modelo X09 restaurado, para medir enrutamiento, replay, rollback, contexto original, aislamiento de estados y regresiones.

## Limitaciones pendientes

P06 todavía depende de un catálogo supervisado. No demuestra comprensión libre de paráfrasis no vistas, cambios de significado sutiles, negación arbitraria, todas las formas del español, ni traducción universal. P10 corresponde a la ampliación bilingüe. La integración real en APK Android y la restauración completa desde la entrega X09 son validaciones pendientes separadas. Los cambios aquí no representan nuevas ponderaciones de una IA generativa.
