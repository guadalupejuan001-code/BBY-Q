# BBY Q U03 / C03 — Caché de modelos autenticados (sin APK)

**Rama base:** U03 C02 / PR #88, commit 4868ceb7ffc0a38959d61685ef9a569f07b61458.
Todos los componentes originales de XI/Ether, REVERSE-PC, el banco C1,
VQC3, QRL3, QMemory, QChat100 y los checkpoints continúan congelados.

## Hallazgo crítico: NO es seguro omitir la segunda ejecución VQC

El primer prototipo intentó reutilizar directamente la probabilidad nativa
cuando una misión compuesta volvía a observar la misma muestra. Se confirmó
una reducción exploratoria de llamadas y latencia, pero el verificador
diferencial **RECHAZÓ** el diseño: el banco V3 persistido cambió en
**32.155 bytes**, a pesar de producir la misma respuesta inmediata.

Diagnóstico real del experimento rechazado:
- CI inicial: https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42332642104
- CI adicional y byte-diff: https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42333102169
- Banco divergente: v3, mismo tamaño 2.718.928 bytes, primera diferencia
  en el offset 21 y 32.155 bytes distintos.
- El resto de bancos y las respuestas permanecieron iguales en esa prueba,
  **pero eso no demuestra que el estado cuántico siguiente sea equivalente**.

Por tanto, C03 **NO salta clasificaciones, lecturas cuánticas, entrenamiento,
percepción, ni efectos de runtime**. El riesgo se documenta en vez de ocultarlo.

## Optimización segura: no descomprimir varias veces los checkpoints congelados

En una misma ejecución de Python, sesiones U02 distintas pueden cargar,
verificar y descomprimir repetidamente las mismas imágenes inmutables
al inicializarse: lector C1, router, readout V3 y bancos de la entidad.

C03 ofrece un adaptador opt-in:
- Usa la carga original U02 para autenticar cada archivo antes de incorporarlo
  a la caché en el primer acceso. No altera los formatos, pesos ni nombres.
- En cada consulta siguiente calcula nuevamente el hash SHA-256 del contenido
  de todas las dependencias: manifiesto, fragmentos comprimidos, vocabulario,
  fuentes nativas asociadas y archivos declarados en la identidad.
- Solo si todos esos bytes son idénticos reutiliza la imagen RVPC2 ya
  autenticada. Cualquier cambio, incluso con igual tamaño, invalida la entrada.
- Admite máximo 12 entradas y 96 MiB en memoria por contexto; devuelve copias
  de los diccionarios y nunca un objeto de modelo entrenable mutable.
- Se elimina al terminar el contexto; no existe caché personal en disco,
  no mezcla bases de datos ni acumula memoria indefinidamente.
- Mantiene el mismo bytecode de los dos inicializadores U02 (Session y
  Legacy.Workspace), con dependencias enlazadas a globals aislados.
  No hay monkey-patching global ni cambio de ninguna transacción SQLite.
- Session.turn se mantiene **exactamente igual**. El número de instrucciones
  XI nativas ejecutadas debe ser idéntico en U02 y C03.
- No confundir caché de imágenes inmutables con caché de resultados cuánticos.

## Uso experimental

    from integration.cache_u03_c03.session import CachedSession, archive_cache_scope

    with archive_cache_scope(max_bytes=96*1024*1024) as models:
        with CachedSession("build/c03/demo.sqlite") as bbyq:
            print(bbyq.turn("1", "calcula 7 + 3"))
        with CachedSession("build/c03/demo.sqlite") as bbyq:
            print(bbyq.turn("2", "lee la regla Faro Azul"))
        print(models.snapshot())

El beneficio aparece al abrir **varias sesiones en un proceso que mantiene
el contexto**. Fuera de ese contexto, CachedSession ejecuta la carga original,
sin conservar imágenes entre turnos.

## Pruebas en GitHub (nunca Android)

Compilar el XI host original con las revisiones REVERSE-PC y mundo-X fijadas
en C00 y ejecutar:

    python3 -m unittest integration.cache_u03_c03.test_cache -v
    python3 -m integration.cache_u03_c03.diagnose
    python3 -m integration.cache_u03_c03.conformance
    python3 -m integration.cache_u03_c03.benchmark --samples 2 --out build/c03/benchmark.json

La CI comprueba:
- fuente e identidades C1/U02 y 159 archivos originales SHA-256;
- igualdad completa de respuestas, histórico y hashes de todos los bancos;
- replay, rollback, feedback y migración U01 mediante verificación original;
- detector de corrupción SHA incluso si el fichero tiene el mismo tamaño;
- capacidad máxima de caché, alcance, eliminación en el cierre y fallos de
  lectura; ningún estado de XI o predicción se obtiene de caché;
- comparación A/B original frente a cache, tiempo, carga de modelos, bytes
  recuperados y cantidad **idéntica** de paquetes XI nativos.

## Pros, contras y siguientes barreras

**Ventajas:** descompresión y validación de estructura una vez por identidad
inmutable, sin modificar los modelos ni la semántica; invalidación por SHA
del contenido real; beneficio potencial al abrir muchas sesiones nativas.

**Costos:** releer y calcular SHA-256 en cada lookup sigue consumiendo E/S y
CPU; la caché consume hasta 96 MiB de RAM por ámbito experimental; el tiempo
de la inferencia XI no se reduce. No hay ganancia garantizada de latencia,
FPS, batería o inteligencia.

El ahorro de trabajo en el proceso anfitrión se compara en GitHub/Linux;
no extrapolarlo a hardware Android ni a un runtime único permanente.
Para eliminar duplicaciones de VQC de forma segura habría que rediseñar
separadamente los estados **persistentes** y los temporales del simulador,
con contrato de equivalencia nativa y migración validada.

**No hay APK, reentrenamiento global, checkpoints modificados ni actualización
de la rama principal.**
