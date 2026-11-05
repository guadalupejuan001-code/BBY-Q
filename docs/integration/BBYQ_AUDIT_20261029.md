# Auditoría de integración BBY Q — 2026-10-29

## Estado y política de integración

Main observado: `337e161af2b333b70c9bc938741e7c08097093e0`. 43 ramas, 11 PR abiertas. Los candidatos E030–E034 y varios registros de autonomía son divergentes respecto a main; NO se deben fusionar en masa ni reemplazar checkpoints de usuario. La rama de auditoría parte de main y conserva intactos sus archivos de ejecución.

Arquitectura objetivo: **BBY Q → w4U → QdU**, XI/Ether como lógica y ejecución. QdU vive en REVERSE-PC; no duplicar la memoria maestra ni copiar su motor a BBY Q.

## Evidencia reproducible existente

- E034, [CI 40808605984](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40808605984), completada success sobre `7d8d8203d63ba8328d0f2ca6a236f20ae39f87e3`.
- E034: 48/48 consultas compuestas, 96/96 referencias tipadas, 168 casos relacionales y 144 temporales conservados. En el informe de origen constan 761 comprobaciones propias y 1069 en reproducción/regresiones.
- Checkpoint E034 declarado: `ai/checkpoints/e034/composition-model.rvp.gz.b64`, SHA256 RVPC2 `876d3f2a82698e9582f17043028d9a75b454e4b5ebaf7cc5949b65a5bac58a10`; requiere verificar bytes y restauración antes de promoverlo.
- Tamaño RVPC2 E034 declarado 863594 bytes; comprimido 123175 bytes. Mediana de consulta compuesta 163.84 ms; pico RSS nativo 39964 KiB. Son métricas de runner Linux y no del teléfono.
- La versión Android REVERSE sigue utilizando E025; E034 no está desplegado.

## Integración pendiente, no completada

Orden de revisión: PR #29 diagnóstico → #30 composición E026 → #33 coexistencia E027 → #35/#36 aprendizaje y conservación E030 → #37 diccionario E031 → #38 tiempo E032 → #40 relaciones E033 → #41 composición E034. PR #28 es autonomía de QdU documental y debe reconciliarse con la estructura propia de QdU en REVERSE-PC; PR #39 es comparación de referencia, no nueva inteligencia que deba mezclarse.

No fusionar ramas antiguas de E005–E022 sin demostrar que sus cambios no están ya contenidos en main. Las pruebas de una PR no acreditan la suma de ramas. Requiere integración por etapas con CI, verificación de SHA de checkpoints y validación Android antes de mover main.

## Próximo ciclo de integración

1. Comparar archivos y dependencias de PR #29–#41 contra main y el candidato más reciente; clasificar incluidos, redundantes, incompatibles y exclusivos.
2. Seleccionar una línea de código E034 y rebasarla sobre main en una rama aislada sin copiar estados de producción ni sobrescribir E025.
3. Ejecutar suites E025/E027/E028/E029 y E030–E034 con checkpoints inmutables; medir tiempos, RSS y tamaño en el mismo runner, guardar logs.
4. Reconciliar w4U y QdU por contrato sin introducir un modelo externo.
5. Solo proponer merge después de CI verde y revisión de conflictos. No cambiar la APK ni las firmas en este ciclo de auditoría.

**Resultado de esta auditoría:** inventario y evidencia histórica comprobada, no prueba nueva de rendimiento ni fusión de funcionalidades.
