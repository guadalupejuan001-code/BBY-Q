# BBY Q — inteligencia artificial progresiva con tecnología propia

**Ruta activa: E004, aprendizaje únicamente en XI, dialecto ejecutable de la familia MX.**

La identidad computacional, memoria y entrenamiento de esta etapa usan
**REVERSE-PC + Inverse Ether Memory + XI + Mundo X**, sin pesos externos, sin
SOVENGI, sin Transformers ni algoritmos de IA implementados en Python/C++.

El agente guarda su estado en **una autoridad RVPC2**: relaciones interpretables,
errores, correcciones y número de generación. Se puede cerrar, reabrir y
continuar el entrenamiento sin iniciar de cero.

## Archivos del proyecto

- `ai/xi/birth.xi`: crea el estado BBY Q desde memoria vacía.
- `ai/xi/learn.xi`: predice, recibe retroalimentación y modifica relaciones.
  Cada ejecución añade 400 experiencias y una nueva época al mismo estado.
- `ai/xi/holdout.xi`: comprueba 240 casos disjuntos, baseline congelado
  y control negativo XOR, sin modificar la memoria.
- [Diseño, protocolo y límites E004](docs/AI_E004_OWN_LANGUAGE.md)
- [Evidencia reproducible en GitHub Actions](https://github.com/guadalupejuan001-code/BBY-Q/actions/workflows/bbyq-xi.yml)

## Estado verificado

La primera prueba nativa E004
([run 40276393053](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40276393053))
compiló el **runtime XI ya existente**, ejecutó dos épocas reales sobre
`Inverse Ether Memory` y guardó/restauró RVPC2.

| Casos nuevos | Modelo XI | Baseline constante | Control XOR |
|---|---:|---:|---:|
| 240 después de 400 experiencias | 223/240 (92,92 %) | 108/240 (45,00 %) | 122/240 (50,83 %) |
| 240 después de 800 experiencias | 224/240 (93,33 %) | 108/240 (45,00 %) | 125/240 (52,08 %) |

Resultados limitados a un microentorno sintético. Ambas épocas:
**cero qubits activos, cero enlaces cuánticos**, y snapshots
inalterados por la evaluación.

**Dependencia temporal declarada:** el intérprete de XI existente en
REVERSE-PC todavía se compila mediante bootstrap C++; el código del
*aprendizaje* no usa C++/Python. El lenguaje fuente canónico a largo
plazo es MX (`.mx`); XI (`.xi`) es su dialecto de ejecución temporal.
No se afirma que MX ya sea autoalojado.

## Ejecutar y continuar

Construye el runtime de REVERSE-PC fijado en
`8e451dd6f2f9a24dc91d1a017252c204cac7fcff` con el Mundo X
fijado por su integración. Luego:

```sh
reverse_pc init blank.rvp
reverse_pc run ai/xi/birth.xi blank.rvp born.rvp
reverse_pc run ai/xi/learn.xi born.rvp generation1.rvp
reverse_pc run ai/xi/holdout.xi generation1.rvp observation1.rvp
reverse_pc run ai/xi/learn.xi generation1.rvp generation2.rvp
reverse_pc run ai/xi/holdout.xi generation2.rvp observation2.rvp
```

## Laboratorio óptico histórico

El receptor de luz y sensores para **Galaxy Watch4 Classic** sigue
preservado en `app/`, `ROADMAP.md` y `docs/RECEPTOR_OPTICO.md`,
sin participar en el aprendizaje E004. Su archivo anterior pertenece
al mismo proyecto pero no se mezcla con la autoridad del agente.

No se reclama conciencia, ventaja cuántica ni generalización universal.
Las próximas etapas son memoria contextual en XI/MX, aprendizaje de
relaciones nuevas, tareas externas y self-hosting de MX.
