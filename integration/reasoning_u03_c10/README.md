# BBY Q U03 C10 — Razonamiento y planificación con prueba XI trazable (sin APK)

**Base exacta:** PR #95 C09, commit f6ea64ed301db2ef37eafea71767ba0dbd0ee579.  
**Autoridad:** BBY Q → w4U → QdU; una sola memoria SQLite U02 y los siete bancos nativos originales.

## Qué hace realmente C10

Se creó una ruta experimental **opt-in** de razonamiento que depende de la auditoría C09. No se reemplaza el razonador original, no se añade un planificador autónomo que decida por el usuario y no se compilan APK.

El proyecto U02 ya tenía dos operaciones útiles de XI que C10 reutiliza:

- **Prueba simbólica:** el programa original C1/Zero puede derivar que «observación Nara es alerta» a partir de un hecho VQC actual y una regla XI realmente registrada. Su salida contiene IDs de prueba nativos.
- **Misión completa:** U02 utiliza QMemory + clasificación VQC + coordinación de Entity/E02 + política QRL + voz QChat. C10 puede consultar su **plan simulado**, no ejecuta ninguna acción física ni altera decisiones de usuario.

## Grafo acotado de dependencias

El plan se construye con IDs y dependencias explícitas, con orden topológico verificable y rechazo de ciclos o pasos desconocidos. Exige:

1. Auditar C09 sobre la revisión de SQLite U02 y comprobar que la memoria C1 está sincronizada.
2. Identificar una observación VQC realmente registrada y su proyección actual. Si la muestra o la versión de percepción cambió, devolver **proyección obsoleta** sin ejecutar nada.
3. Para una misión, exigir asociación QMemory con supervisión explícita. Un dato externo sin autenticar no puede suplirla.
4. Identificar desacuerdos entre valores originales y overlays externos con contenido SHA-256 válido. Un hash de contenido **no prueba autenticidad** del emisor; los conflictos se bloquean.
5. Tomar una copia coherente de SQLite (WAL) y **volver a verificar el hash de la vista C09 en la copia antes de arrancar XI**.
6. Ejecutar el **turno original U02/XI** solo dentro de esa copia desechable, con un ID de solicitud aislado. La prueba simbólica debe existir en la salida nativa; el plan de misión debe incluir todas las operaciones originales necesarias y mantenerse «supported».
7. Auditar de nuevo la base U02 fuente. Si cambió entre el inicio y la entrega, **no publicar la conclusión**; devolver un bloqueo por revisión concurrente.
8. Devolver únicamente IDs de prueba, procedencia del snapshot y, en una misión simulada, la acción sugerida por el **motor nativo original**.

El protocolo **nunca** ejecuta una ruta que modifique la base original: las escrituras nativas de la prueba se publican solo en el archivo SQLite temporal, que se descarta inmediatamente.

## Uso

```python
from integration.reasoning_u03_c10.session import ReasoningSession

with ReasoningSession("build/c10/ejemplo.sqlite") as bb:
    # La observación, la asociación y la regla XI deben existir previamente,
    # creadas mediante los contratos normales de BBY Q.
    report = bb.prove_alert("Nara")
    simulated = bb.plan_mission("Nara", "Faro Azul", position=3)
    print(report["status"], simulated["status"])
```

La interfaz expone solo dos metas tipadas: `prove_alert` y `plan_mission`. No intenta entender comandos abiertos ni planificar acciones no autorizadas.

## Pruebas y reproducción

```bash
bash deps/reverse-pc/scripts/build-xi-session.sh deps/mundo-x deps/reverse-pc/build
python3 -m unittest integration.reasoning_u03_c10.test_planner -v
python3 -m integration.reasoning_u03_c10.conformance
python3 -m integration.reasoning_u03_c10.benchmark --samples 2
python3 -m integration.reasoning_u03_c10.verify_panel
```

La CI compara U02 y C10 en tareas XI reales con el mismo checkpoint de partida. Verifica falta de observación, regla supervisada ausente, conflicto, prueba inexistente, proyección caducada, revalidación nativa después del aprendizaje, idempotencia, rollback, reinicio y SHA de 159 fuentes protegidas. Solo después de CI aprobada se documentan tiempos de auditoría.

## Restricciones y criterios de salida

- Esto agrega **trazabilidad y orden de dependencias** al motor de XI **ya existente**, no un nuevo modelo entrenado de razonamiento general.
- El usuario no recibirá una conclusión como verdad del mundo real: una proyección VQC es **salida del simulador** y la prueba C1/Zero es lógica dentro de la base de hechos disponible.
- El sistema no puede ejecutar órdenes abiertas, conectarse a redes externas, autenticar identidades o activar agentes de w4U/QdU sin permisos. No se altera su cadena de autoridad.
- El cálculo sandbox vuelve a ejecutar XI, con costo extra de hashes, copia de SQLite, reinicio de modelo y verificación. **No es una optimización de latencia**.
- Las pruebas no prueban ventaja cuántica, generalización ilimitada ni capacidad de una IA general.
- Ningún cambio a C06/C07/C08, sus checkpoints o el formato binario propio. C08 sigue sin nueva ganancia de pesos demostrada.
- **Sin APK ni fusión automática a main.**

[Panel completo de secuencias C00–C17](../../docs/BBY_Q_U03_PANEL.md) · [Estado](../../docs/BBY_Q_U03_ESTADO.json) · [Siguiente ciclo](../../docs/BBY_Q_U03_SIGUIENTE.md).
