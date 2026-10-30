# F004 — segunda mitad de Babilonia

Continuación del candidato exacto F003 de la PR #47. No se crea otra IA ni se sustituye el agente posterior de REVERSE.

## Alcance y procedencia

Se trabajaron las páginas 62–122 del PDF inglés de 122 páginas. `second-half.mjs` contiene 128 lecciones originales en español: 24 sobre las cinco leyes, 24 sobre el prestamista, 8 sobre las murallas, 16 sobre el comerciante de camellos, 24 sobre las tablillas y 32 sobre el hombre más afortunado. Cada lección incorpora una definición atribuida al relato y una tarea pedagógica de lectura. Son 256 hechos nuevos; acumulado esperado: 704 hechos / 352 conceptos.

F003 anterior era una selección de TODO el libro, no una cobertura exhaustiva de la primera mitad. El mapa de referencias cubre las páginas del tramo, pero no demuestra aprendizaje de cada frase ni comprensión abierta. No se afirma que ahora esté aprendido el libro entero.

La incorporación es contextual persistente en XI/Ether, no ajuste de pesos. Node prepara y verifica; el ejecutor original calcula las respuestas. Las cautelas de lectura y las aplicaciones no son citas literales del autor. No se usan cuentas ni datos financieros personales.

## Cambios nativos

`patch-memory.mjs` transforma la fuente XI de F003. Amplía 512 a 4096 entradas y 114688 a 917504 bytes de archivo. Conserva 224 bytes por hecho, 255 por entrada y 48 por sujeto. Corrige el lector de valores mayores de 80 bytes. Relocaliza el área temporal de búsqueda para evitar que solape los metadatos ampliados y admite identificadores de cuatro dígitos. El host no cambia. La capacidad sigue siendo finita.

## Reproducción

Requiere Linux x86-64, Node 22 o compatible y el paquete F003 PR47 suministrado en esta conversación. El paquete F004 incluye los archivos mínimos de la base necesarios para reproducir sin descargarlos de otro sitio.

```sh
chmod +x /ruta/base-f003/runtime-linux/reverse_pc
node ai/training/babylon/train-second-half.mjs /ruta/base-f003 /ruta/nueva/resultados
```

El arnés comprueba las identidades de PDF, ejecutor, cápsula y estado de entrada antes de entrenar. No usar otro candidato F003 con el mismo nombre: la PR #46 tenía una cápsula distinta. Las consultas abiertas y contradicciones se prueban sobre estados desechables; no se incorporan a la semilla publicada.

Las pruebas de índices 511, 512, 999, 1000 y 4095 usan estados sintéticos dispersos, no un archivo lleno de 4096 hechos naturales. Los detalles de ejecución, el error inicial de cabecera de un archivo de prueba, su corrección y las limitaciones de la reproducción figuran en `docs/AI_F004_BABYLON_SECOND_HALF.md` y `docs/evidence/f004-local-results.json`.

## Integración

Se conserva BBY Q → w4U → QdU. Fuentes añadidas a la misma rama de la PR #47, sin fusión automática. No se actualiza la APK, no se toca la memoria del operador y no se habilitan transferencias, pagos o trading. Los resultados locales no acreditan una ejecución de GitHub Actions ni pruebas Android.
