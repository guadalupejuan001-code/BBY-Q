# Integración de los VQC3/QRL3 ya entrenados en BBY Q

Esta entrega reúne el acceso a los agentes existentes desde el lanzador `bbyq.mjs`.
No crea un algoritmo conversacional, no reentrena la entrega de 10.000 episodios
y no transforma sus tareas numéricas en comprensión de lenguaje.

## Modelo integrado

- VQC3 y QRL3: 1.000 cúbits funcionales y 1.000 ángulos por agente.
- Checkpoint histórico con 10.000 episodios por agente, conservando los antiguos
  800/800. SHA-256:
  `eaba877ad9921e55fb4c191bea31dd2eb85ff3c72ba5261c3568709757926e76`.
- Ruta original nativa de Ether con grupos entrelazados de cuatro, identificador
  173. No usa MPS y no convierte los grupos en un componente global de 1.000.
- La variante conectada MPS (identificador 174), sus archivos y sus programas
  quedan conservados por separado. Esta integración no ejecuta esa variante.
- El modelo integrado conserva clasificación lineal y navegación con
  deslizamientos. Las variantes de paridad/señal densa del informe pertenecen a
  otros checkpoints y no se adjudican a este archivo combinado.

El circuito y todo el aprendizaje siguen en `ai/xi/quantum3`. JavaScript maneja
sesiones y comandos; Python transmite al intérprete. No hay otro modelo externo,
simulador externo ni aprendizaje implementado en el adaptador.

## Preparar y ejecutar

Compilar REVERSE-PC y Ether en las revisiones fijadas por el manifiesto. El
directorio de runtime debe contener `build/reverse_pc`, `build/xi_session` y
`scripts/xi_session_client.py`:

```sh
bash REVERSE-PC/scripts/build-xi-session.sh mundo-X REVERSE-PC/build

node bbyq.mjs quantum v3 prepare MI_SESION --runtime=REVERSE-PC
node bbyq.mjs quantum v3 status MI_SESION
node bbyq.mjs quantum v3 classify MI_SESION entradas.json
node bbyq.mjs quantum v3 act MI_SESION 3 6 --greedy
```

`entradas.json` contiene 1.000 valores numéricos finitos compatibles con la
codificación del agente. `act` recibe posición y objetivo entre 0 y 6.
El estado informa de episodios reales, parámetros, ancho y arquitectura; no
deduce el aprendizaje de la cantidad de cúbits registrados.

Para elegir otro ejecutable Python, usar `--python=RUTA` durante `prepare`
o la variable `BBYQ_PYTHON`. El runtime y las fuentes quedan fijados por hash
en la sesión. Un cambio posterior se rechaza antes de modificar su modelo.

## Continuar el aprendizaje existente

```sh
node bbyq.mjs quantum v3 learn-class MI_SESION clase-001 entradas.json 1
node bbyq.mjs quantum v3 learn-episode MI_SESION episodio-001 --slip=0.15 --horizon=12
node bbyq.mjs quantum v3 export MI_SESION NUEVO_MODELO.rvp
```

El mismo identificador y la misma entrada devuelven el recibo existente sin
entrenar dos veces. Reutilizar el identificador con otros datos falla.
Los inputs de enseñanza se copian antes de ejecutar para que el recibo
corresponda exactamente a los bytes consumidos.

Un bloqueo excluye escritores concurrentes. Cada actualización produce un
archivo inmutable nuevo y publica `HEAD.json` de forma atómica; los originales
siguen disponibles en `versions/`. Una interrupción anterior a la publicación
puede dejar un archivo huérfano, que nunca se carga automáticamente. Si queda
`.write-lock` tras terminar un proceso, comprobar primero que ese proceso ya
no existe antes de retirarlo. Las sesiones conservan hasta 4.096 recibos de
actualización; el checkpoint exportado conserva todo el aprendizaje.

La inferencia no actualiza pesos ni publica otro checkpoint. `export` rechaza
destinos existentes. Un error de datos, del runtime o de integridad conserva
el último estado confirmado.

## Comprobaciones y alcance

```sh
BBYQ_QUANTUM_RUNTIME=/ruta/REVERSE-PC \
  node --test integration/quantum3/tests/launcher.test.mjs
```

Las pruebas usan el ejecutor XI real y el modelo entregado: 10.000 episodios
restaurados por agente, 1.000 cúbits observados por decisión, reanudación de
aprendizaje supervisado y por refuerzo, inferencia sin mutación, repetición de
solicitudes, conflictos, rollback e integridad. La CI también ejecuta el comando
raíz de BBY Q.

El asistente de conversación existente continúa con su integración anterior.
El siguiente desarrollo del algoritmo conversacional cuántico requiere un
diseño y una validación propios. No se ha creado ese agente en esta entrega.
No se empaqueta ni se declara validada otra APK.
