# BBY Q — inteligencia artificial progresiva en tecnología propia

**Ruta activa: E006 — Jurado XI para promover únicamente relaciones
que mejoran la predicción en casos no usados durante el entrenamiento.**
E005 conserva su historial de nacimiento de relaciones, ahora extendido
con validación, rechazo y protección de conocimiento aprobado.

BBY Q **no utiliza SOVENGI, modelos de IA de terceros, Transformers ni
código Python/C++ para implementar su inteligencia**. Su estado y las
transacciones pertenecen a REVERSE-PC, XI, Inverse Ether Memory y Mundo X,
con **una sola autoridad persistente RVPC2 por agente**.

## E006 — las ideas deben sobrevivir una prueba independiente

En `ai/xi/e006/` hay una entidad nueva (esquema 6) que entrena
relaciones candidatas en modo sombra. El `jury.xi` las compara con
las mismas relaciones desactivadas, sobre 240 experiencias no vistas,
**sin adaptar ninguno de los dos durante el examen**.

- Si el candidato mejora al menos 30/240 y acierta al menos 205/240,
  se promociona como conocimiento activo y se sella.
- De lo contrario, los descriptores espurios y las etiquetas de
  validación se eliminan transaccionalmente del RVPC2.
- La inferencia `infer-grid.xi` no utiliza relaciones no aprobadas.
  Un modelo sellado rechaza entrenamientos improvisados.

**GitHub Actions E006:** [ejecución 40283557920](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40283557920).
12 agentes/controles, tres semillas, 28.800 experiencias; los tres
modelos XOR aprobaron con **240/240** sobre un holdout nuevo y **9/9**
controles negativos/adversos fueron rechazados. Se verificó rollback,
ausencia de etiquetas persistentes, inferencia sellada y rechazo de
juicios repetidos.

[Contrato técnico y controles E006](docs/AI_E006_SHADOW_JURY.md).

**Próxima limitación:** preservar múltiples hipótesis para cambiar de
contexto sin perder las anteriores. E006 protege un único modelo activo;
aún no recupera automáticamente conocimientos previos.

## E005 — relaciones que no existían al nacer

En `ai/xi/e005/` están los programas propios:

- `birth.xi`: nace una entidad con tres pesos base y **cero relaciones
  compuestas** (esquema 5, separado de E004).
- `feed-xor.xi`, `feed-noise.xi`: generan consecuencias en el mismo
  espacio lógico con fuentes de datos desacopladas del aprendiz.
- `learn.xi`: predice antes de leer la consecuencia; tras errores
  recurrentes puede **materializar una composición de predicados**;
  guarda la nueva relación y borra el lote de observaciones y etiquetas
  en una transacción XI.
- `eval-xor.xi`, `eval-noise.xi`: prueban casos no usados en el
  entrenamiento y no modifican el estado.
- `linear-control.xi`, `rollback.xi`, `audit-clean.xi`,
  `input-fingerprint.xi` y `seed-*.xi`: controles de crecimiento,
  aislamiento, compacidad, igualdad de entradas y semillas.

La gramática probada combina los signos de dos señales y tiene
**un máximo de cuatro relaciones materializables**. Todavía no permite
la invención universal de reglas ni identifica automáticamente si el
crecimiento es espurio. La siguiente fase debe añadir selección basada
en utilidad, poda y recuperación de hipótesis, sin introducir motores
paralelos ni otros lenguajes para la inteligencia.

## Evidencia reproducible

[GitHub Actions E005, 3 semillas y 9 agentes/control](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40279710145):
**12 generaciones × 200 experiencias por agente**, es decir, 21.600
ejemplos de entrenamiento en toda la campaña. Después se evaluaron
240 muestras de magnitudes no vistas por cada agente.

| Semilla | Modelo con relaciones nuevas | Lineal con los mismos ejemplos | Entrenado con ruido, evaluado en XOR |
|---|---:|---:|---:|
| 19 | 240/240 | 118/240 | 133/240 |
| 42 | 240/240 | 114/240 | 114/240 |
| 91 | 240/240 | 119/240 | 121/240 |

Después del entrenamiento, la entidad con semilla 42 conserva cuatro
relaciones en un archivo RVPC2 de **5.642 bytes, 22 excepciones lógicas**
y **cero qubits activos**. Antes de eliminar el lote temporal ocupaba
18.673 bytes y 540 excepciones: **69,8 % menos bytes** para el mismo
problema controlado y las mismas 12 generaciones.

La validación incluye controles adversos, captura de un artefacto
RVPC2 reutilizable, rechazo de reentrenamiento de un lote consumido,
conservación exacta del archivo durante evaluación y rollback tanto
para un archivo nuevo como para un destino existente.

[Arquitectura, limitaciones, protocolo y corrección del control negativo](docs/AI_E005_RELATIONS.md).

## Ejecutar y continuar

Se utiliza REVERSE-PC integrado en el commit
`6d4de14a2dfbce4b8a7f1cb50e29d11b9073fe98` y su dependencia
Mundo X comprobada en
`e2778d962af22f6f1a0794058dd4685fc2573966`. Tras compilar
el intérprete XI original, situarse en el repositorio BBY Q:

```sh
reverse_pc init blank.rvp
reverse_pc run ai/xi/e005/birth.xi blank.rvp born.rvp
reverse_pc run ai/xi/e005/seed-42.xi born.rvp entity.rvp
reverse_pc run ai/xi/e005/feed-xor.xi entity.rvp observations.rvp
reverse_pc run ai/xi/e005/learn.xi observations.rvp generation1.rvp
reverse_pc run ai/xi/e005/audit-clean.xi generation1.rvp clean.rvp
reverse_pc run ai/xi/e005/eval-xor.xi generation1.rvp tested.rvp
# Para continuar, usar generation1.rvp como entrada de feed-xor.xi
```

No es necesario conservar `observations.rvp` para que la entidad
recuerde: `generation1.rvp` contiene sus relaciones. No mezclar
directamente un estado E004 y uno E005, pues tienen esquemas diferentes.

## E004 y laboratorio anterior

La [E004](docs/AI_E004_OWN_LANGUAGE.md) se conserva en `ai/xi/`:
8.000 experiencias sintéticas, 227/240 aciertos para su tarea lineal,
sin pérdida de la lógica ni necesidad de modelos externos.

El laboratorio óptico histórico Galaxy Watch4 Classic sigue separado
en `app/`, `ROADMAP.md` y `docs/RECEPTOR_OPTICO.md`.

## Dependencia temporal declarada

**Todo el algoritmo de aprendizaje E005 está escrito en XI.** El
intérprete actual de REVERSE-PC todavía utiliza un **bootstrap C++**
preexistente: no se ha logrado aún compilación nativa autoalojada.
MX (`.mx`) continúa siendo la futura fuente canónica; XI es un
dialecto de runtime propio que debe converger hacia MX. No confundir
este experimento de aprendizaje simbólico en CPU clásica con
ventaja cuántica, conciencia ni inteligencia general.
