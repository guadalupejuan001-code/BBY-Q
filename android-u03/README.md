# BBY Q U03 Android — auténtico núcleo U02 y etapas C00–C15

Esta aplicación **no usa el motor Android antiguo X10/E02 para sustituir U02**. Transporta los fuentes Python originales U02 (unified Session, C1, contratos, QMemory, VQC3, QRL3, E02, QChat100), modelos y estado RVPC2 al intérprete JNI original de REVERSE-PC, con Python 3.12 integrado localmente y una base SQLite-WAL privada.

El mismo bytecode/programa XI se pasa a `reverse_pc::rvpc2::Runtime` dentro de `libreverse_os.so` y se exportan los checkpoints exactos por JNI. En Android no se necesita red ni servidor Python remoto. La aplicación tiene paquete separado `com.bbyq.u03`, no sobrescribe datos de `com.bbyq.personalx`. La adaptación móvil, el empaquetado y el backend Java/Python son nuevos; los originales 159 archivos/checkpoints congelados **no se modifican**.

C11/C12 han probado entrenamiento real sobre copias aisladas y siguen sin promoción; C13 cache no se habilita; C14 es una instrumentación de benchmarking, C15 una campaña Linux de concurrencia/recuperación; ninguno es un "motor nuevo" que deba sustituir checkpoints. Los informes y fuentes históricos se incluyen como referencia, sin presentar como validación Android las pruebas exclusivas de Linux.

La APK sólo debe describirse como **U03 Android funcional** cuando compile, arranque, y verifique en el emulador: 7 bancos autenticados, un turno aritmético C1 nativo, una misión VI/QRL/QMemory/QChat/E02, feedback real, reintento idempotente y persistencia tras reinicio. Si cualquiera falla, no etiquetarla como validada.

La compilación usa Chaquopy 17.2 para Python 3.12, el intérprete XI JNI fijado de REVERSE-PC y SQLite de Python empaquetado. Dependencias Android se descargan durante CI. Estado de modelos U02 inicia frozen; nunca se ejecutan experimentos de entrenamiento C11/C12 sobre la memoria del usuario automáticamente.

El usuario puede abrir un panel de estado para consultar los ciclos C00–C15 sin introducir otra autoridad de memoria o razonamiento.
