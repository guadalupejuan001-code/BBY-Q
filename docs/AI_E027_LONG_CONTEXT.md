# E027 — contexto largo verificable en XI/Ether

## Diagnóstico de base

- **E025-Chain-1** y W4u 0.1 están publicados en main. E025 mantiene 64 temas/referencias y aprende hechos en RVPC2.
- El ingreso individual `app-turn` admite **255 bytes**; no admite un párrafo arbitrariamente largo de una sola vez.
- El diagnóstico E025 de composición medía **96/96** respuestas de un hecho y **0/48** respuestas de dos hechos. E026 trabaja separadamente esa carencia. No se debe mezclar con esta evaluación de memoria.
- El texto bruto de una conversación extensa no estaba recuperable como un archivo continuo. Tener RAM lógica disponible no es lo mismo que usarla para recuperar contexto.

## Nueva capacidad (candidato E027)

`ai/releases/e027/context-prefix.xi` añade un archivo contextual de uso explícito **dentro de XI** antes de la entrada E025 original. La inteligencia factual, las respuestas y el estado aprendido E025 permanecen sin modificaciones. No se cambia el adaptador nativo ni se usa un modelo externo.

- Hasta **512 fragmentos**, **224 bytes** cada uno: **114.688 bytes (112 KiB)** de texto UTF-8 persistente por sesión lógica. La capacidad mide *bytes*, no tokens ni ventana de atención.
- Almacena los bytes contiguos, con descriptores de offset de 24 bits y longitud de 8 bits. Esto permite buscar una cadena que cruce la frontera de dos fragmentos.
- Las órdenes XI: añadir, recuperar por índice, buscar secuencias en orden de más recientes a antiguas, contar y borrar físicamente los bytes almacenados. La búsqueda pliega ASCII mayúsculas/minúsculas; conserva bytes UTF-8 pero **no** normaliza tildes ni hace análisis semántico.
- El estado se conserva entre procesos gracias a la memoria RVPC2 y se publica atómicamente mediante `app-turn`. Una petición rechazada no guarda el fragmento.
- El borrado afecta solo al archivo E027; preserva hechos, referencias y programas E025.
- No se almacenan fragmentos de pruebas en el estado de distribución. El usuario debe ingresar contexto en su RVPC2 real para poder recuperarlo.

### Protocolo temporal

Cada instrucción de entrada sigue dentro del transporte existente de 255 bytes. Enviar fragmentos de 224 bytes o menos:

```text
@ctx add En este proyecto BBY Q conserva el conocimiento en XI/Ether.
@ctx add El contexto largo se indexa y recupera de forma persistente.
@ctx status
@ctx get 0
@ctx find XI/Ether
@ctx clear
```

`get` y `find` devuelven `#NNN <fragmento>` como evidencia inspeccionable; `find` selecciona el último fragmento que contiene la coincidencia, aunque la búsqueda se efectúa sobre el búfer continuo. La secuencia que cruza fragmentos puede requerir recuperar el fragmento siguiente por índice.

**No se afirma** una ventana de 112 KiB para inferencia automática: el razonamiento E025 sigue limitado a sus patrones y evidencia aprendida. En este primer incremento, la memoria extendida se recupera a demanda con `@ctx`. Para interpretar automáticamente párrafos completos y combinar hechos sin comandos explícitos hacen falta un extractor, un índice semántico y un puente XI de recuperación a las consultas.

## Construcción y pruebas

Ramas de desarrollo independientes; conservar el original E025 sin sobrescribir ni alterar sus hashes.

```sh
node ai/releases/e027/build.mjs /ruta/reverse_pc /ruta/evidencia-e027
node ai/releases/e027/test.mjs /ruta/reverse_pc /ruta/evidencia-e027 /ruta/test-e027
```

El workflow `.github/workflows/bbyq-e027.yml` construye el runtime original, reproduce el E025 original, prueba W4u y ejecuta las pruebas nativas de E027. Evalúa 200 fragmentos (más de 40 KiB), recuperación de posiciones distantes, búsqueda por prefijo, frase entre fragmentos, persistencia, caracteres UTF-8, rechazo de un fragmento de 225 bytes, borrado físico y ausencia de regresión de hechos aprendidos. **Los resultados se registran por la CI cuando se ejecute, no por existir este documento.**

## Siguiente iteración después de aprobar E027

1. Admisión automática de texto extenso en la UI de REVERSE-PC, con división consciente de caracteres UTF-8; no modificar aún la APK de producción.
2. Extracción de entidades/hechos en XI, con referencias a fragmentos, revocación y detección de contradicciones; separar memoria textual de conocimiento afirmado.
3. Recuperación semántica real a la consulta, uniendo el selector de E026 cuando pase sus exámenes independientes. Medir exactitud, falsos positivos, contexto adversarial y latencia.
4. Compactación de episodios con procedencia verificable y límites de almacenamiento configurables. No prometer infinitud ni equivalencia con modelos de lenguaje general.

Esta documentación no autoriza reemplazar el E025 original ni alterar la autonomía que coordina Qd, W4u y E026.
