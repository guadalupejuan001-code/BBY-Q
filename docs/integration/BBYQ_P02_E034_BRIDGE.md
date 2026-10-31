# BBY Q — P02: puente verificable entre X10 y el aprendizaje E034

**Fecha:** 31 de octubre de 2026  
**Estatus:** candidato de integración en el mismo punto de entrada conversacional, conservando bancos distintos.  
**Dependencia:** la cápsula nativa E034 exacta se distribuyó en un artefacto histórico de GitHub Actions; el repositorio conserva el código y el checkpoint aprendido, pero no el RXE empaquetado de E034. No fingir que un checkout por sí solo incluye esa cápsula.

## Propósito

X10 preserva un conjunto de entrenamientos X09, pero no invoca de forma automática el ejecutor independiente de E034. Esta implementación ofrece un puente explícito y transaccional: el comando `bbyq.mjs turn` puede invocar la **cápsula original E034** como motor XI auxiliar, sin sobrescribir el RVPC2 de X09/X10.

La cápsula comprobada E034 contiene E027/E028/E029, el aprendizaje de E030/E031/E032, relaciones E033 y composición E034 en su cadena compilada. Eso no significa que cada capacidad tenga cobertura lingüística abierta, ni que se hayan mezclado físicamente las memorias.

## Identidades inmutables verificadas

- Cápsula `composition/composed.rxe`: `a0edbe6122beb5ab57d0e2dbd60c26524bc946737806eb71f2ed133fde068a28`, 1.346.841 bytes.
- Checkpoint aprendido `ai/checkpoints/e034/composition-model.rvp.gz.b64`: descomprimido SHA-256 `876d3f2a82698e9582f17043028d9a75b454e4b5ebaf7cc5949b65a5bac58a10`, 863.594 bytes.
- Fuente histórica y artefacto original: [GitHub Actions E034](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40808605984). La cápsula se extrae de su ZIP y se verifica por hash antes de instalarla.
- La nueva versión preserva sin alterar `native/model.rvp.gz`, `capacity/`, las lecciones y los comprobantes anteriores.

## Funcionamiento

`ai/personal/p02/relational.mjs` instala y comprueba los dos activos E034 en `build/x10/relational/`, sin editar ni reemplazar archivos existentes de X10.

`ai/personal/x10/session.mjs` soporta `module:'e034'` dentro de su transacción SQLite. La primera llamada crea una tabla `relational_state` y carga la semilla E034 aprendida. Las llamadas posteriores recuperan y actualizan el mismo estado auxiliar en la transacción del turno original. Los identificadores de reproducción mantienen su contrato y distinguen módulo, idioma y autorización de aprendizaje.

**No se hace una fusión por bytes de dos checkpoints RVPC2 incompatibles.** En su lugar, X10 utiliza dos estados aislados y un punto de entrada compartido. No se ejecuta un modelo de terceros ni se generan respuestas por JavaScript: la cápsula ejecuta `app-turn` en XI/Ether.

### Escrituras explícitas

La opción `--learn` solo está disponible para `--module=e034`. Sin esa opción, la cápsula recibe el mensaje y calcula la respuesta en un estado temporal, pero el estado publicado se reconstruye desde la memoria previa y **únicamente** conserva los dos bytes documentados de referencia tipada E034. Así no se publican relaciones aprendidas accidentalmente en respuestas a preguntas o afirmaciones informales.

La consulta puede conservar el antecedente tipado para las formas de seguimiento E034, pero **no** preserva todos los cachés o contextos temporales de E027/E028. E034 también contiene límites lingüísticos y de memoria propios. La interfaz rechaza mensajes E034 de más de 240 bytes, independientemente del límite X10 de 1 MiB.

Si la ejecución, la integridad o la confirmación falla, la transacción X10 se revierte. Los activos no verificados se rechazan.

## Instalación y uso

Se necesita una entrega X10 ya preparada y verificada mediante su paquete X09 auténtico. Después, usando el **artefacto histórico exacto** de E034 o directamente el archivo `composed.rxe` extraído:

```bash
node bbyq.mjs --build build/x10 install-e034 BBYQ-E034-relational-composition.zip
```

El instalador lee `composition/composed.rxe` del ZIP y compara su hash. También valida el checkpoint E034 conservado en el repositorio. No borra el estado principal.

Para una sesión X10 existente o nueva:

```bash
node bbyq.mjs --build build/x10 turn /ruta/sesion_x10 t01 --module=e034 --learn "El taller galaxa abre el viernes."
node bbyq.mjs --build build/x10 turn /ruta/sesion_x10 t02 --module=e034 --learn "El taller galaxa está en la sala naranja."
node bbyq.mjs --build build/x10 turn /ruta/sesion_x10 t03 --module=e034 "¿Qué día abre y dónde está el taller galaxa?"
node bbyq.mjs --build build/x10 turn /ruta/sesion_x10 t04 --module=e034 "¿Y dónde está ese taller?"
node bbyq.mjs --build build/x10 status /ruta/sesion_x10
```

Por defecto, sin `--module=e034`, se conserva el trayecto X10/X09 original. Elegir una capacidad explícitamente evita que el módulo relacional se apropie de saludos, cálculos o preguntas fuera de su gramática.

## Pruebas

1. **Autenticidad:** verificar hashes del programa compilado y de la memoria aprendida.
2. **Múltiples turnos nativos:** enseñar día y lugar, responder combinación con dos fuentes, resolver una referencia posterior, leer contexto E027, corregir un valor y conservar el valor anterior como evidencia.
3. **Aislamiento:** una afirmación sin `--learn` no debe modificar relaciones persistidas; solo conservar el referente tipado permitido.
4. **Transacciones:** probar integridad, instalación idempotente y reversión de operaciones fallidas.
5. **Entrada X10 real con base sintética:** compilar los roles originales de X10/P01, ejecutar `transact` y `bbyq.mjs`, verificar replay, conflicto de requestId y fallos inyectados; distinguir esta prueba de una entrega X09 real.
6. **Regresiones:** ejecutar GitHub Actions X09/X10/P01 sobre el cambio para no sustituir el aprendizaje anterior.

### Limitaciones y pendientes

- La cápsula compilada E034 proviene de un artefacto histórico de GitHub Actions con fecha de caducidad; el instalador no depende de una URL permanente inventada. Conviene conservarla o construir una entrega reproducible autónoma a partir de sus fuentes.
- No se ha verificado una sesión completa que simultáneamente ejecute un **X09 binario real restaurado desde su ZIP**, el motor X10 y el módulo E034: la prueba de despacho X10 utiliza una base intencionalmente sintética. Los test nativos E034 sí usan el ejecutor real XI y la cápsula exacta.
- Solo existe **selección explícita de módulo**, no arbitración semántica automática de E034 en lenguaje libre. La integración automática sin falsas derivaciones pertenece a una fase posterior.
- El aprendizaje E034 sigue siendo simbólico en XI/Ether, no entrenamiento de pesos neuronales.
- No hay APK Android construida o validada en P02. La ruta Android pertenece a P12.

## Fuentes

- `ai/personal/p02/relational.mjs`
- `integration/p02/tests/native.mjs`
- `integration/p02/tests/cli.mjs`
- `.github/workflows/bbyq-p02.yml`
- [Fuente E034](https://github.com/guadalupejuan001-code/BBY-Q/tree/main/ai/releases/e034)
