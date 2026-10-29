# BBY Q — consolidación auditada y evidencia de rendimiento

**Fecha:** 29 de octubre de 2026. **Arquitectura:** BBY Q → w4U → QdU, con XI/Ether y memoria RVPC2.  
**Base auditada:** `main@337e161af2b333b70c9bc938741e7c08097093e0`.  
**Rama de integración:** `integrate/bbyq-audited-sources-20261029`, [PR #42](https://github.com/guadalupejuan001-code/BBY-Q/pull/42).

## Qué había en `main` y qué faltaba

El árbol original de `main` tenía el checkpoint E034 y sus evidencias, pero no incluía `ai/releases/e030`…`e034`, necesarios para inspeccionar y reconstruir el código de estas iteraciones. E027, E028 y E029 ya estaban en `main`; las ramas E005–E022 conservaban mayoritariamente código antiguo existente y algunas versiones divergentes obsoletas.

Se auditaron **43 ramas existentes** (incluido `main`). Al iniciar la consolidación se incorporaron **61 archivos de Git ya existentes**, sin sobrescribir los blobs originales de `main`: 

| Procedencia | Archivos recuperados | Destino |
|---|---:|---|
| E030–E034, último candidato relacional | 36 | `ai/releases/e030`…`e034` y documentación |
| Laboratorio E026 y compatibilidad E027 | 9 | `ai/releases/e026`, `e027` |
| Benchmark independiente BBY Q/SOVENGI | 9 | `benchmarks/sovengi-bbyq-20261029` y registro |
| Diagnóstico E025 de dos hechos | 2 | `ai/releases/e025` |
| Ciclo inicial de Qd/Cody | 5 | `docs/history/qd-cycle0`, archivo histórico, no autonomía paralela |

**No se incorporan** los prototipos antiguos Python/C++ de `feature/quantum-ai-lab-20261025` y `feature/ether-native-relations-20261026` al runtime actual de BBY Q: quedan disponibles en sus ramas y no sustituyen XI/Ether. Tampoco se importa automáticamente el paquete `bootstrap/source.bundle` de transporte sin verificar su contenido y necesidad. No se fusionan modelos de SOVENGI.

[Inventario de las 43 ramas y razones](BBYQ_SOURCE_AUDIT_20261029.json).

## Avances funcionales con evidencia real

Las siguientes cifras corresponden a ejecuciones históricas con CI completada y artefactos. **No** miden inteligencia abierta ni prometen rendimiento superior en otras cargas.

| Perfil | Habilidad probada | Resultado |
|---|---|---|
| **E032 temporal** | Preguntas sobre estados y separación de tiempos | **144/144**; 96 controles de aislamiento |
| **E033 relacional** | Consultas sobre relaciones aprendidas en XI | **168/168**, con E032 conservado 144 |
| **E034 composicional** | Combinar dos propiedades del mismo sujeto y dar referencias tipadas | **48/48** compuestas y **96/96** seguimientos |
| **E034 retención** | Recuperar capacidades relacionales y temporales | **168** relacionales y **144** temporales |
| **E034 suite propia** | Invariantes, datos, abstenciones y operaciones | **761 verificaciones**, además de **1.069** reproducciones E033 reportadas |

CI: [E032](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40795445276), [E033](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40802286565), [E034](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40808605984).

### Memoria y ejecución nativa

| Medición | E032 | E033 | E034 |
|---|---:|---:|---:|
| Checkpoint RVPC2, bytes | 836.481 | 856.177 | **863.594** |
| Checkpoint comprimido gzip, bytes | 119.255 | 122.091 | **123.175** |
| Mediana de consulta medida | No comparable | 150,65 ms (consultas cacheadas) | **163,84 ms (consultas compuestas)** |
| Pico RSS del proceso nativo | No comparable | 47.508 KiB | **39.964 KiB** |

**Interpretación:** E034 incorpora sus ocho nuevas formas supervisadas y la composición tipada con **7.417 bytes (+0,87%) más de RVPC2 que E033**. Los tiempos de E033/E034 provienen de tareas y ejecuciones distintas: *no permiten concluir que la nueva versión sea más rápida o más lenta*.

Para 96 hechos de una muestra, la representación relacional normalizada creció **30.038 bytes**, frente a **97.378 bytes** de un archivo de texto nativo: aproximadamente **69,15% menos crecimiento** en esa configuración. No preserva literalmente todos los detalles de formato/capitalización; no es compresión sin pérdida de cualquier texto.

## Benchmark controlado, sin fusionar IA

La comparación histórica contra SOVENGI midió **BBY Q E032**, no E034, y usó el mismo runner con un CPU lógico por worker, 32 preguntas y 12 consultas repetidas. [Ejecución](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40798417876), [resultados completos](../../benchmarks/sovengi-bbyq-20261029/RESULTADO.md).

| Medición | BBY Q E032 | SOVENGI (configuración habitual) |
|---|---:|---:|
| Aciertos semánticos completos | **20/32** | **2/32** |
| Mediana de 12 consultas repetidas | **160,81 ms** | 1.140,65 ms |
| Pico RSS muestreado de árbol de procesos | **45,50 MiB** | 995,11 MiB |

La latencia observada de BBY Q fue aproximadamente **7,09 veces menor** y el RSS muestreado **21,87 veces menor** en **ese protocolo concreto**. La revisión semántica se hizo con IA y no con un jurado humano independiente; los modelos tienen coberturas, tamaños de respuesta y trabajo interno diferentes. BBY Q falló 12/32 preguntas, en especial memoria cotidiana y diálogo abierto. No es una puntuación general de inteligencia ni una comparación de eficiencia de algoritmos equivalentes.

## Lo destacable de la arquitectura

- El uso de **una sola autoridad de estado** para XI/Ether, relaciones y reglas simplifica la persistencia y la regresión; no requiere mantener muchos modelos independientes dentro de BBY Q.
- **Representar entidades, propiedades y eventos compartidos** evita repetir texto cuando el problema es estructurado; el experimento de 96 hechos muestra ese efecto cuantitativamente.
- **BBY Q → w4U → QdU** separa semánticamente inteligencia, coordinación y programación sin multiplicar identidades o memorias maestras. Es un contrato de diseño valioso; aún necesita pruebas para tareas programáticas completas y permisos.
- La validación busca **conservar las capacidades anteriores**, con hash de checkpoint, exámenes reservados y regresiones. Es una elección de ingeniería acertada porque hace auditable la evolución.
- La exactitud 48/48 en composición E034 demuestra una capacidad real **sobre un dominio tipado y supervisado**, no omnisciencia ni que toda computación sea acelerada por mecánica cuántica.

## Dependencias externas que se mantienen explícitas

El código fuente de **E031** se ha recuperado, pero su biblioteca de **236.256 entradas de WordNet/MCR** se obtiene mediante una fuente de datos fijada y un artefacto de aproximadamente 105,6 MB. No se introduce íntegra en el checkpoint ni se afirma que su vocabulario esté disponible sin el transporte de páginas. Su prueba original verificó 152/152 consultas exactas, no comprensión semántica de todo el diccionario. [CI E031](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40793126384).

La reproducción acumulada E034 descarga cápsulas de las CI **E032 y E033** (artefactos con caducidad indicada para enero de 2027). El código y los checkpoints originales ya quedan dentro del repositorio, pero la reproducción CI todavía debe evolucionar a una reconstrucción autosuficiente desde fuentes para depender menos de artefactos transitorios.

## Integración y límites

El contenido importado **no reemplaza** `ai/releases/e025/controller.rvp.gz.b64`, los checkpoints E032/E033/E034 existentes, ni la memoria de un dispositivo Android. El checkpoint E034 es un candidato local/nativo, **no** el motor conversacional desplegado en REVERSE 2.5.1. Para utilizarlo allí hará falta revisión de ABI, migraciones y CI Android específicas.

La [CI de consolidación](https://github.com/guadalupejuan001-code/BBY-Q/pull/42/checks) reconstruye el runtime XI/Ether fijado, E025/w4U, E034, su código exacto y regresiones E027–E029. La fusión en `main` solo se declara cuando GitHub confirma ese hecho. Los archivos de evaluación, su procedencia y las limitaciones también constan en [métricas JSON](BBYQ_PERFORMANCE_20261029.json).

**Conclusión:** el activo importante no es la cantidad de ramas, sino que el código de aprendizaje, la memoria y los exámenes queden juntos, identificables y reproducibles, mientras los prototipos de investigación se conservan sin contaminar el runtime funcional.
