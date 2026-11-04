# BBY Q · X — Android personal

Aplicación independiente `com.bbyq.personalx`, para Android 10 o posterior,
con bibliotecas ARM64 y x86-64. Chat, historial y modelos en almacenamiento
privado; sin permiso de Internet y sin servidor externo.

Reutiliza el motor conversacional XI X08 y su estado canónico de 480 conceptos /
960 relaciones, con el contrato de texto existente. Los agentes VQC3/QRL3
conservan el checkpoint nativo de 10.000 episodios por agente, sin MPS.
No implementa un algoritmo conversacional cuántico nuevo ni pretende portar
toda la capa SQLite/Node X10 del escritorio. Se conserva la aplicación de PC.

La interfaz ofrece chat, enseñanza mediante las lecciones existentes, consultas,
aritmética, historial persistente y exportación de la conversación. En el menú
Mis agentes se consultan sus estados y se ejecuta o continúa la política QRL3.
La interpretación, las respuestas y el aprendizaje se ejecutan en los programas
XI originales; Java gestiona la interfaz, el transporte y la publicación local.

La CI verifica los hashes, prueba seis conversaciones con el ejecutor original,
compila JNI para ambos ABI y ejecuta pruebas nativas e interfaz en Android 15.
La descarga incluye la APK y la evidencia. No solicita permisos de contactos,
micrófono, ubicación ni archivos compartidos; la exportación usa el selector
de documentos de Android.
