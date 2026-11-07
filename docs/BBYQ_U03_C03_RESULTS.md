# BBY Q U03 C03 — Resultados definitivos del ciclo de cachés

**Fecha de ejecución:** 7 de noviembre de 2026 UTC (noche del 6 de noviembre en horario del este de EE. UU.).

**Implementación:** [PR #89](https://github.com/guadalupejuan001-code/BBY-Q/pull/89), basada en C02.

**CI final aprobada:** [GitHub Actions #42333857064](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42333857064).

**Artefacto íntegro:** [BBYQ-U03-C03-native-cache-evidence](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42333857064/artifacts/13558796021), con archivos de benchmark, conformance, diagnóstico y verificaciones U02.

## 1. Experimento VQC rechazado: la respuesta NO basta

Se intentó omitir la segunda ejecución de `vqc_forward` de una misión compuesta, reutilizando la probabilidad del primer circuito. En el mismo input y modelo, la respuesta fue igual, pero **la imagen persistente V3 cambió 32.155 bytes** (mismo tamaño 2.718.928 bytes, primera diferencia en offset 21).

**Decisión:** rechazar la optimización. Ni los 1.000 cúbits simulados de VQC3 ni la memoria cuántica se omiten en la versión aceptada. La igualdad de respuestas no autoriza a descartar efectos internos que cambian un checkpoint.

Evidencia del fallo: [CI inicial](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42332642104) y [diagnóstico de diferencias binarias](https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/42333102169).

## 2. Alternativa aceptada: imágenes autenticadas de modelos congelados

Se implementó una caché por contexto Python para cuatro modelos/archivos de bancos existentes, verificados por SHA-256. Después de la autenticación inicial, se pueden reutilizar sus imágenes descomprimidas **si el hash de todos sus archivos de entrada y dependencias sigue siendo idéntico**.

- 4 fallos de caché durante el primer acceso; **4 aciertos** en la siguiente apertura.
- 33.297.613 bytes de imágenes nativas congeladas reutilizadas (aprox. 31,8 MiB).
- 8.045.944 bytes de archivos comprimidos, manifiestos y fuentes vuelven a comprobarse en cada apertura; la caché **no** suprime ese control de integridad.
- Las cuatro entradas consumieron **33.297.613 bytes de RAM retenida** durante el experimento. La caché de laboratorio admite hasta 96 MiB y 12 entradas; se destruye al cerrar el contexto.
- 0 ejecuciones XI omitidas: VQC3, QRL3, QMemory, QChat100 y los entrenamientos mantienen su ejecución nativa original.

## 3. Comparación A/B: medianas de dos muestras

Runner Linux de GitHub: Intel Xeon Platinum 8573C, cuatro CPU lógicas, Python 3.12.16. Cada observación utiliza una base de datos sintética y un proceso separado.

| Escenario | U02 sin caché | C03 caché modelos | Relación de latencia U02/C03 | EXEC XI original/C03 |
| --- | ---: | ---: | ---: | ---: |
| Reabrir sesión | 134,281 ms | 49,705 ms | **2,70×** | 0 / 0 |
| Aritmética | 1.638,159 ms | 1.513,953 ms | 1,082× | 30 / 30 |
| Misión cooperativa | 2.227,963 ms | 2.188,909 ms | 1,018× | 48 / 48 |
| Feedback verificado | 3.380,235 ms | 3.268,104 ms | 1,034× | 113 / 113 |

La mayor mejora medida corresponde a la apertura repetida de sesiones. La latencia de inferencia propiamente dicha **no se ha reducido por menos operaciones cuánticas**. Diferencias pequeñas entre ejecuciones pueden reflejar ruido del runner; dos muestras no dan una distribución estadística confiable.

## 4. Integridad real y compatibilidad

- Conformance completa U02 y C03: respuestas, recibos, historia, estados de bancos y hashes SHA-256 **idénticos**.
- La sesión original U02 puede reabrir los estados generados por C03.
- El diagnóstico nativo final informa `snapshot_equal: true`, sin ningún banco diferente.
- Las pruebas nativas históricas C1/U02 (readout, gradientes, rollback, migración U01 y memoria) continúan aprobando.
- 159 archivos congelados protegidos permanecen sin cambios.
- Ninguna APK se compiló; ninguna variante experimental está activa en Android ni en `main`.

## 5. Beneficios, costos y restricciones

**Beneficio:** evitar descompresión repetida de archivos de modelos inmutables en procesos Python persistentes sin sacrificar ningún efecto de XI/Ether.

**Costo:** conservar imágenes descomprimidas en RAM y verificar el contenido SHA-256 en cada reutilización, con E/S y CPU adicionales. En Android la disponibilidad de memoria, latencia y batería podrían cambiar la conveniencia.

**No demostrado:** ventaja cuántica, mejora de FPS, ahorro energético, aceleración general de BBY Q ni equivalencia para omitir programas XI arbitrarios.

**Decisión de arquitectura:** conservar C03 como opción reversible. No reintroducir una caché VQC por resultados hasta existir una distinción formal y probada entre estado cuántico temporal y estado persistente del simulador. El ciclo C04 podrá aprovechar estas mediciones para planificación selectiva de tareas, pero deberá demostrar equivalencia por separado.

**Sin APK, sin cambios de modelos, sin fusión automática de las PR C00–C03.**
