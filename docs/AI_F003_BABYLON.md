# F003 — Aprendizaje de El hombre más rico de Babilonia

## Resultado local completo

Código ejecutado: `cb31cd1ba323f5c393f10a04201110ab1d133443`. Los archivos locales coinciden con los blobs de GitHub: `lessons.mjs` = `54ddb434de882b4602197adf28ff610639567922`; `train-f003.mjs` = `a60b185c08bd2a142346a12b515741859c4a16f9`.

**805 comprobaciones aprobadas** en una ejecución local completa. Tres validaciones negativas adicionales de preparación rechazan valores de 81 bytes, sujetos de 49 bytes y sujetos sin canonizar; no se confunden con las 805 pruebas del agente. Los intentos fallidos anteriores no se suman.

| Medida | Resultado |
|---|---:|
| Nuevos conceptos | 64 |
| Nuevos hechos incorporados | 128 |
| Conceptos acumulados | 224 |
| Hechos acumulados | 448 |
| Definiciones nuevas antes / después | 0/64 → 64/64 |
| Respuestas anteriores conservadas | 320/320 |
| Definiciones y requisitos nuevos | 128/128 |
| Composiciones de dos propiedades | 64/64 |
| Seguimientos contextuales | 64/64 |
| Variantes diseñadas del operador | 64/64 |
| Ausencia de evidencia reconocida | 4/4 |
| Respuestas verificadas tras reabrir | 22/22 |

Las categorías están incluidas en las 805 comprobaciones. Antes del entrenamiento, las 64 preguntas respondieron que no había información suficiente. No se afirma generalización a conversación abierta.

## Fuente y contenidos

PDF inglés de 122 páginas: https://cpcglobal.org/publications/The%20Richest%20Man%20in%20Babylon.pdf . La página 2 declara dominio público y distribución gratuita. SHA-256 `76b620d86a163a1934aebeea997f75c1c685d0ecd877f4a0854f0ab3e0e29b69`. No se copia una traducción comercial española.

Lecciones españolas originales: 56 procedentes del libro, 3 aplicaciones modernas explícitamente separadas (REVERSE, BBY Q, Laplace) y 5 distinciones críticas. Cada lección conserva páginas y origen. Incluyen ahorro, control de gastos, reinversión, protección del capital, consejo competente, las siete curas, cinco leyes del oro y el plan de Dabasir.

## Respuestas reales

```text
Operador: pz hablame de pagarse primero
BBY Q: pagarse primero es propuesta de clason de reservar parte del ingreso antes del gasto discrecional [#322].

Operador: que es plan de dabasir
BBY Q: plan de dabasir es plan del relato de 10 por ciento para ahorrar 70 para vivir y 20 para deudas [#416].

Operador: que requiere babilonia aplicado a reverse
BBY Q: babilonia aplicado a reverse requiere medir demanda coste de entrega y un piloto limitado [#433].
```

## Lo que aún no funciona

Cuatro pruebas abiertas exploratorias no resolvieron la tarea: calcular el 10 % de 2000, distribuir 1000 según 10/70/20, aplicar libremente el libro a REVERSE y explicar por qué ahorrar no garantiza riqueza. Todas devolvieron `No tengo información suficiente para responder.` Sus respuestas se registraron y no se contaron como éxitos. Se utilizaron copias de descarte, no la semilla entregada.

Hay 448 diálogos preparados y 128 escenarios numéricos reservados; NO se cuentan como aprendidos. La incorporación demostrada son 128 hechos estructurados en el archivo contextual XI/Ether, no ajuste de pesos neuronales ni memorización literal de 122 páginas.

## Ingeniería y alcance

El runtime y las instrucciones XI se conservan byte por byte. La preparación corrigió un supuesto incorrecto sobre la cabecera de la cápsula; adaptó 11 definiciones al límite de lectura de 80 bytes; canonizó el título porque E028 elimina artículos al consultar, pero no al guardar. Los límites reales y el trabajo pendiente están en `ai/training/babylon/SIGUIENTE.md`.

- Cápsula F003 SHA-256: `98a1a93f9c7385d51209f53c865dc30ba7bee6b732769afbb5a459a645cbdf27`.
- Checkpoint SHA-256: `4b4438b8abb2cf2dd27a6feab09cbed76e6a71d98198a00af63aea71cb7bc308`.
- Checkpoint: 1.861.012 bytes; gzip: 250.336 bytes.
- Ingestión: 36.049 ms; campaña: 252.389 ms en el entorno Linux probado, no en Android.

Se preservan BBY Q → w4U → QdU, los 320 hechos F001/F002 y los archivos originales. No se cambia el agente posterior ni memorias personales. No se actualiza la APK ni se habilitan operaciones financieras. F003 permanece en su rama de entrenamiento.

Resultados estructurados: `docs/evidence/f003-local-results.json`. Este informe acredita la ejecución local; no presenta una CI pendiente como aprobada. Los commits de documentación usan `[skip ci]` para no repetir la campaña por cambios de informe.
