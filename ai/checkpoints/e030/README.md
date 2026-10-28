# Checkpoint E030 preservado sin hechos de examen

`preserved-patterns.rvp.gz.b64` contiene la semilla E025 auténtica más
los dos patrones ya aprendidos por XI en el ciclo del PR #35. Se extrajeron
del checkpoint nativo original, sin invocar learn.xi ni reconstruir ejemplos.

SHA256 del RVPC2 decodificado: `18030f0c4e7098a0d19d07c3b3a93507d982caa1ae70e047bd9c2d118e9a3d4b`.
Semilla: `ce058a65092dd9892b6fd55276a17287b764a16bc526ccbfa0085154baef9631`.
Cápsula compatible: `c9a33a322f58ac6d93f18ff3c59678ef637ac9612bb71845e122e8f5c9de43f9`.
Fuente original: `5a0d469fc70248a2afc7a6a319a9a854d6498fa7682d9351e543f0d701ae7cf6`.
Los dos checkpoints permanecen separados; este archivo no sobrescribe memorias privadas.

`patterns.json` conserva 3072 bytes exactos. La dirección base es una cadena
decimal para evitar pérdida de precisión en JavaScript/JSON.
El rango es [9200000000000000000, 9200000000000003072), extremo excluido.
Se detectó que las notas anteriores habían redondeado ese extremo al serializarlo
como Number; no usar ese número antiguo para restaurar direcciones.

El runner verificó lectura XI de cada byte restaurado, núcleo/bindings y memoria
fuera de la región iguales a la semilla. El archivo contextual está vacío:
ninguno de los 24 sujetos sintéticos de examen anteriores se publica aquí.
Es conservación y restauración, no aprendizaje nuevo.

## Restaurar
Desde la raíz del repositorio:
```sh
python3 -c "import base64,gzip,pathlib; p=pathlib.Path('ai/checkpoints/e030/preserved-patterns.rvp.gz.b64'); pathlib.Path('e030-preserved.rvp').write_bytes(gzip.decompress(base64.b64decode(p.read_text())))"
sha256sum e030-preserved.rvp
```
Compilar la cápsula E030 desde PR #35/código 0061bcda177fc31f609939860ed9d0a75e222d50
con el runner y runtime fijados, comprobar el hash compatible y abrir ese RVPC2.
Python solo decodifica el contenedor, no interpreta lenguaje o aprende.

## Evidencia
https://github.com/guadalupejuan001-code/BBY-Q/actions/runs/40788612882
157 controles: sin patrones 0/48, con patrones restaurados 48/48 en 24 sujetos
nuevos, reinicio por turno. W4u produjo la acción tipada [4,2] desde la cápsula
restaurada; las regresiones originales E025 31 y W4u 21 también pasaron.
El conocimiento factual del examen se ingresó después de guardar el checkpoint
limpio; no está en este archivo.

PR #36 conserva un workflow de comprobación específico de persistencia,
sobre el workflow/runner E029 existente. Antes de fusionarlo como CI general,
reconciliar sus pasos con la batería completa del PR #35. No se hizo despliegue Android.
