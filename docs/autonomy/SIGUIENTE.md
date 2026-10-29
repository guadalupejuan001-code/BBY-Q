# Siguiente ciclo: ampliar representación temporal y aprendizaje

## Continuidad real
Prioridad directa del usuario: inteligencia y tiempos verbales ES/EN.
Candidato E032 en PR #38, rama `feature/bbyq-temporal-learning-20261029`,
código probado `ca501af7e3306cea28eaf41f0f6d9e1db825eeda`.
Main inicial `c93592e0cce4ccfdb3d66a062e6ab737a643dc4a`. Resolver referencias y actividad
actuales antes de continuar; no crear otro ciclo si hay uno activo.

CI https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40795445276, completed/success:
- 48 formas aprendidas por XI desde 96 ejemplos con roles supervisados.
  Se necesitan dos sujetos Y objetos distintos; duplicado no habilita.
- 144/144 preguntas en 24 sujetos y cuatro objetos no usados en demostraciones;
  E031 sobre la misma memoria obtiene 0/144 respuestas temporales exactas.
- 96 controles de aislamiento: evidencia pasada no implica presente/futuro.
- Futuro siempre no confirmado; negación y contradicción dentro de la misma
  categoría, consultas sin publicar hechos y persistencia verificadas.
- 539 comprobaciones; 31 E025 original + 31 candidato + W4u 21 y acción [4,2].
- E030 aprendido y admisión E029 conservados; CLI real de diccionario comprobado
  con perro/dog sobre la cápsula E032. No se reimportó el diccionario.
- Hash de programa igual antes/después de enseñar:
  `d2c5e4ebb2b0c3b7af74abc881d6f8c1a5ff2e106f621d0ceba5cb312b525048`.
- Modelo aprendido durable: `ai/checkpoints/e032/temporal-model.rvp.gz.b64`.
  RVPC2 `f1c2ace6a8d35643c0ae68103f3cb0aa33a0325c9fea004f00fd5e38d60ffb56`. Enseñanza solo cambió la región
  decimal `8650000000000000000`, longitud 86016; conocimiento anterior intacto.
  Checkpoint guardado ANTES de ingresar hechos temporales de examen.
- Cápsula, registros y transcripciones: https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40795445276/artifacts/12863926371.

La reproducción de la base E031 fue verificación exacta del entorno, no
aprendizaje nuevo. El aprendizaje nuevo es de las 48 formas supervisadas y
su uso temporal acotado. El motor de posesión/tiempo es ingeniería XI.

## Qué falta y cómo avanzar
No afirmar dominio de tiempos verbales completos: solo posesión, un token
ASCII por sujeto/objeto, tres categorías temporales. Ayer/hoy/mañana son
formas docentes que etiquetan esas categorías, sin fecha anclada al reloj.
No hay orden de dos eventos dentro del pasado ni paso automático de días.

1. Revalidar ramas/commits/checkpoints y exclusión del workflow existente.
2. Restaurar el checkpoint E032 durable con cápsula compatible y conservar
   los E030/E031 anteriores. Usar direcciones como cadenas decimales + tamaño.
3. Añadir una representación de eventos con referente temporal explícito,
   orden y procedencia; poder preguntar por estado antes/después de cambios.
   Separar observación pasada/presente, previsión, intención y condición.
4. Mantener roles/conjugación aprendidos desde ejemplos con código fijo.
   Extender a otras relaciones requiere representar el predicado semántico:
   no enseñar comer/mover como si fueran posesión. No ampliar solo un listado
   de frases y contar eso como razonamiento general.
5. Evaluar historias nuevas ES/EN con cambios de estado, negación, orden de
   eventos y futuro incumplido; reservar sujetos/objetos y oraciones completas.
   Aceptación: respuestas derivadas del orden de eventos con evidencia, sin
   mezclar épocas ni convertir una intención en un hecho; conservar 144 casos
   actuales y regresiones pertinentes.
6. Reintegrar CI general E029/E028/E027 y pruebas históricas de cantidades.
   El empaquetado actual excluye en futuras ejecuciones la copia redundante
   de bancos del smoke test; no cambia código/modelo ni resultados ya probados.

Usar solo el runner E029 ubuntu-latest y pins actuales REVERSE-PC
a1b935ae0adf38615996bac92727e95289ad7cc1/Mundo X
e2778d962af22f6f1a0794058dd4685fc2573966. Sin modelos externos.
W4u se verificó con fixtures y acción nativa, no como coordinador autónomo
de ingeniería. No desplegar ni reemplazar memorias privadas de Android aquí.
Actualizar ESTADO, SIGUIENTE y registro incluso ante fallo.
