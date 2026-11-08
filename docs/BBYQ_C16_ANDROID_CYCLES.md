# BBY Q U03 C16 — integración móvil por ciclos verificables

Base exacta: PR #103, `58ef4bff2e6d53dcbb55cc97d0d4249807ffb750`. La rama anterior y los 159 archivos protegidos se conservan. No fusionar automáticamente.

| Subciclo | Entrega exigida | Prueba de cierre | Estado inicial |
|---|---|---|---|
| M01 | Bibliotecas JNI y diagnóstico de arranque | ELF 16 KB en todos los ABI, carga real, diagnóstico exportable | en implementación |
| M02 | C03/C04/C05/C09/C10 en rutas móviles accesibles | Recibos/snapshots equivalentes, memoria verificada, plan XI real y ausencia de escritura en plan | en implementación |
| M03 | Checkpoints originales C06/C07/C08 ejecutables | SHA de las campañas originales y predicciones XI reales; no simples fuentes archivadas | en implementación |
| M04 | C11/C12 entrenables y comparables en laboratorio aislado | Feedback nativo, huellas de pesos y evaluación independiente; memoria personal intacta | en implementación |
| M05 | C01/C02/C13/C14/C15 adaptados como experimentos móviles | Paridad de transporte/persistencia, caché acotada, perfil JNI, rollback/replay y concurrencia en bases desechables | en implementación |
| M06 | APK, interfaz y pruebas Android integradas | Todas las rutas anteriores accesibles y comprobadas; SHA final y alcance explícito | pendiente |

No equivale conservar código a conectarlo. Ninguna fila se marca verificada sólo porque el archivo exista. C11/C12 y C08 no se promocionan por estar disponibles; pueden ejecutarse en bancos experimentales y compararse sin sobrescribir los siete bancos del usuario. C13 no se activa globalmente sin control de concurrencia y paridad. C06/C07 mantienen su alcance de semántica/evidencia sintética, no verdad externa. El objetivo es integrar capacidades ejecutables y diagnósticos sin inventar superioridad de modelos.

El error «Library not found» del teléfono aún no tiene traza exacta. Se detectó en la APK anterior `libreverse_os.so` con alineación ELF 4096; se corregirá a 16384 y se expondrá diagnóstico ABI, directorio nativo y causa real. Eso no basta para afirmar que el dispositivo del usuario ya funciona.

GPU-VIRTUAL/QSSD no se declaran integrados en el cálculo de IA: requieren su propia ruta de cómputo y pruebas. No se reemplaza la arquitectura BBY Q → w4U → QdU ni se introduce otra autoridad de memoria.
