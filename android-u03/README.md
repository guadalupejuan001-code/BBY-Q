# BBY Q 0 — edición personal C18

Una aplicación personal con dos destinos: **Conversar** y **Mi BBY Q**. El chat es la pantalla de inicio; el entrenamiento, la memoria, las copias y las herramientas de desarrollo están en el espacio del modelo.

## Usarla

1. Escribe en **Conversar** y pulsa **Enviar**. Puedes saludar, calcular, hacer consultas admitidas por el modelo y enseñar mediante peticiones explícitas como «recuerda que Lira es robot».
2. En **Mi BBY Q**, consulta la memoria o entra en **Entrenar BBY Q**.
3. La guía incluida contiene seis dibujos y dos rutas completas: hechos/reglas y ejercicios conjuntos de parámetros.
4. Comprueba un candidato antes de activarlo. La conversación usa la misma memoria personal que recibe esa activación.
5. Exporta el ZIP de la sesión para evaluar el entrenamiento, o el JSON de la conversación para revisar sus respuestas y procedencia.

La enseñanza se inicia con una petición explícita. Las preguntas no escriben conocimiento. Una conversación nueva conserva el aprendizaje y archiva la vista anterior.

## Android y actualización

- Etiqueta: **BBY Q 0**.
- Versión: U03.18.0-personal, código **4**.
- Paquete conservado: com.bbyq.u03.training.
- Android 10 o posterior, ARM64 y x86_64.
- Firma de entrega: la clave personal persistente utilizada para C17. La clave no está en el repositorio.

Esta versión actualiza C17 con el mismo paquete y firma. Conserva la autoridad SQLite y el formato de las sesiones de entrenamiento; añade el diario de conversación.

UiKit aplica los márgenes medidos de las barras del sistema, recortes y teclado, por ventana, tanto en actividades como en los diálogos de pantalla completa. Se prueban gestos, tres botones, teclado visible, horizontal y texto grande.

## Conversación y aprendizaje

La memoria, las reglas y el aprendizaje personal conservan el núcleo U02/XI original. Para saludos y conocimiento previo acotado se reutiliza el programa y checkpoint E025 original, autenticado y ejecutado en una copia de sólo lectura. La memoria personal tiene prioridad. La procedencia de cada respuesta distingue el texto nativo, la presentación de resultados, la interfaz y la abstención.

Las preguntas personales y cálculos se ejecutan en copias para preservar los bancos personales. Las peticiones explícitas de enseñanza utilizan la misma autoridad que el entrenamiento C17. No se incorpora ningún modelo externo.

C17 no reentrena E025. Los ejercicios conjuntos modifican los bancos personales U02, y la referencia E025 conserva su checkpoint. La aplicación no promete conversación ilimitada ni integración de cómputo GPU/QSSD.

## Verificación y desarrollo

El workflow Android ejecuta:

- 5 pruebas de interfaz y conversación con límites geométricos, teclado real, toques, historial y desplazamiento real de la guía.
- Las 5 pruebas C17 de enseñanza, validación, activación, restauración y exportación.
- Las 16 pruebas de funciones originales.
- Reinicios externos originales y de entrenamiento, incluyendo la conversación persistente y la repetición exacta de mensajes.
- Autenticación de los 159 archivos protegidos, checkpoints y bibliotecas nativas.

La evidencia efectiva está en build/android-c18/validation.json, los informes de pruebas y las capturas. La versión Android probada se obtiene del dispositivo, no se supone.

Se conserva **BBY Q → w4U → QdU**. No se fusionan PR automáticamente. Consulta [el panel C00–C17 y los cambios C18](../docs/BBY_Q_0_PERSONAL_C18.md).
