# BBY Q E007 — Ether Vault: memoria reversible de contextos

## Dirección experimental

**Pregunta**: después de aprender dos regularidades opuestas, ¿puede BBY Q
recuperar la primera sin volver a aprenderla y sin que el evaluador le
entregue la etiqueta del contexto?

E007 conserva la arquitectura E006 y añade un **archivo compacto de hipótesis
dentro del mismo Inverse Ether Memory/RVPC2**. No se crean otro motor de IA,
una base de datos externa o pesos derivados de modelos preentrenados.

La unidad de estado es *un solo RVPC2*: identidad, registros lógicos,
relaciones activas, relaciones archivadas, contador de cambios y evidencia.
El intérprete XI ejecuta cada paso como una transacción con rollback.

## Flujo verificable

1. Nacimiento E006: ninguna relación compuesta.
2. Entrenar XOR como **A** durante 12 generaciones de 200 experiencias.
   Jurado E006 usa 240 observaciones de magnitud impar para aprobar.
3. `checkpoint.xi`: guarda base y relaciones de A en direcciones archivadas
   *dentro del mismo RVPC2*, manteniendo el modelo activo intacto.
4. `unlock-next.xi`: crea un nuevo espacio sombra **B** sin alterar A.
5. Entrenar B sobre la regularidad inversa (XNOR) durante otras
   12 generaciones. El jurado E006 también exige evidencia independiente
   antes de publicar B.
6. `probe-feed-xor.xi` o `probe-feed-anti-xor.xi`: prepara 240
   consecuencias nuevas sin una etiqueta textual "contexto A/B" para el
   selector. `probe-feed-noise.xi` es un control adverso.
7. `recall.xi`: predice con las **dos** hipótesis antes de observar
   cada consecuencia; tras consumir el lote, intercambia las dos
   representaciones sólo si la archivada obtiene **205/240** aciertos
   y supera a la actual por **al menos 30/240**. La nueva configuración
   y la eliminación del lote se confirman en un único programa XI.
8. `audit-vault.xi`: verifica que ambos contextos estén conservados
   y diferenciados, que no sobrevivan etiquetas ni muestras temporales,
   y que ninguna consulta modifique el archivo persistente.

El orden de prueba fue B activo → A recuperado → B recuperado →
ruido (mantener B) → A recuperado → A repetido (mantener A).
La primera vuelta A→B requirió entrenar las dos regularidades; las
recuperaciones posteriores *no* vuelven a entrenar.

## Mapa lógico adicional, base 7000000000000000000

E007 se ejecuta sobre un agente E006 aceptado, con firma `66,81,6`.
No reinterpreta los estados E004/E005.

| Offset | Significado |
|---|---|
| +401..+403 | Tres pesos base del modelo archivado, almacenados en bytes |
| +404 | Número de relaciones compuestas del modelo archivado |
| +420..+423 | Descriptores compuestos archivados |
| +440..+443 | Pesos de esas composiciones |
| +500 | Archivo disponible (1) |
| +503 | Identidad del contexto activo (1 ó 2 en el experimento) |
| +504 | Identidad del contexto archivado |
| +505 | Conteo de recuperaciones con intercambio |
| +506 | Conteo de consultas de contextos |
| +507/+508 | Aciertos del contexto activo/archivado en última consulta |
| +509 | Último veredicto, 1=intercambio, 0=conservar |

Las direcciones +200 y +220 siguen siendo el modelo activo, idénticas
a E006. Las hipótesis dentro del mismo archivo son dos bancos de
conocimiento, no dos autoridades de estado. Los datos de experiencia
usan +10000..+12239 y se borran hasta el último byte después del juicio.

## Evidencia nativa

[GitHub Actions, run 40284681769](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40284681769):
tres semillas (19, 42, 91); dos contextos entrenados por semilla,
cada uno con 12 generaciones × 200 experiencias. **14.400 experiencias
de entrenamiento** para 6 hipótesis en total, además de evaluaciones.

En **cada semilla** sucedió lo siguiente:

| Consulta tras aprender A y B | Aciertos activo | Aciertos archivo | Intercambio |
|---|---:|---:|---|
| Regresa A (XOR) | 0/240 | 240/240 | Sí, A activa |
| Regresa B (XNOR) | 0/240 | 240/240 | Sí, B activa |
| Datos aleatorios | Cerca del 50 % en ambos | Cerca del 50 % | No |
| Regresa A otra vez | 0/240 | 240/240 | Sí, A activa |
| A sigue siendo válido | 240/240 | 0/240 | No |

**Semilla 42, control aleatorio:** modelo actual 119/240, archivo
121/240: no cambió. La auditoría final informó **tres cambios** en
cinco consultas, **43 excepciones lógicas**, **cero enlaces cuánticos**
y **cero qubits activos**. Estado RVPC2 final: **6.162 bytes**.
Se rechazó una segunda consulta al mismo lote ya consumido.

Los artefactos contienen los dos estados aprendidos por semilla
(antes de la primera recuperación y después de las cinco consultas),
resultados JSONL de cada comparación y cada auditoría:
[descargar artefactos nativos E007](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40284681769/artifacts/12632299620).

## Restricciones y criterios de falsación

- **Sólo dos contextos**: uno activo y uno archivado. No hay todavía
  política de múltiples hipótesis ni reemplazo por utilidad.
- La identidad 1/2 es un marcador interno de cuál banco se activó
  después de la decisión, **no** una etiqueta de contexto que lea el
  programa selector para acertar la respuesta.
- El mecanismo necesita observar consecuencias binarias de la
  realidad simulada. No detecta un régimen únicamente a partir
  de la distribución de señales no etiquetadas. Tampoco explora
  activamente qué pregunta hacer al entorno.
- La regularidad A y B comparte gramática fija (dos signos). El paso
  de prueba a un mundo más general exige nuevos operadores,
  descubrimiento de variables y controles contra fuga de feedback.
- La comparación utiliza código auditado que hace predicciones
  *antes* de leer cada resultado. El mismo RVPC2 contiene las etiquetas
  temporalmente: esto no constituye aislamiento criptográfico.
- El aprendizaje está implementado por completo en el lenguaje
  original `.xi` de REVERSE-PC; el runtime preexistente sigue teniendo
  bootstrap C++ y MX es el futuro lenguaje fuente canónico, sin
  self-hosting confirmado.
- Las demostraciones son de IA simbólica sobre datos sintéticos en
  **CPU clásica**. No probaron ventaja cuántica, vida artificial,
  generalización semántica ni inteligencia general.

## Dirección E008

Expandir de dos contextos a un banco acotado de reglas independientes.
Seleccionar hipótesis por evidencia y calibración, no sólo coincidencia
de etiquetas; registrar falsos positivos bajo ruido, transiciones
rápidas y contextos inéditos. Evitar que más memoria implique
mayor coste sin utilidad, y ampliar la gramática de representación
antes de proclamar evolución abierta.
