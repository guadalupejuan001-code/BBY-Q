# Comparación de inferencia SOVENGI / BBY Q

Solicitud: probar ambas sin fusionarlas ni modificar sus modelos. Rama exclusiva de evaluación; no fusionar su reemplazo temporal del workflow de desarrollo.

Se conservan los originales: BBY Q E032 fuente ca501af7e3306cea28eaf41f0f6d9e1db825eeda, cápsula d2c5e4ebb2b0c3b7af74abc881d6f8c1a5ff2e106f621d0ceba5cb312b525048 y checkpoint f1c2ace6a8d35643c0ae68103f3cb0aa33a0325c9fea004f00fd5e38d60ffb56; SOVENGI main 58345eec2cb6a05d3fb0491e3a2f3d914cd1a48c, configuración predeterminada y catálogo completo de 35 modelos. Solo se cambia en una copia la ruta de sesión privada para aislar la prueba. No hay entrenamiento, mezcla de pesos, despliegue ni modificación de main.

## Protocolo fijado antes de ejecutar

32 preguntas nuevas: ocho de posesión temporal, ocho de memoria cotidiana, ocho de composición de hechos y ocho abiertas; ambas reciben los mismos hechos y pregunta final. Las dos familias específicas exponen también las limitaciones de cada diseño. Los sujetos de temporalidad no son los del currículo E032. No se afirma ausencia de palabras comunes en todos los corpus históricos de SOVENGI.

El examinador no inserta respuestas ni interpreta preguntas para los motores. BBY Q recibe los hechos como turnos nativos sobre una copia del checkpoint; SOVENGI recibe esos mismos mensajes originales en su pipeline de contexto. Se mide por separado el ingreso de hechos de BBY Q. Los tiempos de la consulta incluyen arranque y E/S de estado nativos y, en SOVENGI, carga perezosa y preparación de contexto. No son comparaciones de kernels ni de igual número de tokens. SOVENGI conserva su coordinador y hasta cuatro generaciones de 48 tokens; BBY Q conserva su respuesta nativa breve.

Un solo runner ubuntu-latest y un solo CPU lógico por worker, un hilo Torch. Tres repeticiones de cuatro casos para medir latencia tras la primera pasada; el conjunto SOVENGI rota y se conserva su traza. Sin pruebas simultáneas entre brazos. Se registra CPU, tiempos individuales, errores y RSS de procesos. El pico RSS muestreado cada 10 ms suma worker y descendientes; puede contar páginas compartidas dos veces. Se excluye el driver externo. No mide energía, Android ni RAM mínima garantizada.

Los 32 criterios semánticos se congelan en cases.json. La corrección se revisa sobre las respuestas originales después de generar, sin ajustar modelos, ejemplos ni inferencia. La revisión es de IA, no humana independiente; un simple acierto literal puede ser incoherente. Se informan resultados por categoría; el total no es una puntuación de inteligencia general.

## Aceptación de ejecución

44 llamadas de consulta por brazo, 32 de calidad y 12 de tiempo. Copias originales y pesos deben mantener sus hashes; cualquier fallo conserva evidencia parcial y se identifica como fallo técnico. Un resultado semántico negativo es un resultado válido. Solo la disponibilidad de una nueva ejecución prueba acceso actual al runner.

Workflow existente reutilizado: .github/workflows/bbyq-e029.yml, job native-e029, timeout 25 minutos, mismo mecanismo concurrency. El script run.py es examinador externo Python; la inteligencia de BBY Q continúa en XI/Ether y SOVENGI usa su motor propio sin cambios.
