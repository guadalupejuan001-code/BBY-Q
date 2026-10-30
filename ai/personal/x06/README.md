# X06 — P11 y P12

Esta entrega añade planificación de tareas declaradas y una interfaz de texto v2
sobre X05. La interpretación, la validación UTF-8, el orden de tareas y las
respuestas nuevas se ejecutan en XI. El motor C++ y la APK conservan sus versiones.
El adaptador Node transporta bytes, invoca el motor, comprueba integridad y publica
un archivo nuevo. Se probó con Node 24.22.1 y el motor indicado en `build.json`.

## P11: un plan que se puede corregir

El usuario declara el objetivo, los pasos y sus criterios. XI ordena hasta 16
tareas para una persona. Valida referencias, detecta ciclos, respeta dependencias
y elige entre las tareas disponibles por prioridad (1 primero) y luego por ID.
Calcula intervalos acumulados y avisa cuando el tiempo pendiente supera el
disponible. Un bloqueo deja fuera también a las tareas que dependen de él. No
supone que una tarea se haya completado porque haya transcurrido su duración.
El presupuesto expresa el tiempo disponible declarado. Confirmar una tarea
reduce el trabajo pendiente, pero no mide ni descuenta tiempo real transcurrido;
actualiza el presupuesto con `Cambia tiempo disponible a N min.` cuando cambie.

```text
Planifica: Preparar una entrega
Tiempo disponible: 80 min
Tarea 1: Preparar material | 15 min | depende de - | prioridad 4 | listo cuando material reunido
Tarea 2: Construir | 30 min | depende de 1 | prioridad 1 | listo cuando pieza construida
Tarea 3: Comprobar | 10 min | depende de 2 | prioridad 1 | listo cuando pruebas aprobadas
Tarea 4: Documentar | 10 min | depende de - | prioridad 2 | listo cuando documento revisado
```

El orden esperado es 4, 1, 2, 3; suma 65 minutos. La prioridad de la tarea 2 no
permite saltarse su dependencia. Las líneas aceptan LF o CRLF. Los encabezados
aceptan mayúsculas/minúsculas ASCII y las variantes latinas declaradas; las
etiquetas y los criterios conservan exactamente su escritura.

Correcciones admitidas, una por mensaje:

```text
Muestra el plan.
Replanifica.
¿Cuál es el siguiente paso?
Cambia tiempo disponible a 90 min.
Cambia duración de tarea 1 a 7 min.
Cambia prioridad de tarea 1 a 1.
Cambia dependencias de tarea 3 a 1,4.
Bloquea tarea 1.
Desbloquea tarea 1.
Completa tarea 1: material reunido
Reabre tarea 1.
Añade tarea 5: Empacar | 3 min | depende de 3 | prioridad 2 | listo cuando caja cerrada
Elimina tarea 5.
Cancela el plan.
```

Para completar una tarea se requiere el criterio exacto y que sus dependencias
estén completadas. Es una confirmación del usuario, no una comprobación del mundo
físico. Una edición inválida conserva íntegro el plan. No se puede borrar una
tarea todavía referenciada ni reabrir una tarea si una dependiente ya completada
quedaría incoherente. Consultar, repetir una confirmación o repetir la cancelación
es idempotente. Un plan nuevo válido reemplaza al anterior y aumenta su generación.

Límites: IDs 1–16; objetivo 160 bytes; etiqueta 96 bytes; criterio 160 bytes;
duración 1–10.000 minutos; presupuesto 1–160.000 minutos; prioridad 1–9.
`-` expresa ausencia de dependencias; varias se separan con comas. Los campos
intermedios usan el separador literal ` | `. Se permiten referencias a tareas que
aparecen después en la entrada.

Falta descomponer automáticamente objetivos libres, estimar tiempos, gestionar
varias personas, recursos, calendarios, fechas, incertidumbre o buscar un plan
óptimo con restricciones generales. No equivale a planificación general.

## P12: contrato de texto v2

Use `x06/run.mjs`, que acepta texto o `--file`. El límite es 16.384 bytes por
mensaje y 65.536 bytes de respuesta. La entrada debe ser UTF-8 canónico; se admiten
TAB, LF y CR y se rechazan los demás controles C0 y DEL. Se conservan BOM, CRLF,
acentos, emojis y secuencias Unicode combinadas. No hay normalización ni recorte.
Una cadena JavaScript con sustitutos Unicode sin pareja se rechaza antes de
codificarla; no se sustituye silenciosamente por U+FFFD.

Los mensajes largos/multilínea tienen dos consumidores nativos nuevos:

