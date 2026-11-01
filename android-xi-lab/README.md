# BBY Q C13 — Android XI Lab

Este es un **laboratorio Android autónomo y funcional**, no una conversión engañosa de X10. Usa el intérprete XI/REVERSE-PC original a través de JNI Android para ejecutar los motores experimentales VQC2, QRL2 y política C12. No utiliza frameworks de aprendizaje automático externos.

## Funciones de la edición 0.1

- El usuario envía `quantum estado`, `quantum entrena xor`, `quantum entrena xnor`, `quantum evalua`, `quantum clasifica 0 1`, `quantum entrena agente` o `quantum planea 1 0`. El programa XI `conversation-route.xi` decide qué acción y argumentos se aceptan.
- Ejecuta realmente entrenadores e inferencias XI sobre REVERSE-PC en Android (no botones ni datos ficticios), con una memoria RVPC2 privada dentro del sandbox de la APK.
- La política C12 consulta el clasificador de intención P01 XI y ejecuta `policy-decide.xi` con un contexto sin historial P05 (`2*intent+0`). Es observación exclusivamente; solo `policy-update.xi` aprende de la recompensa explícita 0–100 que el usuario suministra.
- Las consultas no guardan el estado temporal. Los entrenamientos se publican mediante `android.util.AtomicFile` después de que el motor XI finalice correctamente. Los estados X10 originales permanecen fuera de esta aplicación.
- El código Android y Java únicamente transporta bytes, muestra resultados y solicita acciones. La selección de puertas, tablas Q, reglas lingüísticas, decisiones y recompensas se procesan mediante los programas XI del repositorio.

## Límites

**La aplicación no incluye el motor conversacional completo X10**, su biblioteca SQLite con el entrenamiento histórico del usuario, la memoria P05 de largo plazo, ni un runtime Node 24 en Android. No afirma haber importado ninguna de esas piezas, ni demostrar ventaja cuántica. El VQC y el agente secuencial son experimentos sintéticos con dos cúbits.

## Compilación reproducible

Desde la raíz de BBY-Q, con JDK 17, Node 24, Gradle 8.9 y Android SDK 35 + NDK 27:

```sh
git clone https://github.com/guadalupejuan001-code/REVERSE-PC.git deps/reverse-pc
git -C deps/reverse-pc checkout a1b935ae0adf38615996bac92727e95289ad7cc1
git clone https://github.com/guadalupejuan001-code/mundo-X.git deps/mundo-x
git -C deps/mundo-x checkout e2778d962af22f6f1a0794058dd4685fc2573966
python3 deps/reverse-pc/scripts/prepare-ether-compat.py deps/mundo-x build/ether-compat
node android-xi-lab/scripts/prepare-assets.mjs
node android-xi-lab/scripts/verify-contract.mjs
gradle -p android-xi-lab :app:assembleDebug
```

APK: `android-xi-lab/app/build/outputs/apk/debug/app-debug.apk`. GitHub Actions publica el APK y el informe de hashes una vez que la compilación finaliza correctamente. La firma debug es **de desarrollo**, no una identidad estable de actualización de una instalación previa.

**Siguiente fase para el verdadero C13 completo:** incorporar X10, su SQLite/recibos, 480 lecciones X09 y sus capacidades lingüísticas conservadas en Android. Esta tarea necesita portabilidad nativa probada y los binarios originales íntegros.
