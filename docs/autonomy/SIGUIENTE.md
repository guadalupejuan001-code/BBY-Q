# Siguiente ciclo

## Base vigente comprobada

Candidato **E027-CtxCompose-2-dev** en la rama `autonomy/bbyq-context-composition-20261028`, PR #33, revisión probada `9485ec2e366718de8d84ff82e5310d80287c84a9`. Resolver de nuevo referencias, PR y trabajo activo antes de continuar.

La propuesta anterior partía de E026 aislado, pero main añadió E027 con un constructor que volvía a E025. Este ciclo priorizó reunir las capacidades existentes para no perder ninguna al avanzar. No repetir la integración ni volver a construir una rama sobre E026 aislado sin contrastar los cambios posteriores.

CI nueva: https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40773600595
- 31 pruebas E025 y 31 sobre el candidato, más 21 del núcleo W4u.
- 429 comprobaciones de archivo contextual: 200 registros, 42.200 bytes ejercitados; 114.688 bytes de capacidad nominal, no íntegramente ejercitada aquí.
- 48/48 consultas compuestas de desarrollo y 48/48 con sujetos nuevos dentro de cuatro formas diseñadas; 150 controles adicionales.
- 11 pruebas de coexistencia: el archivo sobrevive a consultas dobles y vaciarlo no borra hechos ni composición.
- Cápsula c7ad1e99d556d730cb6dd64feceb39c86eed8d52b86b55da6d3ce002a5032fc8; semilla E025 conservada ce058a65092dd9892b6fd55276a17287b764a16bc526ccbfa0085154baef9631.

Informe persistente: `docs/autonomy/evidencias/ciclo-contexto-composicion-20261028T2138-results.json`. Cápsula, XI enlazado y transcripciones: https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40773600595/artifacts/12854310856. El examinador de composición conserva la etiqueta E026, pero el hash del informe demuestra que examinó la cápsula combinada.

## Objetivo pendiente: aprender una forma nueva en XI con código fijo

1. Retomar esta base combinada y leer su documentación antes de introducir otra representación. Examinar los mecanismos existentes de enseñanza/normalización para reutilizarlos.
2. Elegir una forma nueva de pregunta doble ES y otra EN que aún se rechacen; medir el resultado antes de enseñar.
3. Enseñar cada forma con dos sujetos distintos y roles supervisados; XI debe validar/inducir y persistir el patrón en RVPC2. El código docente solo transporta los ejemplos.
4. Reservar otros 24 sujetos para 48 consultas ES/EN y controles de ausencia, negación y cambio de sujeto; las respuestas del examen quedan fuera del proceso de aprendizaje.
5. Comprobar hash idéntico del programa antes/después de enseñar y un cambio de memoria solo en las regiones aprendidas declaradas. Reabrir el checkpoint para comprobar persistencia.

Criterio de aceptación: mejora medible hasta 48/48 respuestas completas en ese examen acotado por cambio persistente de memoria, con código fijo; conservar contexto, las formas anteriores y regresiones pertinentes. Si falla, conservar el candidato validado y registrar la causa, sin promover resultados parciales.

## Alcance e integración

Archivo contextual no equivale a que todas las preguntas ya usen el historial semánticamente. La recuperación continúa explícita mediante @ctx. Esta integración no añadió patrones aprendidos ni conversación abierta general.

La cápsula tiene identidad propia y no fue desplegada en Android. No sobrescribir memorias privadas existentes. W4u fue probado con fixtures y una acción tipada nativa, no como coordinador autónomo de ingeniería del repositorio.

Usar el workflow E027 configurado con runtime a1b935ae0adf38615996bac92727e95289ad7cc1 y Mundo X e2778d962af22f6f1a0794058dd4685fc2573966, salvo configuración nueva verificada. Actualizar ESTADO.json, este archivo y el registro incluso si el intento falla.
