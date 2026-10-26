# BBY Q — contrato de estado y mecanismo de interpretación v0.1

## Flujo real de información

```text
Ambiente oculto                   Agente BBY Q
observación (dos señales)  --->  vector de relaciones activadas
                                          |
                          combinación ponderada de hipótesis
                                          |
                               predicción + confianza
                                          |
acción -1/+1  --------------------------> | interacción
         <-----------------------------  consecuencia 0/1
                                          |
                          error de predicción y corrección
                                          |
                              actualizar pesos relacionales
                                          |
                       estado JSON canónico, codificado en bytes
                                          |
                      XI -> InverseMemory -> RVPC2 persistente
```

No existe información sobre la función oculta en el agente ni tabla de respuestas. `world.py` es un módulo independiente y solo el evaluador puede llamarlo para obtener la consecuencia. El agente ve `signal`, `pressure`, la acción y, **después de predecir**, el resultado observado.

## Representación inicial (hipótesis falsable)

Cada observación activa cinco relaciones `bias`, `signal`, `pressure`, `action`, `signal × action`. Se usan valores numéricos con signo. La hipótesis interna es el peso aprendido por relación, inicialmente 0. La predicción es `sigmoid(sum(weight × feature))`; el error es `outcome - probability` y se actualiza `weight += 0.24 × error × feature`. Este mecanismo de gradiente en línea es **conocido**; aquí funciona como experimento de aprendizaje interpretable, no como una arquitectura patentable o superior.

Sus consecuencias se pueden observar en `predict` (contribución de cada relación), `step` (predicción **antes** del resultado, error y delta de cada peso), e `inspect` (hipótesis e historial de 32 experiencias). La mejora se decide por datos de evaluación retenidos, no por crecimientos de pesos ni cambios visuales.

El entorno sintético genera coeficientes secretos deterministas por semilla para una relación lineal con interacción. También se prueba una relación XOR/paridad **no lineal** que no pertenece a la clase de hipótesis elegida. No se enseña al agente el valor verdadero de los coeficientes. El modo de paridad y el cambio invertido identifican fallos y olvido, respectivamente.

## Una autoridad de persistencia

`NativeStore` usa la CLI real integrada de REVERSE-PC. `birth` invoca `reverse_pc init` y escribe el estado serializado en InverseMemory con `mem_store`. Una dirección lógica base `1000000000000000` y siguientes guardan **cuatro bytes de longitud + JSON UTF-8 canónico**; un fondo global 0 significa que no se crean excepciones para bytes 0. Se escriben solo posiciones diferentes y se limpia la cola si el estado disminuye.

El fichero `entity.rvp` RVPC2 integra esos bytes con el estado del núcleo REVERSE-PC. **No se generan qubits** en este esquema. El proceso ejecuta `mem_materialize` bajo el contrato XI real para leer el texto antes de volver a usarlo. La longitud se valida antes de la proyección. El presupuesto local es 24.000 bytes de JSON (por debajo de límites 65.536 del motor); el historial se acota a 32 experiencias para evitar crecimiento ilimitado. Una variable local durante una operación es un candidato temporal, no otra fuente persistente.

Todas las operaciones de lectura/transformación/escritura se serializan con `flock` en Linux, fuera del estado científico. La escritura se ejecuta en un **solo programa XI**, y el CLI guarda mediante archivo `.pending` y rename tras una transacción exitosa. Un programa inválido no muta `entity.rvp`. `RVPC2` incluye checksum de corrupción accidental (no autenticación criptográfica). No se soporta escritor concurrente que ignore el protocolo de bloqueo. El estado inicial no se reemplaza si ya existe.

Los observables nativos `mem_stats` y `stats` deben confirmar que hay bytes diferenciales pero **cero qubits activos** y cero enlaces cuánticos en los experimentos de IA. El coste de transporte XI podría superar a un almacén clásico para ciertas tareas; se mide y se conserva aunque resulte desfavorable.

## Progresión y decisiones

| Etapa | Resultado exigible | Estado |
|---|---|---|
| 1. Nacimiento | Identidad, transición, memoria y continuidad tras reiniciar; rollback y trazas | Implementado; CI debe confirmar compilación y e2e nativos |
| 2. Aprendizaje | Error observable; predicción mejora frente a versión congelada sobre holdout | Primer experimento local ejecutado; no se afirma semántica general |
| 3. Generalización | Transferencia entre tareas y contextos, no solo muestras nuevas | Pendiente; muestreo holdout solo prueba interpolación estructural |
| 4. Evolución | Representaciones candidatas, validación A/B, rollback y retención | Pendiente; está prohibida la autoedición de código en v0.1 |
| 5. Utilidad | Tarea externa y baseline comercial pertinente | Pendiente |
| 6. Producto | SDK/aplicación sustentada por demanda y ventaja real | Pendiente |

## Siguiente hipótesis a contrastar

Añadir memoria de contextos/regímenes y selección por evidencia, sin modificar el estado aprendido del contexto anterior. Comparar contra el presente modelo de pesos únicos y contra múltiples expertos clásicos, con igual presupuesto de datos y hardware. Esta es una **propuesta**, no una mejora demostrada.


## Extensión E002: hipótesis de contexto recuperables

BBY Q incorpora una segunda representación experimental: contexto activo con
relaciones aprendidas y un conjunto acotado de hipótesis archivadas. El agente
no recibe etiquetas de régimen; detecta contradicciones consecutivas,
compara verosimilitud de los resultados observados y decide conservar,
recuperar o crear un contexto. Los contextos inactivos no se duplican
en el activo, sino que se intercambian. `predict` sigue siendo lectura,
`contextual_experience` convierte feedback en transición, y `inspect`
expone identidades, pesos, contadores y presupuesto. Todo cabe en la misma
autoridad Inverse Ether Memory/RVPC2 de REVERSE-PC.

Las reglas de reconocimiento y el modelo de pesos están implementados en
BBY Q; **Ether no implementa aprendizaje semántico en origen**. El
cálculo aritmético sigue siendo Python, mientras XI/REVERSE-PC aporta
persistencia y rollback. E002 no prueba generalización a funciones
desconocidas, ni mejora universal de tiempo o recursos. Contrastar E001,
E002 y condiciones adversarias documentadas en
[AI_E002_CONTEXT.md](AI_E002_CONTEXT.md).
