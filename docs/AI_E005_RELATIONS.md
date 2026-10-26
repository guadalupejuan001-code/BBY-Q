# BBY Q E005 — nacimiento de relaciones por error, sólo en XI

## Decisión arquitectónica

E004 ajustaba cuatro relaciones entregadas de antemano; no podía ampliar
su clase de hipótesis. E005 prueba un cambio verificable: **relaciones
compuestas que no están almacenadas al nacer aparecen después de recibir
evidencia de errores reiterados**. Se implementa enteramente en programas
del dialecto XI, usando la autoridad única de REVERSE-PC + Inverse Ether
Memory (RVPC2) y la dependencia propia Mundo X fijada.

La gramática de esta etapa es deliberadamente acotada: componer dos
predicados de signo de dos señales. No crea semánticas arbitrarias ni
inventa su lenguaje o un algoritmo a voluntad. La hipótesis que se intenta
refutar es concreta: un agente lineal no puede representar XOR exacto,
pero los términos conjuntivos nacidos por error podrían hacerlo.

## Separación del mundo y del aprendiz

```text
feed-xor.xi / feed-noise.xi
  observaciones y consecuencias -> regiones temporales InverseMemory
  (mismo RVPC2, una sola autoridad, nunca una base externa)
                    |
                    v
learn.xi: lee observación -> predice -> lee consecuencia
     |                                          |
     +--- si falla, modifica pesos base --------+
                   |
                   +-- evidencia repetida?
                        | no: acumular indicio
                        | sí: materializar una relación compuesta
                                    |
                                    v
                             descriptor + peso
                           en la misma InverseMemory
                                    |
                                    v
                 RVPC2 persiste generación y relaciones
                                    |
                                    v
eval-xor.xi / eval-noise.xi: holdout SIN escritura
```

Los generadores tienen la verdad de su entorno y el aprendiz **no** contiene
la regla XOR ni pseudocódigo de generación de etiquetas. El programa
aprendiz sólo lee una etiqueta después de producir cada predicción.
Esto es una separación de código, **no una frontera de seguridad**:
el estado de entrada contiene las etiquetas del lote y un programa XI
malicioso podría consultarlas antes. La corrección se asegura por revisión
del código, pruebas y orden observable, no por aislamiento criptográfico.

## Memoria de un agente

Esquema nuevo E005 `66, 81, 5`, incompatible deliberadamente con
`66, 81, 4` de E004. La migración entre etapas requiere conversor futuro,
nunca reinterpretar bits como pesos.

| Coordenada lógica, relativa a 7000000000000000000 | Propósito |
|---|---|
| +0..+2 | Firma y esquema de entidad |
| +3 | Perfil: 1 crecimiento, 0 control lineal |
| +16 | Generación persistente, con máximo de 250 |
| +20 | Semilla para datos de prueba |
| +30 | Cantidad de relaciones nuevas |
| +40 | Confirmación de un lote nuevo, impide reentrenar con lote viejo |
| +64..+66 | Pesos base: bias, signo de X, signo de P |
| +120..+123 | Evidencia de error por composición candidata |
| +200..+203 | Descriptores de relación materializada |
| +220..+223 | Pesos de relaciones, codificados como valor+128 |
| +10000..+10199 | Señal temporal (valor+100); se elimina tras consumirla |
| +11000..+11199 | Segunda señal temporal; se elimina |
| +12000..+12199 | Consecuencia temporal, consultada tras predecir; se elimina |

Al nacer los 4 descriptores son **cero (ausentes)**. Una relación nace
únicamente cuando el mismo patrón de coactivación contribuyó a **tres
errores**; el agente entonces materializa descriptor y peso en las
direcciones lógicas. La evidencia se calcula desde signos observados,
sin tabla precargada de respuestas XOR. No se materializa ningún qubit
físico ni virtual por byte.

Al terminar un lote, `learn.xi` devuelve las **600 coordenadas de datos
temporales** al fondo Ether cero en la **misma transacción** que guarda
relaciones y generación. `audit-clean.xi` demuestra que no queda ninguna
etiqueta, señal ni marcador de lote. Se preservan únicamente pesos, evidencia
estructural e identidad persistente.

Los pesos base se acotan a `[-24,24]`, los relacionales a `[-112,112]`
y se guardan codificados como `peso+128`. Las operaciones del programa
están sujetas al rollback XI completo de REVERSE-PC. El crecimiento se
detiene si los cuatro slots admitidos están ocupados. No existe todavía
poda, autorrevisión de gramática ni descubrimiento universal.

## Controles que deben decidir si merece continuar

- **Crecimiento:** `birth.xi` + `feed-xor.xi` +
  `learn.xi`, sin ninguna etiqueta incrustada en el aprendiz.
- **Contrafactual lineal:** mismo `birth.xi` con
  `linear-control.xi`, mismo `feed-xor.xi`, mismo algoritmo y
  número de experiencias, pero se prohíbe materializar composiciones.
- **Control aleatorio:** mismo aprendiz con crecimiento, pero
  `feed-noise.xi` entrega etiquetas pseudoaleatorias mediante un generador
  de realimentación *separado* del generador de señales; usa bits altos,
  nunca la paridad consecutiva del mismo generador. Los dos mundos tienen
  exactamente la misma secuencia de observaciones, comprobada por
  `input-fingerprint.xi`. Evaluar tanto XOR como ruido separado.
