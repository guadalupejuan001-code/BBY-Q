# BBY Q · X10 Android 2.1 E01

`com.bbyq.personalx`, Android 10+, ARM64 y x86-64. Una transacción SQLite
publica juntos mensajes, contexto, lecciones, estados y comprobante del turno.
El reintento con el mismo identificador devuelve el resultado guardado; un
identificador reutilizado con otro texto se rechaza. Un fallo anterior al commit
revierte todos los cambios. Los archivos de la versión 1 se conservan tras la
migración de conversación, agentes y mensajes.

Java administra almacenamiento y bytes. Los programas XI originales ejecutan
intención, lecciones paginadas, texto por páginas, razonamiento acotado,
composición, contexto y reformulaciones. La base de 480 conceptos y sus modelos
originales se conservan. Las consultas ordinarias no reentrenan esa base.

| Motor | Integración móvil | Alcance conservado |
| --- | --- | --- |
| X10 | Sesión paginada, P01/P03/P04/P05/P06 | Gramáticas acotadas, no conversación general |
| VQC3/QRL3 | Mismo chat, consulta y política | 1.000 cúbits simulados por agente; E01: 11.500 y 11.512 episodios |
| QChat100 | Saludos admitidos y `qchat TEXTO` | Generador de 100 cúbits, 74.660 actualizaciones, 16 tokens máximos |
| QMemory | Claves binarias persistentes en el chat | 250 asociaciones de cuatro sitios; 1.000 cúbits totales, sin MPS |

El V3 nativo conserva su arquitectura histórica de grupos independientes.
QChat100 conserva un codificador Clifford fijo y pesos de salida entrenados.
QMemory usa la puerta de escritura ya aprendida y lectura Z; reemplazar una
asociación reinicializa ese slot y vuelve a escribir. No se atribuye ese reemplazo
al entrenamiento de ángulos ni a la corrección recurrente experimental.
Las variantes, campañas y herramientas de escritorio siguen en sus rutas
originales; esta app no porta Node, Python, las tareas de escritorio ni sus
grandes corpus externos. No se afirma una IA general o ventaja cuántica.

La actualización archiva los modelos 2.0 y conserva lecciones, historial y
asociaciones binarias. Un agente V3 entrenado adicionalmente en el teléfono
conserva sus parámetros personales. Los modelos E01 y sus resultados se
documentan en `integration/balance/README.md`.

XI admite el antecedente de QChat para los seguimientos de su currículo, como
«dime más». Los temas nuevos y saludos reciben contexto vacío. Ese antecedente
pertenece al generador, sobrevive al reinicio y al paso por órdenes de memoria
o V3, caduca tras 32 turnos y se elimina con `@context clear`.

Ejemplos desde una misma conversación:

```text
calcula 17 + 25
¿qué dije antes?
memoria guarda faro 1
memoria consulta faro
memoria corrige faro 0
quantum v3 estado
quantum v3 planea 3 6
qchat hola
```

Los programas usan sesiones nativas acotadas: el estado no se serializa después
de cada byte o token. Solo se materializan las páginas necesarias; la memoria
lógica compacta y los checkpoints RVPC2 se mantienen. Las sesiones JNI tienen
identificadores verificados, cierre explícito y un máximo de ocho handles.

La preparación verifica hashes de modelos y fuentes. La CI ejecuta fixtures
del motor histórico, compila ambos ABI y prueba conversación, memoria real,
reanudación, rollback, corrupción, migración, reintentos simultáneos e interfaz
en Android 15. La evidencia pertenece a cada ejecución; una compilación sin
pruebas aprobadas no constituye una entrega validada. La app funciona sin red.
