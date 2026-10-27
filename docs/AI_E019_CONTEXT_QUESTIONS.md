# E019 — Intención de pregunta y contexto factual acotado

Continúa el E018 auténtico, sin repetir su currículo ni añadir un modelo
externo. Toda interpretación, reconstrucción de referencias, aprendizaje de
construcciones, deducción y respuesta se ejecutan en XI. El programa sigue
siendo fuente XI textual; esta etapa no implementa una ISA binaria compacta.
`--compact` sigue designando el protocolo de respuesta anterior.

## Qué significa reconocer una pregunta

BBY Q identifica una intención operativa y sus papeles semánticos cuando
una construcción aprendida coincide con la entrada: consultar propiedades,
verificar una relación, explicar evidencia o enseñar explícitamente una
afirmación. No requiere siempre un signo de interrogación. Una interrogación
con un marcador de enseñanza no puede convertirse en una escritura de hechos.

Esto no implica conciencia de estar siendo interrogado ni comprensión de
cualquier formulación. El selector compara restricciones aprendidas, tipa
las variables y pide aclaración si dos interpretaciones igualmente específicas
asignan papeles distintos. Una forma desconocida puede quedar fuera de alcance.

## Continuación del aprendizaje

La capacidad pasa de 64 a 96 construcciones. Sus registros de 96 bytes
siguen en la región original: el último termina antes del mapa de tipos en
`U+20000`, sin mover ni reescribir las 64 construcciones previas. `U` es
`7800000000000000000`.

Se enseñan 32 construcciones nuevas, con 60 presentaciones etiquetadas:
12 formas de pregunta explícita y 20 de continuación contextual. Seis formas
léxicas y dos fragmentos bilingües de aclaración se añaden al estado.
Los marcos con variables requieren ejemplos que varíen sus papeles explícitos;
repetir el mismo predicado no habilita un marco cuyo único papel sea ese
predicado. Las cuatro construcciones enteramente literales no necesitan
descubrir posiciones variables.

La semántica de los cuatro actos contextuales está implementada en XI;
el entrenamiento descubre qué secuencias los invocan y dónde están sus
argumentos. No se presenta esa implementación como descubrimiento autónomo.

| Intención | Conserva del tema anterior | Toma de la nueva entrada |
|---|---|---|
| 9, propiedad contextual | Sujeto | Predicado |
| 10, verificación contextual | Sujeto | Predicado y objeto |
| 11, cambio de sujeto | Predicado | Sujeto; busca sus propios objetos |
| 12, clasificación contextual | Sujeto | Consulta la relación `es/is` |

## Referencias y ejemplos

Se reutilizan los descriptores persistentes `U+12..19`: validez, modo y
sujeto/predicado/objeto de la última pregunta factual apoyada. Las respuestas
factuales anteriores de E016 también pueden aportar su descriptor válido.
La ruta de cuentas conserva la propiedad de «y Luis» o «y las peras» cuando
el tema activo es una cuenta. No se confunden cantidades con clasificaciones.

Ejemplo didáctico con un nombre reservado para el examen:

```text
Usuario: aprende que neral es clasea
BBY Q:   Aprendí esa afirmación del diálogo.
Usuario: sabes qué requiere neral
BBY Q:   Según lo aprendido: Neral requiere agua.
Usuario: y qué requiere
BBY Q:   Según lo aprendido: Neral requiere agua.
Usuario: what is it
BBY Q:   From the taught statements: Neral is clasea.
```

La regla y la propiedad de la clase son las didácticas ya calibradas en
E017. El nombre nuevo y la consecuencia consultada no aparecen en las
demostraciones sintácticas. Cambiar a otro sujeto obliga a consultar su
propia evidencia; no se copia la respuesta del sujeto anterior.

Una consulta sin resultado, una ambigüedad, una contradicción o un cambio
de dominio invalida el contexto aplicable. Una consulta delegada al buscador
anterior solo conserva sus descriptores si la búsqueda realmente tuvo éxito.
El reinicio explícito del episodio borra las referencias. Cerrar y abrir el
proceso conserva un contexto válido, en el mismo RVPC2.

Si falta esa referencia, el nuevo acto supervisado responde:
«Necesito una referencia anterior o una pregunta completa».
Las respuestas de incertidumbre anteriores conservan su texto.

## Examen reproducible

