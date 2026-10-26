# E013 — Rendimiento medido de XI y memoria, con el mismo conocimiento

Base reproducible: E012 `7b39a752e23e87946f98481a1b62becf1d657b33`.
Checkpoint original: 157.115 bytes, SHA-256
`8961833bb7140d7b63494dbd96ff02136559fd25eeca5a51f65fe3148131844f`.
No se reentrena ni se sustituye ese archivo. REVERSE OS sigue pospuesto.

## Qué participa realmente en la estructura

«Madre/padre» no aparece como nombre formal de una interfaz del repositorio.
La base verificable en esta prueba es:

| Componente | Participación observada |
|---|---|
| XI | Analiza, consulta, calcula, deduce y construye las respuestas |
| Inverse Ether Memory | Autoridad lógica de palabras, hechos, reglas y memorias; 6.034 excepciones en el checkpoint base |
| QuantumRuntime de REVERSE-PC/Mundo X | Candidatos transaccionales, rollback y publicación coherente de núcleo y memoria |
| InfiniteCore | Se conserva completo; **0 qubits activos, 0 componentes y 0 reglas Ether cuánticas** en esta carga |
| Persistencia RVPC2 | Se escribe antes de anunciar cada respuesta, también en sesión residente |

Las cifras **no demuestran aceleración cuántica**: no se ejecutaron puertas
ni enlaces de qubits. Evalúan esta ruta simbólica de XI y su memoria dispersa.

REVERSE-PC sigue fijado en `6d4de14a2dfbce4b8a7f1cb50e29d11b9073fe98`
y Mundo X en `e2778d962af22f6f1a0794058dd4685fc2573966`.
No se modifican esos repositorios ni se introduce otro modelo de IA.

## Dónde se iba el tiempo y qué cambió

Un perfil por etapas encontró unos 7–8 ms de costo de proceso/restauración/
publicación aun para una operación vacía. La limpieza de miles de posiciones
añadía varios milisegundos. La entrada de usuario también volvía a enlazar
todos los módulos mediante numerosos procesos de shell en cada consulta.
Las mediciones por etapa usan entradas reales y un no-op equivalente;
sus medianas **no se suman como una descomposición exacta** de la latencia.

Se implementaron tres cambios:

1. **Limpieza acotada en XI.** Se borran los bytes reales de entrada, los
   slots de tokens/resoluciones y los nodos visitados. La cola incluye el
   objetivo encontrado y se registra antes de cualquier salida. Se conserva
   la auditoría E012 que exige cero residuos en todo el espacio temporal.
2. **Caché de código enlazado.** Guarda solamente instrucciones, nunca
   preguntas, hechos ni respuestas. La huella cubre todos los módulos;
   una edición invalida la copia. Un control cambia el renderizador en
   una copia aislada y verifica que la nueva fuente sí se ejecute.
3. **Sesión nativa residente.** Mantiene cargado un QuantumRuntime y el
   programa XI. El adaptador C++ transporta bytes y reutiliza directamente
   el bootstrap original mediante `#include "reverse_pc.cpp"`; no contiene
   tokenizador, clasificador, hechos ni razonamiento alternativo.

La sesión todavía ejecuta el intérprete XI y escribe el checkpoint en cada
turno. El candidato solo sustituye a la autoridad activa después de que
`save_state` termina. No se difieren los guardados hasta cerrar la sesión.

## Resultados locales de una deducción representativa

Entrada: `gato es organismo?`, misma respuesta y camino de prueba.
Linux x86-64; ejecución serial, caché de disco del sistema sin vaciar.
No son mediciones de un Samsung ni de Android.

| Ruta | E012 | E013 | Alcance |
|---|---:|---:|---|
| Ejecutor, proceso nuevo con programa preparado | 18,18 ms | 14,62 ms | Incluye restaurar y publicar RVPC2 |
| Entrada CLI completa, código caliente | 65,78 ms | 48,11 ms | Incluye shell, transporte y respuesta |
| Sesión residente, entre turnos | 9,78 ms | **7,29 ms** | Misma persistencia por respuesta |

Pasar de la entrada anterior a la sesión E013 reduce la mediana de ese caso
aproximadamente **89 %**. El ahorro combina cambio de ruta y optimización
del núcleo: no se atribuye todo a un único algoritmo.

La mejora del mismo modo residente es aproximadamente 25 %. La preparación
inicial de la fuente/sesión se mide aparte; los tiempos entre turnos no
representan el arranque completo de la aplicación.

## Escala con datos realmente enseñados

