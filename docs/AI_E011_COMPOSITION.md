# E011 — Reanudar BBY Q y conectar aprendizaje con texto

Base: `main` **1d621ba9875435fd46bdbc13b7459c8c62faef9b**, E010 fusionada
por PR #12 el 26 de octubre de 2026. La captura del chat interrumpido no
era el estado más reciente: el currículo bilingüe sí había terminado.
Esta iteración conserva esa base y **pospone REVERSE OS**.

## Continuidad

Se recuperó el RVPC2 real del artefacto E010, ejecución `40303541105`, sin
repetir E004–E010 ni borrar aprendizaje. Sus 18.722 bytes tienen SHA-256
`de1a02a77c93cab6f2671858a2543dd65c7bf2d2858917290808ae1ae3c5ff1f`.
El checkpoint y el nuevo estado quedan conservados en `ai/checkpoints/`,
con manifiesto de procedencia y huellas, sin depender de artefactos temporales.

Toda la inteligencia añadida está escrita en **XI**, sobre REVERSE-PC
`6d4de14a2dfbce4b8a7f1cb50e29d11b9073fe98` y Mundo X
`e2778d962af22f6f1a0794058dd4685fc2573966`, sin modificarlos.
El examinador Python solo transporta bytes, proporciona consecuencias,
genera preguntas y compara resultados. No analiza el texto para BBY Q,
no selecciona operaciones del agente y no forma sus respuestas.

## Capacidad programada y aprendizaje adquirido

E010 daba nombres a observaciones y calculaba desde entradas estructuradas.
E011 reutiliza esos conceptos numéricos y efectos para trabajar con
microexpresiones de texto y mantener un resultado entre turnos.

| Parte | Procedencia real |
|---|---|
| Nombres ES/EN de cero a nueve | Léxico auténtico aprendido en E010 |
| Efectos de aumentar y disminuir | Modelos aprendidos en E010 |
| `mas`, `plus`, `menos`, `minus`, `juntar`, `quitar`, `y`, `and`, `zeta`, `omega` | Nuevas asociaciones aprendidas desde demostraciones y consecuencias |
| Significado de cada palabra de operación | Se contrasta la consecuencia con los efectos heredados; no hay tabla de palabras en el ejecutable |
| Separación de palabras, normalización ASCII, composición decimal y orden de evaluación | Gramática diseñada e implementada, **no descubierta por el agente** |
| Cadenas de hasta siete operaciones y continuidad de un resultado | Memoria de trabajo y composición programadas sobre asociaciones aprendidas |

Una palabra requiere **dos pares de operandos distintos** que apoyen el
mismo efecto. Repetir un ejemplo no la promueve. Una consecuencia
contradictoria revierte la transacción. En otra copia experimental se enseña
`zeta` como quitar y `omega` como juntar: el mismo código obedece a esa
evidencia, no a las letras de los nombres.

Ejemplos comprobados, emitidos por XI:

```text
dos mas tres                 -> cinco
menos uno                    -> cuatro
plus two                     -> six
nueve mas nueve menos uno    -> 17
65535 menos 65530            -> five  [salida EN]
65535 mas uno                -> ?
```

Las cantidades mayores de nueve se expresan por **composición de dígitos
decimales**. No se afirma haber aprendido «diez», «once» o miles de nuevos
conceptos. Las cantidades se limitan a 0..65535 **en cada paso** y las
operaciones se aplican de izquierda a derecha. No hay precedencia algebraica,
multiplicación ni división. Un turno fallido invalida la referencia anterior.

## Resultados locales

El examen no envía respuestas correctas a la inferencia: solo texto.
La respuesta esperada permanece en el examinador. Las cuatro parejas
de operandos de enseñanza se excluyen del barrido sistemático.

| Examen independiente | Cálculo correcto | Abstención correcta | Total |
|---|---:|---:|---:|
| Combinaciones bilingües nuevas de números 0–9 | 294 | 90 | 384 |
| Cadenas aleatorias, semilla 170119 | 226 | 74 | 300 |
| Cadenas aleatorias, semilla 270127 | 231 | 69 | 300 |
| Cadenas aleatorias, semilla 370129 | 228 | 72 | 300 |
| Total del protocolo | **979** | **305** | **1.284** |

También pasan mayúsculas y espacios, ES/EN, continuidad con reinicio de
proceso, ceros iniciales, siete operaciones, desconocidos, Unicode no
soportado, sintaxis inválida, desbordamiento, capacidad de 32 palabras,
cabecera dañada, repetición de evidencia y lecciones contradictorias.

Se comparan el **núcleo completo y todos los bytes lógicos anteriores**:
ninguna entrada fuera de la región E011
`7300000000000000000..7300000000000002047` puede cambiar. Las auditorías
E008/E009/E010/E011 dejan el archivo completo intacto. La revisión global
de memoria sí avanza al escribir la ampliación; no se afirma igualdad
del archivo completo con E010.

El estado aprendido ocupa **21.252 bytes** (+2.530), con SHA-256
`efe5585761d4745b868c83e55cc1c6356291f396649458c03814ca27b2f6b453`.
Dos campañas locales produjeron esa huella. Los tiempos en
`docs/evidence/e011-results.json` incluyen procesos y verificación del
examinador; no miden un Samsung ni demuestran ventaja de hardware.

## Reproducir o utilizar el estado conservado

Con el runtime XI fijado ya compilado:

```bash
base64 -d ai/checkpoints/E010-original.rvp.b64 > original.rvp
python3 ai/xi/dialogue/tests/native-composition.py /ruta/reverse_pc original.rvp \
  --out evidence/e011 --seeds 170119 270127 370129 --cases-per-seed 300

base64 -d ai/checkpoints/BBYQ_E011_Compositional_ES_EN.rvp.b64 > bbyq.rvp
bash ai/xi/dialogue/text.sh /ruta/reverse_pc bbyq.rvp 'dos mas tres' es
bash ai/xi/dialogue/text.sh /ruta/reverse_pc bbyq.rvp 'minus one' en
```

`text.sh` transporta bytes, enlaza módulos y publica una transacción;
no interpreta preguntas ni calcula respuestas. `bbyq.rvp` es la copia
de trabajo y los checkpoints se conservan. XI realiza lectura, resolución,
interpretación y respuesta en una autoridad RVPC2. Un bloqueo evita
escritores simultáneos de esa copia.

## Distancia respecto a una IA conversacional grande

**El examen no prueba «medio nivel» de una IA grande.** Es finito y estrecho.
BBY Q todavía no conversa sobre temas abiertos: ASCII, 255 bytes por entrada,
15 palabras de hasta 16 letras, 32 palabras de operación y una referencia
numérica entre turnos.

Para acercarse al objetivo falta demostrar:

1. Identidades semánticas compartidas por lenguaje y escuela, relaciones
   nuevas y respuestas a formulaciones distintas sobre muchos conceptos.
2. Más vocabulario, Unicode, estructura de frases y memoria de varios
   referentes; comprensión y seguimiento de instrucciones nuevas.
3. Razonamiento en varios dominios y problemas verbales sin exponer
   respuestas al agente ni resolverlos en el programa anfitrión.
4. Percepción real, prácticas elegidas por los errores, transferencia
   y retención con exámenes separados.
5. Una rúbrica común frente a una referencia concreta. Estas cuentas
   no permiten calcular un porcentaje de inteligencia general.

No se agregan modelos externos ni integración de escritorio.
