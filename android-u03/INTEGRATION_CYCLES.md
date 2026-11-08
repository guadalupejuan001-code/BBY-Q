# Entrega consolidada por ciclos A00–A06 / C16 M01–M06

La fuente de implementación conservada es C16 PR #104, commit `eefb0e26c3cbe2838f7701ce300389930d902a65`, que ya ejecutó los módulos en Android (CI #42467333087). Esta revisión conserva ese núcleo, sus pruebas completas, sus candidatos guardados y las comparaciones en ambos brazos, en lugar de reemplazarlos por una implementación paralela con menor cobertura. Los intentos de la PR #105 permanecen en el historial; no se entregan los artefactos que fallaron.

| Ciclo | Trabajo comprobable |
|---|---|
| A00 | Auditoría de APK real y los 159 checkpoints. Comparación contra las ramas existentes; ninguna fuente protegida se modifica. |
| A01 / M01 | JNI original y transporte C01. ELF LOAD 16 KB; verificación adicional de todas las extensiones Python anidadas. Diagnóstico exportable sin exigir arranque Python. |
| A02 / M02 | Sesión ReasoningSession con C03/C04/C05/C09 y planes/pruebas nativos C10. |
| A03 / M03 | Checkpoints originales C06/C07/C08 autenticados. Evaluación semántica y de evidencia tipada ejecutable, no sólo archivos. |
| A04 / M04 | C11/C12 realmente entrenan, auditan seis regiones, guardan candidatos y permiten probarlos sin sobrescribir el modelo personal. |
| A05 / M05 | C02 persistencia, C13 comparación de dos brazos, C14 perfil/ablaciones, C15 rollback/replay y dos escritores/dos lectores por brazo en Android. |
| A06 / M06 | Mantener las 16 pruebas y reinicio de proceso de C16; corregir botones bajo la barra de navegación y añadir puerta geométrica de UI. APK sólo entregable si la CI de su commit exacto aprueba. |

La corrección de pantalla maneja insets de barras, recorte y teclado; botones de una sola línea y altura 48 dp. No cambia la IA ni los checkpoints. No demuestra compatibilidad con el teléfono físico del usuario: Android 15 x86_64 se prueba en emulador; ARM64 se compila y sus ELF se comprueban estáticamente. La causa individual de «Library not found» sigue necesitando el diagnóstico del dispositivo.

GPU-VIRTUAL compute no integrado; C11/C12 y caché C13 no se promocionan automáticamente. No se fusiona ninguna PR a main ni se borra la memoria privada de aplicaciones anteriores. La nueva aplicación puede coexistir con `com.bbyq.u03`.
