# F004 — Libro en dos etapas nativas

A: páginas 1–61. B: páginas 62–122. B comienza únicamente después de las pruebas y el checkpoint de A.

Se incorpora el texto extraído completo en inglés: 1.171 fragmentos con página y orden. Se agregan, por separado, 64 síntesis educativas en español (dos hechos por concepto, 32 conceptos por mitad). El texto se normaliza en espacios y controles C0; no se enseña el contenido de imágenes. Ingestión completa de texto NO significa comprensión completa ni ajuste de pesos neuronales.

La memoria y las respuestas se ejecutan en XI/Ether. Node emite programas XI, entrega entradas ABI y examina salidas; no genera respuestas. El host original se conserva y se verifica por SHA-256.

## Reproducción

Se requiere el paquete F004 con `base-f003`, `libro` y `runtime-linux`, o la preparación de `.github/workflows/bbyq-babylon-halves.yml`.

```sh
node ai/training/babylon-halves/train.mjs /ruta/paquete /ruta/nueva/campana
node ai/training/babylon-halves/boundary-tests.mjs /ruta/paquete /ruta/nueva/campana /ruta/nueva/limites
```

El modo normal rehúsa sobrescribir resultados. Hay modos explícitos `--resume-a` y `--resume-b` que verifican la fuente XI, los estados y las transcripciones conservadas; no convierten intentos fallidos en campañas aprobadas. Los exámenes se realizan en copias. Las ocho preguntas abiertas se registran aparte y no se aprueban por recuperar definiciones.

## Entrega del estado entrenado

La cápsula A incluye su estado entrenado. El estado completo B supera, junto con el código, el límite de 8 MiB del empaquetador original. B se distribuye como motor nativo `BBY-Q-F004-B.rxe` más estado entrenado `checkpoint-B.rvp.gz`. No se recorta texto ni se modifica el host.

IMPORTANTE: ejecutar solo `app-init` sobre la cápsula B recupera la semilla F003 de 448 hechos. Para usar el libro completo hay que descomprimir y restaurar el checkpoint B adjunto. El módulo verifica esa restauración por hash y prueba la recuperación de las 122 páginas. La entrega descargable incluye un lanzador que restaura el checkpoint automáticamente en un estado separado.

## Consulta nativa

`@libro pagina 62` reconstruye el texto de esa página desde el archivo contextual; no desde una respuesta alojada en JavaScript. Las preguntas compatibles, como `que es babilonia demanda de metales`, consultan las síntesis españolas.

## Cambios y límites

Capacidad de registros: 512 → 4.096. Se preservan 224 bytes por registro y 255 bytes por entrada. Se amplían identificadores y marcador de ausencia, y se mueve la tabla temporal de búsqueda para que no invada metadatos. Los lotes se subdividen al alcanzar límites de instrucciones o salida del host; no se contabiliza un intento fallido como aprobado.

La búsqueda general `@ctx find` en el archivo completo alcanza el presupuesto de instrucciones en los casos probados. Se registra como limitación separada; no se confunde con la consulta nativa por página ni con los controles aprobados de metadatos en una copia sintética.

No se instala una APK ni se reemplaza el agente más reciente de REVERSE. No se habilitan cuentas, pagos, transferencias ni trading. Las capacidades de razonamiento abierto y el uso en Android deben medirse por separado.
