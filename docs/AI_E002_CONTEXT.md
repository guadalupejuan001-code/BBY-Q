# BBY Q E002 — memoria contextual sin etiquetas de régimen

## Motivación y restricción tecnológica

El E001 retiene una única hipótesis aprendida. Cuando el ambiente invierte
sus relaciones, esa hipótesis se reescribe y pierde precisión al regresar.
E002 investiga **recuperación de representaciones** antes de extender el
espacio de parámetros: no entrena con ChatGPT, Claude, SOVENGI, Transformers
ni pesos externos. La lógica de interpretación se implementa aquí en BBY Q;
su único estado persistente se almacena mediante **Inverse Ether Memory,
XI y RVPC2 de REVERSE-PC**, sin qubits por defecto.

Limitación explícita: las operaciones aritméticas de aprendizaje todavía
se ejecutan en Python de BBY Q. REVERSE-PC garantiza el medio persistente,
transaccional y de direcciones lógicas; **no se afirma que Ether ya compute
el aprendizaje semántico** ni que esta implementación tenga un algoritmo
de aprendizaje enteramente nativo.

## Hipótesis y decisión observable

- Una hipótesis activa contiene cinco relaciones ponderadas del E001.
- Hasta tres hipótesis **inactivas** pueden almacenarse con sus propios
  identificadores y contadores de actualización. No hay una copia redundante
  de la hipótesis activa: se mueve entre el campo activo y el archivo lógico.
- Se predice **antes** de recibir el resultado del entorno. El historial
  conserva esa predicción original aunque el feedback active una transición.
- Si hay tres contradicciones de alta confianza consecutivas, y el contexto
  actual posee al menos 60 actualizaciones, se compara la pérdida logarítmica
  reciente con las hipótesis archivadas y con la hipótesis neutra 0,5.
- Si una archivada explica los resultados suficientemente bien, se **recupera**.
  Si ninguna los explica mejor, se crea un contexto nuevo de pesos inicialmente
  nulos, conservando el anterior sin reescribirlo.
- Las observaciones sorprendentes de un contexto maduro se guardan pero pueden
  **suspender** la actualización de ese contexto, para proteger conocimientos.
- El límite de cuatro contextos es estricto; el sistema no descarta silenciosamente
  hipótesis cuando se agota. El límite se expone al inspeccionar el estado.

La selección posterior al feedback es una actualización del estado: nunca se
contabiliza como una predicción acertada de ese mismo feedback. El diagnóstico
de probabilidad tras la selección es distinto de la predicción prefeedback.

## Protocolo reproducible

Por semilla, entorno de coeficientes ocultos:
1. 400 experiencias del régimen A; evaluación en observaciones nuevas.
2. 400 experiencias en régimen invertido B, **sin indicar el cambio a la IA**;
   evaluación separada del régimen B.
3. Retorno a A con 36 experiencias para detectar que el contexto reapareció,
   sin transmitir ninguna etiqueta de régimen.
4. Evaluación inmóvil en un holdout de 240 casos, comparada con el mismo
   algoritmo de E001 que solo conserva un modelo. Inputs train/test disjuntos;
   las reglas de entorno viven fuera del agente.

Comando:

```bash
PYTHONPATH=ai python -m bbyq experiment --contextual \
  --seed 42 --runs 5 --train 400 --test 240 --recovery 36 \
  --output experiment002.json
```

## Evidencia local (antes del CI nativo)

Media de 5 semillas 42–46, 240 holdout cada una:

| Métrica | Resultado |
|---|---:|
| Precisión tras el aprendizaje inicial A | 95,08 % |
| Precisión aprendida en B invertido | 93,92 % |
| A antes de retorno/reconocimiento | 6,08 % |
| A después de 36 observaciones de retorno | **95,00 %** |
| A después de 36 observaciones: modelo único E001 | **67,33 %** |
| Contextos finales | 2 |
| Cambios de contexto | 2 (creación B + recuperación A) |

Prueba ampliada local: 25 semillas (1–25), 160 holdout por semilla;
precisión A recuperada **95,05 %**, modelo único **60,75 %**,
25/25 recuperaciones reales. La prueba cuenta eventos `recalled`, no
solo una precisión alta obtenida al reentrenar desde cero.

**Controles negativos y límites:** bajo paridad/XOR no lineal, una prueba
local de 25 semillas logró alrededor de 55,76 % de precisión media:
E002 no resuelve ese tipo de estructura por sí solo. El cambio B es una
inversión de una relación conocida, no una demostración de transferencia
semántica o generalización universal. La creación de contextos puede
fallar con ruido, regímenes progresivos, ventanas escasas o más de cuatro
hipótesis; se mantienen pruebas negativas y no se imputan valores faltantes.

## Estado y auditoría de errores

La autoridad de estado sigue siendo un solo archivo RVPC2. E002 conserva
`model.weights` solo para el contexto activo, junto a `model.archived`
para los inactivos. `NativeStore` escribe diferencias de bytes con
`mem_store`, sin SQL, pesos externos ni otro runtime persistente.

Corrección independiente de E002: el nacimiento es ahora publicación
atómica de un archivo inicial preparado y verificado, evitando estados
`*.rvp` incompletos cuando una inicialización falla. Las pruebas nativas
comprueban un nacimiento rechazado y la restauración de contextos.

El CI ejecuta suites Python, el programa XI compilado desde REVERSE-PC
fijado y la persistencia del agente E002 completo. Los costes de RAM,
tiempo, payload lógico y RSS no se deducen de la precisión.

## Siguiente interrogante falsable

Explorar cambios de contexto **graduales y ambiguos**, estimación de
incertidumbre, olvido bajo presupuestos finitos y representaciones
no lineales. Antes de atribuir novedad tecnológica o utilidad comercial,
comparar con mecanismos clásicos conocidos de detección de cambios y
memoria contextual, en igualdad de datos y presupuestos.


## Optimización posterior BQL2

La representación de hipótesis contextual de E002 se mantiene, pero los
bytes físicos codificados pueden comprimirse por referencias lógicas
repetidas (codec BQL2 desarrollado en BBY Q). En una ejecución local,
una entidad E002 de 16.744 bytes canónicos se representó como 4.920 bytes
BQL2 (29,4 % del tamaño; ahorro 70,6 %), recuperándose exactamente.
Esta cifra **no** es el tamaño físico RVPC2 ni una latencia nativa:
ambos se medirán en el workflow real y se reportarán por separado.
