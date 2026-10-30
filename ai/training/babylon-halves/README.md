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

El script rehúsa sobrescribir resultados. Los exámenes se realizan en copias; las ocho preguntas abiertas se registran aparte y no se aprueban por recuperar definiciones. Los resultados solo existen al terminar efectivamente la campaña.

## Consulta nativa

`@libro pagina 62` reconstruye el texto de esa página desde el archivo contextual; no desde una respuesta alojada en JavaScript. Las preguntas compatibles, como `que es babilonia demanda de metales`, consultan las síntesis españolas.

## Cambios de implementación

Capacidad de registros: 512 → 4.096. Se preservan 224 bytes por registro y 255 bytes por entrada. Se amplían los identificadores y el marcador de ausencia, y se mueve la tabla temporal de búsqueda para que no invada metadatos. Los lotes se subdividen al alcanzar límites de instrucciones o salida del host; no se contabiliza un intento fallido como aprobado.

No se instala una APK ni se reemplaza el agente más reciente de REVERSE. No se habilitan cuentas, pagos, transferencias ni trading. Las capacidades de razonamiento abierto y el uso en Android deben medirse por separado.