Los estados de prueba se construyen mediante los programas XI de aprendizaje:
138 alias adicionales y hechos sintéticos etiquetados como control. Se
consulta el último alias y una relación densa. No son reservas de direcciones
vacías ni se publican esos hechos artificiales como conocimiento real.

| Hechos / entradas léxicas | Archivo RVPC2 | CLI E012 | Sesión E013 | RAM residente E013 |
|---|---:|---:|---:|---:|
| 185 / 374 | 157.115 B | 65,78 ms | 7,29 ms | 3,79 MiB |
| 256 / 512 | 211.356 B | 67,81 ms | 7,97 ms | 4,14 MiB |
| 512 / 512 | 243.285 B | 68,97 ms | 8,63 ms | 4,34 MiB |

Mismo caso representativo; otras rutas y sus percentiles están en los JSON.
Los hechos adicionales no hacen más profunda esa deducción: esta tabla mide
costo de crecer en datos, no razonamiento universal sobre 512 hechos a la vez.

Se rechazan transaccionalmente la entrada léxica 513 y el hecho registrado
513. Esos son límites implementados y probados, no recursos ilimitados.

## Resistencia, memoria y conservación

- **1.000 turnos consecutivos**, todos con respuesta verificada y el archivo
  legible antes de cerrar la sesión. Mediana 7,28 ms y p95 10,53 ms en esa
  mezcla de cinco tareas; es otro trabajo distinto del caso de la tabla.
- RAM residente muestreada: 3.719–3.781 MiB entre comienzo y turno 900;
  pico `getrusage(RUSAGE_SELF)` de 17,66 MiB, incluyendo el ciclo de vida
  del proceso. El tamaño aprendido y todos sus bytes canónicos se conservan.
- Un grafo ancho alcanza las **64 expansiones** y se abstiene limpiamente.
  Un camino de **31 pasos** se demuestra; el de 32 se abstiene sin residuos.
- Fallos de XI y de escritura conservan tanto el archivo como el contexto
  cargado. Tras fallar una suma, el turno siguiente conserva el número previo.
- Segundo escritor, acceso por enlace simbólico, reinicio y corrupción del
  checkpoint se comprueban. El bloqueo corresponde a la ruta canónica.
- La campaña E012 completa sigue pasando: 1.522 consultas, evidencia,
  contradicción/recuperación, vocabulario nuevo y preguntas E009/E011.

La revisión de escritura del contenedor puede variar por el nuevo registro
temporal de visitas. Por eso la CI E012 compara **todo el núcleo, todos los
bytes lógicos y todos los enlaces**, no exige una revisión de I/O idéntica.
El checkpoint histórico E012 permanece intacto.

## Método y evidencia

Las comparaciones usan el mismo binario base, estados iguales por tamaño,
ocho tipos de consulta y orden aleatorio determinista intercalado entre A/B.
También se intercalan las dos sesiones residentes. Se verifica cada salida
fuera de la ventana de tiempo. La publicación del checkpoint está incluida.

Por caso: 30 muestras de ejecutor/sesión y ocho de CLI en la base; 20 y cinco
en los estados mayores. p95/p99 usan rango más cercano; con pocas muestras
no describen colas de producción con precisión. La CPU de procesos hijos
se obtiene por diferencias de `RUSAGE_CHILDREN`; su RSS es un máximo acumulado
del lanzador y **no** se usa como RAM exclusiva de la IA. Los valores de la
tabla vienen de `VmRSS` leído por el propio proceso nativo; el pico es SELF.

Evidencia resumida:

- `docs/evidence/e013-baseline-profile.json`
- `docs/evidence/e013-performance-base.json`
- `docs/evidence/e013-performance-facts-256.json`
- `docs/evidence/e013-performance-facts-512.json`
- `docs/evidence/e013-stress.json`

Los artefactos CI incluyen muestras individuales y estados sintéticos de
control. Ninguna cifra implica comparación con modelos grandes o velocidad
garantizada en un teléfono. El currículo y la gramática siguen acotados.

## Usar la sesión

Con el runtime original y Mundo X fijados ya preparados:

```bash
bash ai/native/build-session.sh /ruta/REVERSE-PC /ruta/session-build
base64 -d ai/checkpoints/BBYQ_E012_Knowledge_ES_EN.rvp.gz.b64 | gzip -dc > bbyq.rvp
python3 ai/native/session_client.py /ruta/session-build/bbyq_session bbyq.rvp --language es
```

Cada línea de stdin es un turno; EOF cierra y libera el escritor. El cliente
solo transporta bytes y muestra los registros de salida. Las lecciones
estructuradas se ejecutan tras cerrar la sesión para mantener una autoridad.
