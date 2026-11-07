# BBY Q U03 / C03 — Caché nativa dentro del turno (experimental, sin APK)

## Base congelada

Continúa exactamente desde C02 / PR #88, commit
`4868ceb7ffc0a38959d61685ef9a569f07b61458`.
Los 159 archivos protegidos por C00, incluidos los modelos,
checkpoint VQC/QRL, memoria, gradientes y código original XI, NO se modifican.

No se instala Android ni se genera APK. La sesión estable U02 permanece intacta.

## Qué redundancia elimina

En una misión compuesta, la gramática U02 ejecuta:

1. `observe(name, seed)` => `vqc_sample -> forward -> u2_apply`
2. `mission(name, rule, position)` => recuerda QMemory y vuelve a clasificar
   las **mismas** observaciones, sin una actualización V3 entre ambos pasos.
3. El objetivo E02, política QRL3 y QChat100 dependen de esa clasificación.

El experimento C03 permite reutilizar el primer **resultado nativo real**,
sin ejecutar una segunda vez el mismo programa de percepción. No calcula una
clase o probabilidad en Python.

La traza de la respuesta U02 conserva las dos referencias al dato nativo
para mantener compatibles recibos/checkpoints históricos; el perfilador
separado registra el número real de ejecuciones XI ahorradas. Un "hit" no
representa una segunda ejecución.

También existe una caché de las lecturas `qm_read` idénticas,
en el **mismo turno**, solo cuando no se ha escrito un banco QMemory entre
las dos. Su beneficio es condicional: las misiones U02 de referencia no
repiten normalmente la misma lectura QMemory.

## Reglas de integridad

- **Alcance:** solo dura un `Session.turn`; nada de entradas persistidas,
  bases globales o reutilización entre turnos. Cada instancia Quantum tiene
  su propia LRU independiente y descartable de **máximo 8 entradas por banco**.
- **Clave VQC:** SHA-256 del *programa XI completo* y el input tipado que
  transporta, revisión de percepción, identidad de readout y argumentos de
  observación. Clave QMemory: programa XI exacto, revisión y slot.
- **Invalidación:** cualquier otra operación nativa en V3 (por ejemplo
  política QRL, feedback, SGD/Adam) invalida el VQC; cualquier operación
  mutante de QMemory invalida lecturas anteriores.
- **Nunca se cachean** ablations destructivas, `qprepare` de borrado,
  entrenamiento, reintentos de conflictos C02, ni resultados de otros turnos.
- **Error:** una ejecución XI fallida no se guarda; todos los datos privados
  del turno se descartan en cualquier rollback, y el U02 original decide
  cuándo publicar el estado.
- **Inyección sin mutar archivos U02:** CachedSession ejecuta el mismo objeto
  de código Python de Session.turn original con una tabla de globals aislada
  que sustituye SOLO la clase Quantum. No hay monkey-patching global entre
  hilos ni cambios en el runtime de REVERSE-PC.
- **Admisión de despliegue:** si un checkpoint completo difiere siquiera en
  un byte (SHA), o una ablation cambia, la prueba diferencial falla. El
  modo no se activa en producción.

## Cómo reproducir

Con las revisiones fijadas de REVERSE-PC y mundo-X usadas en C02:

    bash deps/reverse-pc/scripts/build-xi-session.sh deps/mundo-x deps/reverse-pc/build
    python3 -m unittest integration.cache_u03_c03.test_cache -v
    python3 -m integration.cache_u03_c03.conformance
    python3 -m integration.cache_u03_c03.benchmark --samples 2 --out build/c03/benchmark.json

Ruta opt-in:

    from integration.cache_u03_c03.session import CachedSession
    with CachedSession("build/c03/sandbox.sqlite") as q:
        response = q.turn("mision-1", "guarda la regla Faro Azul con valor 1 observa Nara con muestra 88113 y resuelve desde 3")
        print(q.last_cache_stats)

Usar exclusivamente bases temporales hasta validar completamente compatibilidad.
El workflow `.github/workflows/bbyq-u03-c03-cache.yml` repite además
todas las pruebas nativas C1/U02, rollback, migración U01, feedback, nuevas
observaciones, ablations y reinicios con Session original.

## Ventajas potenciales

- Evitar un ciclo de 1000 cúbits virtuales dividido en 250 grupos de cuatro
  cuando el resultado nativo idéntico ya existe dentro del turno.
- Reducir llamadas XI, tráfico de fuente e instrucciones repetidas.
- Mantener independientes las memorias de sesiones y detener reutilización
  después de cualquier actualización.
- Conservar íntegra la arquitectura propia XI/Ether y su checkpoint.

## Límites y contras

- **No es una caché entre solicitudes**: la reejecución entre turnos sigue
  existiendo por seguridad de estados, procedencia y aprendizaje.
- El resultado nativo de una lectura puede influir en estado interno:
  la igualdad estricta de snapshot completo es condición obligatoria antes
  de considerar habilitar una omisión.
- La estructura del recibo sigue siendo U02, pero para medir el trabajo real
  se requiere el contador de cache separado; no inferir dos EXEC de dos
  referencias en la traza.
- Una LRU evita consumo ilimitado, pero ocupa un mínimo de RAM por turno.
- Los benchmarks en GitHub/Linux no demuestran mejora en Android, FPS,
  batería ni ventaja cuántica.
- El diseño experimental opt-in no combina simultáneamente C01 pool ni
  C02 SQLite optimista: esa combinación necesita pruebas específicas
  de revisión, bloqueo y restauración antes de una integración.
- La exactitud que se demuestre corresponde solo a las operaciones
  y escenarios probados, no a estados cuánticos arbitrarios.

**C03 no modifica los pesos ni autoriza una nueva APK.**