El examinador nativo continúa el padre identificado por SHA-256
`df074a27d284025ccd033373c92f116c5c3237455e9f51891fcfa0392828aaec`.
Las respuestas esperadas permanecen fuera del proceso del agente; solo texto
y preferencia de idioma cruzan el transporte de cada turno.

El examen cubre las 32 formas sobre parejas de entidades nuevas. El predicado
`requiere/requires` del examen no es uno de los predicados usados para enseñar
las posiciones de estas nuevas formas. Se prueban también transitividad sobre
aristas nuevas, cambio de sujeto con respuestas diferentes, negación explícita,
excepciones a una herencia, contradicción entre afirmaciones directas, retirada,
preguntas con aspecto de enseñanza y referencias después de una duda.

El diagnóstico antes/después usa 32 sondas fijas. Esa puntuación describe
solo esas sondas; no es un examen de comprensión general del lenguaje.
El resultado local pasa de **0/32 a 32/32**. La campaña completa aprueba
**5.617 verificaciones**: incluye 32 diálogos de 67 turnos (2.144 turnos),
con 1.024 problemas de las formas nuevas; además vuelve a comprobar las 25
construcciones E018 en 20 diálogos nuevos de 12 turnos. No se publica el
contenido de esos diálogos como conocimiento del modelo.

Aplicar las 60 presentaciones sintácticas, seis formas léxicas y dos
fragmentos de aclaración sobre el runtime ya compilado tarda **1,84 s** en
esta ejecución. Excluye el desarrollo, la compilación y el examen. Las 1.024
consultas medidas tienen mediana de 26,92 ms y percentil 95 de 37,65 ms,
incluido guardar antes de confirmar. No es una comparación de aceleración.
El proceso nativo informa 7.000 KiB residentes y 22.448 KiB de pico en esa
sesión, con cero qubits activos. No se midió Android.

La regresión vuelve a examinar las 1.522 consultas anteriores en ambas
superficies, las construcciones E018 sobre nuevos sujetos, reinicio, rollback
y clientes públicos. La CI reconstruye además las etapas anteriores.

Los resultados completos se publican en `docs/evidence/e019-results.json`
y el diagnóstico en `docs/evidence/e019-diagnostic.json`. El manifiesto fija
el padre, el checkpoint y las huellas de los datos nuevos. La reproducción
compara núcleo, memoria lógica y enlaces completos; el contador de revisiones
MXIM2 puede cambiar con escrituras temporales sin alterar ese estado lógico.

## Estado y límites

El estado publicado conserva los hechos y reglas anteriores. No incorpora
afirmaciones, alias ni nombres del examen. No se amplían las dos familias
de deducción calibradas: transitividad y herencia de propiedades.
Ocupa **319.274 bytes**, con SHA-256
`aa8be33d964af55d9976f46745775113d6996630cbbfad3bb5c2b4d75833e9d0`.
Los 64 registros sintácticos anteriores permanecen idénticos; solo se añaden
registros declarados y se actualizan los contadores de léxico y construcciones.

Se mantiene un referente factual activo, además del dominio anterior de
cuentas. No hay resolución general de correferencias entre muchos personajes,
interpretación libre de párrafos largos, inferencia general de intenciones ni
conversación abierta. Siguen los límites de 255 bytes y 15 palabras por turno,
64 nodos de búsqueda, 32 de prueba y ocho resultados. Las 96 construcciones
ocupan la capacidad de esta versión.

REVERSE-PC permanece fijado en
`6d4de14a2dfbce4b8a7f1cb50e29d11b9073fe98` y Mundo X en
`e2778d962af22f6f1a0794058dd4685fc2573966`. El runtime C++ y los examinadores
Python siguen siendo infraestructura; no interpretan preguntas por el agente.
No se integra REVERSE OS ni se afirma ventaja cuántica o aceleración general.

```bash
base64 -d ai/checkpoints/BBYQ_E019_Context_Questions_ES_EN.rvp.gz.b64 | gzip -dc > bbyq.rvp
python3 ai/native/session_client.py /ruta/bbyq_session bbyq.rvp --language es
```

Para continuar desde el padre auténtico:

```bash
base64 -d ai/checkpoints/BBYQ_E018_Concise_Dialogue_ES_EN.rvp.gz.b64 | gzip -dc > parent.rvp
python3 ai/xi/open/tests/native-e019.py /ruta/reverse_pc /ruta/bbyq_session parent.rvp --out evidence/e019 --dialogs 32
```