1. El planificador y sus ediciones.
2. `Repite exactamente:` o `Responde exactamente:`, seguido de LF o CRLF y el
   texto literal. Los comandos que aparezcan dentro de ese texto son datos.

Un mensaje de una línea y hasta 255 bytes puede pasar a los módulos anteriores.
Sus respuestas multilínea, por ejemplo `Escribe uno por línea: sol, luna, mar.`,
ahora llegan completas por esta interfaz. El transporte ampliado no amplía las
gramáticas de los módulos antiguos: un texto largo/multilínea sin consumidor
compatible devuelve `E_UNSUPPORTED_TEXT` y no se publica una sesión nueva.

El programa valida la entrada completa antes de interpretarla. El anfitrión
trabaja sobre una copia privada y publica el RVPC2 mediante un enlace exclusivo
solamente después de validar salida, terminar los roles y borrar los buffers
transitorios. La entrada original nunca se sobrescribe. Si el transporte falla,
devuelve `ok:false, committed:false, error:{code,message,phase}, output:null` y no
crea el archivo de salida. Un rechazo del contenido del plan es una respuesta
normal (`ok:true`) que conserva el plan y consume las autorizaciones antiguas
como cualquier mensaje nuevo aceptado.

Errores de entrada: `E_EMPTY`, `E_SIZE`, `E_UTF8`, `E_CONTROL`, `E_VERSION`,
`E_LANGUAGE`, `E_UNSUPPORTED_TEXT`, `E_UTF16`. También se distinguen errores de
integridad, esquema, destino, salida y ejecución nativa. Una salida mal formada,
vacía o demasiado grande impide publicar la sesión. No se sobrescribe un destino
existente. La recepción exacta de los bytes no implica comprensión libre del texto.

La cápsula conserva el perfil RXE2 legado de 255 bytes para compatibilidad. El
comando C++ `app-turn` conserva también sus restricciones antiguas: la interfaz
v2 usa el RXE de inferencia y su buzón nativo adicional. La APK todavía no invoca
este adaptador; integrar y probar esa ruta en Android es P13.

## Ejecutar y migrar

Desde la raíz de la entrega, con un `reverse_pc` compatible:

```bash
/ruta/reverse_pc app-init BBY-Q.rxe semilla.rvp
node BBY-Q/ai/personal/x06/run.mjs /ruta/reverse_pc . semilla.rvp plan.rvp --file ejemplos/plan.txt
node BBY-Q/ai/personal/x06/run.mjs /ruta/reverse_pc . plan.rvp plan-2.rvp 'Bloquea tarea 1.'
```

Para conservar una sesión anterior, migre a un archivo nuevo antes de usarla:

```bash
node BBY-Q/ai/personal/x06/migrate.mjs /ruta/reverse_pc . anterior.rvp migrada.rvp
```

La migración aplica las fases nativas que falten desde E038/X02/X03/X04/X05 y
rechaza colisiones de espacios de memoria. No vuelve a entrenar ni borra memoria
personal. Repetirla es idempotente. El preflight de solo lectura se optimizó con
comprobaciones de bytes desenrolladas, conservando las mismas direcciones y
rechazos, para caber en el presupuesto original de un millón de pasos incluso
desde E038. Los roles de programación y verificación X05 se reutilizan sin cambios.

El estado local, el motor y el manifiesto son parte de la base de confianza;
los hashes comprueban correspondencia de archivos, no son una firma remota ni
protegen un RVPC2 completamente manipulado por su propietario. Se verifica una
colisión de destino durante la publicación y un fallo de limpieza posterior:
la primera conserva el otro archivo y el segundo informa la limpieza pendiente
sin ocultar una sesión ya publicada. No se hicieron pruebas de estrés con varios
escritores simultáneos ni cortes de alimentación.
Las pruebas finales se ejecutan en serie. En pasadas concurrentes preliminares
aparecieron fallos intermitentes de los adaptadores heredados X05 y X03; en una
importación X03 se repitieron cuatro identificadores de fragmento y faltaron esos
avances en el estado. La causa no se aisló. No se declara validada la ejecución
concurrente de esos adaptadores.

## Verificación

`audit-six/cases-frozen.json` conserva las entradas y criterios establecidos
antes de implementar. `test.mjs` cubre planes, correcciones, errores y transporte.
`properties.mjs` contrasta planes reservados contra la enumeración independiente
de órdenes válidos; no importa el planificador. `edge.mjs` comprueba límites,
errores nativos, migración, colisiones, BOM y un ciclo real de programación XI.
Las evidencias y la lista actualizada de pendientes acompañan la entrega.
No se ejecutó una comparación directa contra ChatGPT o Claude.
