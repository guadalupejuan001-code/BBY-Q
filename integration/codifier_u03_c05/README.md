# BBY Q U03 — Ciclo C05: Codificador semántico sin pérdida (XI/Ether)

**Estado:** implementación experimental, opt-in. **No APK, no entrenamiento del
modelo congelado, no publicación de nueva inteligencia general.**

**Origen:** [C04 PR #90](https://github.com/guadalupejuan001-code/BBY-Q/pull/90),
commit `6e76dffd5ab8daccd5c87d6ea31515ad7106236e`.
No se modifican los bancos de los motores C1, VQC3, QRL3, QMemory, QChat100,
E02 ni los checkpoints originales. C05 preserva su interfaz pública y
todas las operaciones XI de la versión U02.

## Problema que resuelve

C1 ya conserva el orden, los bytes originales, los números y la negación
en su transporte exacto, pero su cabeza conversacional congelada sigue
confundiendo algunas paráfrasis y no expone un marco estructurado de
proposiciones con alcance de negación y referencias conversacionales.

**No se necesita destruir C1 ni reemplazarlo por una IA convencional.**
C05 añade una capa semántica de datos, versionada y reversible, junto al
C1 nativo. Este ciclo construye el soporte para entrenar composición en C06.

## Representación

Archivo: `integration/codifier_u03_c05/semantic.py`.

- Usa **exactamente el tokenizador y el diccionario C1 existentes**. No
  introduce una normalización que borre mayúsculas, tildes, emojis,
  espacios o distinciones de carácter. Conserva el texto original UTF-8
  con todos sus bytes, y cada token con posición en bytes, tamaño e ID C1.
- Expone **eventos estructurados candidatos**: verbo/acción, posición
  original, roles respaldados por spans explícitos (por ejemplo nombre de
  regla, objeto observado, muestra, posición, propietario, nombre propio).
- La negación incluye **alcance** y tipo: prohibición de acción, exclusión
  contrastiva de tema, ausencia o caso sin resolver.
- Los valores numéricos incluyen **lexema, signo, separador decimal y
  Decimal exacto** sin pérdida por redondeo binario del host. Esto no cambia
  el canal numérico aprendido de C1 ni afirma que el modelo pueda calcular
  todos los decimales arbitrarios.
- Registra marcadores de condición `si ... entonces` y distingue
  `sí` afirmativo. Conserva referencias como `repítelo` como
  **candidatos no verificados**. Si hay antecedentes múltiples o falta
  contexto explícito, devuelve referencia sin resolver.
- El paquete **C05SEM1** tiene longitud acotada, versión, SHA-256 y validación
  semántica de fuente al decodificar. Una cadena con anotaciones falsas,
  aunque tenga su SHA recompuesto, es rechazada.

### Ejemplo: negación no es lo mismo que exclusión

| Texto | Representación |
| --- | --- |
| `no definas memoria` | Prohibición cuyo alcance incluye la acción "definir" |
| `define memoria no interferencia` | Definir "memoria"; excluir el tema "interferencia"; **no** prohibir la acción |
| `no quiero que definas memoria, explica interferencia` | Primer verbo prohibido; segundo verbo no negado por esa cláusula |
| `sin datos no hay respuesta` | Ausencia / negación cuya interpretación no se fuerza artificialmente |
| `repítelo` tras `define memoria` | Antecedente candidato; resolución todavía pendiente de validación |

Esta gramática es **deliberadamente limitada y conservadora**; los spans
no equivalen a comprensión libre ni a razonamiento validado. Los eventos
desconocidos siguen preservando el texto literal para aprendizaje futuro.

## XI nativo y compatibilidad con el codificador C1

`ai/xi/c05/semantic-frame.xi` contiene un validador real del
nuevo marco. Sobre un checkpoint C1 **temporal** inicializado con el runtime
original REVERSE-PC:

1. `C1.Model.prepare` ejecuta el codificador XI de siempre.
2. Se compara la memoria nativa `RAW/HRAW` y cada longitud del
   token nativo `TL` contra la representación C05.
3. Las posiciones y alcances se transportan a una zona XI temporal distinta.
4. `call c05_validate_frame` verifica **en XI** los límites
   de bytes, tokens y negaciones. Un marco excedido produce estado 4.
5. No se guarda el banco temporal ni se incorpora este código al modelo
   congelado. La inferencia y el entrenamiento originales permanecen iguales.

Esta comprobación nativa acredita **transporte y límites**, no que XI haya
aprendido todavía los roles semánticos; eso corresponde a C06.

## Integración con BBY Q U03

`SemanticSession` hereda la sesión C04 e incorpora la
representación antes de cada turno, conservándola **solo en memoria** como
`last_semantic` y `last_semantic_wire`. Después
ejecuta **el mismo turno nativo**: rutas, decisiones, feedback, checkpoints,
SQLite, SHA, rollback y respuestas siguen sin cambios.

    from integration.codifier_u03_c05.semantic import analyze, wire_encode, wire_decode
    from integration.codifier_u03_c05.session import SemanticSession

    with SemanticSession("build/c05/synthetic.sqlite") as bbyq:
        answer = bbyq.turn("id-1", "no resuelvas Nara")
        print(answer)
        print(bbyq.last_semantic["negations"])

Por seguridad, esta capa **no inyecta todavía roles no entrenados** en la
decisión aprendida. C06 podrá consumirlos tras el entrenamiento con
separación real entre entrenamiento, validación y tests independientes.

## Pruebas y reproducción

Linux, Python 3.12, Node 24, REVERSE-PC
`08c363e6c6855c14026c86046af7183a45f45a98` y mundo-X
`e2778d962af22f6f1a0794058dd4685fc2573966` fijados.

    python3 -m unittest integration.codifier_u03_c05.test_semantic -v
    bash deps/reverse-pc/scripts/build-xi-session.sh deps/mundo-x deps/reverse-pc/build
    python3 -m integration.codifier_u03_c05.verify_native
    python3 -m integration.codifier_u03_c05.conformance
    python3 -m integration.codifier_u03_c05.benchmark --samples 2 --out build/c05/benchmark.json

CI: `.github/workflows/bbyq-u03-c05-codifier.yml` audita C1/U02,
gradientes, rollback, migraciones, bytes del protocolo y el benchmark.
Los 159 archivos protegidos deben conservar SHA-256 idénticos.

**Criterio de salida:** C05 no se considera validado hasta que pasen
los contratos de negación/números/roles, la comprobación XI, U02/C04/C05
con hashes de checkpoint idénticos, la prueba de fallos y la comparación
de costo. No se declara una mejora de exactitud de QChat hasta C06.

## Pros y contras de arquitectura

**Pros:** representación composicional reutilizable; datos originales
totalmente conservados; roles explicables por posiciones y procedencia;
números exactos en metadatos; separación entre rechazo explícito de acción
y exclusión contrastiva de un tema; sin cambiar el ABI de XI ni el formato
de bancos RVPC2.

**Contras:** una capa extra cuesta CPU y RAM y su análisis es limitado;
las expresiones ambiguas requieren aprendizaje y validación, no reglas
que inventen significados; C05 por sí solo no reduce los fallos del
generador C1 ni transforma los 1000 cúbits en una AGI.

**No APK. Sin fusión automática. C05 es prototipo de codificación, no el
ciclo de entrenamiento C06.**
