# BBY Q — plan prioritario de experimentación física

Diseñar una ruta **verificable** para usar un evento del mundo exterior (primero señales ópticas del Watch4 y luego un chasquido) como entrada física a BBY Q, pasar de simulación controlada por sensores a una interacción física medible y evaluar después un acoplamiento con hardware cuántico real.

**No confundir**:
- BBY Q puede desarrollar estados cuánticos **simulados** en computación clásica. Los qubits lógicos no son qubits físicos.
- Chasquido + micrófono/reloj + código = señal clásica que puede controlar un Hamiltoniano simulado.
- Enlazar física cuántica real requiere un dispositivo con grados de libertad cuánticos controlables y medidas físicas independientes. Ninguna operación de software puede por sí sola entrelazar un estado virtual con una partícula física.

## Primer hito ya implementado: laboratorio óptico Wear OS
- [x] Aplicación Wear OS independiente: acelerómetro, giroscopio, luz ambiental y pulso procesado por permisos.
- [x] Adaptador opcional Samsung Health Sensor SDK para PPG ADC verde/rojo/infrarrojo.
- [ ] Validar capturas reales del Watch4, latencia, ruido y permisos con el SDK suministrado legítimamente.
- [ ] Diseñar protocolos de controles: muñeca quieta/movimiento, reloj fuera de muñeca, variación ambiental.
- [ ] No afirmar fotones individuales, coherencia o entrelazamiento físico a partir de lecturas digitales.

## Etapa A · Gatillo acústico real, sin hardware extra (PRIORIDAD 1A)
- [ ] Crear un experimento Android aparte (independiente del reloj y con permiso explícito) que escuche el micrófono del **teléfono bajo permiso explícito y durante sesiones**.
- [ ] Detectar un chasquido por su transitorio acústico. Registrar marca temporal, amplitud y frecuencia; establecer umbrales y tasa de falsos positivos.
- [ ] Galaxy Watch4 Classic como canal alternativo: acelerómetro/giroscopio para identificar gestos; no asumir datos médicos ni permisos automáticos.
- [ ] Traducir evento a un control documentado H(t)=H0+s(t)V. Controlar una evolución en el simulador propio de BBY Q, registrando norma, observables, latencia y reproducibilidad.
- [ ] Probar tres condiciones: chasquido real, sonido de control y ejecución sin sonido. Todo resultado debe tener trazas y reproducirse con una señal grabada/sintética.
- [ ] Ejecutar un benchmark sobre Android real, con presupuesto explícito de CPU/RAM/batería y sin prometer entrelazamiento físico.

**Definición de éxito A:** un chasquido detectado produce un cambio numérico predecible y repetible en el **estado simulado** que no se confunde con el ruido o con una animación; se puede repetir una captura y verificar el cálculo.

## Etapa B · Salida física controlada (PRIORIDAD 1B)
- [ ] Probar un actuador/sensor real de bajo riesgo (p. ej., piezoeléctrico de bajo voltaje + acelerómetro) para que el evento accione una perturbación **física real** mensurable en un material.
- [ ] Modelo y medición independientes, controles de estímulo encendido/apagado, repetición y separación de efecto mecánico convencional frente a una hipótesis cuántica.
- [ ] No afirmar entanglement físico si sólo hay transmisión clásica de datos.

**Definición de éxito B:** un efecto exterior medido que pueda ser atribuido causalmente al estímulo y reproducirse en condiciones de control.

## Etapa C · Plataforma cuántica física (PRIORIDAD 1C, depende de hardware adecuado)
- [ ] Seleccionar un sistema real (p. ej., centros NV en diamante en colaboración experimental, o qubits reales accesibles en un procesador de investigación).
- [ ] Modelar acoplamiento espín-campo o espín-deformación basado en un Hamiltoniano respaldado por medidas.
- [ ] Preparar/leer coherencia con secuencias físicas reconocibles (Ramsey / Rabi, según plataforma) y **probar entrelazamiento únicamente entre subsistemas cuánticos físicos** mediante un test apropiado.
- [ ] Comparar resultados contra hipótesis clásicas, ruido, calibración e incertidumbre experimental.

**Definición de éxito C:** observables que demuestren control coherente físico; entrelazamiento sólo cuando una prueba independiente lo justifique. El reloj actúa como entrada o canal, nunca como prueba de entrelazamiento.

## Referencias y dependencias
- BBY Q no depende de otro motor ni de otro repositorio para recopilar señales o generar sus propios cálculos.
- Samsung Developer: Galaxy Watch4 accesibilidad de acelerómetro/giroscopio y APIs de sensores.
- Nano Letters (2026), Acoustic Control of Spin States in Diamond Nitrogen-Vacancy Centres, DOI: 10.1021/acs.nanolett.6c02496, demuestra respuesta espín-deformación bajo condiciones instrumentadas de laboratorio, NO entrelazamiento por un chasquido ni por smartwatch.

**Orden de trabajo:** Primero terminar A con pruebas físicas y numéricas honestas; B exige interacción real reproducible; C sólo cuando exista hardware cuántico apropiado. No sustituir pruebas físicas por imágenes o métricas de software.