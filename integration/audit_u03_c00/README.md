# BBY Q U03 / C00 — Auditoría inmutable y perfilado nativo

**Estado:** ciclo de instrumentación. Esta entrega NO modifica modelos, etiquetas, gradientes, memoria personal, XI/Ether, runtime REVERSE-PC ni Android. **Sin APK.**

## Identidad y alcance

- Punto de partida: PR #85, commit ae3afcf52500954ce8849d9bf7c8f0286f5b172b.
- Dependencias fijadas por el workflow: REVERSE-PC 08c363e6c6855c14026c86046af7183a45f45a98 y mundo-X e2778d962af22f6f1a0794058dd4685fc2573966.
- Checkpoints y fuentes comprobados antes/después: integration/sequence1/experiment, integration/sequence2/release, integration/entity/release, integration/unified/release, ai/xi/qmemory y ai/xi/quantum3.
- Los verificadores nativos existentes comprueban identidad, checkpoint, readout, gradientes, rollback, migración y aprendizaje.
- La auditoría es independiente: cada escenario utiliza un proceso nuevo y base SQLite desechable; NO utiliza el historial o estado personal del usuario.

## Reproducción

En Linux con Python 3.12, Node 24 y las dependencias fijadas:

    bash deps/reverse-pc/scripts/build-xi-session.sh deps/mundo-x deps/reverse-pc/build
    python3 -m unittest integration.audit_u03_c00.test_profile -v
    mkdir -p build/sequence2 build/unified
    python3 integration/sequence2/verify_release.py
    python3 -m integration.unified.verify_release
    python3 -m integration.unified.verify_perception
    python3 -m integration.unified.verify
    python3 -m integration.unified.verify_upgrade
    python3 -m integration.audit_u03_c00.profile --samples 2 --out build/c00/profile.json

El [workflow C00](../../.github/workflows/bbyq-u03-c00-audit.yml) publica build/c00/profile.json como artefacto descargable durante 30 días. No ejecuta Gradle ni instala Android.

## Escenarios medidos

| Escenario | Qué se mide | Verificación |
| --- | --- | --- |
| initialization | Apertura de BBY Q y snapshot inicial | Sesión válida |
| arithmetic | Petición de cálculo 7 + 3 | Resultado admitido |
| text | Pregunta cotidiana sobre memoria | Registra respuesta o rechazo; NO se cuenta automáticamente como respuesta correcta |
| mission | C1, QMemory, VQC3, QRL3, E02, QChat | Misión y voz fiel |
| feedback | Aprendizaje verificado tras misión sintética | Feedback admitido |
| replay | Repetición exacta de ID existente | Recibo idéntico y estado intacto |

Se almacenan duración de pared, CPU Python, contadores de EXEC y SAVE,
bytes de fuente XI reenviados, llamadas invocadas desde el preludio y su duración
de paquete. En Linux también se observan CPU de procesos XI, VmHWM y E/S
del kernel, cuando están disponibles. p95 utiliza rango cercano: **con solo
dos repeticiones coincide con el máximo y no establece percentiles estables**.

Una llamada XI puede envolver varias subrutinas: los tiempos reportados por
subrutina se superponen y **no son tiempos exclusivos que puedan sumarse**.
El registro VmHWM y la E/S observada no incluyen necesariamente toda la
vida del proceso. Son mediciones del runner Linux, NO del Galaxy A16.

## Criterios de aceptación

1. Verificadores nativos C1 y U02 aprobados, sin modificar sus parámetros.
2. Todos los hashes de checkpoints/fuentes antes y después idénticos.
3. Pruebas de instrumentación y contrato correctas.
4. Seis escenarios observados; excepciones técnicas hacen fallar la auditoría.
5. Cero APK nuevas en las carpetas de compilación.
6. Informe completo con entorno, unidades, método y limitaciones.

La campaña de 200 misiones y 1024 observaciones permanece en las evidencias
originales; las seis pruebas de rendimiento no la sustituyen.

## Cuellos de botella candidatos

- integration/unified/session.py mantiene una transacción SQLite BEGIN IMMEDIATE durante gran parte del turno. Concurrencia de escritores potencialmente limitada.
- Cada turno crea archivos temporales, materializa bancos y abre procesos XiSession.
- integration/sequence2/engine.py agrega el texto de la biblioteca XI a cada EXEC; se sospecha costo repetido de análisis y transporte.
- Una traza de misión U02 incluye dos vqc_forward; se requiere medir y comprobar la reutilización antes de eliminar el segundo.
- VQC3/QRL3 emplean 1000 cúbits simulados cada uno, en 250 bloques de cuatro. No equiparar esto con un circuito genérico arbitrario.

Estas son **hipótesis basadas en código**, no mediciones de aceleración.
C01 deberá comparar en las mismas condiciones, manteniendo identidad de
modelo, corrección, tolerancia a fallos y resultados verificables.
