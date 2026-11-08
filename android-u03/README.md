# BBY Q Android — C17 · Entrenamiento personal

Esta entrega añade **Entrenar BBY Q** a la conversación original. Dentro de la aplicación hay cuatro etapas: Sesión, Enseñar, Probar y Guardar. La guía sin conexión contiene seis dibujos SVG y dos recorridos completos.

## Recorrido de memoria y reglas

1. Crear una sesión desde el estado personal actual.
2. Enseñar el hecho «Nara es robot» y la regla «si es robot, es máquina».
3. Reservar la consulta «es Nara máquina» antes de ver su respuesta.
4. Comprobar el candidato frente a su referencia y las regresiones originales.
5. Activarlo para usarlo en la conversación o continuar enseñando.
6. Exportar el ZIP para evaluar después el modelo y sus ejemplos.

## Recorrido de aprendizaje conjunto

1. Elegir muestra, regla y posición; por ejemplo 2023144612 / 1 / 3.
2. Registrar la predicción XI y después revelar la clase correcta.
3. Aplicar el feedback original, que modifica parámetros de los motores.
4. Comprobar con muestras sintéticas reservadas y comparar con el estado inicial.
5. Activar la sesión aprobada y exportar el resultado.

Los hechos/reglas modifican memoria nativa. Los ejercicios conjuntos ejecutan el aprendizaje XI original. La aplicación distingue ambos mecanismos; no presenta las tareas sintéticas como entrenamiento universal de lenguaje.

## Durabilidad y evaluación

Cada sesión conserva su referencia, versiones de candidato, comprobantes y datos de evaluación. Repetir exactamente una solicitud no vuelve a entrenar. El candidato se activa sólo después de una comprobación vigente y si la conversación no cambió desde el inicio de la sesión. La versión anterior se conserva para restaurar.

El ZIP incluye `manifest.json`, `report.json`, `baseline.sqlite` y `candidate.sqlite`. El manifiesto enlaza los bytes con SHA-256; el informe identifica el código, el runtime, ejemplos, predicciones, correcciones y pruebas. Incluye la memoria de partida de la sesión. No se envía automáticamente a un servicio.

## Compilación y pruebas

- Paquete: `com.bbyq.u03.training`.
- Versión: `U03.17.0-training`.
- Android 10 o posterior; ARM64 y x86-64.
- 20 bibliotecas ELF con segmentos de al menos 16 KB.
- Runtime XI de REVERSE-PC y Ether fijados en el workflow.
- Se preservan los 159 archivos/checkpoints históricos.

El workflow `.github/workflows/bbyq-u03-android-native.yml` compila y ejecuta los 16 controles Android de C16, cinco pruebas de entrenamiento y verificaciones de cierre/reinicio en procesos distintos. También captura la interfaz y la guía dentro de Android. `validation.json` contiene el resultado real; este README no sustituye los resultados CI.

El APK de CI se firma localmente con la clave persistente propia de BBY Q para la entrega. El nuevo identificador permite instalarlo junto a C16, cuya firma de desarrollo anterior puede ser distinta. La clave de firma no se guarda en el repositorio.

GPU-VIRTUAL/QSSD computacional no se anuncian como integrados. Se conservan las rutas y laboratorios anteriores sin fusionar automáticamente las PR. Consulta [el panel completo C00–C17](../docs/BBY_Q_U03_PANEL_C17_TRAINING.md).
