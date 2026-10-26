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
| +10000..+10199 | Primera señal observada, byte de valor+100 |
| +11000..+11199 | Segunda señal observada |
| +12000..+12199 | Consecuencia, consultada sólo después de predicción |

Al nacer los 4 descriptores son **cero (ausentes)**. Una relación nace
únicamente cuando el mismo patrón de coactivación contribuyó a **tres
errores**; el agente entonces materializa descriptor y peso en las
direcciones lógicas. La evidencia se calcula desde signos observados,
sin tabla precargada de respuestas XOR. No se materializa ningún qubit
físico ni virtual por byte.

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
  `feed-noise.xi` entrega etiquetas pseudoaleatorias sin relación
  con las señales; evaluar tanto XOR como ruido en datos diferentes.
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

Tampoco se demuestra aquí computación cuántica acelerada: `InverseMemory`
conserva bytes lógicos deterministas, sin materialización cuántica
automática. El éxito sobre XOR sería una prueba de capacidad
representacional ampliada, no inteligencia general.
