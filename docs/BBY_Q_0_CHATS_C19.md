# BBY Q 0 — chats y continuidad C19

Base: PR #107, commit 6ee0f7b3a5aaf09d02339f789ea5f897a5510d95.
Rama: codex/bbyq-0-chat-continuity-20261109.
Paquete: com.bbyq.u03.training; versión U03.19.0-chats, código 5.

## Problema observado

C18 guardaba el diario completo, pero `send.messages` contenía sólo el par del turno actual. La pantalla asignaba ese par al historial visible. Por eso un nuevo envío hacía desaparecer visualmente los intercambios anteriores. Las pruebas consultaban el diario y recreaban la actividad, pero no exigían que varios turnos siguieran juntos en pantalla inmediatamente después de enviarlos.

Además, «Nueva conversación» cambiaba una vista numérica sin ofrecer una lista para volver a las anteriores. El estado visible y el borrador eran únicos, y el contexto utilizable era insuficiente para conversaciones independientes.

## Corrección

**Conversar** mantiene el historial del chat abierto, su título y un acceso visible a **Chats**. La lista permite crear, buscar, reabrir, renombrar, archivar y recuperar conversaciones. El borrador, la selección y la posición pertenecen al hilo. Se conservan los dos destinos principales, Conversar y Mi BBY Q, y la protección frente a las barras de Android y al teclado.

Un resultado de envío es un recibo inmutable del turno; la pantalla carga por separado el historial completo del `conversation_id` correspondiente. Repetir una solicitud antigua no selecciona su chat, no duplica mensajes y no sustituye la conversación que el usuario está mirando.

## Migración sin pérdida

El diario permanece en conversation-v1/conversation.sqlite. La migración transaccional añade una tabla de conversaciones e índices; no reescribe los mensajes ni los resultados de solicitudes C18. Cada vista que existe en mensajes o solicitudes, además de la vista activa, recibe un identificador estable legacy-view-N. No se inventan vistas intermedias sin datos.

Las conversaciones anteriores aparecen en la lista normal. El usuario de C18 nunca dispuso de una acción explícita de archivado, por lo que C19 no oculta ese historial automáticamente. El archivado nuevo es reversible. La vista activa conserva su selección, y las solicitudes pendientes siguen ligadas a su hilo original.

## Contexto y memoria

El contexto local resuelve referentes sustentados por turnos de la misma conversación: un sujeto identificado o un resultado numérico, además de explicaciones y repetición del último razonamiento admitido. Las resoluciones conservan su procedencia y se convierten en entradas al motor XI original. Si falta un referente o resulta ambiguo, la interfaz pide aclaración sin atribuir esa pregunta al modelo.

La memoria personal U02 sigue siendo la autoridad de hechos, reglas y parámetros. Lo enseñado explícitamente es compartido por el modelo; los referentes de un chat no se heredan de otro. Las preguntas y la gestión de chats no entrenan el modelo. La referencia E025 permanece congelada y autenticada. No se añade un modelo externo ni conversación general ilimitada.

## Verificación exigida

1. Tres envíos por la interfaz dejan seis burbujas reales, con identificadores, textos y orden conservados antes de recrear la actividad.
2. Los chats se crean, reabren, renombran, archivan y recuperan por controles reales; los borradores y cursores permanecen asociados a su hilo.
3. Los seguimientos usan el referente de su conversación, conservan los siete bancos personales y piden aclaración ante ambigüedad.
4. Un diario con el esquema C18 original conserva vistas dispersas, mensajes, recibos y una solicitud pendiente durante la migración.
5. El APK C18 autenticado se instala, genera datos y se actualiza con `adb install -r` al nuevo APK. Se verifican los mensajes, el conocimiento personal, el contexto migrado y la repetición exacta del recibo antiguo.
6. El cierre forzado del proceso conserva varios hilos, el activo, sus borradores, el historial visible y el contexto; se mantienen también todos los controles de entrenamiento anteriores.
7. Las 26 pruebas C18 siguen obligatorias y se añaden cuatro pruebas de continuidad. Las fases de actualización y reinicio son comprobaciones adicionales.
8. Los 159 originales permanecen idénticos. El APK entregado se firma con la clave personal anterior y conserva todos los contenidos del APK comprobado, salvo las firmas.

El workflow genera validation.json, chat-continuity-proof.json, chat-upgrade-seed.json, chat-upgrade-verify.json, evidencias de reinicio y capturas. La evidencia de cada compilación determina sus resultados; este documento no sustituye la ejecución real. El teléfono físico del usuario no se da por probado.

## Panel conservado

El panel C00–C17 y sus alcances se conserva en [C18](BBY_Q_0_PERSONAL_C18.md). C19 corrige la aplicación de chats y su contexto; no promueve experimentos ni añade GPU/QSSD al cálculo. Se respeta BBY Q → w4U → QdU y no se fusiona automáticamente ninguna PR.
