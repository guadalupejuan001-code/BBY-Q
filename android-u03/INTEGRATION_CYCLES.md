# Integración Android por ciclos A00–A06

Base fija: PR #103, `58ef4bff2e6d53dcbb55cc97d0d4249807ffb750`. No fusionar automáticamente, no sustituir estados anteriores, preservar los 159 archivos/checkpoints y BBY Q → w4U → QdU.

| Ciclo móvil | Entrega y aceptación |
|---|---|
| A00 | Auditar APK real, fuentes activas vs archivadas y candidatos C06–C08 originales. |
| A01 | Corregir ELF 16 KB; carga JNI diagnosticable; comparación del transporte C01 con llamadas originales. |
| A02 | C03/C04/C05 en la ruta normal; C09 memoria y C10 planificación con ejecución XI, no sólo panel. |
| A03 | C06–C08: cargar los checkpoints originales autenticados, ejecutar semántica y evaluación de evidencia sin sobrescribir decisiones de C1. |
| A04 | C11/C12: entrenamiento conjunto reproducible en copia aislada, auditoría de pesos reales, comparación y conservación del candidato sin promoción automática. |
| A05 | C02/C13/C14/C15: persistencia, caché experimental, ablaciones y pruebas móviles reales de rollback/replay/concurrencia; sin fingir resultados Linux como Android. |
| A06 | Pruebas Android end-to-end y de reinicio; manifiesto de capacidades basado en resultados; APK firmada con SHA y cobertura ARM64 explícita. |

Estados de ciclo: sólo `verificado` después de una ejecución satisfactoria y vinculada a su commit; código preparado no significa validado. GPU-VIRTUAL no se declara integrada sin despacho y evidencia reales. No se presupone que el error reportado en el teléfono tenga una causa concreta sin su registro.

Hallazgo A00: en la APK anterior `libreverse_os.so` ARM64 tenía segmentos LOAD alineados a 4096, mientras las bibliotecas Chaquopy tenían 16384. Es un defecto objetivo de compatibilidad; por sí solo no identifica la causa del error en el dispositivo del usuario.
