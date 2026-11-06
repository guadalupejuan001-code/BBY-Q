# BBY Q U03 / C01 — Transporte XI con biblioteca residente (experimental)

**Objetivo:** eliminar el reenvío de bibliotecas XI idénticas en cada
petición EXEC, conservando exactamente la máquina XI, los modelos,
checkpoints, RNG, validaciones y transacciones. **Sin APK.**

## Arquitectura

Anterior: cada ejecución transmite cabecera del programa, HALT y biblioteca
completa XI. El proceso xi_session interpreta cada fuente recibida.

C01, opt-in:

1. Compilar xi_cached_session.cpp como binario adicional xi_session_c01, a
   partir de la misma implementación de REVERSE-PC fijada en C00.
2. CachedXiSession transmite una biblioteca por CODELIB solo una vez por
   proceso. El servicio devuelve un identificador secuencial.
3. EXECREF transmite el identificador y el programa variable que termina en
   HALT. El servidor reconstruye los mismos bytes del programa original.
4. Se llama al original Runtime::execute, sin sustituir representación,
   circuito, métricas de entrenamiento o control de errores.
5. En modo cached, la caché se destruye al cerrar el proceso. En modo pooled, hasta seis procesos XI permanecen residentes dentro de la prueba. Solo se reutiliza un estado sin RESTORE cuando el SHA-256 de la imagen RVPC2 coincide exactamente con el último SAVE de ese proceso y no ocurrió ningún EXEC posterior; en cualquier otro caso, RESTORE autentica y reemplaza el estado. Al terminar la prueba se cierran todos los trabajadores.

Compatibilidad: EXEC, SAVE y METRICS están disponibles; CODELIB y EXECREF
son comandos adicionales del binario experimental. Un identificador inválido
se rechaza sin ejecutar el programa. Límites: 128 bibliotecas por proceso,
16 MiB agregados y 16 MiB de fuente reconstruida.

**Importante:** NO se cachean predicciones ni gradientes, y NO se modifican pesos.
El modo pooled conserva el último estado cuántico completo en memoria, pero
solo lo reutiliza tras comparar su snapshot guardado SHA-256 y certificar
que no hubo nueva ejecución desde ese SAVE. Un estado distinto o sucio
se restaura con el cargador original RVPC2. El intérprete XI todavía analiza
la fuente reconstruida y sigue habiendo snapshots completos.
El programa antiguo sigue siendo la ruta por defecto.

## Reproducción

Con REVERSE-PC 08c363e6c6855c14026c86046af7183a45f45a98,
mundo-X e2778d962af22f6f1a0794058dd4685fc2573966,
Linux y Python 3.12, usar el workflow bbyq-u03-c01-runtime.yml. Comandos:

    bash deps/reverse-pc/scripts/build-xi-session.sh deps/mundo-x deps/reverse-pc/build
    g++ -std=c++17 -O2 -pthread -DREVERSE_PC_HAVE_BOUNDED_PRODUCT_IMPORT=1 \
      -Ideps/reverse-pc/build/ether-compat -Ideps/mundo-x/native/include \
      -Ideps/reverse-pc/src integration/runtime_u03_c01/xi_cached_session.cpp \
      -o deps/reverse-pc/build/xi_session_c01
    python3 -m unittest integration.runtime_u03_c01.test_client -v
    python3 -m integration.runtime_u03_c01.conformance
    python3 -m integration.runtime_u03_c01.verify_native
    python3 -m integration.runtime_u03_c01.benchmark --samples 3 --out build/c01/comparison.json
    python3 -m integration.runtime_u03_c01.warm --samples 2 --out build/c01/warm.json

El workflow verifica también C1/U02, readout, gradientes, rollback,
migración y congelamiento de modelos. Toda prueba utiliza una base SQLite
temporal con entrada sintética. No se ejecuta Gradle ni Android.

## Criterios

- Resultados nativos, trazas y hashes de checkpoints idénticos salvo métricas
  de duración del generador.
- Reproducción exacta, replay, recuperación de memoria y rollback.
- 159 archivos protegidos, fuentes y modelos SHA-256 idénticos antes/después.
- A/B de seis escenarios con muestras intercaladas y mismas instrucciones.
- No fingir aceleración si solo baja el tráfico del protocolo.
- Sin APK y sin entrenamiento fuera del feedback sintético aislado.

