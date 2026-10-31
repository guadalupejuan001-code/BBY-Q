# BBY Q — P05: memoria conversacional acotada y referencias entre turnos

## Objetivo

P05 incorpora a X10 un **índice conversacional transaccional de corto alcance**, separado de los pesos, lecciones y checkpoints previos. La clasificación de las peticiones y la selección de mensajes anteriores se ejecutan en XI. SQLite conserva el texto y su huella; Node.js solo monta bytes y muestra literalmente el turno seleccionado junto a su número de generación.

No se afirma comprensión general de pronombres, resumen semántico libre de miles de mensajes ni aprendizaje neuronal.

## Qué funciona

### Historial automático de sesión

Cada turno exitoso de X10 (incluidos P03/P04 y E034) registra, si cabe, una copia de la entrada del usuario y una vista acotada de la respuesta. El índice contiene como máximo **32 turnos** y admite recuperar hasta **8 turnos recientes** en una consulta nativa. El límite por mensaje indexado es **384 bytes**. Un mensaje más largo se registra como barrera vacía, impidiendo que una pregunta posterior con pronombre recupere sin querer un tema antiguo.

Se guardan los datos en la tabla `conversation_turns` de `memory.sqlite`, dentro de la **misma transacción y el mismo mecanismo de replay de X10**. La tabla contiene generación, identificador de solicitud, texto original, fragmento de respuesta y SHA-256 del texto registrado. No modifica `state`, `lessons`, `relational_state` ni el checkpoint X09.

### Consultas demostrables

```text
Luna es un gato.
¿Y qué dije de ella?
```

P05 reconoce una estructura restringida: un sujeto de una palabra seguido de `es`, `tiene`, `esta` o `está`. Si la pregunta cita `ella`, `él`, `eso` o `ese tema` y ese sujeto está inequívocamente en el **mensaje anterior indexado**, devuelve la cita exacta de ese mensaje y su número de turno. Si el último mensaje cambia de tema o contiene varios sujetos, el sistema no toma uno arbitrariamente.

También admite búsquedas por tema explícito como `¿Qué dije sobre Luna?`, `¿Qué dije de Luna?`, `¿Te acuerdas de Luna?` y `¿Qué dije acerca de Luna?`. La búsqueda examina los últimos ocho mensajes con comparación ASCII sin distinguir mayúsculas, y respeta límites de palabra para que `Ana` no coincida por error con `Anabel`. Los nombres acentuados y las formas no contempladas necesitan gramáticas posteriores; no se presume una equivalencia semántica ilimitada.

Comandos de consulta:

- `@context status`: número de entradas indexadas.
- `@context recent`: hasta cinco mensajes recientes, reproducidos con su procedencia.
- `@context last` o `¿Qué dije antes?`: el mensaje anterior verificable.
- `@context answer` o `¿Qué me respondiste antes?`: última respuesta completa disponible (si cabe en el límite establecido).
- `@context clear`: vaciar únicamente el **índice conversacional reciente**. Los recibos históricos de X10 y las lecciones aprendidas permanecen; la respuesta lo advierte explícitamente.

**Privacidad:** `@context clear` no borra los recibos normales de una sesión X10 ni datos ya almacenados en otras memorias. No debe presentarse como «olvido total». Es un mecanismo de control del contexto de trabajo.

## Ejecución

Con una compilación X10 nueva que incluya `context.rxe`:

```bash
# Archivar una frase sin enseñarla como conocimiento permanente
node bbyq.mjs --build build/x10 turn /ruta/sesion u01 --module=p05 "Luna es un gato."

# Consultar el historial por nombre o pronombre
node bbyq.mjs --build build/x10 turn /ruta/sesion u02 "¿Qué dije sobre Luna?"
node bbyq.mjs --build build/x10 turn /ruta/sesion u03 "¿Y qué dije de ella?"

# Ver y limpiar solo el índice breve
node bbyq.mjs --build build/x10 turn /ruta/sesion u04 "@context status"
node bbyq.mjs --build build/x10 turn /ruta/sesion u05 "@context clear"
```

En X10 normal, las peticiones reconocidas se envían a P05 automáticamente. Las entradas que P05 no entiende continúan su ruta anterior X10/P01/P02/P03/P04 y, si la operación tiene éxito, se anotan para referencias posteriores. `--module=p05` permite guardar un mensaje de contexto puro, sin enviarlo al aprendizaje del modelo.

## Seguridad y coherencia

1. **Solo lectura del conocimiento:** P05 no inserta lecciones ni corrige hechos E034; su único almacenamiento es el índice de mensajes reales del usuario, dentro de X10.
2. **Sin recuerdos fabricados:** la salida muestra el texto exacto de un mensaje identificado, o declara que no existe referencia válida.
3. **Referencias conservadoras:** los pronombres no buscan arbitrariamente en conversaciones anteriores: solo se resuelven frente a un antecedente inmediato de sintaxis segura.
4. **Límites estrictos:** 256 bytes por consulta nativa, 384 bytes por mensaje indexable, 8 entradas de búsqueda, 32 de retención; la entrada X10 original mantiene su límite independiente.
5. **Replay idempotente:** repetir un `requestId` devuelve el recibo de X10 sin insertar una segunda entrada. Un fallo revierte los cambios en el índice.
6. **Compatibilidad:** los roles de X09/X10, P01–P04 y el módulo XI E034 se conservan. La compilación X10 debe reconstruirse para que el rol `context.rxe` esté disponible.
7. **No persistir temas falsos:** las preguntas de consulta a P05 no se rearchivan como nuevas afirmaciones.
8. **Integridad:** se verifica la huella de cada mensaje recuperado del índice.

## Pruebas reproducibles

```bash
node --test integration/p01/tests/contracts.test.mjs integration/p02/tests/contracts.test.mjs integration/p03/tests/contracts.test.mjs integration/p04/tests/contracts.test.mjs integration/p05/tests/contracts.test.mjs
node integration/p05/tests/native.mjs /ruta/reverse_pc /ruta/nueva-evidencia
node integration/p05/tests/cli.mjs /ruta/reverse_pc /ruta/nueva-evidencia-cli
```

El examen nativo incluye pronombres, nombres no vistos, límites de palabra, ausencia de sujeto, cambio de tema y resistencia a cambios de memoria XI fuera de la región P05. La batería CLI ejecuta el **X10 real con una base sintética sin modelo X09** para comprobar transacciones, integración, replay, rollback, ventana y conservación de estados P02.

**No validado aquí:** uso real de un ZIP completo X09 de producción, Android/APK, aprendizaje de pesos neuronales, memoria de múltiples conversaciones independientes, inferencia libre de antecedentes a larga distancia ni comprensión general del texto.

El objetivo P05 es una base segura y medible para P06, P08 y la futura memoria conversacional extensa.
