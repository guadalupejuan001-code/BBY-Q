# Siguiente ciclo

## Base comprobada y estado real
Candidato **E030-Learned-Frames-1-dev**, PR #35, rama `autonomy/bbyq-learned-forms-20261028`,
código probado `0061bcda177fc31f609939860ed9d0a75e222d50`.
Main inicial `beea73210fb3e6375a6bd90f3b88b476a4c175d2` ya contenía E029/E028.
Las notas iniciales todavía apuntaban a E027 combinado; se contrastaron con
código, commits y ejecuciones reales. Resolver todo de nuevo al activar.

CI: https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40781527990 — completed/success.
- Aprendizaje nativo XI: **181 comprobaciones**, dos marcos de pregunta ES/EN.
  **0/48 antes → 48/48 después**, 24 sujetos reservados distintos de tutora/tutorb.
  E029 con la misma memoria aprendida: **0/48** (ablación del nuevo intérprete).
- Cápsula fija antes/después: `c9a33a322f58ac6d93f18ff3c59678ef637ac9612bb71845e122e8f5c9de43f9`.
  Solo cambió la región aprendida T..T+3071 durante enseñanza; núcleo/bindings
  y memoria anterior iguales. Reinicio nativo por turno. Examen sin adaptar patrones.
- Regresiones sobre la cápsula nueva antes de enseñar: E025 **31**, E029 **285**,
  E028 **464**, E027 **429**; W4u **21** y acción tipada nativa del candidato.
  Tras enseñar: consultas canónicas, conocimiento E025, archivo, borrado,
  negación, ausencia, mezclas y persistencia incluidos en las 181 comprobaciones.
- Semilla E025 intacta `ce058a65092dd9892b6fd55276a17287b764a16bc526ccbfa0085154baef9631`.
- Checkpoint experimental `e030-learning/learned-checkpoint.rvp` en el artefacto:
  `5a0d469fc70248a2afc7a6a319a9a854d6498fa7682d9351e543f0d701ae7cf6`.
  Checkpoint previo, posterior al examen, cápsulas y transcripciones conservados.
  Artefacto https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40781527990/artifacts/12857507917; caduca 2027-01-26T22:38:33Z.
  Los hechos sintéticos del examen no son conocimiento publicado del agente.

## Objetivo siguiente: reconciliar fuentes antes de unir candidatos
E030 continúa main/E029 y conserva el PR #33 con E026+E027 como candidato
independiente. No afirmar que se fusionaron: E029 compone sobre archivo textual,
E026 sobre hechos E025. Falta una política común de prioridad y conflictos.

1. Revalidar referencias, instrucciones y actividad en el workflow existente;
   no iniciar otro job si hay ciclo activo real. No borrar su bloqueo.
2. Preservar el checkpoint experimental y exportar desde el runner la región
   de patrones aprendidos a un formato durable y verificable del repositorio,
   separándola de los hechos sintéticos; no copiar hechos de examen al estado
   publicado ni reentrenar lo ya adquirido. Conservar el checkpoint y hash original.
3. Revisar E028 `e28_missing`, `e28_conflict` y fallback, y E026 prefix/suffix.
   Implementar un candidato único con una política explícita: evidencia
   contextual negativa/conflictiva no puede convertirse en respuesta positiva
   por fallback a E025; falta de archivo no debe borrar hechos E025 aprendidos.
4. Reservar sujetos distintos para: solo hechos E025, solo archivo E027,
   ambas fuentes concordantes, contradicción entre fuentes y negación.
   Verificar ambas lenguas y formas aprendidas, con procedencia cuando exista.
5. Reejecutar los casos E026/PR #33 pertinentes, E029/E028/E027/E025 y W4u.
   Comparar con ambos candidatos actuales y conservarlos si hay regresión.

Aceptación: una sola cápsula que responda correctamente en ambos almacenes,
se abstenga en todos los conflictos/negaciones de la matriz reservada y
conserve los 48 casos de las formas aprendidas, archivo y capacidades previas.
Declarar el aprendizaje existente como conservación, no aprendizaje nuevo.

## Límites y permisos
Los nuevos marcos tienen un sujeto ASCII alfanumérico de 1..31 bytes y dos
lados literales de 1..80 bytes; la intención doble está supervisada.
No son gramática abierta. No se instaló Android. W4u se verificó en runtime
REVERSE-PC fijado con fixtures/acción tipada; no se demostró coordinación
autónoma de ingeniería, ni interacción con un dispositivo Android actual.

Usar únicamente el runner del workflow E029 ya configurado
(ubuntu-latest, runtime a1b935ae0adf38615996bac92727e95289ad7cc1,
Mundo X e2778d962af22f6f1a0794058dd4685fc2573966).
Actualizar ESTADO, este archivo y el registro incluso si falla el intento.
