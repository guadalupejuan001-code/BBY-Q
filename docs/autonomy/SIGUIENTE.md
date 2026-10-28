# Siguiente ciclo

## Base real y trabajo completado

E025-Chain-1 + W4u 0.1 se publicaron en BBY-Q/main; no regresar a E022 porque el estado antiguo lo mencionaba. La revisión observada antes de este diagnóstico fue 783d7aff4385687d416e2f3a67ed81dca89d9fb9. Resolver nuevamente los HEAD y checkpoints al iniciar.

Diagnóstico del PR #29, rama `autonomy/bbyq-two-facts-e025-20261028`, código `2f0f5eb02b851faaa4a5157096ef851cd516184f`:
- 96/96 controles de hechos individuales.
- 0/48 respuestas con cobertura de dos hechos, con 24 sujetos y dos peticiones fijas ES/EN.
- 31 comprobaciones E025 y 21 del núcleo W4u aprobadas.
- Cápsula y semilla originales intactas. Son métricas nuevas de diagnóstico, no aprendizaje añadido al agente publicado.

Evidencia: https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40754152612
Informe persistente: `docs/autonomy/evidencias/ciclo-dos-hechos-e025-20261028T1925-results.json`. Transcripciones completas: artefacto enlazado en el registro. Los casos se enseñan a copias desechables de RVPC2; no se promovieron a checkpoint.

## Objetivo siguiente: composición nativa de dos hechos

1. Leer primero el PR #29 y los cambios posteriores; no repetir el diagnóstico idéntico sin cambiar una hipótesis.
2. Inspeccionar las transcripciones de las dos formulaciones para localizar en XI si se descarta una intención, falta representar dos consultas o falta componer sus respuestas. El resultado 0/48 por sí solo no identifica el componente defectuoso.
3. Implementar en XI/Ether una petición compuesta que seleccione y exprese dos hechos respaldados del mismo referente. Python/JS solo examinan o transportan: no generan la respuesta del agente.
4. Conservar E025 y su reconstrucción exacta. Para un programa cambiado usar versión candidata con identidad y manifiesto propios; no modificar los hashes esperados para fingir identidad con E025. Conservar la memoria anterior y demostrar una migración compatible si procede.
5. Usar las 48 consultas publicadas como conjunto de desarrollo. Separar enseñanza de patrones y reservar otro examen: 24 sujetos nuevos y reformulaciones no utilizadas para ajustar el código; 48 consultas ES/EN. Registrar los conjuntos y sus diferencias.
6. Añadir controles con un hecho ausente, negación y cambio de sujeto. Comprobar las proposiciones completas y evidencia, no solo palabras coincidentes.

Criterio de aceptación: mejora medible frente a 0/48 del conjunto de desarrollo; 48/48 consultas independientes que expresen ambos hechos respaldados sin mezclar referentes; controles sin invención y persistencia tras reinicio. Conservar las regresiones E025/W4u y las de E022 afectadas por cualquier cambio compartido. No promover un candidato con pérdidas.

## Ejecutor y continuidad

Usar el workflow configurado E025, con runtime fijado a a1b935ae0adf38615996bac92727e95289ad7cc1 y Mundo X e2778d962af22f6f1a0794058dd4685fc2573966, salvo nueva configuración verificada. Comprobar primero trabajo activo. W4u ahora tiene fuentes y pruebas en ai/xi/w4u y docs/W4U_ENGINE.md; el antiguo bloqueo de fuentes ausentes ya no aplica. Las pruebas de fixtures no equivalen a coordinación general del desarrollo ni a una prueba Android nueva.

Actualizar ESTADO.json, este archivo y el registro incluso si falla el intento. Guardar la causa concreta y la operación pendiente; no repetir un intento idéntico sin evidencia nueva.
