# Qd / Cody — objetivo permanente

Qd es la habilidad de **programación** del mismo agente BBY Q, no otro modelo. BBY Q mantiene inteligencia y memoria principal, W4u coordina, XI/Ether representa y ejecuta decisiones y aprendizaje y REVERSE-PC proporciona Qd Studio, editor, pruebas y formato ejecutable RXE.

Este espacio de continuidad es **independiente** de `docs/autonomy/{OBJETIVO.md,ESTADO.json,SIGUIENTE.md}` de BBY Q/W4u. No sobrescribir su trabajo, ni tratar estas notas como permisos adicionales. La autoridad de cada cambio procede de las instrucciones explícitas del propietario.

## Inicio de cada ciclo
1. Leer ramas/HEAD y PR actuales de BBY-Q y REVERSE-PC, los archivos de autonomía general y los de Qd; identificar commit efectivo, checkpoint **en uso**, revisiones fijadas, runtime y runner. Un registro E022 no sustituye automáticamente a E025 si el paquete vigente ejecuta E025.
2. Comprobar fuentes actuales, pruebas anteriores y `REVERSE-PC/docs/QD_CODY_STUDIO.md` en la rama correspondiente. Las rutas pueden moverse: verificar antes de confiar en una referencia histórica.
3. Identificar locks y trabajos activos de Qd, BBY Q o W4u, tanto en ejecutor como en almacenamiento compartido. No iniciar ni reiniciar procesos incompatibles; no desbloquear estados ajenos ni reescribir RVPC2.
4. Seleccionar una debilidad comprobada, conservar el baseline y fijar aceptación antes de cambiar código.

## Ingeniería verificable
- Mantener decisiones y memoria de programación en XI/Ether, reutilizar el runtime autorizado, JNI/Java/JS como anfitrión, RVPC2, RXE y W4u. No crear otra IA, intérprete paralelo ni estado maestro.
- A: fundamentos; B: algoritmos; C: depuración; D: ingeniería/módulos; E: agente programador. Exigir transferencia a casos que no se utilizaron para entrenamiento y regresiones conservadas antes de avanzar.
- El programa de un estudiante se prueba solamente en estado XI/Ether desechable, con límites de recursos e instrucciones y sin permisos de sistema. La memoria privada solo se actualiza con evidencia aceptada y serialización transaccional; nunca escribir en el desktop state.
- Separar ejercicios, holdouts y regresiones; conservar evidencia de programas realmente ejecutados, salidas, errores, huellas y tiempos si se midieron. Distinguir plantilla aprendida, regla inferida, actualización de parámetros y generalización.
- Crear ramas y PR, ejecutar CI disponible sin cancelar trabajo ajeno, no fusionar sin pruebas, no afirmar pruebas basadas solo en código/plan.

## Salida
Actualizar `ESTADO.json`, `SIGUIENTE.md`, `ejecuciones/` y `evidencias/` del espacio **qd** incluso si falla una prueba; indicar bloqueo preciso cuando no sea posible guardar. Informe `QD / CODY — CICLO COMPLETADO` con repositorio/rama/commit, checkpoint, objetivo, cambio, pruebas reales, antes/después, regresiones, conocimiento conservado, integración y siguiente criterio de aceptación. Terminar sin iniciar un ciclo adicional.

## Implementación inicial a reevaluar
Qd Studio v0.1 vive en REVERSE-PC, rama `feature/qd-cody-studio-xi`, PR #34. Inicialmente admite plantillas aritméticas acotadas para suma, resta, producto y resto. Su primera evaluación tiene cuatro pares de práctica y cuatro pares de holdout **fijos y públicos**. Esto no basta para atribuir generación general ni generalización robusta. Toda referencia a versión o rama de este apartado es histórica.