Definiciones: wall_ratio_baseline_over_variant mayor que 1 significa
menos tiempo de pared para la variante; menor que 1 significa regresión.
La reducción de payload de protocolo no es RAM liberada ni velocidad de red.

## Trabajo pendiente tras este subpaso

- Evitar el análisis repetido de programas XI (necesita soporte nativo de
  instrucciones ya analizadas y comprobación de integridad).
- Habilitar sesiones residentes fuera de laboratorio solo después de medir
  memoria retenida, concurrencia, presupuesto energético y reversión real en Android.
- Optimizar snapshots y escrituras largas: planificado para C02.
- Validar consumo real en Android físico: C16.

**Ruta reversible:** el contexto activate() cambia temporalmente la clase
XiSession; al salir, restaura todas sus referencias originales y cierra
los procesos en reposo. El pool tiene un máximo de seis procesos ociosos;
puede retener más RAM durante un experimento y NO está habilitado en el
producto. Cada proceso reutilizado acepta exclusivamente un estado RVPC2
verificado, y un RESTORE fallido destruye el proceso en lugar de continuar
con estado anterior.


## Resultados reproducibles de C01 (6 de noviembre de 2026)

[Workflow final aprobado](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42277894399) · [Artefactos JSON completos](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42277894399/artifacts/13534985897)

Medianas en milisegundos, tres repeticiones por escenario. Versiones del
modelo, parámetros y entradas idénticos; CPU de runner Linux, no Galaxy A16.

| Escenario | XI original | Solo CODELIB/EXECREF | Pool + SHA-256 | Cambio pool frente a original |
| --- | ---: | ---: | ---: | ---: |
| Inicialización | 587,8 | 588,4 | 579,5 | -1,4 % |
| Aritmética | 1.719,8 | 1.858,6 | 1.653,7 | -3,8 % |
| Texto | 1.959,0 | 2.040,4 | 1.913,1 | -2,3 % |
| Misión | 2.468,7 | 2.571,3 | 2.457,4 | -0,5 % |
| Feedback verificado | 3.748,9 | 3.826,3 | 3.464,4 | -7,6 % |
| Replay exacto | 8,46 | 8,06 | 8,08 | -4,5 % (ruido dominante) |

**El transporte cacheado por sí solo empeoró la latencia** en la mayoría
de los escenarios aunque redujo entre 78,6 % y 89,4 % los bytes de biblioteca
XI transmitidos. No se aceptó como aceleración; sigue siendo una ruta
experimental que sirve de base para la reutilización segura de procesos.

### Uso continuado: cinco turnos después de una misión inicial

Dos muestras de una secuencia con tres lecturas, un feedback y una lectura
posterior, excluyendo el tiempo de preparación inicial:

- XI original: mediana **9.821 ms**.
- Pool con restauración selectiva: mediana **8.764 ms**.
- Reducción de tiempo de pared: **10,8 %**, equivalente a **1,121x**
  de relación original/optimizado.
- Durante el tramo medido, el pool reutilizó **17 estados exactos SHA-256**,
  realizó **13 restauraciones completas** y arrancó **un proceso XI nuevo**.
- El transporte del tramo bajó de aproximadamente 10,4 MB de programa lógico
  a 0,525 MB de payload real, sin alterar el resultado.
- Los hashes de todos los bancos al final de la secuencia fueron iguales
  entre ambas variantes.

### Evidencia y limitaciones

- Se verificaron los resultados de aritmética, texto, misión, memoria,
  replay, feedback, recuperación y fallo inyectado, comparados con U02
  (solo se excluyó la duración variable de generación al comparar respuestas).
- Se conservaron **159 archivos protegidos** sin cambios de SHA-256.
- El test nativo rechazó un estado RVPC2 corrupto, conservó el estado previo
  tras el rechazo y restauró el checkpoint válido byte a byte.
- Ninguna APK fue compilada ni instalada.
- Tres muestras por caso y dos de uso continuado NO permiten afirmar una
  ventaja estadísticamente generalizable. El rendimiento Android y la
  energía no se han medido.
- El pool puede retener hasta seis procesos XI entre turnos; la mejora de
  latencia **tiene un costo potencial en RAM residente**. No se activa
  globalmente ni se incorpora al teléfono sin verificar ese intercambio.

**Veredicto de C01:** funcionalmente aprobado y con una mejora exploratoria
en sesiones continuadas; conservar el runtime original como ruta de
producción, con C01 opt-in. La reducción de snapshots y del bloqueo SQLite
pertenece al siguiente ciclo C02.