- **Holdout:** valores de magnitud par en entrenamiento, impar en
  evaluación; distintas secuencias. La evaluación puede repetir la
  categoría de signo, por lo que prueba **composición categórica** y
  transferencia entre magnitudes, no extrapolación a nuevos predicados.
- **Integridad:** igualdad de bytes RVPC2 antes/después de cada
  `eval-*.xi`; error deliberado tras alterar peso, sin publicar
  snapshot parcial; rechazo de entrenamiento si no existe lote nuevo.

Las métricas se publican **crudas**, por semilla y control. No afirmar
éxito por mero crecimiento de excepciones, por caída del error en
entrenamiento, ni por comparar con una línea base entrenada en otra
tarea. La hipótesis E005 se sostiene sólo si supera al aprendiz lineal
entrenado en el mismo XOR y se acerca al azar en ruido independiente.

## Lenguaje y límites

Los archivos E005 de IA son exclusivamente `.xi`:
`birth.xi`, `feed-xor.xi`, `feed-noise.xi`, `learn.xi`,
`eval-xor.xi`, `eval-noise.xi`, `rollback.xi`, controles de semilla
y de capacidad. No se añadirá código Python, C++, JS ni modelos
preentrenados para el aprendizaje de BBY Q.

**XI es el dialecto nativo ejecutable; MX (`.mx`) continúa siendo el
lenguaje fuente canónico previsto.** El ejecutable de XI está todavía
compilado con el bootstrap existente en C++; los cambios de E005 no
eliminan ese requisito. La migración honesta hacia MX exigirá ampliar
el lenguaje, probar compatibilidad y eliminar el bootstrap únicamente
cuando exista una cadena de compilación MX autoalojada equivalente.

Un límite importante revelado por los controles: el aprendiz bajo ruido
también llegó a crear cuatro composiciones. E005 **no distingue aún
estructuras útiles de estructuras espurias**; el siguiente criterio de
progresión será retener/promover sólo candidatos que mejoren validación
independiente, probar podas reversibles y contextos A→B→A.

Tampoco se demuestra aquí computación cuántica acelerada: `InverseMemory`
conserva bytes lógicos deterministas, sin materialización cuántica
automática. El éxito sobre XOR sería una prueba de capacidad
representacional ampliada, no inteligencia general.

## Resultado observado y evidencia íntegra — 26 de octubre de 2026

CI final [E005, ejecución 40279710145](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40279710145):
3 semillas independientes (19, 42, 91), **12 épocas de 200 experiencias
para cada uno de 9 agentes/controles**; 21.600 observaciones de
entrenamiento en total, sin contar holdouts y pruebas adversas.

El entrenamiento sobre XOR (2.400 experiencias por agente) se comparó con
un aprendiz lineal que recibió **exactamente los mismos ejemplos** y el
mismo presupuesto de trabajo, excepto que no pudo crear términos compuestos.

| Semilla | Aprendiz que compone relaciones | Control lineal en mismo XOR | Control entrenado con ruido, evaluado en XOR | Ruido entrenado, evaluado en ruido |
|---|---:|---:|---:|---:|
| 19 | 240/240 | 118/240 | 133/240 | 126/240 |
| 42 | 240/240 | 114/240 | 114/240 | 129/240 |
| 91 | 240/240 | 119/240 | 121/240 | 122/240 |

La campaña confirmó 4 descriptores materializados en cada agente
de crecimiento y **0** en controles lineales. Cada holdout es sólo
lectura y su RVPC2 coincide byte por byte con el archivo de entrada.
Cada mutación fallida deja intacto un destino nuevo o ya existente.
Se rechaza reutilizar un lote de realimentación después de procesarlo.
`audit-clean.xi` se ejecutó tras cada época, comprobando eliminación
real del lote entero. El fingerprint de los dos generadores demuestra
coincidencia de entradas para una semilla/época igual.

**Incidente de control y corrección.** Una versión intermedia usó la
paridad de valores consecutivos del mismo generador lineal congruencial;
con semilla 19 el control negativo resultó accidentalmente correlacionado
con XOR (240/240). Esa evaluación no se aceptó: se separó el PRNG del
feedback, se usaron bits altos y se añadieron auditorías explícitas de
correlación, después se repitió todo. Los números finales arriba provienen
del protocolo corregido.

**Compactación real, mismo experimento semilla 42:** antes de borrar los
lotes temporales el archivo RVPC2 tenía **18.673 bytes y 540 excepciones
lógicas** (CI
[40279320860](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40279320860)).
Después de borrarlos de modo transaccional, **5.642 bytes y 22 excepciones**
(CI [40279710145](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40279710145)):
aproximadamente **69,8 % menos bytes** de persistencia. Sigue habiendo
**cero qubits activos y cero enlaces cuánticos**: el ahorro se atribuye
a memoria lógica por reglas, no a aceleración cuántica.

No se ha medido equivalencia semántica con datos externos, prevención
de olvido en cambio de entorno, invención de operadores de gramática
nueva, capacidad abierta, ni independencia del bootstrap C++ ya existente.

[Artefactos binarios RVPC2 y resultados JSONL](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40279710145)
permiten reconstruir el estado final de los nueve agentes estudiados.
