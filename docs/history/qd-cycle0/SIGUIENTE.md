# Qd — siguiente ciclo técnico

## Situación de partida

El último diagnóstico de Qd (2026-10-28) encontró `REVERSE-PC#34` abierto en `feature/qd-cody-studio-xi` (`fe2ca5a27c810a18bc1082b47f767b6141f688b3`). La UI pasó CI, pero la CI Android integrada aún estaba en ejecución en el momento de verificarla: [run 40746891634](https://github.com/guadalupejuan001-code/REVERSE-PC/actions/runs/40746891634). Comprobar el resultado ACTUAL antes de actuar; un paso parcial completado no equivale al workflow aprobado. El motor E025/W4u se fija en el workflow de REVERSE-PC, no en el estado histórico E022 de la autonomía general.

Se creó continuidad propia, sin ejecutar aprendizaje nuevo ni modificar código de producción. Si una rama/PR más reciente ya resuelve la debilidad, seleccionar otra, no repetir trabajo.

## Prioridad — medir y reforzar la generalización aritmética

**Debilidad comprobable:** en `QdEngine.java` las cuatro entradas de `HELD` son fijas y se conocen por el código; `judge.xi` / `learn.xi` solo aceptan exactamente ocho respuestas; `qd-native.cjs` repite ocho pares fijos en las cuatro familias. Ello permite almacenar un patrón que apruebe esas entradas sin funcionar fuera de ellas.

**Criterio de aceptación (definir antes de editar):** el evaluador debe rechazar al menos una plantilla deliberadamente sobreajustada que pase los ocho casos antiguos pero falle entradas reservadas nuevas; una plantilla aritmética correcta debe aprobar todos los casos adicionales independientes, con retención RVPC2, sentinel W4u intacto, fallo transaccional y sin regresiones E025/desktop/Android. Registrar tamaño, tiempo y número REAL de casos. Si se cambia el total de pruebas, armonizar `QdEngine.java`, `judge.xi`, `learn.xi` y ensayos sin permitir que el anfitrión sustituya decisiones XI.

1. Resolver HEAD/PR/checkpoints vigentes. Comprobar bloqueo W4u, Qd y ejecución CI; no reescribir `feature/qd-cody-studio-xi` mientras otra campaña la modifica.
2. Conservar baseline de fallos con una plantilla sobreajustada, una correcta y controles de división/resto por cero. Mantener los inputs de evaluación excluidos de los ejemplos de aprendizaje.
3. Introducir holdouts variables reproducibles con semillas registradas en la evidencia, sin compartirlos con el programa candidato durante la enseñanza. Evitar que una semilla conocida se confunda con generalización estadística; documentar límites y contar casos únicos.
4. Programas, decisión XI, evaluación independiente y guardado transaccional deben probarse en el runtime REAL aislado; ejecutar CI de Qd e integración Android. Comprobar persistencia tras reiniciar y no afectar BBY Q ni W4u.
5. Si CI o memoria están ocupados, cerrar con bloqueo verificado, sin ejecutar otra campaña ni promocionar aprendizaje.

Cuando todo pase, preparar la etapa B (condiciones/ciclos) conservando el mismo runtime y sin introducir una segunda memoria.
