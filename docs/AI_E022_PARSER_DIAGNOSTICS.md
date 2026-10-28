# E022 — diagnóstico y corrección del intérprete XI

La revisión parte de `e8498b765a6a95aa556d0e816aab926257769391`, con el
checkpoint E022 publicado de 500.410 bytes y SHA-256
`33a2490be0d7a9252222991da1cd376e7cfb4ecb0014987c65d1b8b24278f20f`.
No se repite su entrenamiento ni se publica otro estado aprendido. Las dos
correcciones están en XI; el adaptador nativo y las dependencias permanecen
iguales.

## Fallos reproducidos y correcciones

1. **Interrogación después de un preámbulo.** «Oye, ¿qué requiere neral?»
   fallaba antes de interpretar la pregunta: el lector solo admitía `¿` al
   principio del turno. Con E022 activo se admite una única apertura en un
   límite entre palabras, también después de un preámbulo. Se conserva la
   marca de pregunta que impide convertir una consulta en una lección.
   Las aperturas repetidas o dentro de una palabra siguen rechazándose.
2. **Palabras funcionales descartadas dentro de la pregunta.** El analizador
   compositivo aceptaba «qué requiere neral si» o «what does neral require if»
   como si esas palabras finales no existieran. Ahora toda la cláusula desde
   el interrogativo debe coincidir con el sufijo de una construcción aprendida
   de consulta de propiedad: longitud completa, literales, sujeto y predicado.
   Consulta las dos tablas de construcciones existentes. No contiene una lista
   nueva de palabras prohibidas ni respuestas codificadas.

Las construcciones completas ya reconocidas conservan su precedencia. La vía
de generalización sigue admitiendo un preámbulo nuevo ante una cláusula cuya
estructura esté aprendida. Si esa cláusula está incompleta o no tiene una
estructura admitida, se abstiene. No se enseña una condición hipotética ni se
afirma que exista comprensión general del lenguaje.

## Comparación del diagnóstico

Se utiliza el mismo checkpoint, runtime, adaptador, enseñanza descartable y
examinador para ambos programas XI. Las 46 formulaciones se aplican a cuatro
sujetos nuevos: 184 consultas por versión. Incluyen transferencia a `alcanza`,
idiomas ES/EN, conocimiento desconocido y preguntas con apariencia de enseñanza.

| Grupo | Código anterior | Código corregido |
|---|---:|---:|
| Apertura `¿` tras un preámbulo | 0/36 | 36/36 |
| Abstención en cláusulas incompletas | 4/72 | 72/72 |
| Entradas inválidas y consultas sin escritura | 44/44 | 44/44 |
| Consultas válidas conservadas | 32/32 | 32/32 |
| **Total** | **80/184** | **184/184** |

Son pruebas de regresión elegidas a partir del diagnóstico. Las formulaciones
guiaron la corrección; el porcentaje no es una evaluación independiente de
conversación general. Las respuestas esperadas permanecen en el examinador.
Las consultas no modifican hechos, vocabulario ni reglas, y las respuestas
vuelven a funcionar después de reiniciar el proceso.

Las 32 consultas válidas compartidas tuvieron medianas de 41,75 ms antes y
42,58 ms después en esta corrida local. Los tiempos de respuestas rechazadas
y resueltas no se comparan como si fueran el mismo trabajo. No es un benchmark
de rendimiento ni una afirmación de aceleración.

## Conservación y reproducción

El examinador de diagnóstico carga el checkpoint E022 auténtico y reutiliza
las pruebas anteriores de composiciones, temas, inferencia, contradicciones,
negación, ambigüedad, reinicio, fallo de guardado, las 1.522 consultas históricas
en ambos formatos y las 1.024 cuentas reservadas. Las mutaciones de las pruebas
de aprendizaje se hacen en copias descartables. El checkpoint publicado no
se vuelve a entrenar ni se modifica.

**Resultado local completo: 6.303 verificaciones de conservación aprobadas**,
además de las 184 consultas del diagnóstico. Se conservan las 110/110
composiciones E022 y las 16/16 reformulaciones de desarrollo. El examen
aritmético aprueba 1.024 consultas numéricas nuevas y sus controles, 1.062
comprobaciones de texto en total. Estos contadores corresponden a esta corrida;
los 6.365 históricos de E022 incluyen también la enseñanza, que aquí se omite.

La primera corrida de conservación se interrumpió con `cannot write state`:
había una carpeta vacía `state.rvp.pending` de la inyección de fallos. Esa
corrida no se cuenta como aprobada. Cinco ciclos aislados de fallo y recuperación
pasaron; la campaña completa se repitió en un directorio nuevo, comprobando
después de cada fase que no quedara ese fixture. La repetición completa pasó.

[Resultados locales completos y transcripciones del diagnóstico](evidence/e022-parser-diagnostics.json).
La nueva CI queda preparada; todavía no se ha ejecutado para esta corrección.

Los manifiestos E021/E022 conservan los digests originales de los archivos
corregidos en `source_compatibility_fixes`; sus verificaciones de fuentes usan
los digests actuales para reproducir los estados y las regresiones. Los
digests de los checkpoints y los resultados históricos permanecen intactos.

```bash
python3 ai/xi/diagnostics/tests/native-diagnostics.py \
  /ruta/reverse_pc /ruta/bbyq_session \
  --baseline-root /ruta/BBY-Q-en-e8498b7 --out evidence/diagnostics
```

`--quick` ejecuta únicamente el diagnóstico, sin la campaña de conservación.
La nueva CI obtiene la referencia anterior por su SHA, ejecuta el diagnóstico
y la conservación sin reentrenar, y publica resultados y transcripciones.

REVERSE-PC sigue fijado en `6d4de14a2dfbce4b8a7f1cb50e29d11b9073fe98`;
Mundo X, en `e2778d962af22f6f1a0794058dd4685fc2573966`. Son medidas Linux.
Persisten 15 palabras y 255 bytes por entrada, cierre `?` al final, ocho temas
y los límites de búsqueda anteriores. No se implementan párrafos, condiciones
hipotéticas generales, generación libre ni integración con REVERSE OS.
