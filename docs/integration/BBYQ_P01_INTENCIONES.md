# BBY Q — P01: comprensión de intenciones (XI)

## Propósito

P01 introduce una clasificación **nativa XI** de las intenciones presentes en el mensaje del usuario antes del fallback desde X10 hacia X09. La primera entrega incorpora nueve etiquetas: `unknown`, `greeting`, `question`, `explanation`, `creation`, `teaching`, `correction`, `statement` e `instruction`.

El módulo no sustituye el motor de razonamiento y **no genera texto libre**; ese trabajo corresponde a P03 y P04. Los resultados de clasificación se incluyen en el comprobante de cada turno X10 como `intent`, `intent_confidence`, `intent_rule` e `intent_read_only`.

## Arquitectura

- `ai/personal/p01/intent.mjs` conserva el currículo de señales explícitas y **genera instrucciones XI**. Las preguntas no se clasifican mediante expresiones regulares de JavaScript en producción.
- `integration/x10/prepare.mjs` compila `intent.xi` → `intent.rxe` utilizando el runtime `reverse_pc` original, y guarda su hash en el manifiesto verificado de X10. X09 y el checkpoint original no cambian.
- `ai/personal/x10/pages.mjs` entrega una página UTF-8 al ejecutor XI y recupera los cuatro campos de intención. Entran como máximo 190 bytes en el análisis lingüístico de P01. Las operaciones anteriores de hasta 1 MiB siguen sujetas a sus contratos de X10.
- `ai/personal/x10/session.mjs` conserva los caminos X10 de lecciones y texto y las respuestas originales del fallback X09. Cuando la clasificación no corresponde a una enseñanza explícita o corrección/olvido de lección, la ejecución del legado ocurre sobre una copia temporal; las modificaciones al estado de conocimiento RVPC2 **no se publican**. El recibo de la operación sí se registra.
- Para consultas que deben ver lecciones actualizadas aún pendientes de sincronización, la lectura temporal aplica esas correcciones sin borrar `dirty_slots` de la base persistente.
- Un mensaje que comience con una orden explícita y no interrogativa como `recuerda que`, `aprende`, `enseña traducción`, `corrige lección`, `olvida lección` o variantes declaradas puede utilizar el mecanismo de escritura ya existente. Frases citadas o interrogativas no autorizan escritura.
- Si una respuesta heredada afirmaba literalmente «Registré tus datos» o «Registré esa afirmación» pero la ejecución fue de solo lectura, el adaptador reemplaza esa **confirmación falsa** por una aclaración de que no se guardó conocimiento. Esta compatibilidad no clasifica el texto de entrada.

## Seguridad, precisión y compatibilidad

Se aplica «solo lectura» por defecto. El módulo normaliza ASCII y algunos caracteres acentuados del español dentro de XI, identifica marcadores de pregunta, y usa coincidencias de palabras completas. Las señales de enseñanza/corrección se aceptan solamente al comienzo (incluidas variantes explícitas como `oye recuerda que`). Se limita el tamaño del catálogo y de los registros temporales.

Los límites de esta primera etapa son deliberados:

1. **No es entrenamiento neuronal:** se trata de reglas supervisadas y auditables. No existen nuevos pesos de un LLM.
2. **No prueba conversación general ni comprensión profunda:** una intención correcta puede seguir derivando en una respuesta X09 insuficiente. P03, P04, P05 y P06 siguen pendientes.
3. **No conserva aún el contexto de turnos no instructivos:** se ha priorizado no aprender por accidente. La memoria temporal de seguimiento requiere el trabajo P05 y la política de aprendizaje P08.
4. **X10 requiere reconstrucción de activos:** una entrega X10 compilada antes de P01 carecerá de `intent.rxe`, y el código actualizado la rechazará en lugar de omitir el control silenciosamente.
5. **No se atribuyen avances a Android:** la ejecución X10/P01 en APK no ha sido validada.
6. **No hay prueba X10 completa sin el X09 ZIP verificado:** los tests nativos de P01 utilizan el ejecutor XI original y verifican la clasificación y el aislamiento de memoria; integrar el paquete X09 y probar el chat íntegro requiere el binario de entrega correspondiente.

## Reproducibilidad

Pruebas estáticas y de contratos (Node 24+):

```bash
node --test integration/p01/tests/contracts.test.mjs
```

Examen XI nativo con un ejecutor compatible y verificado:

```bash
node integration/p01/tests/native.mjs /ruta/reverse_pc /ruta/salida-nueva
```

El examen registra cada entrada, intención esperada, intención obtenida, política de escritura, regla reconocida y latencia real. A su vez, verifica que el módulo no toca una región extranjera de memoria ni modifica celdas fuera de sus regiones propias. El resultado reproducible se publica como artefacto temporal del workflow [bbyq-p01.yml](../../.github/workflows/bbyq-p01.yml).

Este módulo se integra en el código sin tocar archivos de entrenamiento originales, pesos anteriores, ni el ejecutor XI/Ether del repositorio REVERSE-PC.
