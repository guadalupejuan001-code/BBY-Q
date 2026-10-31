# BBY Q — P03: razonamiento conversacional mediante XI

**Objetivo:** inferencia verificable a partir de premisas proporcionadas por el usuario, sin cambiar los datos aprendidos ni atribuir a BBY Q comprensión universal del lenguaje.

## Arquitectura y alcance

P03 añade una capacidad **nativa XI/Ether** al motor X10. Sus operaciones de reconocimiento de frases, normalización, almacenamiento temporal de relaciones, búsqueda en grafo, comprobación de negaciones y generación de cadenas de evidencia se ejecutan en XI. No es un Transformer, no incorpora pesos neuronales ni delega el razonamiento al anfitrión JavaScript.

La fuente XI auditada se conserva en `ai/personal/p03/reason.xi.gz.b64` (texto XI comprimido con gzip y codificado en base64). El archivo `ai/personal/p03/reason.mjs` comprueba su SHA-256 antes de compilarlo con el ejecutor XI original.

SHA-256 del texto XI descomprimido: `90e377f00e0be1a1c2b8fb3ed0800af2b0fdfd261c94bd66c4f2519db0ae5317`.

## Inferencias soportadas

- Silogismos categóricos en español: `Todos los gatos son mamíferos. Luna es un gato. ¿Luna es mamífero?`.
- Cadenas múltiples: `Todos los gatos son mamíferos. Todos los mamíferos son animales. Luna es gato. ¿Luna es animal?`.
- Comparaciones transitivas estrictas: `A es mayor que B. B es mayor que C. ¿A es mayor que C?` o `Si A es mayor que B y B es mayor que C, ¿A es mayor que C?`.
- Evidencia negativa directa: `Luna no es gato. ¿Luna es gato?`.
- Detección de contradicción **respecto de la pregunta** cuando existe una cadena positiva y una negación explícita, o relaciones opuestas de «mayor que».
- Abstención cuando no hay prueba ni refutación; no usar el desconocimiento como demostración de que algo es falso.
- Trazas de conclusión con una cadena real de referentes, no respuestas prefabricadas a nombres determinados.

La gramática actual usa palabras de un único token (nombres propios de una palabra, clases de una palabra), normalización ASCII con vocales acentuadas y una singularización deliberadamente acotada para plurales regulares. Cada problema admite hasta **640 bytes**, **64 tokens**, **12 oraciones**, **12 premisas** y una exploración interna limitada a 16 nodos. Estas cotas evitan que el problema agote el motor XI.

Una frase que no coincide con la gramática establecida no se interpreta parcialmente como prueba. La demostración se basa en lo que el usuario **plantea como premisa**, no certifica esos enunciados como hechos reales del mundo.

## Integración con la conversación X10

El rol `reason.rxe` se compila en `integration/x10/prepare.mjs`, queda identificado por hash en el manifiesto original y se invoca desde `NativePages.reason()`. Las operaciones existentes de X09/X10, P01 y el módulo E034 de P02 no se reemplazan.

En el chat normal X10, si una entrada contiene premisas y una pregunta compatibles, el módulo XI puede resolverla automáticamente. Si hay oraciones no reconocidas, longitud excesiva, o preguntas fuera del alcance, se conserva el flujo anterior. Esto evita confundir una falta de gramática con una prueba negativa.

También existe un modo explícito para examinarlo sin recurrir al fallback:

```bash
node bbyq.mjs --build build/x10 turn /ruta/sesion p03-001 --module=p03 "Todos los gatos son mamíferos. Luna es un gato. ¿Luna es mamífero?"
```

Las respuestas incluyen metadatos de tipo de conclusión, número de premisas, tamaño de la cadena de prueba e indicación de solo lectura. Todos los resultados se guardan en el historial normal de comprobantes X10, pero **no** modifican los modelos RVPC2 originales ni las lecciones persistentes.

## Reproducibilidad y pruebas

```bash
# Verificación de SHA, API y regresiones de contratos
node --test integration/p01/tests/contracts.test.mjs integration/p02/tests/contracts.test.mjs integration/p03/tests/contracts.test.mjs

# Ejecución XI real con runtime compilado fijado
node integration/p03/tests/native.mjs /ruta/reverse_pc /ruta/evidencia-nueva

# Ruta real X10 y CLI con sesión de prueba sin modelo X09
node integration/p03/tests/cli.mjs /ruta/reverse_pc /ruta/evidencia-cli
```

El workflow `.github/workflows/bbyq-p03.yml` reconstruye el ejecutor REVERSE-PC de un commit fijado, compila el rol nativo y ejecuta la batería. Los casos nuevos contienen nombres distintos de los ejemplos del documento; la comparación exige modo y traza correctos, no solo coincidencia de palabras.

El test de entrada X10 crea una base SQLite sintética para comprobar el despacho, aislamiento de estado, reintentos y fallos inyectados sin requerir el ZIP X09 original. **No se presenta como una prueba completa de una conversación X09 real restaurada.**

## Límites conocidos y pendientes

1. **No hay conversación libre general:** las frases complejas, negación de universales, cuantificadores arbitrarios, correferencias libres y entidades de varias palabras siguen fuera de la gramática.
2. **Sin memoria interturno de premisas P03:** el problema se analiza sobre el texto de la petición actual; el historial de X10 conserva el recibo pero no se extraen automáticamente premisas de turnos anteriores. P05 cubre la memoria conversacional.
3. **Conflictos acotados:** se detectan contradicciones relevantes para la pregunta. No hay un verificador lógico global de todas las proposiciones posibles.
4. **No se certifica veracidad externa:** una respuesta puede ser correcta condicionalmente a premisas falsas.
5. **Android y X09 completo:** sin validación de APK ni batería con el ZIP nativo X09 original todavía.
6. **No reentrena pesos:** este ciclo amplía el operador de razonamiento simbólico XI y su interfaz, no un modelo neuronal.

P03 se considera implementado en el código cuando las pruebas de CI publicadas confirman ejecución XI, inferencia y no regresión. Las limitaciones anteriores no deben ocultarse.
