# BBY Q — auditoría de reutilización y procedencia (2026-10-25)

## Identidad del software inspeccionado

- BBY Q `main` inicial y rama preliminar `feature/quantum-ai-lab-20261025`: `a5cde7b06d5b3f80714560048d34285c2b435173`; **idénticos** antes de este trabajo. Respaldo creado: `archive/watch4-optics-20261025`.
- REVERSE-PC `main`: `063d871c27de2d4f10904ec5c3e1363c2fe16d86` (código `src/reverse_pc.cpp`, `src/integration/`, `docs/unified-authority.md`, `CMakeLists.txt`). Es **la dependencia de integración fijada para este PR**.
- Mundo X origen: commit `e2778d962af22f6f1a0794058dd4685fc2573966`, **fijado por REVERSE-PC**, con verificaciones de cabeceras y adaptaciones locales documentadas. La punta actual de Mundo X no sustituye ese commit sin revisión independiente.
- SOVENGI: **no usado**. Ningún Transformer, API remota, peso o tokenizer ajeno alimenta las predicciones.

## Qué tiene y qué no tiene la tecnología

| Componente | Contrato observado | Uso real aquí | Límite |
|---|---|---|---|
| Ether | Marco global, transformación simbólica de observables Pauli admitidos | Fuente de diseño de representación compacta; no se simula un circuito Ether en esta prueba | No interpreta significado ni aprende relaciones semánticas por sí solo |
| InfiniteCore/CompactCore | Una autoridad de estado cuántico activo, Clifford compacto | Conservado dentro del runtime original, no se invoca con qubits en BBY Q v0.1 | No es un motor de aprendizaje |
| AdaptiveReduced/Reduced | Estados no-Clifford adaptativos con presupuestos explícitos | No se encienden para clasificación o actualización clásica | 1000 qubits ensayados no significan eficiencia arbitraria ni ventaja para IA |
| Inverse Ether Memory | Fondo byte, excepciones, enlaces explícitos; `mem_store`, `mem_materialize`, `mem_stats` | **Autoridad persistente real** de identidad, experiencias e hipótesis serializadas como deltas | 65.536 overrides/materialización por defecto; no ofrece búsqueda semántica nativa |
| XI/QuantumRuntime | Transacción conjunta, programa abortado sin commit, RVPC2, restauración | **Ejecutado** por CLI `reverse_pc run`; un programa escribe bytes modificados en una unidad | Transporte de proceso/archivo no es una interfaz de aprendizaje de alta frecuencia |
| Estado BBY Q | Esquema y modelo nuevos de este PR | Interpreta, aprende, explica peso por relación, conserva continuidad | La representación inicial es deliberadamente pequeña y de capacidad limitada |

`REVERSE-PC` implementa su propia integración sobre un checkout de Mundo X fijado y verificado; BBY Q reutiliza el **ejecutable compilado**, no copia encabezados ni crea estados cuánticos duplicados. Su única fuente de verdad duradera es `entity.rvp`; `.lock` es un fichero de coordinación. La entidad en RAM durante una operación es candidata temporal y se descarta tras la ejecución.

## Contratos revisados

- REVERSE-PC `README.md`: compilación, revisión Mundo X fijada, costes por circuitos, regresiones, restricciones 1000 qubits.
- REVERSE-PC `docs/unified-authority.md`: `RVPC2`, transacciones, revisiones, RNG, límites, estado cuántico compartido.
- REVERSE-PC `docs/NEXT_ITERATION_2026-10-25.md`: últimas restricciones de control de flujo XI, observaciones, benchmarks.
- REVERSE-PC `src/reverse_pc.cpp`: `init OUTPUT.rvp`, `run PROGRAM.xi INPUT.rvp OUTPUT.rvp`, checksum RVPC2 y rename tras éxito.
- Mundo X `native/include/mundo_x/infinite_program.hpp`: instrucciones de bytes y lectura `mem_materialize` como JSON Lines.
- Mundo X `native/include/mundo_x/inverse_memory.hpp`: override sparse, retorno de handle ante byte cuántico no determinista, no asignación automática de qubits.

## Faltantes comprobables

1. Representación relacional general, incertidumbre y aprendizaje semántico: **no están resueltos por Ether**. Primer experimento usa señales numéricas, pesos y actualización por gradiente, no conceptos universales.
2. Recuperación de episodios por significado y reorganización estructural autónoma: **no existen aún**; se conserva registro reciente y resumen de pesos.
3. Retención ante cambio de tarea: **falla** en el control de inversión; no silenciar.
4. Escrituras escalables: cada `step` de v0.1 invoca XI como subproceso, lee y escribe RVPC2. Medir coste real antes de diseñar interfaz incremental o nativa.
5. 4K/8K gráficos, sensores del reloj, hardware cuántico y agentes de lenguaje: no necesarios para validar este mecanismo de IA, por tanto no se integran.
