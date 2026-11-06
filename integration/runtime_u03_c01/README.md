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
5. En modo cached, la caché se destruye al cerrar la sesión. En modo pooled, un conjunto limitado de procesos XI queda residente dentro del alcance de la prueba y cada uso posterior ejecuta RESTORE desde el RVPC2 autenticado, antes de procesar instrucciones. Al salir del alcance se cierran todos los trabajadores.

Compatibilidad: EXEC, SAVE y METRICS están disponibles; CODELIB y EXECREF
son comandos adicionales del binario experimental. Un identificador inválido
se rechaza sin ejecutar el programa. Límites: 128 bibliotecas por proceso,
16 MiB agregados y 16 MiB de fuente reconstruida.

**Importante:** NO se cachean resultados, pesos ni estados cuánticos.
El intérprete original vuelve a analizar la fuente reconstruida. El modo
pooled sí evita volver a lanzar procesos ya existentes entre turnos, pero
RESTORE sigue leyendo y comprobando el snapshot completo. No elimina
los snapshots completos ni garantiza aceleración de CPU.
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
    python3 -m integration.runtime_u03_c01.benchmark --samples 3 --out build/c01/comparison.json

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

Definiciones: wall_ratio_baseline_over_cached mayor que 1 significa
menos tiempo con C01; menor que 1 significa regresión. La reducción de
payload del protocolo no es RAM liberada ni ancho de banda de Internet.

## Trabajo pendiente tras este subpaso

- Evitar el análisis repetido de programas XI (necesita soporte nativo de
  instrucciones ya analizadas y comprobación de integridad).
- Mantener sesiones XI entre turnos, con confirmación/rollback de versiones.
- Optimizar snapshots y escrituras largas: planificado para C02.
- Validar consumo real en Android físico: C16.

**Ruta reversible:** el contexto activate() cambia temporalmente la clase
XiSession; al salir, restaura todas sus referencias originales y cierra
los procesos en reposo. El pool tiene un máximo de seis procesos ociosos;
puede retener más RAM durante un experimento y NO está habilitado en el
producto. Cada proceso reutilizado acepta exclusivamente un estado RVPC2
verificado, y un RESTORE fallido destruye el proceso en lugar de continuar
con estado anterior.
