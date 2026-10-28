# E027-CtxCompose-2-dev

Candidato que reúne las dos extensiones nativas existentes:

- Archivo contextual E027: 512 segmentos de hasta 224 bytes, lectura por índice, búsqueda léxica y vaciado explícito.
- Composición E026: cuatro formas diseñadas de pregunta doble ES/EN, con respuestas atómicas del programa original.

El código se enlaza como **prefijo de contexto → adaptador de composición → programa E025 → continuación de composición**. Un comando `@ctx` termina en su propia limpieza; una entrada ordinaria usa el adaptador E026. Ambos comparten un único RVPC2, con regiones separadas: composición temporal en 8800000000000000000..+511 y contexto en 8900000000000000000 y sus bancos declarados por context-prefix.xi.

El agente E025 y su semilla se conservan. Los constructores no implementan aprendizaje ni respuestas: solo enlazan, compilan y empaquetan XI en el runtime original. La cápsula candidata tiene identidad propia y no está desplegada en Android.

## Reproducción

Usar el workflow configurado bbyq-e027.yml y sus dependencias fijadas. Después de construir el runtime:

```sh
python3 ai/releases/e027/regression.py /ruta/reverse_pc /ruta/evidencia/e027
node ai/releases/e027/test.mjs /ruta/reverse_pc /ruta/evidencia/e027 /ruta/evidencia/contexto
python3 ai/releases/e026/test.py /ruta/reverse_pc /ruta/evidencia/e027 /ruta/evidencia/composicion
node ai/releases/e027/interop.mjs /ruta/reverse_pc /ruta/evidencia/e027 /ruta/evidencia/coexistencia
```

Las pruebas comprueban las regresiones originales sobre el candidato combinado, el archivo de 200 registros con reinicios entre turnos, la composición exacta y la coexistencia de ambas capacidades. En coexistencia se archiva texto, se enseñan hechos y se responden preguntas dobles; después se recupera y se vacía el archivo sin perder los hechos ni la composición.

La capacidad nominal del archivo no equivale a la cantidad de bytes ejercitada por el examen. La búsqueda léxica explícita no es síntesis semántica automática de todo el historial. Las cuatro formas de composición están diseñadas; esta integración no enseña patrones nuevos.

Los resultados reales se registran en docs/autonomy junto a los IDs de ejecución y los hashes. La propuesta siguiente de aprendizaje debe partir de este código combinado y contrastarse con los cambios posteriores del repositorio.
