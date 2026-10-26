# BBY Q — inteligencia artificial progresiva en tecnología propia

**Ruta activa: E008 — Ether Constellation, cuatro conocimientos
reversibles y decisiones de aprendizaje en el lenguaje propio XI.**
E007 conserva la memoria dual; E006 sigue siendo el jurado de
relaciones y E005 preserva el nacimiento de estructuras.

BBY Q **no utiliza SOVENGI, modelos de IA de terceros, Transformers ni
código Python/C++ para implementar su inteligencia**. Su estado y las
transacciones pertenecen a REVERSE-PC, XI, Inverse Ether Memory y Mundo X,
con **una sola autoridad persistente RVPC2 por agente**.

## E008 — Cuatro conocimientos y una política de exploración

**Cinco agentes, cada uno con cuatro hipótesis propias dentro de un único
RVPC2**. Aprenden XOR, XNOR, AND y OR sin incorporar la regla del
generador del mundo en el programa de aprendizaje. Tras su aprobación,
`recall4.xi` compara predicciones antes de consultar las consecuencias,
selecciona un banco reconocido o **se abstiene** si las contradicciones
son demasiado grandes. No vuelve a entrenar los cuatro bancos al
cambiar de entorno.

`plan-next.xi` analiza los desacuerdos y residuos para decidir una
acción epistémica: usar lo aprendido, consultar un experimento
discriminante, investigar la región más sorprendente o ampliar
la representación. La política no ejecuta todavía investigaciones
físicas ni modifica su propia gramática sin pruebas.

**Validación final sellada**
([GitHub Actions 40289515756](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40289515756)):

- **20/20** situaciones conocidas identificadas; **15/15**
  desconocidas rechazadas sin alucinar una clase.
- **20/20** reconocidas bajo 15 % de corrupción independiente;
  **18/20** bajo 25 % (dos abstenciones seguras).
- **1.600 decisiones** adicionales con entradas cambiantes:
  1.070 selecciones correctas y 530 abstenciones, sin modificar
  las hipótesis ni romper la persistencia.
- Estado RVPC2 de semilla 42: **6.632 bytes** después de 320
  decisiones de longevidad. Las cuatro hipótesis ocupan
  un único espacio Ether con checksum por banco.
- **Cero qubits activos y cero entrelazamientos** en
  estos experimentos de aprendizaje simbólico en CPU clásica.

[Contrato, datos crudos, límites y evaluación de «organismo»](docs/AI_E008_CONSTELLATION.md).
[Archivos persistentes y resultados E008](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40289515756/artifacts/12635511438).

**Diagnóstico:** el proyecto avanza como agente computacional
persistente con aprendizaje y metacontrol limitado. Aún **no es
un organismo biológicamente vivo ni una IA general**, no controla
sus propios recursos/actuadores y la evolución de relaciones
permanece restringida a una gramática de dos signos.

## E007 — Ether Vault: una memoria que recuerda sin reaprender

La entidad aprende **A: XOR** y **B: XNOR** con un mismo jurado de E006.
Las hipótesis quedan en dos bancos compactos dentro de un solo RVPC2.
El selector `ai/xi/e007/recall.xi` compara ambas sobre experiencias
nuevas, intercambia la activa cuando la archivada supera por al menos
30/240 casos y alcanza 205/240, y destruye los datos temporales.

[CI E007: recuperación reversible con feedback parcialmente corrupto](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40285381399).
En cada semilla, la secuencia A→B→A-ruidoso→B-ruidoso→A→B→ruido→A→A
cambió de modelo cuando había evidencia y se mantuvo bajo ruido puro
o cuando el activo seguía siendo correcto. Se realizaron **cinco
recuperaciones sin volver a entrenar** las dos hipótesis.

- Estado final por semilla: dos hipótesis completas, una autoridad
  Inverse Ether Memory/RVPC2, **cero qubits activos**.
- Semilla 42: **6.162 bytes RVPC2**, 43 excepciones lógicas y
  cinco recuperaciones. Los dos modelos siguen disponibles.
- Los programas E007, incluido el selector y la transacción
  reversible, están exclusivamente en el lenguaje propio XI.
- El selector toleró entre 54 y 69 etiquetas corruptas de
  240 en tres semillas, usando un criterio comparativo estricto.
- Límite actual: dos contextos, dos señales categóricas y
  feedback binario; no se ha probado recuperación general.

[Contrato, evidencia y limitaciones de E007](docs/AI_E007_CONTEXT_VAULT.md).

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
